import argparse
import os
import visualizer
from charTable import CharTable
from charTable import get_move_addrs
from graph import Graph
from memoryReader import MemoryReader
from navigator import Navigator
from routing import (
    payload_at_0x80011b8e4,
    payload_at_0x800c0030,
)
from menu_constants import hira_to_kata_arrow, hira_alt_up_index

from bad_addresses import (
    no_no_addrs,
    all_no_no_indices,
    hira_no_no_indices,
    kata_no_no_indices,
    latin_no_no_indices,
    hira_most_no_no_indices,
    hira_all_no_no_indices,
)

BIN_FILE = "saveMenuNoInitHira_j.bin"
BIN_DIR = os.path.join("..", "saveStates")
DEFAULT_BIN = os.path.join(BIN_DIR, BIN_FILE)


def generate_ace(mem, weighted):
    # have to start with the kata menu (hira and english can't make it to bifurcate the nop)
    graph_dict = {}
    graph_dict["hira"] = Graph.from_char_table(
        CharTable(mem, table_id=0),
        no_no_addrs=no_no_addrs,
        no_no_indices=hira_no_no_indices,
        weighted_graph=weighted,
    )
    graph_dict["kata"] = Graph.from_char_table(
        CharTable(mem, table_id=1),
        no_no_addrs=no_no_addrs,
        no_no_indices=kata_no_no_indices,
        weighted_graph=weighted,
    )
    graph_dict["latin"] = Graph.from_char_table(
        CharTable(mem, table_id=2),
        no_no_addrs=no_no_addrs,
        no_no_indices=latin_no_no_indices,
        weighted_graph=weighted,
    )

    # TODO(Lazy) could it be possible to rewrite memory to be able to navigate back from 0x0C? Have to load a new mem/bin dump here
    # mem_post = MemoryReader("../saveStates/hira_post_0x34.bin")
    graph_dict["hira_terminal"] = Graph.from_char_table(
        CharTable(mem, table_id=0),
        no_no_addrs=[0x000B7E44],
        no_no_indices=hira_most_no_no_indices,
        remove_terminal_subgraphs=False,
        weighted_graph=weighted,
    )

    graph_dict["kata_terminal"] = Graph.from_char_table(
        CharTable(mem, table_id=1),
        no_no_addrs=[0x000B7E44],
        no_no_indices=hira_most_no_no_indices,
        remove_terminal_subgraphs=False,
        weighted_graph=weighted,
    )

    graph_dict["latin_terminal"] = Graph.from_char_table(
        CharTable(mem, table_id=0),
        no_no_addrs=[0x000B7E44],
        no_no_indices=hira_most_no_no_indices,
        remove_terminal_subgraphs=False,
        weighted_graph=weighted,
    )

    nav = Navigator(graph_dict, "hira")
    payload_at_0x80011b8e4(nav)
    #payload_at_0x800c0030(nav)
    print(nav.input_tracker.gen_debug_string(metadata_required=True))
    print('\n')
    print(nav.gen_tas(True))

    # TODO(Lazy) expose visualization options
    # used_edges = nav.input_tracker.get_used_edges()
    # print(graph_dict)
    # print(used_edges)
    # graph_infos = visualizer.gen_graph_infos(graph_dict, used_edges)
    # visualizer.visualize(graph_infos, visualizer.CursorLocation("hira", 61), show=True, save=True)
    # cursor_locs = nav.input_tracker.get_cursor_locations()
    # visualizer.visualize(graph_infos, cursor_locs[1], "test", save=True)
    # visualizer.gen_movement_gif(graph_infos, cursor_locs, "main_route_low_res")


# TODO(Lazy) move this to it's own file?
def debug_node(index: int, table: int, mem: MemoryReader):
    debug_graph = Graph.from_char_table(
        CharTable(mem, table_id=table, cursor_index=index),
        search_depth=4,
        weighted_graph=True,
    )
    debug_char_table = CharTable(
        mem,
        table_id=table,
        cursor_index=index,
        alt_up_movement=False,
    )

    get_move_addrs(debug_char_table, cursor_index=index)
    nodes = debug_graph.get_all_nodes()
    for node in nodes:
        if node.switch_case in [1, 2]:
            print(node)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bin",
        "-b",
        type=str,
        default=DEFAULT_BIN,
        help="The location of the binary file used (relative to ../saveStates)", #TODO(Lazy) this should maybe be less hacky
    )
    parser.add_argument(
        "--weighted",
        "-w",
        action="store_true",
        help="Generate a weighted graph where multiple inputs cost exponentially more." \
            "Better suited for humans where fewer multiple directional inputs are desired." \
            "WARNING: If this is a new route, this will almost assuredly require debug work.",
    )

    ## debug args
    parser.add_argument(
        "--debug_index",
        "-dn",
        type=int,
        default=None,
        help="Prints out helpful information about a given index. If no --debug_table is specified 0/hira will be used",
    )
    parser.add_argument(
        "--debug_table",
        "-dt",
        type=int,
        default=0,
        help="Provides a way to specify which table to use when debugging an index. REQUIRES --debug_index (-dn)",
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    mem = MemoryReader(args.bin)
    if args.debug_index is not None:
        debug_node(args.debug_index, args.debug_table, mem)
    else:
        generate_ace(mem, args.weighted)

if __name__ == "__main__":
    main()