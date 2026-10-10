"""Collect the English versions of every file the Russian repack archives replace into mod/.

The Igruha repack adds 00RussianZH.big (Zero Hour folder) and 00Russian.big / 00SibSpeech.big
(base Generals folder). They sort first, so they override the English files. Our mod archive
(!ZHOverhaul.big) sorts before them, so shipping the English copies in mod/ restores English
without touching either install. Each file is taken from the archive the engine would have used
without the Russian archives: Zero Hour folder first, then base Generals, alphabetical within each.

Base-game unit voices (00SibSpeech.big) have no English copy in this install and stay Russian.

Usage: python tools/make-english.py
"""
import os
import sys

import bigtool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIR = os.path.join(ROOT, "mod")
ZH_DIR = os.path.join(ROOT, "Command Conquer Generals - Zero Hour", "Command & Conquer(tm) Generals Zero Hour")
BASE_DIR = os.path.join(os.path.dirname(ROOT), "Command Conquer Generals - Zero Hour", "Command & Conquer(tm) Generals")
RUSSIAN = {"00russianzh.big", "00russian.big", "00sibspeech.big"}


def archives(directory):
    names = sorted((f for f in os.listdir(directory) if f.lower().endswith(".big")), key=str.lower)
    return [os.path.join(directory, f) for f in names
            if f.lower() not in RUSSIAN and os.path.getsize(os.path.join(directory, f)) > 0]


def main():
    english = {}  # lower-case name -> (archive, offset, size, name), first archive wins
    for archive in archives(ZH_DIR) + archives(BASE_DIR):
        for name, offset, size in bigtool.read_index(archive):
            english.setdefault(name.lower(), (archive, offset, size, name))

    written, missing = 0, 0
    for directory in (ZH_DIR, BASE_DIR):
        for f in os.listdir(directory):
            if f.lower() not in RUSSIAN:
                continue
            for name, _offset, _size in bigtool.read_index(os.path.join(directory, f)):
                source = english.get(name.lower())
                if source is None:
                    missing += 1
                    continue
                archive, offset, size, real_name = source
                dest = os.path.join(MOD_DIR, real_name.replace("\\", os.sep))
                if os.path.exists(dest):
                    continue  # never overwrite a file the mod already has (it may carry fixes)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(archive, "rb") as src, open(dest, "wb") as out:
                    src.seek(offset)
                    out.write(src.read(size))
                written += 1
    print(f"wrote {written} English files to {MOD_DIR} (existing mod files kept); {missing} files have no English copy (base-game voices)")


if __name__ == "__main__":
    sys.exit(main())
