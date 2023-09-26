from charTable import CharTable
from memoryReader import MemoryReader
from charTable import get_move_addrs, get_move_datas


def addrs():
    one_mem = MemoryReader("../saveStates/coco_nom.bin")
    two_mem = MemoryReader("../saveStates/hardware.bin")

    #debug_graph = Graph.from_char_table(CharTable(debug_mem, table_id=0, cursor_index=96))#, search_depth=10)
    one_char_table = CharTable(one_mem, table_id=0, alt_up_movement=False)
    two_char_table = CharTable(two_mem, table_id=0, alt_up_movement=False)

    one_addrs = []
    two_addrs = []
    for index in range(-2500, 500):
        one_addrs.extend(get_move_addrs(one_char_table, index, False))
        two_addrs.extend(get_move_addrs(two_char_table, index, False))

    one_addrs = sorted(set(one_addrs))
    two_addrs = sorted(set(two_addrs))
    #for (one_addr, two_addr) in zip(one_addrs, two_addrs):
    #    #print(f"0x{one_addr:08X}", f"0x{one_addr:08X}")
    #    print(f"0x{one_addr[0]:08X}", f"0x{two_addr[0]:08X}", f"{one_addr[1]}", f"{two_addr[1]}")

    difference_result = set(one_addrs).symmetric_difference(set(two_addrs))
    addrs_difference_result = list(difference_result)

    #print("diff", len(addrs_difference_result))
    ones = list(set(one_addrs) - set(two_addrs))
    twos = list(set(two_addrs) - set(one_addrs))
    info = []
    for (ones, twos) in zip(ones, twos):
        one_info = f"1 | {ones[2]}) 0x{ones[0]:08X}", f"{ones[1]}"
        two_info = f"2 | {twos[2]}) 0x{twos[0]:08X}", f"{twos[1]}"
        info.append(one_info)
        info.append(two_info)
    info = sorted(info)
    for msg in info:
        print(msg)



def main():
    addrs()

if __name__ == "__main__":
    main()