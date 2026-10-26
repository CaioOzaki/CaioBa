# Cloudcourt VR v23 — rounded hand style and pause UI audio

Baseline: delivered v22-correcoes (9e5914caae8d4a4f464c5a77b6549ecc03bb1643).
Verified recovery backup: versions/cloudcourt-v22-antes-v23 (17 game files,
239 source files). Prior ZIPs preserved. sources/ remains read-only.

## Authorized changes

- Default open/closed hands are 10% thinner in the palm-normal local X direction.
  Their width, length, cuff, tracking transforms and physical hit shapes remain.
- Thumbs-up and cupped setting hands now share the same rounded palm/cuff and
  scale as the standard glove. Continuous smooth rounded digits replace the
  thinner segmented gesture look. Four curled fingers/+Y thumb edge, mirrored
  left/right winding and spread/flexed setting fingers are retained.
- The bot's connected wrist uses the corresponding new thumb mesh at the same
  anchor and 1.30 scale. Per-player skin tones, GRAB/second-touch conditions,
  post-IK arm lifecycle and the approved ball/aim-assist physics remain intact.
- UI click source alone now ignores AudioListener.pause, using the verified
  Unity native binding cached through il2cpp_resolve_icall. Global listener,
  timeScale and gameplay audio are never resumed or changed. Existing 2D local
  feedback keeps its cached source/clip; inactive/disabled buttons stay silent.
  Null binding fallback is safe and the source is configured on recreation.

## Evidence and scope

The real Unity probe confirmed ordinary Time 0 already played UI clicks. The
reproduced silent branch was AudioListener.pause=true: original Resume/Leave
played 0 samples, while the corrected source advances 1646 samples. Leave keeps
both Time 0 and listenerPause=true, proving the change is source-only. Actual
pause-menu pointer clicks reach Button.Press once; the main-menu source remains
active and is reused after match transition. Probe preferences were restored
and only the owned disposable game process was stopped.

The geometry helper changes 13 existing MeshFilter links and adds 8 authored
meshes. All previous objects outside that exact whitelist are byte-identical,
including textures/materials, transforms, controllers, colliders, physics and
scripts. Tests verify smooth finite normals, outward nondegenerate triangles,
mirrors, bounds, common palm/cuff, default 10% thickness and idempotency. Offline
serialized-geometry previews include equal-scale v22/v23 and bot wrist views.

Focused native/audio/input/menu/pause regressions and complete installer tests
are recorded in analysis/v23-*.json. Prior v22 gameplay/IK/network tests remain
applicable because those mechanisms are unchanged; do not claim rerunning all
previous suites. Final installation, ZIP hash and public commit are recorded
in installation-status.json and analysis/v23-release-summary.json.

No new Quest 3/headset-focus/FPS or real two-PC playtest is claimed. In particular,
the hardware-specific focus sequence that sets listener pause remains a user
playtest. This delivery retains v22 room namespaces and pose protocol:
Cloudcourt-2v2-v22 / Cloudcourt-4v4-v22. Friends should use the same v23 package
for identical visuals; each still needs a compatible separately owned base game.

Publish only scoped sources, original art and validation summaries to
CaioOzaki/CaioBa; no game binaries, extracted assets, ZIPs or backups. Install
only with game closed. Keep the continuation automation active as requested;
after recorded delivery, only external playtests remain.
