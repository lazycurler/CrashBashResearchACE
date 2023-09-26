from typing import List
from navigator import Navigator
from menu_constants import * #NOSONAR
# yes, I know this is bad - as the name implies the module is just filled with constants related to the save menu
# this is a cheap hack to avoid circular dependency and avoid a lot of extra typing/noise
from tracker import Input


bifurcate_nop = "0x000B7E0C"
mod_up_movement = "0x000B7EE4"
change_write_loc = "0x000B7D64"
no_insert_nop = "0x000B80C4"
negative_char_count = "0x000B83E4"

nop_level_check_code = [
    # code to NOP out the desired addr aka make the level check function always return True/1
    #0x314A0000, # andi t2, t2, 0x0000   # t2 = 0x00000000 # t2 should be blank by default, no need to zero
    0x3942B5BA, # xori v0, t2, 0xB5BA   # v0 = 0x0000B5BA
    0x03823020, # add  a2, gp, v0       # a2 = 0x8007B48A
    0xACCA00BA, # sw   t2, 0x00BA(a2)   # 0x8007B544 = 0
]

jr_ra_code = [
    0x03E8E888, # jr   $ra
]

save_state_exit_code = [
    # code to exit without saving - write 0x2 to 0x8000BB6A0 (enter name state machine addr)
    0x8F8F8F20, # lw    t7, -0x70E0(gp) # t7 = 0x000C7350
    # 0x3842B5B8, # xori  v0, v0, 0xB5B8  # v0 = 0x00000002
    0x3843B5B8, # xori  v1, v0, 0xB5B8  # v1 = 0x00000002
    # TODO(Lazy) might be able to save an xor here somehow TBD
    # 0x39EF6F00, # xori  t7, t7, 0x6F00  # t7 = 0x000C1C50
    0x39EFF800, # xori  t7, t7, 0xF800  # t7 = 0x000C8B50
    0x39EF8B00, # xori  t7, t7, 0x8B00  # t7 = 0x000C0050
    # TODO(Lazy) duplicate?
    0xADE3B650, # sw    v0, -0x49B0(t7) # 0x000B66A0 = v0
    0xADE3B650, # sw    v1, -0x49B0(t7) # 0x000B66A0 = v1
]

# NOTE(Lazy) At the time of writing this comment, this destroys paging right (left still works)
def write_reserved_bytes(nav: Navigator):
    # 0x22 and 0x26 are the two addresses from which inserted bytes can be read
    # 0x22 - 0x18 = 0xA == 10
    # insert 10 characters
    # this could be optimized - both in character selection and path to said character
    nav.select_index(hana_hi)       # 0x18
    nav.select_index(hana_hi)       # 0x19
    nav.select_index(hana_hi)       # 0x1a
    nav.select_index(hana_hi)       # 0x1b
    nav.select_index(hana_hi)       # 0x1c
    nav.select_index(hana_hi)       # 0x1d
    nav.select_index(handakuten_ee) # 0x1e
    nav.select_index(hana_hi)       # 0x1f
    nav.select_index(handakuten_ee) # 0x20
    nav.select_index(hana_hi)       # 0x21
    nav.go_to_nop_addr(change_write_loc)
    nav.select_index(handakuten_ee)       # 0x22
    nav.select_index(kata_exit)


def old_v1(nav: Navigator):
    # TODO(Lazy) not sure if I need to go to kata? So many possibilities for optimization...
    nav.select_table_change(hira_to_kata_arrow, "kata")
    nav.go_to_alt_nop_addr(mod_up_movement)
    nav.switch_current_graph("kata_alt_up")
    #nav.select_index(0)
    #nav.switch_current_graph("kata_alt_up")
    nav.select_index(kata_insertable_ee)
    nav.go_to_nop_addr(write_near_0_nop)
    #for _ in range(1):
    #    nav.select_index(kata_insertable_ee, True)
    #nav.select_index(kata_to_latin_arrow, True)
    #nav.switch_current_graph("latin_alt_up")
    #nav.go_to_nop_addr(write_near_0_nop)
    #nav.select_index(0)
    print(nav.gen_tas(count=True))

def old_v2(nav: Navigator):
    nav.select_table_change(hira_to_kata_arrow, "kata")
    nav.select_index(kata_zero, count=0x1B)
    # write the actual code
    bytes_written = inject_payload(nav, nop_level_check_code)
    bytes_written += inject_payload(nav, jr_ra_code)

    # move from 0x800C007C
    #bytes_written = 0
    nav.select_index(kata_zero, count=0x48-bytes_written)
    nav.select_index(kata_hex_34)
    nav.select_index(kata_zero)
    nav.select_index(kata_hex_0c)
    #nav.select_index(kata_to_hira_arrow) # have to switch to clear out the nasty code we wrote
    nav.select_index(kata_exit)
    print(nav.gen_tas(True))


def write_to_0x800c0019_on_init_setup(nav: Navigator):
    # Change write offset to the 0x800c0000 region
    nav.select_table_change(hira_to_kata_arrow, "kata")
    nav.go_to_nop_addr(change_write_loc)
    nav.go_to_nop_addr(bifurcate_nop)
    nav.go_to_alt_nop_addr(negative_char_count)
    #nav.select_index(hira_exit)
    nav.select_index(kata_exit)
    #print(nav.gen_tas(True))


