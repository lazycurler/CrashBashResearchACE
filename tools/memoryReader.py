import struct

CURSOR_INDEX_ADDR=0xc11d4
CUR_CHAR_TABLE=0xc11d8
CURSOR_TABLE_ADDR=0xbb724
CHAR_TABLE_PTR_ADDR=0xbb398
CHAR_INFO_LUT=0x5c670

# TODO(Lazy) Load Word Left? unaligned (really any load)

class MemoryReader():
    def __init__(self, bin_file):
        with open(bin_file, "rb") as dump:
            mem = dump.read()
        self.mem = mem

    @staticmethod
    def remap_addr(addr):
        # emulate the memory mirrors essentially mapping
        # 0x00000000, 0x80000000, and 0xA0000000 together
        # aka KUSEG, KSEG0, KSEG1
        top_nibble = addr >> 28
        if top_nibble == 0x8 or top_nibble == 0xA:
            addr = (addr & 0x0FFFFFFF)
        return addr

    @staticmethod
    def valid_addr(addr):
        addr = MemoryReader.remap_addr(addr)
        # this may not strictly be true, but this is the max size of ram dumps from bizhawk
        return addr <= 0x1FFFFC

    def r8u(self, addr):
        addr = self.remap_addr(addr)
        return struct.unpack('B', bytearray([self.mem[addr]]))[0]

    def r8s(self, addr):
        addr = self.remap_addr(addr)
        return struct.unpack('b', bytearray([self.mem[addr]]))[0]

    def r16u(self, addr):
        addr = self.remap_addr(addr)
        start, stop = addr, addr+2
        return struct.unpack('H', bytearray(self.mem[start:stop]))[0]

    def r16s(self, addr):
        addr = self.remap_addr(addr)
        start, stop = addr, addr+2
        return struct.unpack('h', bytearray(self.mem[start:stop]))[0]

    def r32u(self, addr):
        addr = self.remap_addr(addr)
        start, stop = addr, addr+4
        return struct.unpack('I', bytearray(self.mem[start:stop]))[0]

    def r32s(self, addr):
        addr = self.remap_addr(addr)
        start, stop = addr, addr+4
        return struct.unpack('i', bytearray(self.mem[start:stop]))[0]


def toHex(val, nbits=32):
    return f"0x{((val + (1 << nbits)) % (1 << nbits)):08X}"

# useful tools that didn't fit elsewhere so no live here
def find_address_within_range(mem: MemoryReader, desired_addr, start_addr):
    print("desired", hex(desired_addr))
    print("start", hex(start_addr))
    found = []
    desired_addr = MemoryReader.remap_addr(desired_addr)
    start_addr = MemoryReader.remap_addr(start_addr)
    min_start_addr = start_addr - 0x8000
    max_start_addr = start_addr + 0x7FFF
    min_data_addr = desired_addr - 0x8000
    max_data_addr = desired_addr + 0x7FFF
    for addr in range(min_start_addr, max_start_addr, 4):
        data = MemoryReader.remap_addr(mem.r32u(addr))
        if min_data_addr <= data <= max_data_addr:
            addr_offset = toHex(addr - start_addr)
            data_offset = toHex(data - desired_addr)
            print(f"{addr_offset}({toHex(start_addr)}) == {toHex(data)}")
            print(f"{data_offset}({toHex(data)}) == ?\n")
            addr |= 0x80000000
            found.append(addr)
    return found

def find_address_with_upper(mem: MemoryReader, desired_upper, start_addr):
    found = []
    desired_upper = MemoryReader.remap_addr(desired_upper)
    start_addr = MemoryReader.remap_addr(start_addr)
    min_start_addr = start_addr - 0x8000
    max_start_addr = start_addr + 0x7FFF
    for addr in range(min_start_addr, max_start_addr, 4):
        data = MemoryReader.remap_addr(mem.r32u(addr))
        #if MemoryReader.remap_addr(data) ^ MemoryReader.remap_addr(desired_upper) == 0:
        #    #print(toHex(min_start_addr), toHex(addr), toHex(max_start_addr), toHex(min_data_addr), toHex(data), toHex(max_data_addr), toHex((addr - start_addr)), toHex(data - desired_addr))
        #    addr |= 0x80000000
        #    found.append(addr)
        found.append((toHex(data), toHex(addr)))
    return found
