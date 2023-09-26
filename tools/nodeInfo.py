from dataclasses import dataclass

@dataclass
class NodeInfo():
    #TODO(Lazy) should these be strings?
    vert: int # hacky way to keep track of which vertex this is associated with
    nop_addr: int # the address that will be NOP'd if the cursor is here
    alt_nop_addr: int # the address that will be NOP'd if the index math is changed (NOP'd) effectively resulting in a bifurcated NOP stream
    is_modifier: int # whether the would be inserted character is treated as a "modified" character aka (han)dakuten
    cursor_index: int # the location of the blinking, player-controlled, cursor. Starts at 0 which is the upper left corner of the menu
    byte: int # the byte that would be inserted (assuming the user pressed "X" and valid switch case)
    switch_case: int # the resulting action if a user was to press "X" at this index
    hazard: bool # Some lookups result in invalid memory access - whether or not "byte" is valid
    dead_end: bool # If False, node has at least one outgoing edge (to another node). If True, you can never leave; Hotel California.