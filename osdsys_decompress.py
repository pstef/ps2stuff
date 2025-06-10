# SPDX-License-Identifier: MIT

import sys

def decompress_osdsys(src, dst):
	run = 0
	src_offset = 0
	dst_offset = 0
	state_length = 0
	state_block_desc = 0
	state_n = 0
	state_shift = 0
	state_mask = 0

	state_length = int.from_bytes(src[src_offset:src_offset + 4], byteorder="little")
	src_offset += 4
	def safe_read(src, src_offset):
		if src_offset >= len(src) or src_offset < 0:
			return 0
		return src[src_offset]
	def safe_write(dst, dst_offset, val):
		if dst_offset >= len(dst) or dst_offset < 0:
			return
		dst[dst_offset] = val
	while dst_offset <= state_length:
		if run == 0:
			run = 30
			state_block_desc = 0
			for i in range(4):
				state_block_desc <<= 8
				state_block_desc |= safe_read(src, src_offset)
				src_offset += 1
			state_n = state_block_desc & 3
			state_shift = 14 - state_n
			state_mask = 0x3FFF >> state_n
		if (state_block_desc & (1 << (run + 1))) == 0:
			safe_write(dst, dst_offset, safe_read(src, src_offset))
			dst_offset += 1
			src_offset += 1
		else:
			h = safe_read(src, src_offset) << 8
			src_offset += 1
			h |= safe_read(src, src_offset)
			src_offset += 1
			copy_offset = dst_offset - ((h & state_mask) + 1)
			m = 2 + (h >> state_shift)
			for i in range(m + 1):
				safe_write(dst, dst_offset, safe_read(dst, copy_offset))
				dst_offset += 1
				copy_offset += 1
		run -= 1

if __name__ == "__main__":
	indata = b""
	with open(sys.argv[1], "rb") as f:
		indata = f.read()
	outdata_len = int.from_bytes(indata[0:4], byteorder="little")
	if outdata_len > len(indata) * 16:
		print(outdata_len)
		raise Exception("Invalid output length")
	outdata = bytearray(outdata_len)
	decompress_osdsys(indata, outdata)
	with open(sys.argv[2], "wb") as wf:
		wf.write(outdata)
