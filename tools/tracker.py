from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from graph import Move
from copy import deepcopy
from visualizer import CursorLocation

@dataclass
class Input:
    up: bool = False       # U
    down: bool = False     # D
    left: bool = False     # L
    right: bool = False    # R
    triangle: bool = False # T
    cross: bool = False    # X
    square: bool = False   # Q
    circle: bool = False   # O
    # TODO(Lazy) Add other buttons in the future
    ALL_INPUT_LINE = "|    0,....|  128,  128,  128,  128,UDLR..TXQO.......|"
    NO_INPUT_LINE  = "|    0,....|  128,  128,  128,  128,.................|"

    @classmethod
    def from_str(cls, string):
        up = "U" in string
        down = "D" in string
        left = "L" in string
        right = "R" in string
        triangle = "T" in string
        cross = "X" in string
        square = "Q" in string
        circle = "O" in string
        return cls(up, down, left, right, triangle, cross, square, circle,)

    def tas_str(self) -> str:
        # Note, currently all analog directions are set to "no movement"
        u = "U" if self.up else "."
        d = "D" if self.down else "."
        l = "L" if self.left else "."
        r = "R" if self.right else "."
        t = "T" if self.triangle else "."
        x = "X" if self.cross else "."
        q = "Q" if self.square else "."
        o = "O" if self.circle else "."

        return f"|    0,....|  128,  128,  128,  128,{u}{d}{l}{r}..{t}{x}{q}{o}.......|"

    def direction_str(self) -> str:
        u = "U" if self.up else ""
        d = "D" if self.down else ""
        l = "L" if self.left else ""
        r = "R" if self.right else ""
        return f"{u}{d}{l}{r}"

    def is_directional(self) -> bool:
        return len(self.direction_str()) > 0

    def is_selection(self) -> bool:
        return (self.circle or self.cross)

    def is_blank(self) -> bool:
        return not (self.up \
            and self.down \
            and self.left \
            and self.right \
            and self.triangle \
            and self.cross \
            and self.square \
            and self.circle)

    def is_pure_directional(self) -> bool:
        return self.is_directional() and not self.is_selection()

    def is_pure_selection(self) -> bool:
        return self.is_selection() and not self.is_directional()


@dataclass
class Metadata():
    src_index: Optional[int] = None # current index before this input is registered
    dst_index: Optional[int] = None # future index after this input is registered
    byte_selected: Optional[int] = None
    table_change: Optional[str] = None # used to mark what table is currently being used
    comment: Optional[str] = None # any other meta information desired

    def is_none(self):
        return (self.src_index is None \
                and self.dst_index is None \
                and self.byte_selected is None \
                and self.table_change is None \
                and self.comment is None)

@ dataclass
class MetaInput():
    input: Input
    metadata: Optional[Metadata] = None


