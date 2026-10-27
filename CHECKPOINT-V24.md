# Cloudcourt VR v24 — celebrations, trigger spawn, graphics and sleeves

Baseline: delivered v23-maos-audio, commit acbb35b012b43aba88b50ee9feae6d2e5ae93f1c.
Recovery backup verified before edits: versions/cloudcourt-v23-antes-v24
(17 game files and 251 source files). Prior delivered ZIPs are preserved.
sources/ remains read-only. Only the native DLL, resources.assets and level0
change from v23; the other 14 packaged game files remain byte-identical.

## Player-facing changes

Winning bots point their existing connected thumbs-up arm and look at the
same human teammate until the real serve whistle. The authoritative host
prefers the actual winning human last hitter, including a direct human ace;
otherwise it chooses a random eligible teammate once for that point. The
recipient remains stable while moving. Tracked head height is followed, with
safe torso/root fallbacks. A removed, destroyed or switched-team recipient
is replaced by a deterministic eligible teammate. No human teammate means
no gesture. Original animation rotations/hand scale restore before native
IK and after celebration. Gameplay root transforms are never rotated.

The original Hand.WantsToGrab combines trigger and grip. Serve and practice
spawn/recall now separately require IController.GetTrigger (slot 4), never
GetGrip (slot 1). Existing hand attachment/throwing, single owned lobby ball,
fresh-press transfer, UI exclusion and remote-hand ownership checks remain.
GRAB continues controlling the approved setting/thumbs-up hand gestures.

Wrist sleeves now match each player's selected outfit for all eight hand
visual variants. Tank tops show a bare wrist matching the chosen hand tone.
Sleeve color is separate from hand skin and uses sampled cloth colors from
the authored outfit atlas. Existing appearance packets synchronize the choice;
no extra sleeve messages are sent. The v23 hand vertex data and bot hand
meshes stay unchanged; only player cuff triangles move to decorative children.

Settings > GRAPHICS offers a locally saved preset (default ULTRA):

| Setting | LOW | MEDIUM | HIGH | ULTRA |
|---|---:|---:|---:|---:|
| XR render scale | 70% | 85% | 95% | 100% |
| MSAA | Off | 2x | 4x | 4x |
| Texture resolution | Half | Full | Full | Full |
| Anisotropic filtering | Off | Enabled | Forced | Forced |
| Shadows | Off | Hard | Soft | Soft |
| Shadow resolution enum | 0 | 0 | 1 | 2 |
| Shadow distance | 15 m | 30 m | 60 m | 150 m |
| LOD bias | 0.6 | 1.0 | 1.4 | 2.0 |
| Soft particles / realtime reflections | Off | Off | On | On |

Individual render settings are used instead of SetQualityLevel, preserving
physics/skinning/scheduling settings. Original AdaptiveGraphics event setup
remains; its scale-only setter is replaced by the chosen scale. OVRManager
continues tracking/input updates while only its two automatic rendering flags
are disabled, so it cannot overwrite MSAA or render scale. This adds no
per-frame object searches or buffer reallocation loop.

## Validation and limits

Component tests cover bot targets/head restoration and reliable recipient
packets, human ace attribution without changing GameRules fields, sleeve
geometry/material caches, presets/preferences and UI bounds. Integrated x64
tests exercise both formats, relocated layouts, independent peer rosters,
trigger-only attachment, lobby recalls, pause/audio, appearances and scoring.
See analysis/v24-*.json and the final integration audit for exact evidence.

Controlled Unity tests verified six actual CurvedUI rays/PointerClicks,
rendering getter values, Adaptive/OVR override protection and persisted MEDIUM
on a fresh process before any selection. A controlled 15-second final startup
loaded Indoor successfully. The disposable runtime had no headset: XR eye
buffer allocation/render scale and FPS still require Quest 3 testing. Actual
two-PC multiplayer has not been tested. No headset/FPS claim is made.

Both online formats use new room namespaces because the point packet carries
the host-selected recipient: Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24.
All friends must use v24. Each still needs a compatible separately owned base
game. Ball/aim-assist physics and authored textures remain unchanged.

Final install hashes, backup, ZIP and commit are recorded in installation-status.json
and analysis/v24-release-summary.json. Installation requires the game closed;
never stop a user's match. Publish only scoped sources, authored artwork and
compact validation records; no base-game files, binary deltas, ZIPs or backups
on GitHub. Keep the continuation automation active as requested. Once the
recorded delivery is complete, only external playtests remain.
