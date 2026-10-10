"""List, extract and pack Command & Conquer Generals / Zero Hour .big archives.

Format (verified against retail INIZH.big / WindowZH.big): "BIGF" magic,
little-endian u32 archive size, then big-endian u32 entry count and u32
offset of the first file's data; then per entry big-endian u32 offset,
u32 size and a NUL-terminated name; then an 8-byte "L231" marker.

Usage:
  python bigtool.py list    ARCHIVE.big
  python bigtool.py extract ARCHIVE.big OUTDIR [--filter SUBSTR]
  python bigtool.py pack    SRCDIR ARCHIVE.big
"""
import argparse
import os
import struct
import sys


def read_index(path):
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic not in (b"BIGF", b"BIG4"):
            raise ValueError(f"{path}: not a BIG archive (magic {magic!r})")
        f.read(4)  # archive size, unused by the game
        count, _header_size = struct.unpack(">II", f.read(8))
        entries = []
        for _ in range(count):
            offset, size = struct.unpack(">II", f.read(8))
            name = bytearray()
            while (c := f.read(1)) != b"\0":
                if not c:
                    raise ValueError(f"{path}: truncated index")
                name += c
            entries.append((name.decode("latin-1"), offset, size))
    return entries


def cmd_list(args):
    for name, _offset, size in read_index(args.archive):
        print(f"{size:>10}  {name}")


def cmd_extract(args):
    entries = read_index(args.archive)
    if args.filter:
        needle = args.filter.lower()
        entries = [e for e in entries if needle in e[0].lower()]
    with open(args.archive, "rb") as f:
        for name, offset, size in entries:
            rel = name.replace("\\", os.sep)
            dest = os.path.normpath(os.path.join(args.outdir, rel))
            if not dest.startswith(os.path.normpath(args.outdir)):
                raise ValueError(f"refusing path outside outdir: {name}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            f.seek(offset)
            with open(dest, "wb") as out:
                out.write(f.read(size))
    print(f"extracted {len(entries)} files from {args.archive}")


def cmd_pack(args):
    files = []
    for dirpath, _dirs, names in os.walk(args.srcdir):
        for n in names:
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, args.srcdir).replace(os.sep, "\\")
            files.append((rel, full))
    files.sort(key=lambda x: x[0].lower())

    names = [rel.encode("latin-1") for rel, _ in files]
    header_size = 16 + sum(8 + len(n) + 1 for n in names)
    # Retail archives follow the index with an 8-byte "L231" marker.
    data_start = header_size + 8
    offset = data_start
    index = bytearray()
    sizes = []
    for (rel, full), n in zip(files, names):
        size = os.path.getsize(full)
        index += struct.pack(">II", offset, size) + n + b"\0"
        sizes.append(size)
        offset += size

    with open(args.archive, "wb") as out:
        out.write(b"BIGF")
        out.write(struct.pack("<I", offset))
        out.write(struct.pack(">II", len(files), data_start))
        out.write(index)
        out.write(b"L231\0\0\0\0")
        for _rel, full in files:
            with open(full, "rb") as src:
                out.write(src.read())
    print(f"packed {len(files)} files into {args.archive} ({offset} bytes)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list"); s.add_argument("archive"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("extract"); s.add_argument("archive"); s.add_argument("outdir")
    s.add_argument("--filter"); s.set_defaults(fn=cmd_extract)
    s = sub.add_parser("pack"); s.add_argument("srcdir"); s.add_argument("archive"); s.set_defaults(fn=cmd_pack)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
