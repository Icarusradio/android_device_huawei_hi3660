#!/usr/bin/env python3
"""Rename Huawei's legacy camera metadata exports without moving ELF symbols.

The numeric suffixes make each equal-length alias hash to the same GNU-hash
bucket as its legacy name in all three approved blobs. Inputs are current
post-fixup extraction outputs; unknown firmware must be reviewed before use.
"""
import hashlib
import os
import stat
import struct
import sys
import tempfile

OLD = {
    "vendor/bin/CameraDaemon": "2d7f57d1a9897822abb7dbffbe5a95eea4979e92bd04f7e85d2d4efdc395146f",
    "odm/lib64/hwcam/hwcam.hi3660.m.CMR.so": "4d77a898e4a2b61d94b562f572c2a5eddab8cfb162316c3fb5aff04dec37f014",
    "odm/lib64/hwcam/hwcam.hi3660.m.SHT.so": "ff7685b3ac20fe457ac160f879d4b56afb27a36d882ef64090b7c26a4480543a",
}
FINAL = {
    "vendor/bin/CameraDaemon": "fbfcfb4b91c1239cd20f4b2770bfbb47f74c9e66eaaf1d367765ab4a9fef175a",
    "odm/lib64/hwcam/hwcam.hi3660.m.CMR.so": "59c1a6e2b71eb897407ba8fc3e74f98c88cecddb6dd7cd9577d462c01b12def7",
    "odm/lib64/hwcam/hwcam.hi3660.m.SHT.so": "578c8862b6758925af379ada113c855467008bb2644af006d81a97c9d42d367b",
}
# Combined state after the separate CameraDaemon Looper DT_NEEDED fixup.
# Metadata remains unchanged; accepting it keeps extraction idempotent.
CAMERA_DAEMON_LOOPER_SHA256 = "2d02f7dae4c9e37c1611ab3f987e4789e3a8403c828757eb4c74a9c04cb704aa"
RENAMES = ((b"camera_metadata_section_bounds", b"huawei_metadata_bounds_0000036"),
           (b"camera_metadata_section_names", b"huawei_metadata_names_0000207"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def gnu_hash(name):
    h = 5381
    for c in name:
        h = ((h * 33) + c) & 0xffffffff
    return h


def parse(data):
    if len(data) < 64 or data[:4] != b"\x7fELF" or data[4:6] != b"\x02\x01":
        raise ValueError("expected ELF64 little-endian")
    eh = struct.unpack_from("<16sHHIQQQIHHHHHH", data, 0)
    if eh[2] != 183 or eh[1] != 3 or eh[11] != 64 or eh[12] == 0:
        raise ValueError("expected AArch64 ELF with section headers")
    shoff, shentsize, shnum, shstrndx = eh[6], eh[11], eh[12], eh[13]
    if shentsize != 64 or shoff + shentsize * shnum > len(data) or shstrndx >= shnum:
        raise ValueError("invalid section table")
    shdrs = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shentsize) for i in range(shnum)]
    names_hdr = shdrs[shstrndx]
    names = data[names_hdr[4]:names_hdr[4] + names_hdr[5]]
    sections = {}
    for sh in shdrs:
        end = names.find(b"\0", sh[0])
        if sh[0] < len(names) and end >= 0:
            sections[names[sh[0]:end].decode("ascii", "replace")] = sh
    for required in (".dynsym", ".dynstr", ".gnu.hash"):
        if required not in sections:
            raise ValueError("missing " + required)
    sym, strings, gh = sections[".dynsym"], sections[".dynstr"], sections[".gnu.hash"]
    if sym[9] != 24 or sym[6] >= shnum or shdrs[sym[6]] != strings:
        raise ValueError("unexpected dynamic symbol/string table layout")
    if strings[4] + strings[5] > len(data) or sym[4] + sym[5] > len(data) or gh[4] + gh[5] > len(data):
        raise ValueError("section extends past EOF")
    nb, so, bloom_size, bloom_shift = struct.unpack_from("<IIII", data, gh[4])
    if not nb or not bloom_size:
        raise ValueError("invalid GNU hash header")
    bloom_off = gh[4] + 16
    buckets_off = bloom_off + bloom_size * 8
    chains_off = buckets_off + nb * 4
    nsyms = sym[5] // 24
    if so > nsyms or chains_off + (nsyms - so) * 4 > gh[4] + gh[5]:
        raise ValueError("GNU hash chain table size mismatch")
    return sections, shdrs, strings, sym, gh, (nb, so, bloom_size, bloom_shift, bloom_off, buckets_off, chains_off, nsyms)


