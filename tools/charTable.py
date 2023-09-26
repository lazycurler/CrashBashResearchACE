from ctypes import c_int, c_ubyte
from nodeInfo import NodeInfo
from typing import List

CURSOR_INDEX_ADDR=0xc11d4
CUR_CHAR_TABLE=0xc11d8
CURSOR_TABLE_ADDR=0xbb724
CHAR_TABLE_PTR_ADDR=0xbb398
CHAR_INFO_LUT=0x5c670

# helpers for CharTable
def add32BitNumbers(a, b):
    res = a + b
    if res > 2**32:
        res = res - 2^32
    return res

def lShift32BitNumber(num, amount):
    res = num * (2**amount)
    if res > 2**32:
        res = res - 2**32
    return res

# interface for accessing various bytes/words of the character table(s) both in and out of "bounds"
class CharTable():
    def __init__(self, mem, table_id=0, cursor_index=0, alt_up_movement=False):
        self.mem = mem
        self.table_id = table_id
        self.cursor_index = cursor_index
        self.alt_up_movement = alt_up_movement

    # gets the current table index - aka charTableAddr + cursorLoc
    # this also takes the table id into account
    def get_table_index(self, offset=0):
        char_table_addr = self.mem.r32u(CHAR_TABLE_PTR_ADDR + self.table_id*5*4)
        return char_table_addr + (self.cursor_index * 0x10 + offset)

    # for determining what the result of the switch case might be (if "X" or "O" was pressed)
    def get_switch_case(self):
        addr = self.get_table_index(8)
        return self.mem.r16u(addr)

    # check for dakuten/handakuten case (as seen in the insertCharacter function)
    # TODO(Lazy) verify this is correct
    def is_modifier_char(self, input_char=None):
        if input_char is None:
            input_char = self.get_insert_byte()
        input_char = int(c_ubyte(input_char).value)
        always_zero_maybe = 0
        #return ((self.mem.r8u(CHAR_INFO_LUT + input_char + 0x100*self.table_id) & 2) != 0)
        return ((self.mem.r8u(CHAR_INFO_LUT + input_char + 0x100*always_zero_maybe) & 2) != 0)

    # assuming the 0th case (cursor over a regular character) what byte would be added to the save name str
    def get_insert_byte(self):
        ptr = self.get_table_index(4)
        addr = self.mem.r32u(ptr)
        #print(f"ptr: 0x{ptr:08X}, addr: 0x{addr:08X}")
        return self.mem.r8u(addr)

    # TODO(Lazy) should alt be an option or should this return a tuple?
    def get_nop_addr(self, alt=False):
        if alt:
            index=self.cursor_index
            offset=lShift32BitNumber(index, 2)
            offset=add32BitNumbers(offset, index)
            offset=lShift32BitNumber(offset, 2)
            #offset=add32BitNumbers(offset, index) this is the line that gets NOP'd out
            offset=lShift32BitNumber(offset, 3)
        else:
            offset = self.cursor_index*0xa8
        return add32BitNumbers(CURSOR_TABLE_ADDR, offset)

    def get_node_info(self, vert_id):
        insert_byte = 0
        modifier = False
        hazard = True
        try:
            # it's possible for this check to access invalid memory
            insert_byte = self.get_insert_byte()
            modifier = self.is_modifier_char()
            hazard = False # if the lookup didn't cause an exception then no problem/hazard
        except IndexError:
            # hacky, but this isn't production :p
            pass

        return NodeInfo(vert_id,
                        self.get_nop_addr(),
                        self.get_nop_addr(alt=True),
                        modifier,
                        self.cursor_index,
                        insert_byte,
                        self.get_switch_case(),
                        hazard,
                        self.is_dead_end())

    def get_left_move_index(self):
        addr = self.get_table_index(0xa)
        #print(hex(addr))
        return self.mem.r8s(addr)

    def get_right_move_index(self):
        addr = self.get_table_index(0xb)
        return self.mem.r8s(addr)

    def get_up_move_index(self, combo_move=False):
        # multi_move True when this up is pressed in combo with another button
        if self.alt_up_movement:
            if combo_move:
                return -1
            else:
                return add32BitNumbers(self.cursor_index, self.cursor_index)
        addr = self.get_table_index(0xc)
        #print(hex(addr))
        return self.mem.r8s(addr)

    def get_down_move_index(self):
        addr = self.get_table_index(0xd)
        return self.mem.r8s(addr)

    def move_l(self):
        self.cursor_index += self.get_left_move_index()

    def move_r(self):
        self.cursor_index += self.get_right_move_index()

    def move_u(self):
        if self.alt_up_movement:
            self.cursor_index = self.get_up_move_index()
        else:
            self.cursor_index += self.get_up_move_index()

    def move_d(self):
        self.cursor_index += self.get_down_move_index()

    def move_lu(self):
        self.cursor_index += self.get_left_move_index() + self.get_up_move_index(combo_move=True)

    def move_ld(self):
        self.cursor_index += self.get_left_move_index() + self.get_down_move_index()

    def move_ru(self):
        self.cursor_index += self.get_right_move_index() + self.get_up_move_index(combo_move=True)

    def move_rd(self):
        self.cursor_index += self.get_right_move_index() + self.get_down_move_index()

    def move_lr(self):
        self.cursor_index += self.get_left_move_index() + self.get_right_move_index()

    def move_ud(self):
        # not a combo move since it's first and thus the register isn't stale (in the same way)
        self.cursor_index += self.get_up_move_index() + self.get_down_move_index()

    def move_lru(self):
        self.cursor_index += self.get_left_move_index() + self.get_right_move_index() + self.get_up_move_index(combo_move=True)

    def move_rud(self):
        self.cursor_index += self.get_right_move_index() + self.get_up_move_index(combo_move=True) + self.get_down_move_index()

    def move_lrd(self):
        self.cursor_index += self.get_left_move_index() + self.get_right_move_index() + self.get_down_move_index()

    def move_lud(self):
        self.cursor_index += self.get_left_move_index() + self.get_up_move_index(combo_move=True) + self.get_down_move_index()

    def move_lrud(self):
        self.cursor_index += self.get_left_move_index() + self.get_right_move_index() + self.get_up_move_index(combo_move=True) + self.get_down_move_index()

    def get_move_options(self):
        return [("L", self.move_l),
                ("R", self.move_r),
                ("U", self.move_u),
                ("D", self.move_d),
                ("LU", self.move_lu),
                ("LD", self.move_ld),
                ("RU", self.move_ru),
                ("RD", self.move_rd),
                ("LR", self.move_lr),
                ("UD", self.move_ud),
                ("LRU", self.move_lru),
                ("RUD", self.move_rud),
                ("LRD", self.move_lrd),
                ("LUD", self.move_lud),
                ("LRUD", self.move_lrud),
                ]

    def is_dead_end(self):
        dead_end = True
        starting_index = self.cursor_index
        for _, move_func in self.get_move_options():
            old_index = self.cursor_index
            move_func()
            if self.cursor_index != old_index:
                dead_end = False
                break
        self.cursor_index = starting_index
        return dead_end

