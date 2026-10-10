# Generals Reforged

A fan mod for **Command & Conquer Generals Zero Hour**, built on the open-source
[TheSuperHackers GeneralsGameCode](https://github.com/TheSuperHackers/GeneralsGameCode) engine.

- Proper 16:9 widescreen (Hor+ 3D view, UI scaled without stretching, 4:3 still works)
- Farther zoom-out, smoother rendering at your monitor's refresh rate, graphics tweaks
- Better group movement: groups move side by side instead of single file;
  Ctrl+F formations keep their shape and move at the speed of the slowest unit
- 70+ retail bug fixes (data and engine), English text everywhere
- LAN multiplayer: everyone runs the same package, so the game rules match on every PC

## Play

You need your own installed copy of **C&C Generals Zero Hour 1.04** (Steam or EA app,
"Command & Conquer The Ultimate Collection"). Nothing here contains or changes the original game.

1. Install Zero Hour (Steam or EA app), start it once normally, then quit.
2. Download `GeneralsReforged-<version>.zip` from [Releases](../../releases),
   right-click it → **Extract All** (don't run it from inside the zip).
3. Double-click `Play-Generals-Reforged.cmd` in the extracted folder.
4. If it cannot find the game: Steam → right-click the game → Manage → Browse local files,
   copy that folder's path (the one with `WindowZH.big`), paste it into `game-folder.txt`
   next to the launcher, save, and run it again.
5. Windows may warn about an unknown app: **More info → Run anyway**.
6. In the game, set Options → resolution to your screen (e.g. 1920×1080).

The game folder is never modified; to remove Reforged, delete the extracted folder.

LAN with a friend: both use the same release, then Multiplayer → Network, one creates a game,
the other joins. Not on the same network? Use a virtual LAN such as Radmin VPN or ZeroTier.
Allow the game through Windows Firewall when asked.

## Repository

| Path | What |
|---|---|
| `mod/` | Reforged game data (INI, strings, UI), packed into `ZHReforged.big` |
| `docs/reforged-engine.patch` | Engine changes against GeneralsGameCode `0909348122717b4b758d7f45b8e14c5b31cbadb9` |
| `docs/` | Design notes, bug audit, test captures |
| `tools/` | Archive tool, engine build script, release packager, faction generator |
| `parked/` | Unfinished new-faction work (not in the release) |

Build the engine: clone GeneralsGameCode at the commit above, `git apply docs/reforged-engine.patch`,
then `tools/build-engine.cmd` (VS 2022 Build Tools). Build a release: `python tools/make-release.py v1.0`.

## License and credits

Engine code: GPL-3.0 (see `LICENSE.md`), © Electronic Arts and TheSuperHackers contributors.
Command & Conquer is a trademark of Electronic Arts. This is a non-commercial fan project,
not affiliated with or endorsed by EA. Game data files remain EA's; you need a legal copy of the game.
