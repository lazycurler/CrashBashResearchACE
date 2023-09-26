from typing import Dict, List, Optional, Tuple
import igraph as ig
import matplotlib.pyplot as plt
from graph import Graph
import random
from dataclasses import dataclass
from PIL import Image
import glob
import os

@dataclass
class GraphInfo():
    table_name: str
    movement_graph: Graph
    ig_graph: ig.Graph
    used_edges: List[Tuple[int, int]]
    subgraph_map: Dict[int, int]

def gen_graph_infos(graph_dict: Dict[str, ig.Graph],  used_edges: Dict[str, List[Tuple[int, int]]]) -> List[GraphInfo]:
    graph_info = []
    for name, movement_graph in graph_dict.items():
        if name in used_edges:
            ig_graph, subgraph_map = create_subgraph(movement_graph, used_edges[name])
            graph_info.append(GraphInfo(name, movement_graph, ig_graph, used_edges[name], subgraph_map))
    return graph_info

def create_subgraph(movement_graph: Graph, used_edges: List[Tuple[int, int]]):
    original_graph = movement_graph.graph
    subgraph = ig.Graph(directed=original_graph.is_directed())

    # extract a list of relevant vertices
    selected_vert_indices = set()
    for edge in used_edges:
        src_vert = movement_graph.vert_from_cursor_index(edge[0]).index
        dst_vert = movement_graph.vert_from_cursor_index(edge[1]).index
        selected_vert_indices.add(src_vert)
        selected_vert_indices.add(dst_vert)

    # create mapping between original vertex indices and subgraph vertex indices
    vertex_mapping = {}
    vertices_list = []
    for v in selected_vert_indices:
        vertices_list.append(v)
        original_vertex = original_graph.vs[v]
        subgraph_vertex = subgraph.add_vertex(**original_vertex.attributes())
        vertex_mapping[v] = subgraph_vertex.index

    # remove duplicate vertex indices
    vertices_list = list(set(vertices_list))

    # add edges from the original graph that are between the specified vertices
    seen_edges = set() # track which connections have been created between vertices to prevent multiple connections
    for edge in original_graph.es():
        src_cursor_index = movement_graph.node_from_vert_index(edge.source).cursor_index
        dst_cursor_index = movement_graph.node_from_vert_index(edge.target).cursor_index
        pair = (src_cursor_index, dst_cursor_index)
        # this is a hacky way to prevent multiple edges between nodes
        # multiple edges are actually correct, but for the sake of keeping the graph clean they are ignored
        if pair in used_edges and pair not in seen_edges:
            seen_edges.add(pair)
            subgraph.add_edge(vertex_mapping[edge.source], vertex_mapping[edge.target], **edge.attributes())

    return subgraph, vertex_mapping

@dataclass
class CursorLocation():
    table_name: str
    index: int
    last_byte: int
    last_move: str
    context_info: str

# TODO(Lazy) split out the gif generation?
# TODO(Lazy) nail down framerate
# TODO(Lazy) add frame count
def gen_movement_gif(graphs:List[GraphInfo],
                     cursor_locs:List[CursorLocation],
                     route_name:str,
                     frame_durations:List[float]=[(1/60 * 1000), (1/30 * 1000), 500, 1000]): # default to ingame movement speed
                     #frame_durations:List[float]=[(1/60 * 1000)]): # default to ingame movement speed
    for frame, cursor_loc in enumerate(cursor_locs):
        last_byte = cursor_loc.last_byte
        print(last_byte)
        last_byte_str = "" if last_byte is None else f"0x{last_byte:02X}"
        info_text = f"Table:     {cursor_loc.table_name.capitalize()}\n" \
                    f"Index:     {cursor_loc.index}\n" \
                    f"Last Byte: {last_byte_str}\n" \
                    f"Last Move: {cursor_loc.last_move}\n" \
                    f"Frame:     {frame}"
        visualize(graphs=graphs,
                  cursor_loc=cursor_loc,
                  route_name=route_name,
                  show=False,
                  save=True,
                  file_number=frame,
                  subtitle=cursor_loc.context_info,
                  center_text=info_text)

    # Create the frames
    frames = []
    imgs = sorted(glob.glob(f"../graphs/{route_name}*.png"), key=os.path.getmtime)
    for i in imgs:
        new_frame = Image.open(i)
        frames.append(new_frame)

    for frame_duration in frame_durations:
        # Save into a GIF file that loops forever
        # seems like it's actually every 250 ms not every 1000ms (hence the /4.0)
        frames[0].save(f"../graphs/{route_name}_{int(frame_duration)}.gif", format="GIF",
                    append_images=frames[1:],
                    save_all=True,
                    duration=frame_duration, loop=0)


# TODO(Lazy) this should be exposed (in?)directly via argparse/ace.py but may need a once over
def visualize(graphs:List[GraphInfo],
              cursor_loc:CursorLocation,
              route_name:str,
              show: bool=True,
              save: bool=False,
              file_number:str="",
              subtitle:str="",
              center_text:str=""):
    visual_style = {}
    visual_style["bbox"] = (4000, 4000)
    visual_style["margin"] = 400
    visual_style["vertex_size"] = 1.5
    visual_style["vertex_label_size"] = 13
    visual_style["edge_width"] = 0.5
    visual_style["edge_arrow_size"] = 0.04
    #visual_style["edge_lable_dist"] = 1.5

    # the following is actually the sub title since the above is the super(?) title
    fig, axs = plt.subplots(1, len(graphs), sharey='row', figsize=(16, 9))
    fig.subplots_adjust(hspace = .5, wspace=.001)
    random.seed(62) # make sure the layout never changes
    for ax, graph_info in zip(axs, graphs):
        ig_graph = graph_info.ig_graph
        #ig_graph.vs["label"] = ig_graph.vs["name"]
        #print(ig_graph.es["direction"])
        #ig_graph.es["label"] = ig_graph.es["direction"]
        ig_graph.vs["color"] = ["aliceblue"]
        if cursor_loc is not None and graph_info.table_name == cursor_loc.table_name:
            original_vertex_id = graph_info.movement_graph.vert_from_cursor_index(cursor_loc.index).index
            color_index = graph_info.subgraph_map[original_vertex_id]
            ig_graph.vs[color_index]["color"] = "steelblue4"
        layout = ig_graph.layout("fruchterman_reingold")
        ax.set_title(f"{graph_info.table_name.capitalize()} Character Table", y=-0.1, fontsize=24)
        #ax.patch.set_edgecolor('grey')
        #ax.patch.set_linewidth('2')
        ig.plot(ig_graph, target=ax, layout=layout, **visual_style)

    plt.suptitle("Cursor Navigation Path", fontsize=24)
    text_style = {}
    text_style["ha"] = "center"
    text_style["va"] = "center"
    text_style["multialignment"] = "left"
    text_style["transform"] = plt.gcf().transFigure
    text_style["family"] = "monospace"
    text_style["fontsize"] = 24
    plt.text(0.50, 0.90, subtitle, **text_style)
    text_style["fontsize"] = 16
    plt.text(0.50, 0.80, center_text, **text_style)
    #plt.text(0.10, 0.05, "Centered Left Text", **text_style)
    #plt.text(0.90, 0.05, "Centered Right Text", **text_style)


    if save:
        print(f"saving: {file_number}")
        plt.savefig(f"../graphs/{route_name}{file_number}.png", dpi=100)

    if show:
        plt.show()

    plt.close("all")