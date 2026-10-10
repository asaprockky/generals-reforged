# Group movement and formations

Engine branch `reforged/widescreen-16x9` (uncommitted; full diff in `docs/reforged-engine.patch`).
All changes tagged `Reforged @feature`. **Not yet tested in play**; it changes game logic, so it can't be
checked with existing replays (they desync by design).

## Why units moved single-file

`AIGroup::groupMoveToPosition` sends a clustered group along one shared path that is only 6 cells wide
(`PATH_DIAMETER_IN_CELLS`). Vehicles used 2 lanes 1.5 cells apart (`friend_moveVehicleToPos`), infantry 3
lanes (`friend_moveInfantryToPos`), every unit at its own top speed, so groups stretched into long trains.
Groups that weren't clustered pathfound unit by unit and all picked the same shortest route.

## Changes

| Where | Change |
|---|---|
| `AIGroup::friend_moveAbreastToPos` (new) | Player group moves form a block facing the move direction: up to 5 vehicle / 6 infantry lanes, spacing from the largest unit's radius. Each unit follows the group path at its lane offset; where the line to the next waypoint is blocked it pulls in to half, then zero offset. Front units take the front row, rows keep left-to-right order (no crossing paths), artillery-type units (`MOVES_BACK`) go to the rear. The block ends with its front row on the clicked point |
| `AIGroup::groupMoveToPosition` | Uses the abreast move for `CMD_FROM_PLAYER`; AI keeps the original column move. Helicopters no longer dissolve a Ctrl+F formation |
| `AIFollowPathState::onEnter` | Units in an abreast move keep the pace of the slowest unit of their kind (vehicles with vehicles, infantry with infantry) |
| `AIAttackApproachTargetState::onEnter` | Ctrl+F formations approach an attack target at the pace of their slowest member (attack-move already did, via `AIMoveToState`) |
| `AIGroup::groupCreateFormation`, `computeIndividualDestination`, `friend_moveFormationToPos` | Formation offsets are stored relative to the formation's facing (x forward, y left) and rotated to the move direction, so a formation turns along its path |
| `AI.h` | `m_moveAbreast`, `m_abreastSpeedInfantry/Vehicle` on `AIGroup` (not saved; `AIGroup::xfer` saves no state) |

## How to use

- **Normal selection + move:** units advance abreast; same-type units keep pace.
- **Combined-arms group:** arrange units (tanks in front, infantry behind, helicopters over them), select
  all, press **Ctrl+F**. The group keeps that arrangement, turns with its direction, moves and approaches
  attacks at the slowest member's speed. Ctrl+F again dissolves it.

## Manual test checklist

1. 10 tanks, move across open ground: block of 5 lanes x 2 rows, arrives as a line.
2. Same through a bridge or narrow pass: lanes merge, then spread again.
3. Mixed tanks + Humvees (abreast): vehicles hold one pace.
4. Ctrl+F with tanks in front of infantry + 2 helicopters, order a move behind the group: arrangement turns,
   tanks still in front, helicopters stay with it.
5. Same formation, right-click an enemy: units arrive together, fast ones don't run ahead.
6. Skirmish AI attacks still work (AI movement unchanged).

## Known limits

- Shift-click waypoint moves still use the original logic and dissolve formations.
- Fixed-wing aircraft still break formations (they can't fly at ground speed).
- Speed matching for normal selections is per kind; mixed infantry + vehicles are matched only in Ctrl+F groups.
