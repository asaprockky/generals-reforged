"""Package MOD\\mod into a single archive and install it into the Zero Hour folder.

The engine loads loose files first, then .big archives in case-insensitive
alphabetical order with the first-loaded copy of a file winning (see
engine/Core/GameEngine/Source/Common/System/ArchiveFileSystem.cpp,
loadIntoDirectoryTree). Naming the archive "!ZHOverhaul.big" makes it load
before every retail archive, so our files override retail ones. Removing the
archive restores the retail game.

Usage:
  python tools/deploy.py build      pack mod/ into dist/!ZHOverhaul.big
  python tools/deploy.py install    build, then copy the archive into the game
  python tools/deploy.py uninstall  remove the archive from the game
  python tools/deploy.py status     show what is installed
"""
import argparse
import os
import shutil
import sys

import bigtool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIR = os.path.join(ROOT, "mod")
DIST_DIR = os.path.join(ROOT, "dist")
ARCHIVE_NAME = "!ZHOverhaul.big"
GAME_DIR = os.path.join(
    ROOT, "Command Conquer Generals - Zero Hour", "Command & Conquer(tm) Generals Zero Hour"
)


def build():
    if not os.path.isdir(MOD_DIR) or not any(os.scandir(MOD_DIR)):
        sys.exit(f"nothing to build: {MOD_DIR} is missing or empty")
    os.makedirs(DIST_DIR, exist_ok=True)
    out = os.path.join(DIST_DIR, ARCHIVE_NAME)
    bigtool.cmd_pack(argparse.Namespace(srcdir=MOD_DIR, archive=out))
    return out


def install():
    if not os.path.isdir(GAME_DIR):
        sys.exit(f"game folder not found: {GAME_DIR}")
    built = build()
    dest = os.path.join(GAME_DIR, ARCHIVE_NAME)
    shutil.copy2(built, dest)
    print(f"installed {dest}")


def uninstall():
    dest = os.path.join(GAME_DIR, ARCHIVE_NAME)
    if os.path.exists(dest):
        os.remove(dest)
        print(f"removed {dest}")
    else:
        print("not installed")


def status():
    dest = os.path.join(GAME_DIR, ARCHIVE_NAME)
    if not os.path.exists(dest):
        print("not installed")
        return
    entries = bigtool.read_index(dest)
    print(f"{dest}: {len(entries)} files, {os.path.getsize(dest)} bytes")
    for name, _offset, size in entries:
        print(f"  {size:>10}  {name}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["build", "install", "uninstall", "status"])
    cmd = p.parse_args().command
    {"build": build, "install": install, "uninstall": uninstall, "status": status}[cmd]()


if __name__ == "__main__":
    main()
