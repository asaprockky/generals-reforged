# Graphics and animation upgrades

## 1. Smooth rendering (engine)

Originally the fps limit *was* the game speed: the logic advanced once per rendered frame, so the game
rendered at 30 fps. The engine (TheSuperHackers) can already interpolate drawn movement and animation
between logic frames, but in single player the logic only decouples when the "logic time scale" is on.

`FramePacer::setGameSpeedFps(fps)` (new) sets the logic time scale to the game speed and the render
limit to the display refresh rate (`EnumDisplaySettings`, clamped 30-360, 60 if unknown). Used where the
game speed was set before: engine start (`GameData.ini FramesPerSecondLimit`), new game / skirmish game
speed slider / replays (`GameLogicDispatch`), campaign script `SET_FPS_LIMIT` and script reset.
Network games keep the network logic rate. Ctrl+Numpad +/- still change the render limit.

**Verified:** render 144 fps on the 144 Hz display; game clock advances 1.00 s per wall second
(`logic-speed-at-144fps.png`: 0.23 -> 1.23 -> 2.23 s over 1 s captures).

## 2. Detail presets

| Preset | Change |
|---|---|
| High (`mod/Data/INI/GameLOD.ini`, used by default) | Particles 3000 -> 5000; tank tracks opaque 25 -> 60 edges, visible 60 -> 120 s; heat effects on |
| VeryHigh (`GameLOD.cpp`, Options menu) | Particles 5000 -> 8000; same tank track change |

`MaxTankTrackEdges` stays 100: `W3DTerrainTracks` stores edges in a fixed 100-element array
(`MAX_TRACK_EDGE_COUNT`); more would corrupt memory.

## 3. Texture filtering and anti-aliasing (user options)

`Options.ini` set to `TextureFilter = Anisotropic`, `AnisotropyLevel = 16`, `AntiAliasing = 4` (4x MSAA).
Backup: `MOD/backups/Options.ini.before-graphics.bak`. **Verified** on a fixed frame
(`aa-anisotropic-before-after.png`): thin geometry (railings) and edges anti-aliased; 1.8% of pixels changed.
Note: this file is shared by every exe, including the retail one.

## Not done (needs a decision or assets)

- **New/better unit animations** are art (W3D keyframes); needs 3D tooling and artists, not engine code.
- **HD textures / remodels**: community mods exist (C&C Generals Zero Hour: Enhanced, Modern Warfare,
  Generals HD Patch on ModDB). Their licences are unknown; they are other authors' work, so not copied.
- **Post-processing** (bloom, SSAO, god rays): the DX8 renderer has none; ReShade (via a d3d8-to-d3d9
  wrapper) is the common route and is a user-side install.
## 4. Farther zoom-out

`mod/Data/INI/GameData.ini`: `MaxCameraHeight` 310 -> 500 (1.6x). Engine (`W3DView::getDesiredTerrainDrawSize`):
the player camera switches to the larger 257-cell terrain draw area above height 300 (back below 270, to avoid
rebuilding the terrain buffers repeatedly). The far clip plane already follows the draw area.
Sizing: at pitch 37.5 and 16:9 the view's far edge is ~3.76 x camera height wide, so 129 cells covers up to ~310
and 257 cells up to ~590 with a 15% margin for hills.

**Verified** at height 500, camera rotated 45 deg (temporary test data): undrawn black in the left half of the view
28.9% with the previous build, 0.3% with the new build (`zoom500-yaw45-*.png`). The remaining black is beyond the
map edge.

**Use with the Reforged build only.** The mod archive also applies to the retail and prebuilt exes in the MOD
install; they lack the draw-area change and will show black gaps when zoomed out past the old limit.
