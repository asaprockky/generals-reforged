# Zero Hour Overhaul - Roadmap

Target: Command & Conquer Generals: Zero Hour 1.04.
Scope chosen: engine from source + bug fixes + modernization + balance + new content + total conversion.

Each phase builds on the one before it. A total conversion replaces art, factions and story, so it
comes last: balance and content work done earlier carries over as the mechanical foundation.

## Layout

| Path | What |
|---|---|
| `Command Conquer Generals - Zero Hour/` | Working game install (untracked). Pristine copy: `../Command Conquer Generals + Zero Hour by Igruha.zip` |
| `baseline/zh/` | Untouched extract of retail INI, WND, strings, scripts, map INIs. Reference only - never edit |
| `mod/` | Our modified data (to be created). Deployed as loose files / a `.big` into the install |
| `engine/` | Fork of TheSuperHackers/GeneralsGameCode (GPL-3), built with VS 2022, 32-bit |
| `tools/` | `bigtool.py` (list/extract/pack .big, round-trip verified) and future build/deploy scripts |

## Phases

### 0. Foundation  - in progress
- [x] Survey install, extract baseline data, `.big` tool
- [x] Git repo initialized (baseline not committed yet)
- [x] Prebuilt TheSuperHackers weekly-2026-10-09 installed as `generalszh.exe` (retail exe untouched)
- [x] Engine source cloned to `engine/`
- [x] VS 2022 Build Tools installed (`tools/build-engine.cmd` builds `generalszh.exe`)
- [x] First engine build from source: `engine\build\win32\GeneralsMD\Release\generalszh.exe`
  (needed extra VS components ATL + MFC; the tool shells set `NoDefaultCurrentDirectoryInExePath=1`,
  which breaks `vcvarsall.bat` unless the VS Installer folder is on PATH - handled in the script)
- [x] Deploy script `tools/deploy.py`: packs `mod/` into `!ZHOverhaul.big`; `uninstall` reverts

How the engine picks a file: loose files first, then `.big` archives in case-insensitive alphabetical
order, first-loaded wins; ZH folder before base Generals folder. The `!` prefix puts our archive first.
VS 2022 builds are not CRC-compatible with retail 1.04 (online play and replays with retail players won't work).

Note: the registry `InstallPath` for Generals/ZH points at `C:\projects\Generals\Command Conquer Generals - Zero Hour\`
(the copy outside MOD). ZH loads base Generals archives from there, so that copy must stay in place.

### 1. Engine fixes and modernization (C++)
- Start from TheSuperHackers weekly build: fullscreen crash, AI, pathfinding and many other fixes
- Already upstream: render/logic decoupling (smooth high FPS), "Very High" detail, 2x shadow buffers,
  money-per-minute, ESC skips videos, Alt+F4 quit menu, replay archive
- [x] **16:9 widescreen** (Hor+ camera, centered uniform UI) - automated checks pass, manual test pending.
  See `docs/widescreen/README.md`; build `builds/generalszh-widescreen-16x9.exe`
- Data side: `GameData.ini` caps FPS at 30 (`FramesPerSecondLimit`), `MaxCameraHeight = 310` (zoom)
- Our own fixes on top of upstream

### 2. Data bug fixes (INI / scripts / maps)
- Audit against TheSuperHackers/GeneralsGamePatch change list (hundreds of documented retail bugs)
- Exploits, broken upgrades, wrong armor/weapon values, missing button tooltips, AI script errors

### 3. Balance and gameplay overhaul
- Economy, unit roles, superweapons, generals' powers, AI difficulty

### 4. New content
- Units, buildings, upgrades, powers, maps, missions

### 5. Total conversion
- New setting, factions, art, audio, story - built on the engine and mechanics above