class InputTracker():
    BLANK_INPUT=Input.from_str(Input.NO_INPUT_LINE)
    BLANK_META_INPUT = MetaInput(BLANK_INPUT)

    def __init__(self, start_table):
        self.meta_inputs = []
        self.start_table = start_table

    def add_blank(self, count:int=1):
        for _ in range(count):
            self.meta_inputs.append(self.BLANK_META_INPUT)

    def add_inputs(self, an_input: Input, count=1, comment=None):
        meta_input = MetaInput(an_input, Metadata(comment=comment))
        self.meta_inputs.append(meta_input)
        if count > 1:
            meta_input = MetaInput(an_input)
            for _ in range(count-1):
                self.meta_inputs.append(meta_input)

    def add_input_list(self, inputs: List[Input]):
        self.meta_inputs += [MetaInput(an_input) for an_input in inputs]

    def add_meta_input(self, meta_input: MetaInput):
        self.meta_inputs.append(meta_input)

    def add_meta_input_list(self, meta_inputs: List[MetaInput]):
        self.meta_inputs += meta_inputs

    def add_input_from_strings(self, directions: List[str]):
        new_input = []
        for direction in directions:
            action = (Input.from_str(direction))
            new_input.append(action)
            new_input.append(action)
            new_input.append(Input.NO_INPUT_LINE)
            new_input.append(Input.NO_INPUT_LINE)
        self.add_input_list(new_input)

    def add_moves(self, moves: List[Move]):
        for move in moves:
            an_input = Input.from_str(move.direction)
            # only add the meta information to the first set of input for a given move
            self.meta_inputs.append(MetaInput(an_input, Metadata(move.src_index, move.dst_index)))
            self.meta_inputs.append(MetaInput(an_input))
            # insert two blank frames
            # the game needs two frames before it can process the same input again
            self.add_blank(2)

    def press_circle(self, count:int=1, byte_selected: int=None, table_change:str=None, comment: str=None):
        metadata_full = Metadata(byte_selected=byte_selected, table_change=table_change, comment=comment)
        metadata_byte = Metadata(byte_selected=byte_selected)
        circle_with_full_data = MetaInput(Input.from_str("O"), metadata_full)
        circle_with_byte = MetaInput(Input.from_str("O"), metadata_byte)
        circle = MetaInput(Input.from_str("O"))

        # add initial circle press with full metadata
        self.meta_inputs.append(circle_with_full_data)
        self.meta_inputs.append(circle)
        self.add_blank(2)

        # add additional presses with minimal metadata
        for _ in range(count-1):
            self.meta_inputs.append(circle_with_byte)
            self.meta_inputs.append(circle)
            self.add_blank(2)

    def add_metadata_comment(self, comment: str):
        assert len(self.meta_inputs) > 0, "To add a comment to the last entry there must be at least 1 entry"
        last_input = deepcopy(self.meta_inputs[-1])
        if last_input.metadata is None:
            last_input.metadata = Metadata(comment=comment)
        else:
            last_input.metadata.comment = comment
        self.meta_inputs[-1] = last_input

    def add_table_change(self, table: str):
        assert len(self.meta_inputs) > 0, "To add a table change to the last entry there must be at least 1 entry"
        last_input = deepcopy(self.meta_inputs[-1])
        if last_input.metadata is None:
            last_input.metadata = Metadata(table=table)
        else:
            last_input.metadata.table = table
        self.meta_inputs[-1] = last_input

    def get_used_edges(self) -> Dict[str, List[Tuple[int, int]]]:
        used_edges = {}
        cur_table = self.start_table
        used_edges[cur_table] = []

        # find all the edges used for each table
        for meta_input in self.meta_inputs:
            metadata = meta_input.metadata
            if metadata is None:
                continue

            # check for a table change and verify used_edges contains this table
            table = metadata.table_change
            if table is not None and table != "":
                cur_table = table
                if cur_table not in used_edges:
                    used_edges[cur_table] = []

            # add the index for the current input to the current table
            if metadata.src_index is not None or metadata.dst_index is not None:
                assert metadata.src_index is not None, "src None: Both src and dst index must not be None to compute edges"
                assert metadata.dst_index is not None, "dst None: Both src and dst index must not be None to compute edges"
                used_edges[cur_table].append((metadata.src_index, metadata.dst_index))

        # remove duplicates form each of the list of used edges
        for seen_table in used_edges.keys():
            used_edges[seen_table] = list(set(used_edges[seen_table]))

        return used_edges

    def get_cursor_locations(self) -> List[CursorLocation]:
        cursor_locations = []
        old_table = self.start_table
        old_index = None
        cur_table = self.start_table
        cur_index = None
        last_byte = None
        last_direction = ""
        context_info = ""

        for meta_input in self.meta_inputs:
            direction = meta_input.input.direction_str()
            metadata = meta_input.metadata
            if metadata is not None:
                if metadata.table_change is not None:
                    cur_table = metadata.table_change
                    cur_index = None
                if metadata.src_index is not None:
                    cur_index = metadata.src_index
                if metadata.byte_selected is not None:
                    last_byte = metadata.byte_selected
                if direction != "":
                    last_direction = direction
                if metadata.comment is not None:
                    context_info = metadata.comment

            if cur_index is not None:
                cursor_locations.append(CursorLocation(cur_table, cur_index, last_byte, last_direction, context_info))
                old_table = cur_table
                old_index = cur_index
            else:
                # in the transition to the next table but don't yet know the new index
                cursor_locations.append(CursorLocation(old_table, old_index, None, last_direction, context_info))

        return cursor_locations

    def compress(self, debug: bool=False):
        # removes blank frames between movements that don't share any buttons
        # extremely hacky as this is the end of the project for me and I'm running out of steam here
        compressed_inputs = []
        def _remove_middle_inputs():
            del compressed_inputs[-2]
            del compressed_inputs[-2]
            if debug:
                print(i, curr_direction, prev_direction)

        for i, meta_input in enumerate(self.meta_inputs):
            compressed_inputs.append(meta_input)
            if i < 4:
                continue
            curr_input = self.meta_inputs[i].input
            pre0_input = self.meta_inputs[i-1].input
            pre1_input = self.meta_inputs[i-2].input
            pre2_input = self.meta_inputs[i-3].input

            # detect a set of 4 inputs where:
            # the first is a movement
            # there is a two frame break
            # followed by another movement
            if (curr_input.is_directional()
                and pre0_input.is_blank()
                and pre1_input.is_blank()
                and pre2_input.is_directional()):

                curr_direction = curr_input.direction_str()
                prev_direction = pre2_input.direction_str()
                if not set(curr_direction).intersection(set(pre2_input.direction_str())):
                    _remove_middle_inputs()

            # alternatively compress unrelated directional and selection inputs
            if ((curr_input.is_pure_selection()
                and pre0_input.is_blank()
                and pre1_input.is_blank()
                and pre2_input.is_pure_directional())
                or
               (curr_input.is_pure_directional()
                and pre0_input.is_blank()
                and pre1_input.is_blank()
                and pre2_input.is_pure_selection())):
                _remove_middle_inputs()

        self.meta_inputs = compressed_inputs

    def gen_tas_studio_string(self) -> str:
        return "\n".join([meta_input.input.tas_str() for meta_input in self.meta_inputs]) + "\n\n\n\n"

    # TODO(Lazy) May wish to add file read/write support in the future
    # TODO(Lazy) Reduce cognitive complexity of this function someday
    def gen_debug_string(self, metadata_required: bool=True, all_frames: bool=False) -> str:
        line_separator ="|-----------------------------|\n"
        def safe_str(s: str):
            return "" if s is None else s

        def add_table_break(table: str):
            table_str = line_separator
            table_str += f"| Table Change: {table}\n"
            table_str += line_separator
            return table_str

        debug_str = ""
        debug_str += add_table_break(self.start_table)
        debug_str += "| move |  from |  to   | byte |\n"
        debug_str += "|------|-------|-------|------|\n"

        for meta_input in self.meta_inputs:
            input_str, src, dst, byte, table, comment = "", "", "", "", "", ""
            metadata = meta_input.metadata
            check_circle = False
            no_data = True

            # check for any directional input
            if meta_input.input is not None:
                input_str = meta_input.input.direction_str()

            # make sure this entry contains useful debug information
            if (metadata is not None and not metadata.is_none()):
                no_data = False
                # check to see if a character is being inserted at this location
                selected_byte = metadata.byte_selected
                if metadata.byte_selected is not None:
                    check_circle = True
                    byte = f"0x{selected_byte:02X}"
                src = safe_str(metadata.src_index)
                dst = safe_str(metadata.dst_index)
                table = safe_str(metadata.table_change)
                if table != "":
                    debug_str += add_table_break(table)
                comment = safe_str(metadata.comment)
            # no metadata available
            elif not metadata_required or all_frames:
                check_circle = True

            if (check_circle or all_frames) and meta_input.input.circle:
                input_str += "O"
                no_data = False

            if no_data and not all_frames:
                continue

            debug_str += f"| {input_str:<4} | {src:5} | {dst:5} | {byte:4} | {comment}\n"

        debug_str += line_separator
        debug_str += f"| Frames: {len(self.meta_inputs):5}{'':15}|\n"
        debug_str += line_separator
        return debug_str