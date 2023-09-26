from charTable import CharTable
from graph import Graph
from typing import Dict, List
import tracker

#TODO (Lazy) debug should be a member variable, not per function

class Navigator:
    def __init__(self, graph_dict: Dict[str, Graph], starting_graph: str):
        self.graph_dict = graph_dict
        self.starting_graph = starting_graph
        self.cur_graph = self.graph_dict[starting_graph]
        self.cursor_index = 0
        self.input_tracker = tracker.InputTracker(self.starting_graph)

    def add_graph_from_char_table(self, name: str, char_table: CharTable):
        assert isinstance(name, str)
        self.graph_dict[name] = Graph.from_char_table(char_table)

    def switch_current_graph(self, name: str, new_index: int=None):
        assert isinstance(name, str)
        self.cur_graph = self.graph_dict[name]
        if new_index:
            self.cursor_index = new_index

    def go_to_cursor_index(self, index: int, debug=False):
        start = self.cur_graph.vert_from_cursor_index(self.cursor_index)
        finish = self.cur_graph.vert_from_cursor_index(index)
        moves = self.cur_graph.get_moves(start, finish, debug)
        self.input_tracker.add_moves(moves)
        self.cursor_index = self.cur_graph.node_from_vert(finish).cursor_index

    def select_index(self,
                     index: int,
                     count: int=1,
                     byte_selected: bool=None,
                     table_change: str=None,
                     comment: str=None,
                     debug: bool=False):
        self.go_to_cursor_index(index, debug)
        self.input_tracker.press_circle(count=count,
                                        byte_selected=byte_selected,
                                        table_change=table_change,
                                        comment=comment)

    def select_table_change(self, index: int, table_name: str, debug=False):
        self.go_to_cursor_index(index, debug)
        self.input_tracker.press_circle(count=1,
                                        byte_selected=None,
                                        table_change=table_name)
        self.switch_current_graph(table_name)

    def go_to_nop_addr(self, nop_addr: str, debug: bool=False):
        start = self.cur_graph.vert_from_cursor_index(self.cursor_index)
        finish = self.cur_graph.vert_from_nop_addr(nop_addr)
        moves = self.cur_graph.get_moves(start, finish, debug)
        self.input_tracker.add_moves(moves)
        self.cursor_index = self.cur_graph.node_from_vert(finish).cursor_index

    def go_to_alt_nop_addr(self, alt_nop_addr: str, debug: bool=False):
        start = self.cur_graph.vert_from_cursor_index(self.cursor_index)
        finish = self.cur_graph.vert_from_alt_nop_addr(alt_nop_addr)
        moves = self.cur_graph.get_moves(start, finish, debug)
        self.input_tracker.add_moves(moves)
        self.cursor_index = self.cur_graph.node_from_vert(finish).cursor_index

    def go_to_nearest_byte(self, byte: int, depth_limit=999, dead_ends_allowed: bool=False, debug: bool=False):
        start = self.cur_graph.vert_from_cursor_index(self.cursor_index)
        finish_node = self.cur_graph.get_closest_node_from_byte(byte, self.cursor_index, depth_limit, dead_ends_allowed, debug)
        assert finish_node is not None, f'Unable to find a node containing 0x{byte:02X}'
        finish = self.cur_graph.vert_from_vert_index(finish_node.vert)
        if debug:
            print(f"Getting moves from: {self.cur_graph.node_from_vert(start)} to {self.cur_graph.node_from_vert(finish)}")
        moves = self.cur_graph.get_moves(start, finish, debug)
        self.input_tracker.add_moves(moves)
        self.cursor_index = self.cur_graph.node_from_vert(finish).cursor_index

    def select_nearest_byte(self, byte: int, count: int=1, depth_limit=999, dead_ends_allowed: bool=False, comment: str=None, debug: bool=False):
        self.go_to_nearest_byte(byte, depth_limit, dead_ends_allowed, debug)
        self.input_tracker.press_circle(count=count, byte_selected=byte, comment=comment)

    # this is essentially just a greedy bfs search of the bytes needed
    # TODO(Lazy) for bytes with multiple nodes, pathing could be improved to pick the "best" series of nodes
    # for a given set of instructions. I'm 99.9% sure this is an NP (complete?) problem
    def write_code(self, instructions: List[int], debug=False):
        def _debug(count, byte):
            if debug:
                print(f"Current index: {self.cursor_index}")
                print(f"Locating Byte 0 of instruction {count}: 0x{byte:02X}")

        for count, instruction in enumerate(instructions):
            byte0 = instruction & 0x000000FF
            byte1 = (instruction & 0x0000FF00) >> 8
            byte2 = (instruction & 0x00FF0000) >> 16
            byte3 = (instruction & 0xFF000000) >> 24
            _debug(count, byte0) if debug else None
            self.select_nearest_byte(byte0)
            _debug(count, byte1) if debug else None
            self.select_nearest_byte(byte1)
            _debug(count, byte2) if debug else None
            self.select_nearest_byte(byte2)
            _debug(count, byte3) if debug else None
            self.select_nearest_byte(byte3)

        if debug:
            print("Done writing a section of code...")

    # TODO(Lazy) maybe return count?
    def gen_tas(self, count: bool=False, compress: bool=True):
        if compress:
            self.input_tracker.compress()
        if count:
            print(len(self.input_tracker.meta_inputs))
        return f"\n\n\n{self.input_tracker.gen_tas_studio_string()}"

    # TODO(Lazy) add typing
    def reset(self, starting_graph=None):
        self.cursor_index = 0
        self.input_tracker.inputs.clear()
        if starting_graph:
            self.cur_graph = self.graph_dict[starting_graph]