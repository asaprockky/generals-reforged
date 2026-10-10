# Zero Hour 1.04 retail data bug audit

Date: 2026-10-10
Scope: bugs in data files (INI, WND, map.ini, strings) that can be fixed without engine/C++ changes. They are mapped to the pristine extract in `baseline\zh\`. All paths below are relative to `baseline\zh\`, and all line numbers were checked against that extract. Nothing under `baseline\` was modified.

## Sources

- TheSuperHackers/GeneralsGamePatch ("Patch104p"), v1.0 change logs:
  - [AllSortedBySeverity.md](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md): 924 entries, 464 labelled `bug`, 130 labelled `controversial`
  - [UsaOnlySortedByDate.md](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/UsaOnlySortedByDate.md), [ChinaOnlySortedByDate.md](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/ChinaOnlySortedByDate.md), [GlaOnlySortedByDate.md](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/GlaOnlySortedByDate.md)
  - Each entry's pull request diff, fetched with `gh pr diff`. The exact object and field for each fix come from these diffs.
  - The patch repo's `Patch104pZH/GameFilesOriginalZH/` (the unmodified 1.04 files it patches against) and `GameFilesEdited/` (the patched files, which carry `; Patch104p @bugfix` comments).
- Local pristine extract: `C:\projects\Generals\MOD\baseline\zh\`
- Local engine fork `C:\projects\Generals\MOD\engine\`. Its git history was checked for engine-side fixes that overlap these bugs.

## License finding

- The repo has no `LICENSE` file at its root (`/LICENSE` returns 404). The license is in **`LICENSE.txt` (GNU GPL v3)** together with **`TERMS.txt`**. The README links to both.
- `TERMS.txt` has two layers:
  1. **EA terms** apply to EA-derived assets, which includes every INI, WND and map.ini change. These terms require: non-commercial use only; no music files; the statement *"EA has not endorsed and does not support this product."* at the top of the website and in a root-level license/README file; no use of EA or C&C logos for promotion. EA can revoke the permission at any time.
  2. **The Super Hackers terms**: "You can redistribute and/or modify all EA assets under the same terms and license. **If you do not wish to publish your derivative Product under these terms, then you must not use any work of this Product in your distribution.**" Also: "Derivatives of this Product cannot solicit donations, unless they deviate by a substantial amount." Assets that are not derived from EA content are plain GPL v3.
- **Conclusion:** we may copy their INI changes into our mod **only if** we release the mod under the same terms:
  - GPL v3 plus the EA and TSH terms
  - non-commercial
  - no donation requests, unless the mod deviates substantially from theirs
  - the EA disclaimer is included

  Our engine is already a GPL-3 fork, so that is workable. If we want to keep licensing freedom (for example donations or Patreon, or other terms), **use the patch only as a bug reference** and write our own fixes. The facts about a bug (which field is wrong) are not copyrightable. Many fixes are one-token changes such as adding a KindOf flag or a DeathTypes filter, and re-implementing those independently is low-risk. Larger blocks are copyrightable expression, so re-author them rather than paste them. Examples: their `StructureArmor_NoSubdualDamage` armor, new OCLs, the `*StartingThings` system objects, and the hole-defence objects. Recommendation: **reference-only by default.** Copy only after the team explicitly accepts their terms, and record that decision in our LICENSE/README. (This is not legal advice.)

## Notable findings about our extract

1. **Our baseline matches the patch's 1.04 reference files exactly.** I compared all 215 files in `GameFilesOriginalZH/Data/INI/**` and `Window/**` by git blob hash and then by a whitespace-normalised diff. Every file matches after normalising CRLF and trailing whitespace, with 0 content differences. So every 1.04 bug the patch documents is present in our files.
2. **The live install is a Russian repack that overrides some files.** `Command & Conquer(tm) Generals Zero Hour\00RussianZH.big` (and `00Russian.big` in base Generals) replaces these files at runtime, because `00…` sorts before `EnglishZH.big`/`INIZH.big`/`WindowZH.big`:
   - `Data\English\generals.csf`: the Russian strings file (496 KB, versus 928 KB for the English one in baseline)
   - `Language.ini`
   - `Data\INI\Credits.ini` and `Data\INI\Video.ini`
   - 8 menu WNDs: MainMenu, OptionsMenu, ScoreScreen, LanLobby, MessageBox, NetworkDirectConnect, QuitMenu, ReplayMenu

   Our baseline holds the English originals of these files, so string and tooltip fixes (BUG-055, BUG-072) apply to whichever `generals.csf` we ship. `!ZHOverhaul.big` sorts before `00RussianZH.big` (`!` = 0x21, `0` = 0x30), so our archive still wins. `00SibSpeech.big` replaces about 3,160 English voice WAVs. There is also a non-standard `PatchZH.big` holding `AVAvnger.W3D`, `AVAvnger_D.W3D` and an empty `Data\*` entry. Its origin is unknown; check it before relying on stock Avenger art.
3. **Some of these bugs are already fixed in our engine fork, but the fixes are compiled out.** The relevant commits are:
   - `e6339f011`: Supply Drop Zone instant money when subdued during construction (BUG-006)
   - `a1d23478a` and `042fc8198`: power-plant negative power (BUG-007)
   - `0b9cf8b3e`: Nuke Missile outer-radius damage, which corresponds to the controversial "Nuke can't destroy GLA structures" entry

   The power-plant and Supply Drop Zone fixes sit behind `#if !RETAIL_COMPATIBLE_CRC`, and `Core/GameEngine/Include/Common/GameDefines.h:103` sets `RETAIL_COMPATIBLE_CRC (1)`. They are inactive in a default build. Our VS2022 build is already not CRC-compatible with retail, so building with `RETAIL_COMPATIBLE_CRC=0` would activate them, and the data workarounds for BUG-006/007 would become optional.
4. The patch's per-language hotkey-conflict entries (major, about 800 key fixes) concern the non-English `generals.csf` files. Those files are not in our baseline (English only), and the install actually runs the Russian CSF. They are listed under Unconfirmed.

## Summary

| Severity | Count (main list) |
|---|---|
| critical | 4 |
| major | 27 |
| minor | 43 |
| **total** | **74** |

Separate sections follow for **controversial** items (21), **unconfirmed** items (7), and **engine/C++ or art-dependent** items (10).

Notation: `File:line` means a line in our baseline. For "all variants" bugs every affected object is listed. Sub-faction prefixes: `AirF_`, `Lazr_`, `SupW_` (USA); `Tank_`, `Infa_`, `Nuke_` (China); `Chem_`, `Demo_`, `Slth_` (GLA); `Boss_`. `GC_*` files are the Generals Challenge copies.

---

## Critical

### BUG-001 · critical · GLA · Scud Storm "Scud bug": salvo can be fired before the timer runs out
- **What's wrong:** The Scud Storm's superweapon weapon sits in the PRIMARY slot, so it can be fired through a normal attack order rather than only through the special power. Players use this to launch the 9-missile salvo before the superweapon timer completes.
- **Where:**
  - WeaponSet `Weapon = PRIMARY …ScudStormWeapon` / `AutoChooseSources = PRIMARY NONE` in each Scud Storm object:
    - `Data/INI/Object/FactionBuilding.ini:12155-12156` (GLAScudStorm)
    - `Data/INI/Object/ChemicalGeneral.ini:4280-4281`
    - `Data/INI/Object/DemoGeneral.ini:4413-4414`
    - `Data/INI/Object/StealthGeneral.ini:4323-4324`
    - `Data/INI/Object/BossGeneral.ini:5821-5822`
    - `Data/INI/Object/GC_Chem_GLABuildings.ini:6634-6635`
    - `Data/INI/Object/GC_Slth_GLABuildings.ini:6980-6981`
  - The matching `ProjectileBoneFeedbackEnabledSlots = PRIMARY` lines: FactionBuilding.ini:10959, ChemicalGeneral.ini:3084, DemoGeneral.ini:3217, StealthGeneral.ini:3127, BossGeneral.ini:4624, GC_Chem_GLABuildings.ini:5438, GC_Slth_GLABuildings.ini:5784
  - `Data/INI/ObjectCreationList.ini:4211`: `WeaponSlot = PRIMARY` in `SUPERWEAPON_ScudStorm`
- **Fix:** Move the weapon to the SECONDARY slot in all 7 objects:
  - `Weapon = SECONDARY <weapon>` and `AutoChooseSources = SECONDARY NONE`
  - `ProjectileBoneFeedbackEnabledSlots = SECONDARY`
  - every `WeaponLaunchBone = PRIMARY WeaponA` becomes `SECONDARY WeaponA`
  - the `AliasConditionState … FIRING_A` / `BETWEEN_FIRING_SHOTS_A` entries become `…_B`
  - in the OCL, `WeaponSlot = SECONDARY`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/72

### BUG-002 · critical · China · Nuke Missile exploit
- **What's wrong:** The missile objects that sit in the silo have only `KindOf = UNATTACKABLE`. They lack IMMOBILE/INERT/NO_COLLIDE, which makes the documented Nuclear Missile exploit possible (the patch gives no further mechanics).
- **Where:**
  - `Data/INI/Object/WeaponObjects.ini:1823` (Object NeutronMissile)
  - `Data/INI/Object/WeaponObjects.ini:5523` (Object CruiseMissile)
  - `Data/INI/Object/SuperWeaponGeneral.ini:266` (Object SupW_NeutronMissile)
- **Fix:** `KindOf = IMMOBILE INERT NO_COLLIDE UNATTACKABLE` in all three.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/209

### BUG-003 · critical · GLA · Game crash when a Terrorist or Demo-General infantry unit dies while inside a container
- **What's wrong:** `FireWeaponWhenDeadBehavior` death weapons can fire while the unit is MASKED, meaning inside a transport or Combat Bike. Killing such a rider crashes the game.
- **Where:** each `FireWeaponWhenDeadBehavior` block below lacks `ExemptStatus`.
  - `Data/INI/Object/GLAInfantry.ini:1437` (GLAInfantryTerrorist)
  - `Data/INI/Object/ChemicalGeneral.ini:11979, 11985, 11993, 12001` (Chem_GLAInfantryTerrorist)
  - `Data/INI/Object/DemoGeneral.ini:13301` (Demo_GLAInfantryTerrorist)
  - `Data/INI/Object/StealthGeneral.ini:12981`
  - `Data/INI/Object/GC_Chem_GLAUnits.ini:3645, 3651`
  - `Data/INI/Object/GC_Slth_GLAUnits.ini:2213`
  - Demo infantry in `Data/INI/Object/DemoGeneral.ini`:
    - TunnelDefender 12745, 12752
    - StingerSoldier 13034, 13041
    - Hijacker 15424, 15431
    - Worker 15863, 15870
  - (Demo Rebel and Jarmen Kell death modules are commented out in retail.)
- **Fix:** add `ExemptStatus = MASKED` to every one of those modules. This postpones the explosion until the rider has exited.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/764, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2177

### BUG-004 · critical · All · Selecting a player beacon together with units can crash every client in a match
- **What's wrong:** `MultiplayerBeacon` is `SELECTABLE ALWAYS_SELECTABLE` but is not a STRUCTURE. A mixed selection of a beacon and units hits an engine path that assumes otherwise and crashes all clients. The changelog entry is "0_crash_bug". The commit history of FactionProp.ini identifies this fix: xezon, "Fix beacon crash by adding KindOf STRUCTURE".
- **Where:** `Data/INI/Object/FactionProp.ini:26`
- **Fix:** `KindOf = UNATTACKABLE SELECTABLE NO_COLLIDE ALWAYS_VISIBLE ALWAYS_SELECTABLE STRUCTURE IMMOBILE`. Optionally also add an `ArmorSet` with `Armor = InvulnerableAllArmor` and `DamageFX = DamageFX_Empty`, which silences a WorldBuilder assert.
- **Source:** [AllSortedBySeverity: link__20210822__0_crash_bug](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md#link__20210822__0_crash_bug) (no PR link; found via the file history of `GameFilesEdited/Data/INI/Object/FactionProp.ini`)

---

## Major

### BUG-005 · major · UI · Control Bar and General's Promotion buttons can be unresponsive
- **What's wrong:** These buttons activate only on mouse-up. Clicks get swallowed, especially when the cursor moves slightly during the click. (The patch rates this critical. I rate it major because it is a UX issue, not a crash or desync.)
- **Where:**
  - `Window/ControlBar.wnd:386` (ButtonDeleteBeacon), `:536` (ButtonClearBeaconText), `:632` (ButtonCommand14), `:2924` (OCLTimerSellButton)
  - `Window/GeneralsExpPoints.wnd`: all 23 `ButtonRank*Number*` buttons, STATUS lines 395 to 1429. None of them have `ON_MOUSE_DOWN`.
- **Fix:** append `+ON_MOUSE_DOWN` to those STATUS lines. Example: `STATUS = ENABLED+IMAGE+NOFOCUS+WRAP_CENTERED+ON_MOUSE_DOWN;`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/824

### BUG-006 · major · USA · Supply Drop Zone cash exploit (subdued while under construction)
- **What's wrong:** A Microwave Tank can subdue a Supply Drop Zone that is still under construction. When construction finishes, the zone pays out a large amount of cash immediately.
- **Where:** default `ArmorSet` (`Armor = StructureArmor`, which takes 100% SUBDUAL_BUILDING damage per `Data/INI/Armor.ini:584`) in:
  - `Data/INI/Object/FactionBuilding.ini:19271-19272` (AmericaSupplyDropZone)
  - `AirforceGeneral.ini:14481-14482`
  - `LaserGeneral.ini:14165-14166`
  - `SuperWeaponGeneral.ini:13603-13604`
- **Fix:**
  1. Add a new `Armor StructureArmor_NoSubdualDamage`: a copy of StructureArmor with `SUBDUAL_MISSILE/VEHICLE/BUILDING 0%`.
  2. Use it as the `Conditions = None` ArmorSet, and add a second ArmorSet with `Conditions = PLAYER_UPGRADE` and `Armor = StructureArmor`.
  3. Add `GrantUpgradeCreate` (UpgradeToGrant = a new OBJECT-type `Upgrade_DummyUpgrade`, `ExemptStatus = UNDER_CONSTRUCTION`) plus an `ArmorUpgrade` triggered by that upgrade.
  4. Define `Upgrade_DummyUpgrade` in Upgrade.ini; retail has no such upgrade.

  Alternative: build the engine with `RETAIL_COMPATIBLE_CRC=0` to activate fork commit `e6339f011`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/3, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/831

### BUG-007 · major · USA/China · Permanent negative power from a Power Plant subdued during construction
- **What's wrong:** A power plant disabled by a Microwave Tank while under construction loses power it never produced. Once it is sold or destroyed, the player is left with permanently negative power.
- **Where:** default ArmorSet `Armor = StructureArmor` in:
  - `FactionBuilding.ini:4824-4825` (AmericaPowerPlant) and `:17892-17893` (ChinaPowerPlant)
  - `AirforceGeneral.ini:9681-9682`
  - `LaserGeneral.ini:9381-9382`
  - `SuperWeaponGeneral.ini:17309-17310`
  - `NukeGeneral.ini:10001-10002`
  - `InfantryGeneral.ini:8304-8305`
  - `TankGeneral.ini:7917-7918`
  - `BossGeneral.ini:2374-2375`
- **Fix:** the same armor-swap pattern as BUG-006. Engine alternative: commits `a1d23478a` and `042fc8198` with `RETAIL_COMPATIBLE_CRC=0`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/7, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/831, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/832

### BUG-008 · major · China · Nuke Cannon Neutron Shells usable without the upgrade
- **What's wrong:** The default WeaponSet already contains `SECONDARY NukeCannonNeutronWeapon`. Neutron shells can be fired without researching Neutron Shells.
- **Where:** `Data/INI/Object/ChinaVehicle.ini:1547-1552` (ChinaVehicleNukeLauncher), `InfantryGeneral.ini:2204`, `NukeGeneral.ini:3672`
- **Fix:**
  - The default WeaponSet keeps only `PRIMARY NukeCannonGun`.
  - Add a `WeaponSet` with `Conditions = PLAYER_UPGRADE` containing PRIMARY NukeCannonGun and SECONDARY NukeCannonNeutronWeapon, with the existing AutoChooseSources.
  - Add `Behavior = WeaponSetUpgrade` with `TriggeredBy = Upgrade_ChinaNeutronShells`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/262

### BUG-009 · major · USA/China/GLA · Extended-range exploit (ground units hit from far outside range)
- **What's wrong:** An attack order on an out-of-range target lets the unit auto-acquire and switch targets while still carrying the extended range. Affected units: TOW Humvee, Gattling Tank and Quad Cannon.
- **Where:** `AutoAcquireEnemiesWhenIdle` without `NotWhileAttacking`:
  - `AmericaVehicle.ini:162`, `AirforceGeneral.ini:5264`, `LaserGeneral.ini:4508`, `SuperWeaponGeneral.ini:4987` (Humvees)
  - `ChinaVehicle.ini:1877`, `InfantryGeneral.ini:2531`, `NukeGeneral.ini:3998`, `TankGeneral.ini:4121`, `BossGeneral.ini:20143` (Gattling)
  - `GLAVehicle.ini:3271`, `ChemicalGeneral.ini:15937`, `DemoGeneral.ini:17934`, `StealthGeneral.ini:17350`, `GC_Chem_GLAUnits.ini:2514`, `GC_Slth_GLAUnits.ini:6787` (Quad)
- **Fix:** append `NotWhileAttacking`. Examples: `AutoAcquireEnemiesWhenIdle = Yes NotWhileAttacking` and `= Yes Stealthed NotWhileAttacking`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/285

### BUG-010 · major · USA · Colonel Burton instant Knife Attack exploit
- **What's wrong:** `PreAttackType = PER_ATTACK` means firing the gun first skips the knife's pre-attack delay, so the knife kills instantly.
- **Where:** `Data/INI/Weapon.ini:972` (ColonelBurtonKnifeWeapon)
- **Fix:** `PreAttackType = PER_CLIP`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2287

### BUG-011 · major · GLA/China · Captured faction buildings hand out that faction's inherent upgrades
- **What's wrong:** Inherent sub-faction upgrades are granted by `GrantUpgradeCreate` on buildings, so anyone who captures (or builds) one of these buildings receives the upgrades:
  - Toxin: Toxin Shells and Anthrax Beta
  - Demo: Booby Trap
  - Infantry General: Nationalism
- **Where:**
  - `ChemicalGeneral.ini:868-873` (Chem_GLACommandCenter)
  - `DemoGeneral.ini:1003-1004` (Demo_GLACommandCenter)
  - `InfantryGeneral.ini:4241-4242`, `9727-9728`, `10782-10783` (CC, Barracks, War Factory)
- **Fix:** remove these modules and grant the upgrades from a faction-only source, for example a self-deleting INERT system object spawned for the faction at game start. The patch uses `*StartingThings` objects in System.ini.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/827

### BUG-012 · major · GLA · Destroyed Tunnel, Stinger Site and Demo Trap holes keep a defeated player alive
- **What's wrong:** The defensive structures reuse the generic hole object, whose KindOf includes `MP_COUNT_FOR_VICTORY`. A player who has only a tunnel or stinger hole left is not eliminated.
- **Where:**
  - `FactionBuilding.ini:134` (GLAHole KindOf); reskins at `14577, 15164, 15682, 16230`
  - Same pattern in `ChemicalGeneral.ini:123` (reskins 4572, 5129), `DemoGeneral.ini:256` (4692, 5277, 5860), `StealthGeneral.ini:123` (4621, 5159, 5706), `GC_Slth_GLABuildings.ini:2670, 3203`
- **Fix:** create a `*GLAHole_Defences` copy of each hole object without `MP_COUNT_FOR_VICTORY`, and point the DemoTrap, TunnelNetwork, TunnelNetworkNoSpawn and StingerSite hole reskins at it.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/75 ([changelog entry](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/GlaOnlySortedByDate.md))

### BUG-013 · major · China · General's Powers disappear from the Command Center after the Mines upgrade
- **What's wrong:**
  - The post-Mines command sets drop Frenzy (Nuke and Infantry General).
  - The Infantry General's set swaps in the wrong Carpet Bomb button (`Command_ChinaCarpetBomb` instead of `Early_Command_ChinaCarpetBomb`) and a Napalm Strike button, and moves Paradrop.
- **Where:**
  - `Data/INI/CommandSet.ini:3047-3060` (Nuke_ChinaCommandCenterCommandSetUpgrade: no slot 10, compared with 3041 in the base set)
  - `:3782-3795` (Infa_ChinaCommandCenterCommandSetUpgrade: slots 2, 3, 5 and missing 10, compared with base 3753-3766)
- **Fix:** make each `…Upgrade` set identical to its base set apart from the mines button:
  - Nuke: add `10 = Command_Frenzy`
  - Infa: `2 = Early_Command_ChinaCarpetBomb`, `3 = Infa_Command_Paradrop`, remove the NapalmStrike and slot-5 entries, add `10 = Early_Command_Frenzy`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/301

### BUG-014 · major · USA/China/GLA · Sub-faction-exclusive units cannot be built from another sub-faction's factory
- **What's wrong:** The unlock science for each exclusive unit is only granted by that sub-faction's own building, so the unit cannot be built from another sub-faction's factory:
  - Airforce General: Stealth Fighter from a non-AFG Airfield
  - Nuke General: Nuke Cannon from a normal or Infantry War Factory
  - Stealth General: Hijacker from a vanilla Barracks
- **Where:** `Data/INI/PlayerTemplate.ini:223` (FactionAmericaAirForceGeneral), `:326` (FactionChinaNukeGeneral), `:431` (FactionGLAStealthGeneral), each `IntrinsicSciences = SCIENCE_<SIDE>`
- **Fix:** append `SCIENCE_StealthFighter`, `SCIENCE_NukeLauncher` and `SCIENCE_Hijacker` respectively.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/331

### BUG-015 · major · USA · Strategy Center gun does not attack the ordered target
- **What's wrong:** `AutoChooseSources = PRIMARY NONE` stops the gun from engaging targets that the player orders it to attack.
- **Where:** `FactionBuilding.ini:6970`, `AirforceGeneral.ini:11828`, `LaserGeneral.ini:11516`, `SuperWeaponGeneral.ini:10952`
- **Fix:** delete the `AutoChooseSources` line in all four.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1524

### BUG-016 · major · China · Tank and Nuke Listening Outposts cannot properly attack buildings
- **What's wrong:** These two variants use `AssaultTransportAIUpdate`. The Tank variant also has an armed default WeaponSet. Together this breaks attacks on structures.
- **Where:**
  - `TankGeneral.ini:4876` (AssaultTransportAIUpdate) and `:4809` (`Weapon = PRIMARY ListeningOutpostUpgradedDummyWeapon` in the default set)
  - `NukeGeneral.ini:4745`
- **Fix:**
  - Replace the module with `Behavior = TransportAIUpdate` (with `AutoAcquireEnemiesWhenIdle = No`), as the vanilla outpost does.
  - Make the default WeaponSet `PRIMARY NONE`, and move the dummy weapon into a `Conditions = PLAYER_UPGRADE` set.
  - Add `ArmedRidersUpgradeMyWeaponSet = Yes`, as vanilla does at `ChinaVehicle.ini:2664`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/4, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/484

### BUG-017 · major · China · Nuke Cannon wastes its first shot on the nearest enemy after deploying
- **Where:** `ChinaVehicle.ini:1628`, `InfantryGeneral.ini:2282`, `NukeGeneral.ini:3749` (`AutoAcquireEnemiesWhenIdle = No`)
- **Fix:** `AutoAcquireEnemiesWhenIdle = No NotWhileAttacking`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/269

### BUG-018 · major · China · Inferno Cannon hits sometimes trigger no firestorm and no hit sound
- **What's wrong:** A `HeightDieUpdate` makes the shell die above ground before its detonation logic runs.
- **Where:** `Data/INI/Object/WeaponObjects.ini:5047` (InfernoTankShell), `:5113` (InfernoTankShellUpgraded)
- **Fix:** remove both `HeightDieUpdate` blocks.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1564

### BUG-019 · major · USA · Humvee freezes when it auto-targets an out-of-range aircraft
- **Where:** `Data/INI/Weapon.ini:680` (HumveeMissileWeaponAirDummy `AttackRange = 320.0`)
- **Fix:** `AttackRange = 150.0`. This is the highest range at which missile passengers reliably engage.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/270

### BUG-020 · major · GLA · Battle Bus freezes when it auto-targets an out-of-range aircraft
- **Where:** `Data/INI/Weapon.ini:8420` (BattleBusDummyWeapon `AttackRange = 320.0`)
- **Fix:** `AttackRange = 150.0` (the patch rates this minor, but it is the same bug as BUG-019).
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/267

### BUG-021 · major · GLA · Camo-netted Stealth Palace stays stealthed while its garrison fires
- **Where:** `StealthGeneral.ini:6503` (Slth_GLAPalace `StealthForbiddenConditions = ATTACKING USING_ABILITY TAKING_DAMAGE`), `GC_Slth_GLABuildings.ini:4754` (`= FIRING_PRIMARY`)
- **Fix:** add `RIDERS_ATTACKING` to both.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/75

### BUG-022 · major · GLA · Demo Traps triggered by enemy building scaffolds and base defences
- **Where:** `IgnoreTargetTypes = PROJECTILE UNATTACKABLE` at:
  - `FactionBuilding.ini:14541`
  - `ChemicalGeneral.ini:4525`
  - `DemoGeneral.ini:4656`
  - `StealthGeneral.ini:4585`
  - `GC_Chem_GLABuildings.ini:1147`
  - `GC_Slth_GLABuildings.ini:5717`
- **Fix:** `IgnoreTargetTypes = PROJECTILE UNATTACKABLE FS_BASE_DEFENSE STRUCTURE`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/94

### BUG-023 · major · GLA · Demo Terrorist dies on mines, fire or explosions without detonating
- **What's wrong:** Its death weapon only fires on `SUICIDED`. Other Terrorists also fire on CRUSHED, SPLATTED, LASERED, BURNED and EXPLODED.
- **Where:** `DemoGeneral.ini:13304` (Demo_GLAInfantryTerrorist, ModuleTag_Death08 `DeathTypes = NONE +SUICIDED`)
- **Fix:** `DeathTypes = NONE +SUICIDED +LASERED +BURNED +EXPLODED`. Adding CRUSHED/SPLATTED as well is the controversial part; see C-07.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/316

### BUG-024 · major · GLA · Demo-General infantry get stuck near structures when ordered to suicide
- **Where:** `Data/INI/Weapon.ini:4756` (TerroristSuicideNotARealWeapon `AttackRange = 0.0`)
- **Fix:** `AttackRange = 999999.0`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/914

### BUG-025 · major · GLA · Toxin Tunnel Defender fires its ground and air rockets simultaneously (double DPS)
- **Where:** WeaponSets without `ShareWeaponReloadTime`: `ChemicalGeneral.ini:11327-11339`, `GC_Chem_GLAUnits.ini:796-808`
- **Fix:** add `ShareWeaponReloadTime = Yes` to each WeaponSet.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1334

### BUG-026 · major · GLA · Stinger Site troopers double-fire by switching between ground and air targets
- **Where:** Stinger Soldier WeaponSets without `ShareWeaponReloadTime` (none exist anywhere in GLAInfantry.ini):
  - `GLAInfantry.ini:1054`
  - `ChemicalGeneral.ini:11582, 11589`
  - `DemoGeneral.ini:12886`
  - `StealthGeneral.ini:12601`
  - `GC_Chem_GLAUnits.ini:182, 189`
  - `GC_Slth_GLAUnits.ini:518`
- **Fix:** add `ShareWeaponReloadTime = Yes` to each WeaponSet.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/294

### BUG-027 · major · GLA · Mixed groups of Demo units cannot all be ordered to suicide at once
- **What's wrong:** `Demo_Command_TertiarySuicide` sits in different slots (1, 2, 3, 4, 5, 9, 11, 12, 13) across the Demo command sets. A multi-selection only shows a button when it occupies the same slot for every unit.
- **Where:** `Data/INI/CommandSet.ini`, lines 1962-2461. Examples: 2214, 2226, 2273, 2285, 2300, 2321, 2328, 2376, 2401, 2445.
- **Fix:** move every `Demo_Command_TertiarySuicide` to one common free slot (the patch uses 12) and relocate whatever was in that slot.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/163

### BUG-028 · major · GLA · Demo Scud Launcher deals full 500 suicide damage on any death
- **What's wrong:** The death module has no `DeathTypes`, so it fires on every death type.
- **Where:** `DemoGeneral.ini:19035-19039` (ModuleTag_George, `DeathWeapon = Demo_SuicideDynamitePackPlusFire`, 500 damage per `Weapon.ini:6699`)
- **Fix:**
  - Restrict it to `DeathTypes = NONE +SUICIDED`.
  - Add a second module with `DeathWeapon = Demo_DestroyedWeapon` (50 damage), `StartsActive = No`, `TriggeredBy = Demo_Upgrade_SuicideBomb`, `DeathTypes = ALL -SUICIDED`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1074

### BUG-029 · major · GLA · Upgraded Demo Stinger Site deals about 20x intended damage when destroyed
- **Where:** `DemoGeneral.ini:5825-5831` (ModuleTag999, `Demo_SuicideDynamitePackPlusFire` on `DeathTypes = ALL -SUICIDED …`), plus the always-on `ModuleTag_Death18` at 5819-5823
- **Fix:** set up the death modules the same way as other Demo structures:
  - SUICIDED deaths: Demo_SuicideDynamitePack
  - all other deaths: Demo_DestroyedWeapon
  - both gated by `Demo_Upgrade_SuicideBomb`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2308

### BUG-030 · major · China · Satellite Hack I never reveals Command Centers built after the upgrade
- **What's wrong:** `SpyVisionUpdate` with `SelfPowered` only snapshots the existing Command Centers.
- **Where:** `FactionBuilding.ini:34015-34019` (ChinaInternetCenter), `InfantryGeneral.ini:13734-13738`, `NukeGeneral.ini:16259-16263`, `TankGeneral.ini:15274-15278`
- **Fix:** replace it with a `FireWeaponUpdate` that periodically fires a dummy reveal weapon (the patch uses `SatelliteHackOneDummyWeapon`, gated by the upgrade), or another re-scanning mechanism.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/791

### BUG-031 · major · Civilian · Highrise buildings invisible on snow maps
- **What's wrong:** All 14 SNOW condition states per building reference models that do not exist (`CBHigh0x_S`, `_DS`, `_ES`, `_RS`, `_SG`, `_DSG`, `_SN`, `_DSN`, `_ESN`, `_RSN`, `_SNG`, `_DSNG`). I checked these against the 8,988 entries in `W3DZH.big` and `W3D.big`: none of them exist, while all the day and night models do. The result is an invisible but still garrisonable building.
- **Where:** `Data/INI/Object/CivilianBuilding.ini:18628-18682` (CivilianHighrise01; model lines 18629-18680), `:18831-18885` (CivilianHighrise02; model lines 18832-18883)
- **Fix:** delete or comment out every `… SNOW` ConditionState in these two objects, so they fall back to the day and night models.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/559

---

## Minor

### BUG-032 · minor · GLA · Scud Storm cannot damage itself
- **Where:** `Weapon.ini:1637` (ScudStormDamageWeapon), `:1655` (…Upgraded), `:6568` (Chem_ScudStormDamageWeaponGamma), `:7568` (Demo_ScudStormDamageWeapon), each `RadiusDamageAffects = ALLIES ENEMIES NEUTRALS`
- **Fix:** `RadiusDamageAffects = SELF ALLIES ENEMIES NEUTRALS`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/328

### BUG-033 · minor · GLA · Scud Storm does not reload all its missiles if the salvo is stopped part-way
- **Where:** `Weapon.ini:1580-1625` (ScudStormWeapon), `6509-6556` (GC_Chem_), `7582-7626` (Demo_), `7844-7890` (Chem_). None of them have `AutoReloadWhenIdle`.
- **Fix:** add `AutoReloadWhenIdle = 10100`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1703

### BUG-034 · minor · GLA · A crushed Marauder becomes an indestructible lingering object
- **What's wrong:** The SlowDeath excludes CRUSHED/SPLATTED and only an `FXListDie` handles a crush. Nothing destroys the object.
- **Where:** `GLAVehicle.ini:5774-5799`, `ChemicalGeneral.ini:18128-18152`, `DemoGeneral.ini:20270-20294`, `StealthGeneral.ini:19646-19669`
- **Fix:** add `CreateObjectDie` (`DeathTypes = NONE +CRUSHED +SPLATTED`, `CreationList = OCL_CrusaderTank_CrushEffect`) and `DestroyDie` (`DeathTypes = NONE +CRUSHED +SPLATTED`).
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/90

### BUG-035 · minor · GLA · Heroic Quad Cannon cannot be disabled by the ECM Tank
- **What's wrong:** Heroic max health exceeds `SubdualDamageCap = 440`.
- **Where:** `GLAVehicle.ini:3259`, `ChemicalGeneral.ini:15925`, `DemoGeneral.ini:17922`, `StealthGeneral.ini:17338`
- **Fix:** `SubdualDamageCap = 600`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/442

### BUG-036 · minor · GLA · Stinger Sites auto-attack enemy buildings
- **Where:** `AutoAcquireEnemiesWhenIdle = Yes Stealthed ATTACK_BUILDINGS` at:
  - `GLAInfantry.ini:1100`
  - `ChemicalGeneral.ini:11635`
  - `DemoGeneral.ini:12934`
  - `StealthGeneral.ini:12647`
  - `GC_Chem_GLAUnits.ini:235`
  - `GC_Slth_GLAUnits.ini:561`
- **Fix:** drop `ATTACK_BUILDINGS`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/296

### BUG-037 · minor · GLA · Sub-faction Stinger troopers are not damaged individually by the Microwave Tank (they all die at once)
- **Where:**
  - `PropagateDamageTypesToSlavesWhenExisting` lacks `+MICROWAVE` at `ChemicalGeneral.ini:5050`, `DemoGeneral.ini:5751`, `StealthGeneral.ini:5630`, `GC_Chem_GLABuildings.ini:929`, `GC_Slth_GLABuildings.ini:2595`. Vanilla already has it, at `FactionBuilding.ini:16154`.
  - `Armor.ini:697` (StingerSiteArmor `MICROWAVE 1%`)
- **Fix:** append `+MICROWAVE` to those lines, and set StingerSiteArmor `MICROWAVE 0%`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/913

### BUG-038 · minor · GLA · Scud Launcher missile runs out of fuel before reaching targets at max upgraded range
- **Where:** `WeaponObjects.ini:3075` (SCUDMissile `FuelLifetime = 5000`)
- **Fix:** `FuelLifetime = 9999` and add `DetonateOnNoFuel = Yes`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1041

### BUG-039 · minor · GLA · Vanilla Hijacker and Saboteur can ride the Toxin General's Combat Bike
- **Where:** `ChemicalGeneral.ini:15598-15599` (Rider6/Rider7 = GLAInfantryHijacker / GLAInfantrySaboteur). The patch also edits 3 bikes in `GC_Slth_GLAUnits.ini`.
- **Fix:** remove those rider entries, or point them at the Chem_ variants.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/168

### BUG-040 · minor · GLA · Demo and Stealth Saboteurs level up by collecting crates (vanilla cannot)
- **Where:** `DemoGeneral.ini:15985-15986`, `StealthGeneral.ini:15507-15508` (`IsTrainable = Yes`). Vanilla is at `GLAInfantry.ini:3967` (`IsTrainable = No`).
- **Fix:** `IsTrainable = No` and remove `ExperienceRequired`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1170

### BUG-041 · minor · GLA · Stealth General Rebels are revealed when taking damage (no other stealth unit is)
- **Where:** `StealthGeneral.ini:11779`
- **Fix:** `StealthForbiddenConditions = ATTACKING USING_ABILITY`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1706

### BUG-042 · minor · GLA · Toxin stream times out when firing at distant ground or allies
- **Where:** `WeaponObjects.ini:3624` (ToxinTruckStreamProjectile), `GC_Chem_GLAUnits.ini:983` (`FuelLifetime = 500`)
- **Fix:** `FuelLifetime = 1000`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2063

### BUG-043 · minor · GLA · Worker loses Clear Mines while the Fake Structures command set is open
- **Where:** `CommandSet.ini:63-71` (GLAWorkerFakeBuildingsCommandSet). The normal set has it at `:60`. The Demo_ variant needs the same change.
- **Fix:** add `14 = Command_DisarmMinesAtPosition`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1578

### BUG-044 · minor · GLA · Palace and Tunnel Network lack a Stop button (garrison cannot be told to cease fire)
- **Where:** `CommandSet.ini:1198-1211` (GLAPalaceCommandSet), `:1220-1236` (GLATunnelNetworkCommandSet, where `;12 = Command_Stop` at 1233 is commented out). The sub-faction and GC copies need the same change.
- **Fix:** add `13 = Command_Stop` to the Palace set. For the Tunnel, the patch replaces `13 = Command_SetRallyPoint` with `13 = Command_Stop`; we could instead relocate the rally point if we want to keep it.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/386

### BUG-045 · minor · GLA · Salvage Crate is missing the CRATE KindOf
- **Where:** `Data/INI/Crate.ini:195`
- **Fix:** `KindOf = PARACHUTABLE CRATE SELECTABLE`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1675

### BUG-046 · minor · China · Battlemasters from different sub-factions don't form a Horde
- **Where:** `ChinaVehicle.ini:119`, `NukeGeneral.ini:16463`, `TankGeneral.ini:2793` (`ExactMatch = Yes`)
- **Fix:** `ExactMatch = No`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/255

### BUG-047 · minor · China · Helix Gattling Cannon unreliably shoots aircraft directly in front of it
- **Where:** `ChinaAir.ini:401-402`, `NukeGeneral.ini:680-681` (`Weapon = SECONDARY GattlingBuildingGunAir` and its PreferredAgainst)
- **Fix:** remove the SECONDARY air weapon from the Helix Gattling attachment.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/284

### BUG-048 · minor · China · Speaker Tower cannot research Mines
- **Where:** `CommandSet.ini:962-965` (ChinaSpeakerTowerCommandSet, `; 10 = Command_UpgradeChinaMines` commented out), `:967-970` (…Upgrade, EMP Mines)
- **Fix:** `12 = Command_UpgradeChinaMines` and `12 = Command_UpgradeEMPMines`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/317

### BUG-049 · minor · China · Troop Crawler and Assault Troop Crawler have no Guard button
- **Where:** `CommandSet.ini:428-440`, `:4004-4016`
- **Fix:** add `13 = Command_Guard`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/974

### BUG-050 · minor · China · ECM Tank has no Attack Move button
- **Where:** `CommandSet.ini:414-418` (ChinaVehicleECMTankCommandSet), `:4652-4656` (Tank_)
- **Fix:** add `11 = Command_AttackMove`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2000

### BUG-051 · minor · China · Black Napalm Dragon Tank flamethrower has wrong values
- **What's wrong:** Minimum range 10 instead of 0, and an infinite clip.
- **Where:** `Weapon.ini:2967` (`MinimumAttackRange = 10.0`), `:2979-2980` (`ClipSize = 0`, `ClipReloadTime = 0`) in DragonTankFlameWeaponUpgraded
- **Fix:** `MinimumAttackRange = 0.0`, `ClipSize = 30`, `ClipReloadTime = 40`. These match the unupgraded weapon; check them against `DragonTankFlameWeapon`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1588, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2050

### BUG-052 · minor · China · Artillery Barrage shells randomly kill each other
- **What's wrong:** The result is random damage variance against structures.
- **Where:** `Weapon.ini:5037` (ArtilleryBarrageDamageWeapon)
- **Fix:** `RadiusDamageAffects = ENEMIES NEUTRALS ALLIES NOT_SIMILAR`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1905

### BUG-053 · minor · China · Supply Truck has a tiny mass and is flung sky-high by physics weapons
- **Where:** `Mass = 5.0` at `ChinaVehicle.ini:2059`, `InfantryGeneral.ini:2716`, `NukeGeneral.ini:4179`, `TankGeneral.ini:4306`, `BossGeneral.ini:13804`, `CivilianUnit.ini:10773` (ToxicSupplyTruck)
- **Fix:** `Mass = 50.0`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/96, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2293

### BUG-054 · minor · China · Nuke MiG upgrade cannot be bought on low power (every other upgrade can)
- **Where:** `CommandButton.ini:2512-2520` (Command_UpgradeChinaTacticalNukeMig, no Options line)
- **Fix:** add `Options = IGNORES_UNDERPOWERED`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/376

### BUG-055 · minor · USA · Laser General's Aurora build button shows the Microwave Tank tooltip
- **Where:** `CommandButton.ini:7349` (Lazr_Command_ConstructAmericaJetAurora `DescriptLabel = CONTROLBAR:ToolTipUSABuildMicrowave`)
- **Fix:** `DescriptLabel = CONTROLBAR:ToolTipUSABuildAurora`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/194

### BUG-056 · minor · USA · Paradrop always drops vanilla USA Rangers for the AFG, Laser and Superweapon generals
- **What's wrong:** Paradropped Rangers are the vanilla type, so they are not grouped by double-click with the sub-faction's own Rangers.
- **Where:** `AirforceGeneral.ini:8589-8591`, `LaserGeneral.ini:8309-8311`, `SuperWeaponGeneral.ini:8783-8785`. All use `SUPERWEAPON_Paradrop1-3`; only vanilla and `Infa_` Paradrop OCLs exist, at `ObjectCreationList.ini:4847-4905`.
- **Fix:** add `AirF_`, `Lazr_` and `SupW_SUPERWEAPON_Paradrop1-3` OCLs that spawn each faction's Ranger, and reference them.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/286

### BUG-057 · minor · USA · Destroyed sub-faction Particle Cannons spawn vanilla Rangers
- **Where:** `OCL = FINAL OCL_ParticleUplinkDeathFinal` (which spawns AmericaInfantryRanger, `ObjectCreationList.ini:2224-2227`) at:
  - `AirforceGeneral.ini:10661`
  - `LaserGeneral.ini:10366, 17954, 18906`
  - `SuperWeaponGeneral.ini:9802`
  - `BossGeneral.ini:3407`
- **Fix:** add per-faction death OCLs, for example `OCL_AirF_ParticleUplinkDeathFinal`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/75

### BUG-058 · minor · USA · Sub-faction Avengers retaliate and drive into danger (vanilla doesn't)
- **Where:** KindOf lacking `CANNOT_RETALIATE`: `AirforceGeneral.ini:7123`, `LaserGeneral.ini:6827`, `SuperWeaponGeneral.ini:7301`, `BossGeneral.ini:19238`. Vanilla has it, at `AmericaVehicle.ini:2484`.
- **Fix:** append `CANNOT_RETALIATE`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/157

### BUG-059 · minor · USA · Heroic Pilot walks slower than a normal Pilot
- **What's wrong:** At Heroic the Pilot switches from ColonelBurtonGroundLocomotor to BasicHumanLocomotorPlus25 (speed 25).
- **Where:** `AmericaInfantry.ini:1553` and `1559` (LocomotorSetUpgrade); same at `AirforceGeneral.ini:4343/4349`, `LaserGeneral.ini:3901/3907`, `SuperWeaponGeneral.ini:4380/4386`
- **Fix:** remove the `SET_NORMAL_UPGRADED` locomotor and its `LocomotorSetUpgrade`. Optionally drop the unused Chemical Suits and Advanced Training UpgradeCameos (AmericaInfantry.ini:1396-1397).
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/160

### BUG-060 · minor · USA · Combat, Laser and Superweapon Chinooks gather supplies slower than vanilla
- **What's wrong:** Their delays are 3000/1250 ms against vanilla's 2900/1200 ms (`AmericaAir.ini:2257-2258`).
- **Where:** `AirforceGeneral.ini:17629-17630` (AirF_ Combat Chinook), `LaserGeneral.ini:2014-2015`, `SuperWeaponGeneral.ini:2486-2487`
- **Fix:** `SupplyCenterActionDelay = 2900`, `SupplyWarehouseActionDelay = 1200`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/193

### BUG-061 · minor · USA · Avenger turns its whole chassis when ordered to attack aircraft
- **Where:** `Weapon.ini:8398-8416` (AvengerAirLaserDummy, no AcceptableAimDelta)
- **Fix:** add `AcceptableAimDelta = 180`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/314

### BUG-062 · minor · USA · Units waste shots attacking fuel-air, MOAB and Daisy Cutter gas clouds
- **Where:** `KindOf = IMMOBILE` at `WeaponObjects.ini:100` (MOABGas), `:1779` (DaisyCutterGas), `:5764` (SupW_AuroraFuelAirGas), and `AirforceGeneral.ini:56` (AirF_AuroraBombGas)
- **Fix:** `KindOf = IMMOBILE UNATTACKABLE`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/441

### BUG-063 · minor · USA · Aurora Alpha fuel-air explosion sometimes triggers at the first building it touches, not where the bomb lands
- **What's wrong:** The projectile "dies" on its first collision but keeps travelling, and its die modules spawn the secondary explosion at that point.
- **Where:** `WeaponObjects.ini:5723-5728` (SupW_AuroraFuelAirBomb `CreateObjectDie` (SupW_OCL_FuelAirBomb) and `FXListDie`), plus its `HeightDieUpdate`; the `HeightDieUpdate` of SupW_AuroraFuelAirGas
- **Fix:**
  1. Remove the bomb's CreateObjectDie, FXListDie and HeightDieUpdate.
  2. Trigger `SupW_OCL_FuelAirBomb` and the FX from the detonation of `SupW_AuroraFuelBombWeapon` in Weapon.ini.
  3. Add `Offset = X:0 Y:0 Z:15` in the OCL.
  4. Replace the gas object's HeightDieUpdate with `LifetimeUpdate` (0/0).
  5. Set ParticleSystem `AirF_AuroraBombScatter1` `SystemLifetime = 1`.

  This is the most involved minor fix; check it in game.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/292

### BUG-064 · minor · USA · Toxin weapons cannot target the Fire Base
- **Where:** `Armor.ini:960` (FireBaseArmor `POISON 0%`)
- **Fix:** `Armor = POISON 1%`, matching other structures.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1556

### BUG-065 · minor · USA · Snipers (Jarmen Kell, Pathfinder) can kill Fire Bases on campaign maps CHI03 and GLA03
- **What's wrong:** The map override replaces the HiveStructureBody and drops `PropagateDamageTypesToSlavesWhenExisting = NONE +SNIPER` and the Subdual fields that the base object has (`FactionBuilding.ini:34494-34505`).
- **Where:** `Maps/MD_CHI03/map.ini:128-134`, `Maps/MD_GLA03/map.ini:171-177`
- **Fix:** add `SubdualDamageCap = 600`, `SubdualDamageHealRate = 500`, `SubdualDamageHealAmount = 100`, `PropagateDamageTypesToSlavesWhenExisting = NONE +SNIPER` inside the overriding Body.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2296

### BUG-066 · minor · USA · Shot-down Aurora wrecks can circle forever
- **Where:** `DestructionDelay = 99999999` at `AmericaAir.ini:1340`, `AirforceGeneral.ini:1736`, `BossGeneral.ini:14418`. The patch also caps other plane and helicopter wrecks.
- **Fix:** `DestructionDelay = 10000`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1018, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2194

### BUG-067 · minor · All · Units keep firing at burning or poisoned dying infantry
- **Where:** `Data/INI/Object/System.ini:1262` (FlamingInfantry `KindOf = CAN_CAST_REFLECTIONS INFANTRY`), `:1341` (ToxicInfantry)
- **Fix:** `KindOf = CAN_CAST_REFLECTIONS UNATTACKABLE`. Dropping INFANTRY also stops Point Defense Lasers from targeting them.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2072, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2237

### BUG-068 · minor · USA/China · GPS-scrambled Rangers, Red Guards and Hackers stay stealthed while capturing or hacking
- **What's wrong:** No unit has its own GPS-granted `StealthUpdate`, so the engine default applies and does not forbid USING_ABILITY.
- **Where:** `AmericaInfantry.ini:527-1073` (AmericaInfantryRanger), `ChinaInfantry.ini:3-435` (Redguard), `:1145-1449` (Hacker), plus the sub-faction copies. No `GrantedBySpecialPower` exists anywhere in retail.
- **Fix:** add `Behavior = StealthUpdate` with:
  - `StealthDelay = 2000`
  - `StealthForbiddenConditions = FIRING_PRIMARY FIRING_SECONDARY FIRING_TERTIARY USING_ABILITY`
  - `InnateStealth = No`
  - `GrantedBySpecialPower = Yes`
  - `OrderIdleEnemiesToAttackMeUponReveal = Yes`
  - friendly opacity 50-100%
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/276

### BUG-069 · minor · Boss · Boss General unit stats deviate from their faction originals
- **Where and fix:**

  | Item | Where | Wrong value | Fix |
  |---|---|---|---|
  | Black Lotus health | `BossGeneral.ini:17031-17032` | `MaxHealth`/`InitialHealth = 150` | 200 |
  | Hacker speed inside Internet Center | `BossGeneral.ini:17760` | `CashUpdateDelayFast = 1500` | 1800 |
  | Jarmen Kell vision | `BossGeneral.ini:18109` | `ShroudClearingRange = 300` | 400 |
  | Tunnel Network build time | `BossGeneral.ini:8565` | `BuildTime = 5.0` | 15.0 |
  | Aurora flare evasion | `BossGeneral.ini:14483` | `EvasionRate = 50%` | 30% |

  Reference values elsewhere: Lotus `ChinaInfantry.ini:679` = 200; Hacker `ChinaInfantry.ini:1333` = 1800; Jarmen `GLAInfantry.ini:567` = 400.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/450, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/451, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2170

### BUG-070 · minor · Boss · Boss Scud Storm cannot upgrade Neutron Mines, and the Reinforcement Pad gives the Boss nothing
- **Where:**
  - Boss_ScudStorm uses `CommandSet = Boss_GLAScudStormCommandSet` (`BossGeneral.ini:5814`) with no `CommandSetUpgrade`, although `Boss_GLAScudStormCommandSetUpgrade` exists (`CommandSet.ini:5030`).
  - `TechBuildings.ini:429-441` has no `FactionOCL` for FactionBossGeneral.
- **Fix:**
  - Add `Behavior = CommandSetUpgrade` (`CommandSet = Boss_GLAScudStormCommandSetUpgrade`, `TriggeredBy = Upgrade_ChinaMines`).
  - Add `FactionOCL = Faction:FactionBossGeneral OCL:<new Boss reinforcement OCL>`. The patch spawns a Boss Dragon Tank.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/380, https://github.com/TheSuperHackers/GeneralsGamePatch/pull/375

### BUG-071 · minor · Civilian · Destroying an enemy-held Reinforcement Pad or Repair Pad awards 200 XP
- **Where:** `TechBuildings.ini:406` (TechReinforcementPad), `:628` (TechRepairPad)
- **Fix:** remove `ExperienceValue`.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/308

### BUG-072 · minor · All · Faction-variant units use different hotkeys from their base units (English strings)
- **What's wrong:** Mismatches I confirmed by parsing baseline `Data/English/generals.csf`:

  | Variant (hotkey) | Base unit (hotkey) | Button line |
  |---|---|---|
  | Mini-Gunner (I) | Red Guard (G) | `CommandButton.ini:7138` |
  | Super Lotus (S) | Black Lotus (B) | `:7165` |
  | Attack Outpost (O) | Listening Outpost (S) | `:7246` |
  | Assault Troop Transport (A) | Troop Crawler (T) | `:7228` |
  | Nuke Bomber (K) | Carpet Bomb (T) | `:419` |
  | Laser Tank (T) | Crusader (C) | `:7565` |

  Multi-type selections and muscle memory break.
- **Fix:** change the `&` position in those CSF strings, and apply it to whichever CSF we ship (the install currently loads Russian). The alternative is pointing the buttons at shared labels.
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2143

### BUG-073 · minor · USA · Patriot assist beam causes frame drops
- **Where:** `FactionBuilding.ini:28449` (`InnerBeamWidth = 4`), `:28453` (`Segments = 20`), `:28456` (`TilingScalar = 0.25`) in PatriotBinaryDataStream. The AirF_ and Boss_ copies need the same change.
- **Fix:** `Segments = 5`, `InnerBeamWidth = 5`, `TilingScalar = 0.66`. The patch measured about 60% less lag.
- **Source:** [changelog entry 0_patriot_beam_lag](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md#link__20210822__0_patriot_beam_lag)

### BUG-074 · minor · All · 13 explosion particle systems render broken
- **What's wrong:** `Color1 = R:3 G:0 B:0 0`.
- **Where:** `ParticleSystem.ini` lines:
  - 10225 ArmExplosionSmall01
  - 16980 airCarrierHotPillarArms
  - 18457 BuggyNewExplosionArms
  - 20155, 20268, 20440 airCarrierJetExplosion1/2/3
  - 23900 MammothTankExplosionArms
  - 30989 FireBaseHowitzerPillarArms
  - 32305 HotPillarArms
  - 38449 airCarrierJet01Explosion
  - 47666 BarrelExplosion
  - 48290 airCarrierExplosion2
  - 61576 SpectreHotPillarArms
- **Fix:** `Color1 = R:6 G:6 B:6 0`
- **Source:** https://github.com/TheSuperHackers/GeneralsGamePatch/pull/809

---

## Controversial (balance-flavoured; the patch labels these "controversial")

These are real inconsistencies in the retail data, but fixing them changes balance. Balance will be redesigned later, so they are tracked here rather than in the main list. Line numbers were verified where given. The patch has 130 controversial entries in total; most of the rest are pure balance (XP, speeds, Sentry Drone rework, Internet Center armor and so on). See [ControversialOnlySortedByFaction.md](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/ControversialOnlySortedByFaction.md).

| ID | Faction | Issue | Where (verified) | Patch change | Source |
|---|---|---|---|---|---|
| C-01 | USA | Laser and AFG Avengers secretly get +100 HP from Composite Armor | `AirforceGeneral.ini:7253`, `LaserGeneral.ini:6957` (MaxHealthUpgrade) | remove module | [PR 407](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/407) |
| C-02 | USA | Pilot entering a Humvee may take a passenger seat instead of promoting it | `AmericaVehicle.ini:177` (`AllowInsideKindOf = INFANTRY`) | `ForbidInsideKindOf = NO_GARRISON` | [PR 1220](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1220) |
| C-03 | USA | Missile Defender kills don't trigger Terrorist or Demo death explosions | `Weapon.ini:776`, `:803` (`DeathType = NORMAL`) | `EXPLODED` | [PR 2362](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2362) |
| C-04 | China | Emperor lacks Subliminal Messaging bonus and icon | `TankGeneral.ini:2878`, `:3021-3022` (commented-out cameo and GrantUpgradeCreate) | enable | [PR 236](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/236) |
| C-05 | China | Tank, Infantry and Nuke ECM Tanks auto-attack (vanilla doesn't) | `InfantryGeneral.ini:3054`, `NukeGeneral.ini:4517`, `TankGeneral.ini:4644` (vanilla `ChinaVehicle.ini:2398` = No) | `= No` | [PR 631](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/631) |
| C-06 | China | CC door times 3000 ms, War Factory 4000/2000/5000 ms (slower than USA) | `FactionBuilding.ini:3733-3735`, `:27791-27793` | 1500; 3300/3000/3300 | [PR 785](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/785), [PR 786](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/786) |
| C-07 | GLA | Demo Terrorist can be crushed without exploding | `DemoGeneral.ini:13304` | add CRUSHED/SPLATTED (plus a new low-damage crush weapon, #697) | [PR 316](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/316) |
| C-08 | GLA | Toxin Terrorists chain-kill each other on any death | `ChemicalGeneral.ini:11993-12008` (ModuleTag_92/93, no DeathTypes) | add the standard terrorist DeathTypes | [PR 695](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/695) |
| C-09 | GLA | Toxin Terrorist deals 700 damage before Gamma and 500 after | `Weapon.ini:7912`, `:7932` (Chem_SuicideWeapon / Beta `PrimaryDamage = 200.0`; Gamma at 7892 = 0) | 0.0 | [PR 699](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/699) |
| C-10 | GLA | Car Bomb stops chasing a fleeing target | `Weapon.ini:2309-2330` (SuicideCarBomb, no LeechRangeWeapon) | `LeechRangeWeapon = Yes` | [PR 307](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/307) |
| C-11 | GLA | Promoted Quad Cannon loses damage after picking up scrap | `Weapon.ini:2622-2728` (QuadCannonGun / UpgradeOne / UpgradeTwo veterancy bonuses) | redistribute bonuses | [PR 1055](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1055) |
| C-12 | GLA | Salvage and money crates deleted by building scaffolds | `Crate.ini:195` | add `INERT` | [PR 1676](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1676), [PR 443](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/443) |
| C-13 | China/GLA | Small hazard fields cleaned before large ones | not verified | per-size cleanup health | [PR 2023](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2023) |
| C-14 | USA | Flashbang Rangers cannot target Stinger Sites | not verified | | [PR 297](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/297) |
| C-15 | USA | Laser Turret clip sizes differ per mode | not verified | | [PR 373](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/373) |
| C-16 | USA | AFG Avenger has 30% extra armor vs Jet Missiles | not verified | | [PR 403](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/403) |
| C-17 | China | Frenzy reveals shroud | not verified | | [PR 593](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/593) |
| C-18 | GLA | Demo Trap triggered by Anthrax and radiation puddles | not verified | | [PR 440](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/440) |
| C-19 | GLA | Demo Combat Bike deals no suicide damage when killed by Anthrax Gamma; Demo Terror Bike without upgrade damages allies | not verified | | [PR 104](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/104), [PR 783](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/783) |
| C-20 | All | Evacuate buttons in different slots across transports (group evacuate impossible) | not verified | | [PR 165](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/165), [PR 1894](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1894) |
| C-21 | China | Nuke Missile cannot fully destroy large GLA structures | engine (see engine section) | | [entry 410](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md#link__20210905__410_nuke_missile_blasts) |

---

## Unconfirmed (could not be confirmed in our files)

| Issue | Why unconfirmed | Source |
|---|---|---|
| Granger cannot call the Carpet Bomber in Generals Challenge | `Maps/GC_AirGeneral/map.ini` indeed has no science grant, but the failure is in the AI script inside the binary `.map`, which our baseline doesn't contain | [PR 1085](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1085) |
| Demo Battle Bus vanishes without damage on suicide | Death modules at `DemoGeneral.ini:20859-20935` exist; the patch's fix (dummy OCL object) is more involved and was not traced fully | [PR 102](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/102), [PR 1504](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1504), [PR 2164](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2164) |
| Hotkey conflicts in German, French, Spanish, Italian, Brazilian and Polish strings (about 800 keys; the patch rates these major) | Those `generals.csf` files are not in our baseline; the install runs the Russian CSF from `00RussianZH.big`. Re-audit whichever CSF we ship | [PR 2108](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2108), [PR 2112](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2112), [PR 2117](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2117), [PR 2118](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2118), [PR 2136](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2136), [PR 2138](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2138) |
| Mixed USA sub-faction vehicle groups can't build drones in one click | `SupW_`/`Lazr_Command_ConstructAmericaVehicle*Drone` buttons are confirmed (`CommandSet.ini:3557-3690`, `4336-4402`), but the claim that they are functionally identical to the generic `Command_…Drone` buttons was not verified | [PR 166](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/166) |
| Briefing and speech subtitles print too slowly | `MilitaryCaptionSpeed` lives in the per-language `Language.ini`; the patch calls it a bug only for es/it/ko/zh (a tweak for English), and the install uses the Russian `Language.ini` | [PR 2326](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2326) |
| China Carpet Bomber hotkey breaks when a Nuke CC and another China CC are both owned | `Boss_CommandCenter` and the China CC special-power modules share one enum; the fix needs per-variant OCLSpecialPower modules. Not traced in our files | [PR 299](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/299) |
| Arms Dealer door timing lets the second Technical leave late or early | `DoorWaitOpenTime = 3000`, `DoorCloseTime = 2000` confirmed (`FactionBuilding.ini:25859-25860`, etc.), but the "powered" production timing claim was not reproduced | [PR 538](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/538) |

---

## Engine/C++ or art-dependent (not fixable by data alone)

These need engine work (we are building the engine from source) or new art. The data workarounds above cover the symptoms of several of them.

| Issue | Root cause and status | Source |
|---|---|---|
| Scud bug (BUG-001) | Engine lets a PRIMARY superweapon slot be fired by attack orders. The data workaround is the slot move; no engine fix found in the fork's git log | [PR 72](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/72) |
| Beacon + unit selection crash (BUG-004) | Engine assumes ALWAYS_SELECTABLE non-structures are mobile. Fork has related beacon fixes (`143673a4f`, `4de89c35f`) but none for this exact case | [entry 0_crash_bug](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md#link__20210822__0_crash_bug) |
| MASKED death-weapon crash (BUG-003) | Engine fires a death weapon from inside a container. Fork has OpenContain crash fixes (`eea0e7e03`, `bab63d407`) that may or may not cover this; keep the data guard regardless | [PR 764](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/764) |
| SDZ cash and negative power (BUG-006/007) | Fixed in the fork (`e6339f011`, `a1d23478a`, `042fc8198`) but disabled while `RETAIL_COMPATIBLE_CRC = 1` (`GameDefines.h:103`) | [PR 3](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/3), [PR 7](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/7) |
| Nuke Missile outer-radius damage (C-21) | Fork commit `0b9cf8b3e`, controlled by `PRESERVE_RETAIL_NUKE_MISSILE_OUTER_RADIUS_*` (already 0 = fixed) | [entry 410](https://github.com/TheSuperHackers/GeneralsGamePatch/blob/main/Patch104pZH/ReleaseFiles/English/Changes/v1.0/AllSortedBySeverity.md#link__20210905__410_nuke_missile_blasts) |
| Extended-range and auto-target switching (BUG-009/017) | Engine target-acquisition logic. `NotWhileAttacking` is a data mitigation | [PR 285](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/285) |
| Transport freezes on out-of-range air targets (BUG-019/020) | Engine contained-AI behaviour. The range cap is a mitigation | [PR 270](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/270) |
| GPS Scrambler default stealth ignores USING_ABILITY (BUG-068) | Engine-generated default StealthUpdate. The data module overrides it | [PR 276](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/276) |
| GLA Palace occupants fire from the building centre | Requires new W3D models (`UBPalace_FP9.W3D`, `UBPalace_FPX.W3D`) plus a Draw module; art, not data-only | [PR 1097](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/1097) |
| China Tank Hunters destroy their own Bunker on uneven terrain | Needs new fire-port bones in the Bunker W3D models | [PR 2133](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2133), [PR 2154](https://github.com/TheSuperHackers/GeneralsGamePatch/pull/2154) |
