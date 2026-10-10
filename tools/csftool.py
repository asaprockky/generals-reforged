"""Read and edit a C&C Generals / Zero Hour compiled string table (generals.csf).

File format (all integers little-endian int32), as read by GameTextManager::parseCSF in
engine/Core/GameEngine/Source/GameClient/GameText.cpp:

  header : id ' FSC' (int 'CSF '), version, num_labels, num_strings, skip, langid
  label  : id ' LBL' (int 'LBL '), num_strings, name_len, name (ASCII, name_len bytes)
           then num_strings entries:
  string : id ' RTS' (int 'STR ') or 'WRTS' (int 'STRW'), len (UTF-16 code units),
           text (UTF-16LE, every 16-bit unit bit-inverted),
           and for 'STRW' only: wave_len, wave name (ASCII, wave_len bytes)

The engine only uses the first string of each label. This tool keeps every string and wave
name, so an unmodified file round-trips byte for byte.

Usage:
  python tools/csftool.py list FILE [SUBSTRING]       print labels (and first string) containing SUBSTRING
  python tools/csftool.py get FILE LABEL               print the first string of LABEL
  python tools/csftool.py set FILE LABEL TEXT [-o OUT] replace the first string of LABEL (in place unless -o)
  python tools/csftool.py check FILE                   parse and verify the file round-trips unchanged

Escapes in TEXT: \\n becomes a newline (strings store real newlines), \\\\ a backslash.
Labels match case-insensitively, as the engine does.
"""
import argparse
import struct
import sys

CSF_ID = b" FSC"
LBL_ID = b" LBL"
STR_ID = b" RTS"
STRW_ID = b"WRTS"


class CsfString:
    def __init__(self, text, wave=None):
        self.text = text      # str
        self.wave = wave      # bytes or None (None means plain 'STR ')


class CsfLabel:
    def __init__(self, name, strings):
        self.name = name      # bytes (ASCII)
        self.strings = strings


class CsfFile:
    def __init__(self, header, labels):
        self.header = header  # list of 6 ints: id, version, num_labels, num_strings, skip, langid
        self.labels = labels

    # ---------------------------------------------------------------- reading
    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            data = f.read()
        return cls.parse(data)

    @classmethod
    def parse(cls, data):
        if data[:4] != CSF_ID:
            raise ValueError("not a CSF file (bad magic %r)" % data[:4])
        header = list(struct.unpack_from("<4s5i", data, 0))
        pos = 24
        labels = []
        while pos < len(data):
            tag = data[pos:pos + 4]
            if tag != LBL_ID:
                raise ValueError("expected LBL at offset %d, found %r" % (pos, tag))
            num_strings, name_len = struct.unpack_from("<ii", data, pos + 4)
            pos += 12
            name = data[pos:pos + name_len]
            pos += name_len
            strings = []
            for _ in range(num_strings):
                tag = data[pos:pos + 4]
                if tag not in (STR_ID, STRW_ID):
                    raise ValueError("expected STR/STRW at offset %d, found %r" % (pos, tag))
                (length,) = struct.unpack_from("<i", data, pos + 4)
                pos += 8
                raw = data[pos:pos + 2 * length]
                pos += 2 * length
                units = struct.unpack("<%dH" % length, raw)
                text = struct.pack("<%dH" % length, *[(~u) & 0xFFFF for u in units]).decode("utf-16-le")
                wave = None
                if tag == STRW_ID:
                    (wave_len,) = struct.unpack_from("<i", data, pos)
                    pos += 4
                    wave = data[pos:pos + wave_len]
                    pos += wave_len
                strings.append(CsfString(text, wave))
            labels.append(CsfLabel(name, strings))
        return cls(header, labels)

    # ---------------------------------------------------------------- writing
    def serialize(self):
        out = bytearray()
        num_strings = sum(len(l.strings) for l in self.labels)
        header = list(self.header)
        header[2] = len(self.labels)
        header[3] = num_strings
        out += struct.pack("<4s5i", *header)
        for label in self.labels:
            out += LBL_ID + struct.pack("<ii", len(label.strings), len(label.name)) + label.name
            for s in label.strings:
                encoded = s.text.encode("utf-16-le")
                length = len(encoded) // 2
                units = struct.unpack("<%dH" % length, encoded)
                out += (STRW_ID if s.wave is not None else STR_ID) + struct.pack("<i", length)
                out += struct.pack("<%dH" % length, *[(~u) & 0xFFFF for u in units])
                if s.wave is not None:
                    out += struct.pack("<i", len(s.wave)) + s.wave
        return bytes(out)

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.serialize())

    # ---------------------------------------------------------------- access
    def find(self, name):
        key = name.lower().encode("ascii")
        matches = [l for l in self.labels if l.name.lower() == key]
        if not matches:
            raise KeyError("label not found: %s" % name)
        if len(matches) > 1:
            raise KeyError("label %s occurs %d times" % (name, len(matches)))
        return matches[0]

    def get(self, name):
        label = self.find(name)
        return label.strings[0].text if label.strings else ""

    def set(self, name, text):
        label = self.find(name)
        if label.strings:
            label.strings[0].text = text
        else:
            label.strings.append(CsfString(text))

    def upsert(self, name, text):
        """Set the label's text, adding the label if it does not exist. Returns True if added."""
        key = name.lower().encode("ascii")
        for label in self.labels:
            if label.name.lower() == key:
                if label.strings:
                    label.strings[0].text = text
                else:
                    label.strings.append(CsfString(text))
                return False
        self.labels.append(CsfLabel(name.encode("ascii"), [CsfString(text)]))
        return True


def unescape(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            n = text[i + 1]
            if n == "n":
                out.append("\n")
                i += 2
                continue
            if n == "\\":
                out.append("\\")
                i += 2
                continue
        out.append(c)
        i += 1
    return "".join(out)


def show(text):
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("file")
    p.add_argument("substring", nargs="?", default="")
    p = sub.add_parser("get")
    p.add_argument("file")
    p.add_argument("label")
    p = sub.add_parser("set")
    p.add_argument("file")
    p.add_argument("label")
    p.add_argument("text")
    p.add_argument("-o", "--out")
    p = sub.add_parser("check")
    p.add_argument("file")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    if args.cmd == "check":
        with open(args.file, "rb") as f:
            data = f.read()
        csf = CsfFile.parse(data)
        same = csf.serialize() == data
        print("%s: version %d, %d labels, %d strings, langid %d, round-trip %s"
              % (args.file, csf.header[1], len(csf.labels), sum(len(l.strings) for l in csf.labels),
                 csf.header[5], "OK" if same else "DIFFERS"))
        return 0 if same else 1

    csf = CsfFile.load(args.file)
    if args.cmd == "list":
        needle = args.substring.lower()
        for label in csf.labels:
            name = label.name.decode("ascii", "replace")
            if needle in name.lower():
                first = label.strings[0].text if label.strings else ""
                print("%s\t%s" % (name, show(first)))
    elif args.cmd == "get":
        print(show(csf.get(args.label)))
    elif args.cmd == "set":
        old = csf.get(args.label)
        new = unescape(args.text)
        csf.set(args.label, new)
        out = args.out or args.file
        csf.save(out)
        check = CsfFile.load(out).get(args.label)
        if check != new:
            print("ERROR: read-back mismatch for %s" % args.label, file=sys.stderr)
            return 1
        print("%s: %r -> %r (written to %s)" % (args.label, show(old), show(new), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
