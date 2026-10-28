#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

"""Rename the legacy sk_dup import in the Hi3660 supplicant blob.

This fixup is pinned to the reviewed Huawei blob and patchelf 0.18 output.
The reviewed output moves dynamic metadata into a new PT_LOAD segment; make
that segment read-only before installing the result. A blob or tool update
must be reviewed and assigned new hashes before this script accepts it.
"""

import hashlib
import os
import pathlib
import shutil
import stat
import struct
import subprocess
import sys
import tempfile


ORIGINAL_SHA256 = "5e0b203b6b48285565ad2a31ad8b144f93b28ab67ab51ea54fad55ff3347d80c"
PATCHELF_SHA256 = "7d945c9c2abe71e7ff35c66ce1d21adf42f47c137c4d799e9faa215a34fb1a27"
FIXED_SHA256 = "6bf996f3e634df6169d5cb7098147ce7d71a82b718c5a2be8a4783aea693dca1"

# ELF64 program header fields in the reviewed patchelf 0.18 output.
METADATA_LOAD = (1, 6, 0x240000, 0x240000, 0x240000, 0xAB20, 0xAB20, 0x10000)
PF_R = 4


class FixupError(Exception):
    """The input or generated ELF differs from the reviewed form."""


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_patchelf(path):
    tool = pathlib.Path(path)
    try:
        info = tool.stat()
        if not stat.S_ISREG(info.st_mode) or not os.access(tool, os.X_OK):
            raise FixupError(f"patchelf is not an executable regular file: {tool}")
        result = subprocess.run(
            [str(tool), "--version"], check=False, capture_output=True, text=True
        )
    except OSError as error:
        raise FixupError(f"cannot run patchelf {tool}: {error}") from error
    if result.returncode != 0 or result.stdout.strip() != "patchelf 0.18.0":
        raise FixupError(
            f"expected patchelf 0.18.0, got status={result.returncode}, "
            f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
        )
    return tool


def program_headers(data):
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise FixupError("generated file is not a little-endian ELF64 file")
    if struct.unpack_from("<H", data, 18)[0] != 183:
        raise FixupError("generated ELF is not AArch64")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    phentsize, phnum = struct.unpack_from("<HH", data, 54)
    if phentsize < 56 or phoff > len(data) or phnum > (len(data) - phoff) // phentsize:
        raise FixupError("generated ELF has an invalid program header table")

    entries = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        fields = struct.unpack_from("<IIQQQQQQ", data, offset)
        entries.append((offset, fields))
    return entries


def protect_metadata_load(path):
    data = bytearray(path.read_bytes())
    actual = hashlib.sha256(data).hexdigest()
    if actual != PATCHELF_SHA256:
        raise FixupError(f"unexpected patchelf output SHA-256: {actual}")

    headers = program_headers(data)
    matches = [(offset, fields) for offset, fields in headers if fields == METADATA_LOAD]
    if len(matches) != 1:
        raise FixupError(f"expected exactly one reviewed metadata LOAD, found {len(matches)}")
    offset, _load = matches[0]

    # Changing only p_flags restores the read-only mapping of dynamic metadata.
    struct.pack_into("<I", data, offset + 4, PF_R)
    path.write_bytes(data)
    final = hashlib.sha256(data).hexdigest()
    if final != FIXED_SHA256:
        raise FixupError(f"unexpected read-only ELF SHA-256: {final}")


def patch(blob, patchelf):
    target = pathlib.Path(blob)
    try:
        original_stat = target.lstat()
    except OSError as error:
        raise FixupError(f"cannot stat blob {target}: {error}") from error
    if stat.S_ISLNK(original_stat.st_mode) or not stat.S_ISREG(original_stat.st_mode):
        raise FixupError(f"blob must be a regular non-symlink file: {target}")

    original_hash = sha256(target)
    if original_hash == FIXED_SHA256:
        print(f"{target}: already fixed ({FIXED_SHA256})")
        return
    if original_hash != ORIGINAL_SHA256:
        raise FixupError(f"unrecognized blob SHA-256: {original_hash}")

    tool = check_patchelf(patchelf)
    mode = stat.S_IMODE(original_stat.st_mode)
    with tempfile.TemporaryDirectory(prefix=f".{target.name}.fixup.", dir=target.parent) as temp:
        work = pathlib.Path(temp)
        candidate = work / target.name
        symbol_map = work / "symbols.map"
        shutil.copyfile(target, candidate)
        os.chmod(candidate, mode)
        symbol_map.write_text("sk_dup OPENSSL_sk_dup\n", encoding="ascii")

        try:
            result = subprocess.run(
                [
                    str(tool),
                    "--rename-dynamic-symbols",
                    str(symbol_map),
                    str(candidate),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            raise FixupError(f"cannot run patchelf: {error}") from error
        if result.returncode != 0:
            raise FixupError(
                f"patchelf failed with status {result.returncode}: "
                f"{result.stderr.strip()}"
            )

        protect_metadata_load(candidate)
        os.chmod(candidate, mode)

        current_stat = target.lstat()
        if (
            stat.S_ISLNK(current_stat.st_mode)
            or not stat.S_ISREG(current_stat.st_mode)
            or stat.S_IMODE(current_stat.st_mode) != mode
            or (current_stat.st_dev, current_stat.st_ino)
            != (original_stat.st_dev, original_stat.st_ino)
            or sha256(target) != original_hash
        ):
            raise FixupError(f"blob changed during fixup; refusing to replace {target}")

        os.replace(candidate, target)

    print(f"{target}: renamed sk_dup to OPENSSL_sk_dup ({FIXED_SHA256})")


def main(argv):
    if len(argv) != 3:
        print(f"Usage: {argv[0]} <blob> <patchelf-0_18>", file=sys.stderr)
        return 2
    try:
        patch(argv[1], argv[2])
    except (FixupError, OSError, struct.error) as error:
        print(f"fix_wpa_supplicant_sk_dup: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
