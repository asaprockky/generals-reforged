# Faction generator (Reforged)

Placeholder factions are built by cloning retail blocks and editing them. Art stays retail until real models
exist. One spec per faction: `tools/factiongen/specs/<name>.py`. See `build.py`'s docstring for the spec format
and `specs/soviet.py` for a working example (tested in game).

## Workflow
```
python tools/factiongen/build.py <spec> --dry-run   # validate only
python tools/factiongen/build.py <spec>             # write mod/Data/INI/<Kind>/Reforged_<Side>.ini + out/<Side>.strings.json
python tools/check-ini-refs.py                      # must end with "0 unresolved reference(s)"
```
`merge_strings.py` (strings -> generals.csf), `deploy.py install` and in-game tests are run by the lead, one at a
time (the game allows one instance). Test command: `generalszh.exe -setCwd <game dir> -win -xres 1920 -yres 1080
-skirmishTest Faction<Side> FactionChina "Maps\Death Valley\Death Valley.map"`.

## Engine facts (verified)
- **Full clones only.** `ObjectReskin` can change only Draw/geometry. Every unit/building is a full `Object` copy
  (the builder does this from `clone=`). Never clone an ObjectReskin.
- **Load order.** Science -> PlayerTemplate -> FXList -> Weapon -> ObjectCreationList -> Locomotor -> SpecialPower
  -> Armor -> Object -> Upgrade -> CommandButton -> CommandSet. Each loads `X.ini` then `X\*.ini`. Weapons, armor,
  FX, OCLs, locomotors and special powers are looked up **while parsing** objects, so they must exist in an
  earlier stage (the builder writes each kind to its own folder, which satisfies this). Upgrades and command
  sets referenced from objects are looked up later by name.
- **Unknown names are fatal** in: CommandSet button lists, Science prerequisites, CommandButton
  `Object=/Upgrade=/Science=/SpecialPower=`. The builder checks the common cases; `check-ini-refs.py` more.
- **Unknown fields** inside a block are fatal at startup. Only use fields that exist in retail blocks of the same
  type; when unsure, clone a retail block that already has the field.
- **New side gets for free:** control bar = base side's scheme; build list in skirmish if `StartingBuilding` set.
  No AI (human-only factions, as decided). EVA speech is silent unless added later.
- **General's powers** (promotion panel): all three rank command sets must exist (the builder creates
  `SCIENCE_<SIDE>_CommandSetRank1/3/8` from `FACTION["rank_sets"]`). Slots: Rank1 = 4, Rank3 = 15, Rank8 = 4.
  Chain per power:
  1. root science `SCIENCE_<SIDE>` (auto, intrinsic)
  2. `Science <Name>`: `PrerequisiteSciences = SCIENCE_<SIDE> SCIENCE_Rank1` (or Rank3/Rank8, or another
     science for level 2/3), `SciencePurchasePointCost = 1`, `IsGrantable = Yes`, `DisplayName`/`Description`
     labels (clone a retail science such as `SCIENCE_ChinaCarpetBomb` and edit)
  3. a `PURCHASE_SCIENCE` CommandButton (`Science = <Name>`) in a rank set
  4. a `SpecialPower` with `RequiredScience = <Name>` (clone a retail one, e.g. `SuperweaponCarpetBomb`)
  5. a module on the command center that owns the power (e.g. `OCLSpecialPower` with `SpecialPowerTemplate =`),
     plus a `SPECIAL_POWER` button with `Options = NEED_SPECIAL_POWER_SCIENCE ...` in the CC command set
  6. the same power in `FACTION["shortcut_set"]` with a `*_FROM_SHORTCUT` button (clone a retail one)
- **Superweapons** need a `SpecialPower` + the building's `OCLSpecialPower`/`SpecialAbility` module +
  `Command = SPECIAL_POWER` button. Clone a retail superweapon building and its power, and rename both.
- **Cloned command centers** carry the base faction's general's-power modules. Strip them
  (`remove_modules=["OCLSpecialPower", "SpecialAbility", ...]` or `remove_tags`) and add your own.
- **Melee**: use very short `AttackRange` (5-15) contact weapons; `DamageType` must be a valid retail type.

## Naming
Prefix every block name with the faction prefix (`Ger_`, `Sov_`, `Eng_`, `Imp_`) so factions never collide with
each other or retail. Strings: `OBJECT:<name>` (unit name), `CONTROLBAR:Construct<name>` (button label, `&` marks
the hotkey), `CONTROLBAR:ToolTipBuild<name>` (tooltip); other labels via `STRINGS`.

## Content rules
- WWII Germany: Wehrmacht/Luftwaffe military only. No swastikas, no SS/Nazi-party units or ideology, no
  atrocity references; use the Balkenkreuz (Iron Cross) where an emblem is described.
- Star Wars Empire: personal non-commercial fan content; original text, no quotes from the films.
- Unit names and descriptions: short, factual, game-like. Tooltips under ~120 characters.
