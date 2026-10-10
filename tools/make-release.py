"""Build the shareable Generals Reforged package (release\\GeneralsReforged + zip).

The package never touches a game install: the launcher starts our exe with
-setCwd <Zero Hour folder> -mod <package>\\ZHReforged.big, and -mod archives
override every retail archive.

ZHReforged.big holds MOD\\mod plus the full effective Data\\INI and
Data\\Scripts tree of this install (same first-wins order as the engine:
loose files, then Zero Hour archives, then Generals archives, alphabetical).
That makes the game rules identical on every PC that runs the package, which
LAN games need, whatever language or patch files the local install has.

Usage:
  python tools/make-release.py [VERSION]
"""
import argparse
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bigtool  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIR = os.path.join(ROOT, "mod")
INSTALL = os.path.join(ROOT, "Command Conquer Generals - Zero Hour")
ZH_DIR = os.path.join(INSTALL, "Command & Conquer(tm) Generals Zero Hour")
GEN_DIR = os.path.join(INSTALL, "Command & Conquer(tm) Generals")
EXE = os.path.join(ROOT, "builds", "generalszh-reforged.exe")
STAGE = os.path.join(ROOT, "build-release", "stage")
OUT_DIR = os.path.join(ROOT, "release", "GeneralsReforged")
OWN_ARCHIVES = {"!zhoverhaul.big", "zhreforged.big"}
SYNC_PREFIXES = ("data\\ini\\", "data\\scripts\\")


def norm(path):
    return path.replace("/", "\\").lower()


def mod_files():
    found = set()
    for top, _dirs, files in os.walk(MOD_DIR):
        for f in files:
            found.add(norm(os.path.relpath(os.path.join(top, f), MOD_DIR)))
    return found


def collect_rules(skip):
    """Return {normalized path: (display path, source)}; source is a file path or (archive, offset, size)."""
    chosen = {}

    def offer(name, source):
        key = norm(name)
        if key.startswith(SYNC_PREFIXES) and key not in skip and key not in chosen:
            chosen[key] = (name.replace("/", "\\"), source)

    loose = os.path.join(ZH_DIR, "Data")
    for top, _dirs, files in os.walk(loose):
        for f in files:
            full = os.path.join(top, f)
            offer(os.path.relpath(full, ZH_DIR), full)
    for folder in (ZH_DIR, GEN_DIR):
        archives = sorted((f for f in os.listdir(folder) if f.lower().endswith(".big")), key=str.lower)
        for arc in archives:
            if arc.lower() in OWN_ARCHIVES:
                continue
            path = os.path.join(folder, arc)
            for name, offset, size in bigtool.read_index(path):
                offer(name, (path, offset, size))
    return chosen


def stage(chosen):
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    shutil.copytree(MOD_DIR, STAGE)
    for display, source in chosen.values():
        dest = os.path.join(STAGE, display)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if isinstance(source, str):
            shutil.copyfile(source, dest)
        else:
            arc, offset, size = source
            with open(arc, "rb") as f:
                f.seek(offset)
                data = f.read(size)
            with open(dest, "wb") as out:
                out.write(data)


LAUNCHER = r"""@echo off
setlocal
rem Generals Reforged launcher. Starts the Reforged exe on your own Zero Hour install
rem with the Reforged data (-mod). Nothing in the game folder is changed.
set "HERE=%~dp0"
set "GAME="
if defined ZH_GAME_DIR set "GAME=%ZH_GAME_DIR%"
if not defined GAME if exist "%HERE%game-folder.txt" set /p GAME=<"%HERE%game-folder.txt"
if not defined GAME if exist "%HERE%WindowZH.big" set "GAME=%HERE%"
if not defined GAME if exist "%HERE%..\WindowZH.big" for %%I in ("%HERE%..") do set "GAME=%%~fI"
if not defined GAME for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour" /v InstallPath 2^>nul ^| findstr /i "InstallPath"') do set "GAME=%%B"
if not defined GAME for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour" /v InstallPath 2^>nul ^| findstr /i "InstallPath"') do set "GAME=%%B"
if not defined GAME goto notfound
rem Some installs store the path of Generals.exe instead of the folder.
if /i "%GAME:~-4%"==".exe" for %%I in ("%GAME%") do set "GAME=%%~dpI"
if "%GAME:~-1%"=="\" set "GAME=%GAME:~0,-1%"
if not exist "%GAME%\WindowZH.big" goto notfound
if defined REFORGED_DRYRUN echo "%GAME%"& exit /b 0
start "" /D "%GAME%" "%HERE%GeneralsReforged.exe" -setCwd "%GAME%" -mod "%HERE%ZHReforged.big" %*
exit /b 0

:notfound
echo Could not find your Command ^& Conquer Generals Zero Hour folder.
echo.
echo Fix: open game-folder.txt in this folder with Notepad and paste the full path of the
echo folder that contains WindowZH.big and INIZH.big, for example:
echo   C:\Program Files (x86)\Steam\steamapps\common\Command ^& Conquer Generals - Zero Hour
echo Then run this launcher again.
if not exist "%HERE%game-folder.txt" type nul > "%HERE%game-folder.txt"
pause
exit /b 1
"""