# below are some older functions used for testing/debugging

def get_base_opcodes(mem, debug=False):
    # technically this will include a few characters that aren't selectable, but I'll live with that for now
    ops = []
    for table, size in [(0, 63), (1, 62), (2, 36)]:
        char_table_addr = mem.r32u(CHAR_TABLE_PTR_ADDR + table*5*4)
        for cursor_index in range(size):
            ptr = char_table_addr + cursor_index * 0x10 + 4
            addr = mem.r32u(ptr)
            char = mem.r8u(addr)
            #print(f"{table} | {cursor_index:<2} | 0x{hex(char)[2:4].zfill(2)} | {hex(addr)}")
            ops.append(char)
    ops.sort()
    ops = [*set(ops)]
    if debug:
        for op in ops:
            print(hex(op))
    return ops

def get_routes(char_table,
               seen=None,
               path="",
               search_depth=3,
               neg_limit=c_int(0xffffee26).value,
               pos_limit=c_int(0x7fffffff).value):
    if seen is None:
        seen = {}
    if search_depth <= 0:
        return {char_table.cursor_index: path}

    for move_dir, move_func in char_table.get_move_options():
        old_index = char_table.cursor_index
        move_func()
        cur_index = char_table.cursor_index
        cur_path = f"{path}->{move_dir}"
        if cur_index not in seen and (neg_limit <= cur_index <= pos_limit):
            seen[cur_index] = cur_path
            seen.update(get_routes(char_table, seen, cur_path, search_depth-1))
        char_table.cursor_index = old_index

    return seen

def get_move_addrs(char_table: CharTable, cursor_index=None, debug=True) -> List[int]:
    old_cursor_index = None
    if cursor_index is not None:
        old_cursor_index = char_table.cursor_index
        char_table.cursor_index = cursor_index

    l = char_table.get_table_index(0xa)
    r = char_table.get_table_index(0xb)
    u = char_table.get_table_index(0xc)
    d = char_table.get_table_index(0xd)
    l_d = char_table.get_left_move_index() + cursor_index
    r_d = char_table.get_right_move_index() + cursor_index
    u_d = char_table.get_up_move_index() + cursor_index
    d_d = char_table.get_down_move_index() + cursor_index
    if debug:
        print("l", hex(l))
        print("u", hex(u))
        print("r", hex(r))
        print("d", hex(d))

    if old_cursor_index is not None:
        char_table.cursor_index = old_cursor_index

    return [(l, l_d, cursor_index), (r, r_d, cursor_index), (u, u_d, cursor_index), (d, d_d, cursor_index)]

def get_move_datas(char_table: CharTable, cursor_index=None, debug=True) -> List[int]:
    old_cursor_index = None
    if cursor_index is not None:
        old_cursor_index = char_table.cursor_index
        char_table.cursor_index = cursor_index

    l = char_table.get_left_move_index()
    r = char_table.get_right_move_index()
    u = char_table.get_up_move_index()
    d = char_table.get_down_move_index()
    if debug:
        print("l", hex(l))
        print("u", hex(u))
        print("r", hex(r))
        print("d", hex(d))

    if old_cursor_index is not None:
        char_table.cursor_index = old_cursor_index

    return [l, r, u, d]