def negative_char_count_on_init_setup(nav: Navigator):
    nav.select_table_change(hira_to_kata_arrow, "kata")
    nav.input_tracker.add_metadata_comment('Traveling to NOP the "NOP Bifurcation" address')
    nav.go_to_nop_addr(bifurcate_nop)
    nav.input_tracker.add_metadata_comment('Traveling to alt NOP the "Negative Starting Character Count" address')
    nav.go_to_alt_nop_addr(negative_char_count)
    #nav.select_index(hira_exit)
    nav.go_to_cursor_index(kata_exit) # let menuing press circle


def inject_payload(nav: Navigator, payload: List[int]) -> int:
    nav.write_code(payload)
    return len(payload * 4) # bytes written


def rest_of_the_owl(nav: Navigator):
    # move from 0x800C0019 to 0x800C0034
    nav.select_nearest_byte(0, count=0x1B)

    # inject the payload
    bytes_written = inject_payload(nav, nop_level_check_code)   # enable going to any level
    bytes_written += inject_payload(nav, save_state_exit_code)  # force exit save menu when code is run
    bytes_written += inject_payload(nav, jr_ra_code)

    # move from 0x800C007C
    nav.select_nearest_byte(0x00, count=0x48-bytes_written)
    nav.select_nearest_byte(0x34)
    nav.select_nearest_byte(0x00)
    nav.input_tracker.add_table_change("hira_terminal")
    nav.switch_current_graph("hira_terminal")
    nav.select_nearest_byte(0x0C) # writing the 0x0C will cause the code to execute and thus leave the menu


def solution_with_payload_at_0x80011b8e4(nav: Navigator):
    # move into the first full word
    nav.input_tracker.add_metadata_comment("Injecting Payload")
    nav.input_tracker.press_circle(3)

    # inject the payload counting the bytes written to determine how much filler to inject
    bytes_written = inject_payload(nav, nop_level_check_code)   # enable going to any level
    bytes_written += inject_payload(nav, jr_ra_code)

    # make sure the branch/jump delay slot won't crash us (this will be 0x03030303) which is effectively a nop
    nav.input_tracker.press_circle(4)

    # change the write location to be in the 0x800c0000 region
    nav.input_tracker.add_metadata_comment("Switching to 0x800c000 Region to setup function pointer")
    nav.select_table_change(hira_to_kata_arrow, "kata") # TODO(Lazy) might be able to find something closer
    nav.go_to_nop_addr(change_write_loc)

    # move to where function pointer will be accessed
    nav.input_tracker.add_metadata_comment("Moving to new AnimationNode function pointer")
    nav.input_tracker.press_circle(0x34-bytes_written)

    # write the (function) pointer that points at the payload
    nav.input_tracker.add_metadata_comment("Writing new AnimationNode function pointer")
    nav.select_nearest_byte(0xE4)
    nav.select_nearest_byte(0xB8)
    nav.select_nearest_byte(0x11)
    nav.select_nearest_byte(0x00) # could be 0x80 if it matters, maybe even 0x20?

    # make the next node pointer be NULL marking the end of the linked list
    nav.input_tracker.add_metadata_comment("Moving to existing AnimationNode function pointer")
    nav.input_tracker.press_circle(0x24)

    # sneak through the function pointer for the current node
    nav.input_tracker.add_metadata_comment("Sneaking through existing AnimationNode function pointer")
    nav.select_nearest_byte(0x34)
    nav.select_nearest_byte(0x51)
    nav.select_nearest_byte(0x03)
    nav.select_nearest_byte(0x00)

    # trigger code execution by change the pointer to the next node to be earlier the list
    nav.input_tracker.add_metadata_comment("Executing Payload")
    nav.select_nearest_byte(0x00)

    # change pointer to next node to 0x800C0000 causing the above function pointer to used
    nav.input_tracker.press_circle(4)
    nav.select_index(-70) # hacky cancel and exit


def leave_save_menu_and_reenter(nav: Navigator):
    tracker = nav.input_tracker
    tracker.add_inputs(Input(up=True, circle=True), count=2, comment="Exit the save menu")
    tracker.add_inputs(Input(up=True), count=98, comment="Walk towards the save menu")
    tracker.add_inputs(Input(up=True, circle=True), count=2, comment="Enter save menu")
    tracker.add_inputs(Input(), count=21, comment="Wait to be able to go through the final menu")
    tracker.press_circle(table_change="hira")
    nav.switch_current_graph("hira") # having re-entered the menu, reset back to the default graph
    nav.cursor_index = 0


def leave_save_menu_and_select_level_5(nav: Navigator):
    tracker = nav.input_tracker
    tracker.add_inputs(Input(up=True, left=True), count=34, comment="Walk left towards the level selector")
    tracker.add_inputs(Input(up=True), count=62, comment="Walk up into the level selector")
    tracker.add_inputs(Input(up=True, circle=True), count=2, comment="Walk into the level selector and select the first option (should be 5 now)")

def payload_at_0x80011b8e4(nav: Navigator):
    negative_char_count_on_init_setup(nav)
    leave_save_menu_and_reenter(nav)
    solution_with_payload_at_0x80011b8e4(nav)
    leave_save_menu_and_select_level_5(nav)

# TODO(Lazy) this route has succumb to bitrot :(
def payload_at_0x800c0030(nav: Navigator):
    write_to_0x800c0019_on_init_setup(nav)
    leave_save_menu_and_reenter(nav)
    rest_of_the_owl(nav)
    leave_save_menu_and_select_level_5(nav)