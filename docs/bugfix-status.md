# Retail bug fix status

Audit: `docs/retail-bug-audit.md` (74 confirmed data bugs). Fixes written independently (GamePatch used as a
bug reference only). Every changed line carries `; Reforged @bugfix BUG-0xx` (WND files have no comment syntax).

**Verification so far:** static only, plus a startup and map-load test. `tools/check-ini-refs.py` reports 0
unresolved references over all changed lines; block/`End` counts match the intended edits; the game starts
(all INI files parse) and loads a map with the 142-file mod installed. **No fix has been tested in play yet.**

## Engine fixes

| Fix | Where |
|---|---|
| BUG-006/007 + ~30 other upstream fixes (power plants and Supply Drop Zones under construction, crate double pickup, horde dead units, battle plans on capture, Chinook takeoff, dozer/worker task resume, ...) | `RETAIL_COMPATIBLE_CRC` set to 0 in `GameDefines.h`; save/data/network guards unchanged |
| BUG-030 Satellite Hack misses Command Centers built later; spy-vision counters could go negative | `Player::setUnitsVisionSpied` remembers grants, `applyUnitsVisionSpied` on join/leave, `Object::initObject`, clamp in `Object::setVisionSpied` |
| (found in testing) Scripted cameras showed undrawn terrain at 16:9 | `W3DView::getDesiredTerrainDrawSize` |

## Data fixes

| Status | Bugs |
|---|---|
| Done | 001-005, 008-010, 012-029, 031-058, 060-074 |
| Partial | 011: Infantry General fixed (self-deleting `Reforged_*_StartingThings` starting units grant the upgrades); Toxin/Demo deferred, because the Generals Challenge AI opponents get their CC from the map and no starting units. 059: locomotor fixed, unused Pilot cameos left. 012: Toxin/Demo/Stealth buildings actually spawn the vanilla holes, which are fixed |
| Engine | 006, 007, 030 (above) |

Extras found while fixing: Toxin truck upgraded stream (042), Chem_/Slth_ worker sets (043), Nuke outpost weapon
set (016), Demo Rebel and Jarmen Kell death modules are active, not commented out (003), Lazr_/SupW_ Aurora wrecks (066).

## Behaviour changes to test first

- Scud Storm: fires only through the superweapon; launch animation and missile hiding.
- Beacons as STRUCTURE (crash fix): placement and deletion near beacons.
- Helix Gattling no longer shoots aircraft (047); Battlemasters horde across sub-factions (046).
- Infantry General: Nationalism granted at game start by the new starting object (011).
- Tank/Nuke Listening Outposts (new transport AI), Nuke Cannon neutron shells only after the upgrade (008).
- Hotkey labels: "Super Lotus (B)", "Nuke Bomber (T)", "Laser Tank (C)".
