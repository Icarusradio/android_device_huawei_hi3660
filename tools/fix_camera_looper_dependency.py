#!/usr/bin/env python3
"""Redirect CameraDaemon's libutils dependency through the Looper TLS shim."""

import hashlib
import os
import stat
import struct
import sys
import tempfile


ORIGINAL_SHA256 = "fbfcfb4b91c1239cd20f4b2770bfbb47f74c9e66eaaf1d367765ab4a9fef175a"
FINAL_SHA256 = "2d02f7dae4c9e37c1611ab3f987e4789e3a8403c828757eb4c74a9c04cb704aa"
OLD_NEEDED = b"libutils.so"
NEW_NEEDED = b"libhloop.so"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_sections(data):
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("expected ELF64 little-endian input")

    elf_header = struct.unpack_from("<16sHHIQQQIHHHHHH", data, 0)
    if elf_header[1] != 3 or elf_header[2] != 183:
        raise ValueError("expected AArch64 ET_DYN input")

    section_offset = elf_header[6]
    section_entry_size = elf_header[11]
    section_count = elf_header[12]
    string_section_index = elf_header[13]
    if section_entry_size != 64 or section_count == 0:
        raise ValueError("unsupported section header table")
    if string_section_index >= section_count:
        raise ValueError("invalid section name table index")
    if section_offset + section_entry_size * section_count > len(data):
        raise ValueError("section headers extend past end of input")

    sections = [
        struct.unpack_from("<IIQQQQIIQQ", data, section_offset + index * section_entry_size)
        for index in range(section_count)
    ]
    names_header = sections[string_section_index]
    names_start = names_header[4]
    names_end = names_start + names_header[5]
    if names_end > len(data):
        raise ValueError("section name table extends past end of input")
    names = data[names_start:names_end]

    by_name = {}
    for section in sections:
        name_offset = section[0]
        if name_offset >= len(names):
            continue
        name_end = names.find(b"\0", name_offset)
        if name_end < 0:
            continue
        name = names[name_offset:name_end].decode("ascii", "replace")
        by_name[name] = section

    if ".dynamic" not in by_name or ".dynstr" not in by_name:
        raise ValueError("missing dynamic section or dynamic string table")
    return by_name


def make_candidate(data):
    if len(OLD_NEEDED) != len(NEW_NEEDED):
        raise ValueError("DT_NEEDED replacement must preserve string length")

    sections = parse_sections(data)
    dynamic = sections[".dynamic"]
    strings = sections[".dynstr"]
    entry_size = dynamic[9]
    if entry_size != 16 or dynamic[5] % entry_size:
        raise ValueError("unsupported dynamic entry size")

    string_start = strings[4]
    string_end = string_start + strings[5]
    if string_end > len(data):
        raise ValueError("dynamic string table extends past end of input")

    matches = []
    for entry_offset in range(dynamic[4], dynamic[4] + dynamic[5], entry_size):
        tag, value = struct.unpack_from("<qQ", data, entry_offset)
        if tag != 1:  # DT_NEEDED
            continue
        if value >= strings[5]:
            raise ValueError("DT_NEEDED offset is outside .dynstr")
        name_end = data.find(b"\0", string_start + value, string_end)
        if name_end < 0:
            raise ValueError("unterminated DT_NEEDED string")
        name = data[string_start + value:name_end]
        if name == OLD_NEEDED:
            matches.append((entry_offset, string_start + value))

    if len(matches) != 1:
        raise ValueError("expected exactly one libutils.so DT_NEEDED entry")

    _, string_offset = matches[0]
    result = bytearray(data)
    result[string_offset:string_offset + len(OLD_NEEDED)] = NEW_NEEDED
    candidate = bytes(result)
    if sha256(candidate) != FINAL_SHA256:
        raise ValueError("candidate SHA-256 differs from the approved output")
    return candidate


def replace_atomically(path, candidate, mode):
    directory = os.path.dirname(os.path.abspath(path))
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix=".looper-dependency-", dir=directory
    )
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            output.write(candidate)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary_path, stat.S_IMODE(mode))
        with open(temporary_path, "rb") as check_file:
            if sha256(check_file.read()) != FINAL_SHA256:
                raise ValueError("temporary output verification failed")
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_camera_looper_dependency.py <blob>")

    path = sys.argv[1]
    file_stat = os.lstat(path)
    if not stat.S_ISREG(file_stat.st_mode):
        raise ValueError("input must be a regular non-symlink file")

    with open(path, "rb") as source:
        data = source.read()
    input_sha256 = sha256(data)

    if input_sha256 == FINAL_SHA256:
        print("Looper dependency already redirected; sha256=" + input_sha256)
        return
    if input_sha256 != ORIGINAL_SHA256:
        raise ValueError("unknown CameraDaemon SHA-256")

    candidate = make_candidate(data)
    replace_atomically(path, candidate, file_stat.st_mode)
    print("redirected libutils.so to libhloop.so; sha256=" + FINAL_SHA256)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, struct.error) as error:
        print("fix_camera_looper_dependency.py: " + str(error), file=sys.stderr)
        raise SystemExit(1)