README = """GENERALS REFORGED {version}
=====================================

A mod for Command & Conquer Generals Zero Hour: 16:9 widescreen, farther zoom,
smoother rendering, better group movement and formations, graphics tweaks,
English text, and fixes for 70+ retail bugs.

You need your own installed copy of C&C Generals Zero Hour (1.04), for example
from Steam or the EA app ("Command & Conquer The Ultimate Collection").
This package does not contain the game and does not change your game folder.

INSTALL
1. Unzip this folder anywhere (for example inside your Zero Hour folder).
2. Double-click Play-Generals-Reforged.cmd.
   If it cannot find the game, paste your Zero Hour folder path (the one with
   WindowZH.big in it) into game-folder.txt and run it again.
3. Windows may warn about an unknown app: click "More info" -> "Run anyway".
   Allow it through the Windows Firewall (private networks) for LAN games.

PLAY TOGETHER (LAN)
- Both players must use this same package version. Each player runs
  Play-Generals-Reforged.cmd, then Multiplayer -> Network.
- One player creates a game, the other joins it.
- Not on the same home network? Install a free virtual LAN tool such as
  Radmin VPN or ZeroTier on both PCs, join the same network, then use Network
  as above.
- Original Zero Hour (without Reforged) cannot join Reforged games.

FILES
  GeneralsReforged.exe        game engine (TheSuperHackers GeneralsGameCode, GPL-3.0, plus Reforged changes)
  ZHReforged.big              Reforged game data
  Play-Generals-Reforged.cmd  launcher
  SOURCE.txt                  where the source code is

Fan-made, non-commercial. Command & Conquer is a trademark of Electronic Arts.
Not affiliated with or endorsed by EA.
"""

SOURCE = """Generals Reforged {version}

GeneralsReforged.exe is built from TheSuperHackers GeneralsGameCode
(https://github.com/TheSuperHackers/GeneralsGameCode, GPL-3.0), commit
{commit}, with the Reforged changes in docs/reforged-engine.patch of
https://github.com/asaprockky/generals-reforged. Build: Visual Studio 2022, CMake preset win32,
target z_generals (see tools/build-engine.cmd there).
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", nargs="?", default="v1.0")
    ap.add_argument("--commit", default="0909348122717b4b758d7f45b8e14c5b31cbadb9")
    args = ap.parse_args()

    if not os.path.isfile(EXE):
        sys.exit(f"missing {EXE}")
    chosen = collect_rules(mod_files())
    stage(chosen)
    print(f"staged mod + {len(chosen)} rules files")

    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)
    bigtool.cmd_pack(argparse.Namespace(srcdir=STAGE, archive=os.path.join(OUT_DIR, "ZHReforged.big")))
    shutil.copyfile(EXE, os.path.join(OUT_DIR, "GeneralsReforged.exe"))
    with open(os.path.join(OUT_DIR, "Play-Generals-Reforged.cmd"), "w", newline="\r\n") as f:
        f.write(LAUNCHER)
    with open(os.path.join(OUT_DIR, "README.txt"), "w", newline="\r\n") as f:
        f.write(README.format(version=args.version))
    with open(os.path.join(OUT_DIR, "SOURCE.txt"), "w", newline="\r\n") as f:
        f.write(SOURCE.format(version=args.version, commit=args.commit))

    zip_path = os.path.join(ROOT, "release", f"GeneralsReforged-{args.version}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT_DIR)):
            z.write(os.path.join(OUT_DIR, f), os.path.join("GeneralsReforged", f))
    print(f"package: {OUT_DIR}")
    print(f"zip:     {zip_path} ({os.path.getsize(zip_path) // 1024 // 1024} MB)")


if __name__ == "__main__":
    main()
