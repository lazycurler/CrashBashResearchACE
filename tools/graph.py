from ctypes import c_int
from collections import deque
from dataclasses import dataclass
from nodeInfo import NodeInfo
from typing import List, Tuple
from subgraphTools import remove_all_terminal_subgraphs
import igraph as ig
import matplotlib.pyplot as plt
import sys
import struct
sys.setrecursionlimit(10000)

@dataclass
class Move:
    src_index: int # current cursor index before the move
    dst_index: int # future cursor index after the move
    direction: str # string representing the inputs required for this move

class Graph:
    def __init__(self, graph=None):
        if graph is None:
            self.graph = ig.Graph(directed=True)
        else:
            self.graph = graph

    @classmethod
    def from_char_table(cls, char_table, no_no_addrs=[], no_no_indices=[], search_depth=9999, remove_terminal_subgraphs=True, weighted_graph=False):
        verts, edges = Graph.gen_graph_data(char_table, search_depth=search_depth, no_no_addrs=no_no_addrs, no_no_indices=no_no_indices)
        return cls.from_verts_and_edges(verts, edges, remove_terminal_subgraphs, use_weights=weighted_graph)

    @classmethod
    def from_verts_and_edges(cls, verts, edges, remove_terminal_subgraphs=True, use_weights=False):
        actual_edges, directions, weights, = [], [], []
        for src, dst, direction in edges:
            weight = 1
            if use_weights:
                weight = 10**(len(direction)-1) # logarithmically increase weights - one button 1, two 10, etc
            weights.append(weight)
            #actual_edges.append((src.vert, dst.vert, weight))
            actual_edges.append((src.vert, dst.vert))
            directions.append(direction)
            # TODO(Lazy) make weight choices an argument?

        num_verts = len(verts)
        graph = ig.Graph(num_verts, actual_edges, directed=True)
        names, nop_addrs, alt_nop_addrs, modifiers, inserted_bytes, cases, dead_ends, hazards = [], [], [], [], [], [], [], []
        for vert in verts:
            names.append(vert.cursor_index)
            nop_addrs.append(f"0x{vert.nop_addr:08X}")
            alt_nop_addrs.append(f"0x{vert.alt_nop_addr:08X}")
            modifiers.append(vert.is_modifier)
            inserted_bytes.append(f"0x{vert.byte:02X}")
            cases.append(vert.switch_case)
            hazards.append(vert.hazard)
            dead_ends.append(vert.dead_end)
        graph.vs["name"]  = names
        graph.vs["nop_addr"]  = nop_addrs
        graph.vs["alt_nop_addr"]  = alt_nop_addrs
        graph.vs["modifier"] = modifiers
        graph.vs["byte"] = inserted_bytes
        graph.vs["case"] = cases
        graph.vs["hazard"] = hazards
        graph.vs["dead_end"] = dead_ends
        graph.es["direction"] = directions
        graph.es["weight"] = weights
        # this prevents navigating to an area from which there is no return
        if remove_terminal_subgraphs:
            _ = remove_all_terminal_subgraphs(graph)
        return cls(graph)

    @staticmethod
    def gen_graph_data(char_table,
                       seen=None,
                       search_depth=3,
                       neg_limit=c_int(0xffffee26).value,
                       pos_limit=c_int(0x7fffffff).value,
                       no_no_addrs=[],
                       no_no_indices=[]):

        verts = []
        edges = []
        if seen is None:
            seen = {}
            first_node = char_table.get_node_info(0)
            seen[first_node.cursor_index] = first_node
            verts.append(first_node)
        if search_depth <= 0:
            return verts, edges

        for move_dir, move_func in char_table.get_move_options():
            old_node = seen[char_table.cursor_index]
            # try to move in a direction e.g. press left or press right, up, and down
            move_func()

            # verify the resulting location is within the allowable range
            #TODO(Lazy) more verbose way to ignore nodes/indices
            if neg_limit <= char_table.cursor_index <= pos_limit and char_table.cursor_index not in no_no_indices:
                # note the resulting location and store the information in the directed graph
                cur_index = char_table.cursor_index

                if cur_index > 500 or cur_index < -2400:
                    char_table.cursor_index = old_node.cursor_index
                    continue

                if cur_index not in seen:
                    # TODO(Lazy) this is super hacky...
                    try:
                        cur_node = char_table.get_node_info(len(seen))
                    except struct.error:
                        print(cur_index)
                        char_table.cursor_index = old_node.cursor_index
                        continue
                else:
                    cur_node = seen[cur_index]

                if cur_node.nop_addr in no_no_addrs or cur_node.alt_nop_addr in no_no_addrs:
                    char_table.cursor_index = old_node.cursor_index
                    continue

                edges.append((old_node, cur_node, move_dir))

                if cur_node.cursor_index not in seen:
                    verts.append(cur_node)
                    seen[cur_node.cursor_index] = cur_node
                    # continue with this depth first search
                    new_verts, new_edges = Graph.gen_graph_data(char_table,
                                                                seen,
                                                                search_depth-1,
                                                                no_no_addrs=no_no_addrs,
                                                                no_no_indices=no_no_indices)
                    verts += new_verts
                    edges += new_edges

            # restore the cursor position before trying to move in a different direction
            char_table.cursor_index = old_node.cursor_index

        return verts, edges

    @staticmethod
    def node_from_vert(vert: ig.Vertex) -> NodeInfo:
        return NodeInfo(vert.index,
                        vert["nop_addr"],
                        vert["alt_nop_addr"],
                        vert["modifier"],
                        vert["name"],
                        vert["byte"],
                        vert["case"],
                        vert["hazard"],
                        vert["dead_end"])

    def vert_from_vert_index(self, index: int) -> ig.Vertex:
        return self.graph.vs[index]

    def node_from_vert_index(self, index: int) -> NodeInfo:
        return self.node_from_vert(self.vert_from_vert_index(index))

    def add_vertex(self, node: NodeInfo):
        self.graph.add_vertex(name=str(node.cursor_index), byte=f"0x{node.byte:02X}", case=(node.switch_case))

    def add_edge(self, src: NodeInfo, dst: NodeInfo, dir):
        self.graph.add_edge(str(src.cursor_index), str(dst.cursor_index), dir=dir)

    # It really feels like I'm not doing things the "igraph" way...
    def vert_from_cursor_index(self, cursor_index: int):
        # getting the first vert from the vertex sequence is chill (the indices[0] part)
        # since there can only be one vertex for each cursor index
        return self.vert_from_vert_index(self.graph.vs.select(name_eq=cursor_index).indices[0])

    def vert_from_nop_addr(self, nop_addr: str):
        nop_addr.upper() # all letters in the hex string must be uppercase
        # similar to the cursor index variant, only one nop_addr is unique per node
        return self.vert_from_vert_index(self.graph.vs.select(nop_addr_eq=nop_addr).indices[0])

    def vert_from_alt_nop_addr(self, alt_nop_addr: str):
        alt_nop_addr.upper() # all letters in the hex string must be uppercase
        # similar to the cursor index variant, only one nop_addr is unique per node
        return self.vert_from_vert_index(self.graph.vs.select(alt_nop_addr_eq=alt_nop_addr).indices[0])

    def get_moves(self, start: ig.Vertex, finish: ig.Vertex, debug=False) -> List[Move]:
        edge_path = self.graph.get_shortest_path(start, to=finish, mode=ig.OUT, weights=self.graph.es["weight"], output="epath")
        directions = []
        for eid in edge_path:
            edge = self.graph.es[eid]
            source_vert = self.graph.vs[edge.source]
            target_vert = self.graph.vs[edge.target]
            direction = edge["direction"]
            directions.append(Move(src_index=source_vert['name'], direction=direction, dst_index=target_vert['name']))
            if debug:
                print(f"{direction:4} {target_vert['name']:6}  {target_vert['byte']}")

        #if debug:
        #    path = self.graph.get_shortest_path(start, to=finish, mode=ig.OUT, weights=self.graph.es["weight"], output="vpath")
        #    print(self.graph.vs[path[0]]["name"], self.graph.vs[path[0]]["byte"])
        #    for i in range(1, len(path)):
        #        print(directions[i-1], self.graph.vs[path[i]]["name"], self.graph.vs[path[i]]["byte"], self.graph.es[eid]["weight"])
        return directions

    def is_safe_to_insert(self, cursor_index, dead_ends_allowed=False):
        node = self.node_from_vert(self.vert_from_cursor_index(cursor_index))
        return (node.switch_case == 0 and not node.hazard and (dead_ends_allowed or not node.dead_end))

    def visualize(self, show=True, save=False):
        fix, ax = plt.subplots()

        # TODO(Lazy) option for this? useful for graph debugging
        #self.graph.vs["label"] = self.graph.vs["byte"] # use resulting inserted byte as a vertex label
        #self.graph.vs["label"] = self.graph.vs["name"] # use resulting inserted byte as a vertex label
        #self.graph.es["label"] = self.graph.es["direction"]

        # TODO(Lazy) This needs a once over before being exposed
        # Right now it's in an indeterminate state used for generating the graphs for the writeup
        visual_style = {}
        #visual_style["vertex_size"] = 0.4
        visual_style["vertex_size"] = 0.10
        #visual_style["vertex_label_size"] = 20
        visual_style["edge_width"] = 0.3
        visual_style["edge_arrow_size"] = 0.004
        #ig.plot(self.graph, target=ax, edge_label=self.graph.es["label"], **visual_style)
        #ig.plot(self.graph, target=ax, edge_label=self.graph.es["weight"], **visual_style)
        import random
        random.seed(52) # make sure the layout never changes
        layout = self.graph.layout("fruchterman_reingold")

        #TODO(Lazy) REMOVE DEBUG
        #text_style = {}
        #text_style["ha"] = "center"
        #text_style["va"] = "center"
        #text_style["multialignment"] = "left"
        #text_style["transform"] = plt.gcf().transFigure
        #text_style["fontsize"] = 24
        #ig.plot(self.graph, layout=layout, target=ax, **visual_style)
        #plt.title(f"Vertices: {len(self.graph.vs)}\n Edges: {len(self.graph.es)}", **text_style, y=0.90)
        #text_style["fontsize"] = 32
        #text_style["va"] = "top"
        #plt.suptitle("Hiragana - Fully Pruned", **text_style)

        if show:
            plt.show()

    # some nice info functions
    def get_all_opcodes(self, dead_ends_allowed=False):
        ops = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            opcode = node.byte
            if node.switch_case == 0 and not node.hazard and (True if dead_ends_allowed else not node.dead_end):
                ops.append(opcode)

        # remove duplicates and sort
        ops = [*set(ops)]
        ops.sort()

        return ops

    def get_all_indices(self):
        indices = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            indices.append(node.cursor_index)

        # remove duplicates and sort
        indices.sort()

        return indices


    def get_all_cases(self):
        cases = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            cases.append(node.switch_case)

        # remove duplicates and sort
        cases.sort()

        return cases

    def get_all_byte_addrs(self, char_table):
        addrs = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            try:
                addrs.append(char_table.mem.r32u(node.cursor_index))
            except:
                continue

        # remove duplicates and sort
        addrs.sort()

        return addrs

    # TODO(Lazy) this could be more generic... e.g. match a node instead of a byte
    # TODO(Lazy) there's probably a way to do this with igraph too :(
    def bfs_byte_search(self, byte, start_index, depth_limit, dead_ends_allowed=False) -> NodeInfo:
        # returns the NodeInfo of the closest node with that byte or None if not found
        closest_node = None
        start_vert = self.graph.vs.select(name_eq=start_index).indices[0]
        queue = deque([start_vert])
        seen = {start_vert: True}
        nodes_left_in_cur_depth = 1

        def _add_neighbors(index):
            nonlocal nodes_left_in_cur_depth, seen, depth_limit
            # still haven't found desired byte - add the nearest neighbors (not yet seen) to the queue
            neighbors = self.graph.neighbors(index, mode="out")
            for neighbor in neighbors:
                if neighbor not in seen:
                    seen[neighbor] = True
                    queue.append(neighbor)
            # check if depth limit has been reached and it's time to bail on this search
            if nodes_left_in_cur_depth <= 0:
                depth_limit -= 1
                nodes_left_in_cur_depth = len(queue)

        while len(queue) > 0:# and depth_limit >= 0:
            cur_vert_index = queue.popleft()
            cur_node = self.node_from_vert_index(cur_vert_index)
            nodes_left_in_cur_depth -= 1
            if cur_node.byte == byte and self.is_safe_to_insert(cur_node.cursor_index):
                # this is our desired byte
                closest_node = cur_node
                break
            else:
                #print("No good: ", cur_node, 'safe', self.is_safe_to_insert(cur_node.cursor_index))
                #print(cur_node.byte, cur_node.byte == byte, byte)
                _add_neighbors(cur_vert_index)
                if depth_limit < 0:
                    break

        #if self.debug:
        #if True:
        #    seen_nodes = [self.node_from_vert_index(index) for index in seen.keys()]
        #    seen_tuples = [(node.byte, node.cursor_index, self.is_safe_to_insert(node.cursor_index)) for node in seen_nodes]
        #    seen_tuples.sort()
        #    print("Just got done looking for: ", byte)
        #    for seen_tuple in seen_tuples:
        #        print("saw (index, byte): ", seen_tuple)

        return closest_node

    def get_closest_node_from_byte(self, byte, cur_index=0, depth_limit=999, dead_ends_allowed=False, debug=False) -> ig.Vertex:
        # get's the node that contains the requested byte
        # returns None if not found
        # TODO(Lazy) is this wrapper needed? should an error be thrown?
        if isinstance(byte, int):
            byte = f"0x{byte:02X}"
        node = self.bfs_byte_search(byte, cur_index, depth_limit, dead_ends_allowed)
        if node is not None:
            #if debug:
            #    print(node)
            return node
        else:
            return None

    # TODO(Lazy) this should probably be moved
    # TODO(Lazy) this could be done in a more graph forward way
    def get_all_nodes_from_byte(self, byte):
        if isinstance(byte, int):
            byte = f"0x{byte:02X}"
        nodes = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            if node.switch_case == 0 and node.byte == byte:
                nodes.append(node)
        return nodes

    def get_all_nodes(self):
        nodes = []
        for vert in self.graph.vs:
            node = Graph.node_from_vert(vert)
            nodes.append(node)
        return nodes

    def pretty_print_weighted_graph(self):
        print("Vertices:")
        for vertex in self.graph.vs:
            print(f"{vertex.index}: {vertex['name']}, {vertex['byte']}")

        print("\nEdges:")
        for edge in self.graph.es:
            source = self.graph.vs[edge.source]['name']
            target = self.graph.vs[edge.target]['name']
            weight = edge['weight']
            print(f"{source} --({weight})--> {target}")
