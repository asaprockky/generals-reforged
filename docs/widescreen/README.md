# 16:9 widescreen (1920x1080)

Engine branch `reforged/widescreen-16x9` in `MOD/engine` (base: TheSuperHackers `090934812`, 2026-10-10).
Uncommitted; full diff in `reforged-widescreen-16x9.patch`. All changes are tagged `Reforged @feature`.

## Findings (verified in source before changing anything)

- **3D camera was Hor-.** `W3DView::setWidth` fixes the horizontal FOV at 50 deg; `CameraClass::Set_View_Plane(hfov, -1)`
  derives the vertical FOV from the aspect ratio. At 16:9 the vertical FOV fell from 38.6 deg (4:3) to 29.5 deg, so the
  view was cropped top/bottom and everything was drawn 33% larger.
- **UI was stretched.** All 1670 WND windows are authored at 800x600 and scaled x by width/800 and y by height/600
  (2.4 x 1.8 at 1920x1080). Control bar art (`ControlBarScheme`), its buttons, fonts, sliders, battle-honor icons and
  military subtitles each repeat that math separately.

## Changes

| File | Change |
|---|---|
| `Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DView.cpp` | `getWidescreenHorizontalFov()`: Hor+ (keep the 4:3 vertical FOV, widen horizontally). Used in `setWidth` and the debug-only `setCameraTransform` path. Widening capped at 16:9 |
| `Core/GameEngine/Include/GameClient/Display.h` | `getUIWidth()` = min(width, height*4/3), `getUIOffsetX()` = centering offset |
| `Core/GameEngine/Source/GameClient/GUI/GameWindowManagerScript.cpp` | WND rects scaled uniformly into the centered 4:3 UI area |
| `Core/GameEngine/Source/GameClient/GUI/ControlBar/ControlBarScheme.cpp` | Control bar art and the 9 scheme-placed buttons use the same scale and offset |
| `Core/GameEngine/Source/GameClient/GlobalLanguage.cpp` | Classic font scaling methods (incl. the default) measure the UI area, so text matches box sizes |
| `Core/GameEngineDevice/Source/W3DDevice/GameClient/GUI/Gadget/W3DHorizontalSlider.cpp` | Slider boxes scaled like the UI area |
| `GeneralsMD/Code/GameEngine/Source/GameClient/InGameUI.cpp` | Military subtitle position mapped into the UI area |
| `GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/PopupPlayerInfo.cpp` | Battle-honor icon width scaled like the UI area |
| `Core/GameEngine/Source/GameClient/GUI/ControlBar/ControlBar.cpp` | Full-height world view when the control bar is centered (displays wider than 4:3) |

Displays 4:3 or narrower take exactly the original code paths (`getUIWidth() == getWidth()`, offset 0, FOV unchanged).
Only Zero Hour (`GeneralsMD`) was updated; the base-Generals copies of the last two files were not.

## Automated test results

Captures in `captures/`, taken by `tools/capture-window.ps1` (windowed, game window only). The replay
pauses or plays identically each run, giving a fixed scene to compare.

| Check | Result |
|---|---|
| Build | Clean, no new warnings |
| 16:9 3D: centre 1440 columns of new frame vs 4:3 frame | 0.1% pixels differ: same vertical framing as 4:3, +240 px each side |
| 16:9 3D, old build vs 4:3 (control) | 20.1% differ: old build cropped/zoomed |
| 4:3 3D, new vs old | 0.3-0.55% (smoke/timing): unchanged |
| 4:3 control bar, new vs old | 0.15%: unchanged |
| 16:9 control bar | Proportional, centered; scheme art aligned with buttons and radar |
| Replay recorded by baseline plays on new build | No desync: changes are client-side only |
| Terrain draw area (calculated) | Needs ~109 of 129 cells at max zoom + 45 deg yaw; far clip 1290 > ~936 depth |

## Requires manual testing

Not automatable here (no input control): scroll to all four map edges, max zoom-out with camera rotation (look for
undrawn terrain at screen sides), clicking/selecting units at the far left/right screen edges, every menu screen,
options sliders, tooltips, campaign cinematics, and one game at a 4:3 resolution.
Launch: `MOD\Play-Widescreen-Build.cmd`.

## Known issues

1. ~~Black bottom corners in game~~ Fixed (user chose option A): on displays wider than 4:3 the world is drawn at full
   height (`ControlBar::setScaledViewportHeight`). Framing on 16:9 therefore no longer matches 4:3 pixel-for-pixel:
   the view centre moves down and more terrain shows at the top and corners. 4:3 is unchanged.
2. **Black side bars on menus with static backdrops** (lobbies, score screen, and the main menu when launched with
   `-quickstart`, which turns off the live menu map). A normal launch shows the live 3D map across the full width.
3. HUD overlays positioned as screen fractions (superweapon timers, player list, clock) stay screen-relative, not UI-relative.
4. Edge-scroll map limits use a vertical-only offset; at left/right map edges more off-map border may be visible.

## Rebuild

```
cmd /c "C:\projects\Generals\MOD\tools\build-engine.cmd"
```
Output: `MOD\engine\build\win32\GeneralsMD\Release\generalszh.exe`. Back up working builds to `MOD\builds\` first.
