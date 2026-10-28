#!/usr/bin/env python3
"""Limit the legacy Hi3660 HWC to its native-resolution display config.

The vendor blob advertises three HWC configs but its ROG implementation
reports the same native dimensions for all of them. Internally, the configs
select native, 1080-pixel-wide, and 720-pixel-wide composition buffers. Keep
only the native one.
"""

import pathlib
import struct
import sys


PATCHES = {
    # class, e_machine, full function signature before, bytes to replace
    # within the function, replacement, patched function signature
    1: (
        40,
        bytes.fromhex(
            "91b1806c30b10120002a08600cd00020106009e00320002a086005d0012002210023c2e90010936000207047"
        ),
        4,
        bytes.fromhex("30b1"),
        bytes.fromhex("00bf"),
        bytes.fromhex(
            "91b1806c00bf0120002a08600cd00020106009e00320002a086005d0012002210023c2e90010936000207047"
        ),
    ),
    2: (
        183,
        bytes.fromhex(
            "210200b4088840b9c8000034e8030032280000b9820100b45f0000b90a000014e8070032280000b9e20000b4080200d0009144fde0031f2a5f0800b9400000fdc0035fd6e0031f2ac0035fd6"
        ),
        8,
        bytes.fromhex("c8000034"),
        bytes.fromhex("1f2003d5"),
        bytes.fromhex(
            "210200b4088840b91f2003d5e8030032280000b9820100b45f0000b90a000014e8070032280000b9e20000b4080200d0009144fde0031f2a5f0800b9400000fdc0035fd6e0031f2ac0035fd6"
        ),
    ),
}


def fail(message):
    raise ValueError(message)


def executable_loads(data, elf_class):
    if elf_class == 1:
        if len(data) < 52:
            fail("truncated ELF32 header")
        phoff = struct.unpack_from("<I", data, 28)[0]
        phentsize, phnum = struct.unpack_from("<HH", data, 42)
        minimum_entry_size = 32
    else:
        if len(data) < 64:
            fail("truncated ELF64 header")
        phoff = struct.unpack_from("<Q", data, 32)[0]
        phentsize, phnum = struct.unpack_from("<HH", data, 54)
        minimum_entry_size = 56

    if phentsize < minimum_entry_size or phnum == 0:
        fail("invalid ELF program header table")
    if phoff > len(data) or phnum > (len(data) - phoff) // phentsize:
        fail("truncated ELF program header table")

    loads = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        if elf_class == 1:
            p_type, p_offset, p_vaddr, _p_paddr, p_filesz, _p_memsz, p_flags, _p_align = (
                struct.unpack_from("<8I", data, offset)
            )
        else:
            p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, _p_memsz, _p_align = (
                struct.unpack_from("<II6Q", data, offset)
            )
        if p_type == 1 and p_flags & 1:
            if p_offset > len(data) or p_filesz > len(data) - p_offset:
                fail("executable PT_LOAD exceeds file bounds")
            loads.append((p_offset, p_offset + p_filesz))
    if not loads:
        fail("ELF has no executable PT_LOAD")
    return loads


def patch_blob(path):
    target = pathlib.Path(path)
    data = target.read_bytes()
    if len(data) < 20 or data[:4] != b"\x7fELF":
        fail(f"{target}: not an ELF file")
    elf_class = data[4]
    if elf_class not in PATCHES or data[5] != 1 or data[6] != 1:
        fail(f"{target}: unsupported or malformed ELF identification")

    machine, before, patch_offset, old_bytes, new_bytes, after = PATCHES[elf_class]
    actual_machine = struct.unpack_from("<H", data, 18)[0]
    if actual_machine != machine:
        fail(f"{target}: unexpected ELF machine {actual_machine}")

    before_count = data.count(before)
    after_count = data.count(after)
    if (before_count, after_count) not in ((1, 0), (0, 1)):
        fail(
            f"{target}: expected one known function signature; "
            f"found before={before_count}, after={after_count}"
        )

    is_patched = after_count == 1
    function_signature = after if is_patched else before
    function_offset = data.find(function_signature)
    loads = executable_loads(data, elf_class)
    function_end = function_offset + len(function_signature)
    if not any(start <= function_offset and function_end <= end for start, end in loads):
        fail(f"{target}: known function signature is outside executable PT_LOAD")

    if is_patched:
        print(f"{target}: native-only HWC config patch already present")
        return

    patch_start = function_offset + patch_offset
    if data[patch_start : patch_start + len(old_bytes)] != old_bytes:
        fail(f"{target}: unexpected instruction at validated function offset")

    patched_data = (
        data[:patch_start]
        + new_bytes
        + data[patch_start + len(old_bytes) :]
    )
    if patched_data.count(after) != 1 or patched_data.count(before) != 0:
        fail(f"{target}: patched function signature validation failed")
    with target.open("r+b") as output:
        output.seek(patch_start)
        output.write(new_bytes)
        output.flush()

    print(f"{target}: limited HWC to the native display config")


def main(argv):
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <hwcomposer.hi3660.so>", file=sys.stderr)
        return 2
    try:
        patch_blob(argv[1])
    except (OSError, ValueError, struct.error) as error:
        print(f"fix_hwc_native_config: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