def str_at(data, strings, off):
    base, size = strings[4], strings[5]
    if off >= size:
        raise ValueError("dynamic string offset outside .dynstr")
    end = data.find(b"\0", base + off, base + size)
    if end < 0:
        raise ValueError("unterminated dynamic string")
    return data[base + off:end]


def transform(data):
    sections, shdrs, strings, sym, gh, g = parse(data)
    nb, so, bloom_size, shift, bloom_off, buckets_off, chains_off, nsyms = g
    strtab = data[strings[4]:strings[4] + strings[5]]
    out = bytearray(data)
    found = []
    for old, new in RENAMES:
        if len(old) != len(new) or gnu_hash(old) % nb != gnu_hash(new) % nb:
            raise ValueError("alias length or GNU bucket mismatch")
        old_offsets = [i for i in range(len(strtab)) if (i == 0 or strtab[i - 1] == 0) and strtab.startswith(old + b"\0", i)]
        if len(old_offsets) != 1:
            raise ValueError("expected exactly one dynamic string for " + old.decode())
        off = old_offsets[0]
        if new + b"\0" in strtab:
            raise ValueError("new alias already exists beside old name")
        target = []
        for idx in range(nsyms):
            pos = sym[4] + idx * 24
            nameoff, info, other, shndx, value, size = struct.unpack_from("<IBBHQQ", data, pos)
            if nameoff == off:
                if (info >> 4, info & 15, other & 3, size) != (1, 1, 0, 224) or shndx == 0:
                    raise ValueError("target symbol attributes mismatch")
                target.append((idx, pos, shndx))
        if len(target) != 1:
            raise ValueError("target symbol not unique")
        idx, sympos, shndx = target[0]
        if idx < so:
            raise ValueError("target excluded from GNU hash chains")
        chainpos = chains_off + (idx - so) * 4
        oldchain = struct.unpack_from("<I", data, chainpos)[0]
        oldhash, newhash = gnu_hash(old), gnu_hash(new)
        if (oldhash & 0xfffffffe) != (oldchain & 0xfffffffe):
            raise ValueError("legacy GNU hash chain mismatch")
        out[strings[4] + off:strings[4] + off + len(old)] = new
        struct.pack_into("<I", out, chainpos, (newhash & 0xfffffffe) | (oldchain & 1))
        word = (newhash // 64) % bloom_size
        bit1 = newhash % 64
        bit2 = (newhash >> shift) % 64
        bloompos = bloom_off + word * 8
        bloom = struct.unpack_from("<Q", out, bloompos)[0]
        struct.pack_into("<Q", out, bloompos, bloom | (1 << bit1) | (1 << bit2))
        found.append((old.decode(), new.decode(), off, idx, sympos, shndx, chainpos, bloompos))
    return bytes(out), found


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_camera_metadata_exports.py <blob>")
    path = sys.argv[1]
    st = os.lstat(path)
    if not stat.S_ISREG(st.st_mode):
        raise ValueError("input must be a regular non-symlink file")
    with open(path, "rb") as f:
        data = f.read()
    digest = sha(data)
    suffix = next((k for k in OLD if path.replace(os.sep, "/").endswith(k)), None)
    expected = OLD.get(suffix) if suffix else None
    final_expected = FINAL.get(suffix) if suffix else None
    if expected is None:
        raise ValueError("blob path is not one of the approved extraction paths")
    if suffix == "vendor/bin/CameraDaemon" and digest == CAMERA_DAEMON_LOOPER_SHA256:
        print("camera metadata exports already renamed; looper dependency already redirected; sha256=" + digest)
        return
    if digest == final_expected and final_expected:
        print("camera metadata exports already renamed; sha256=" + digest)
        return
    if digest != expected:
        raise ValueError("approved path has unknown SHA-256")
    changed, _ = transform(data)
    final = sha(changed)
    if final_expected and final != final_expected:
        raise ValueError("candidate SHA-256 differs from the approved output")
    fd, tmp = tempfile.mkstemp(prefix=".camera-metadata-", dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(changed)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, stat.S_IMODE(st.st_mode))
        with open(tmp, "rb") as f:
            check = f.read()
        if sha(check) != final or len(check) != len(data):
            raise ValueError("candidate verification failed")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("renamed metadata exports; sha256=" + final)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, struct.error) as e:
        print("fix_camera_metadata_exports.py: " + str(e), file=sys.stderr)
        raise SystemExit(1)
