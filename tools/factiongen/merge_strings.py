"""Merge every tools/factiongen/out/*.strings.json into mod/Data/English/generals.csf.

Usage: python tools/factiongen/merge_strings.py
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import csftool  # noqa: E402

CSF = os.path.join(os.path.dirname(os.path.dirname(HERE)), "mod", "Data", "English", "generals.csf")


def main():
    csf = csftool.CsfFile.load(CSF)
    added = updated = 0
    for path in sorted(glob.glob(os.path.join(HERE, "out", "*.strings.json"))):
        with open(path, encoding="utf-8") as f:
            for label, text in json.load(f).items():
                if csf.upsert(label, text):
                    added += 1
                else:
                    updated += 1
    csf.save(CSF)
    print(f"generals.csf: {added} labels added, {updated} updated")


if __name__ == "__main__":
    main()
