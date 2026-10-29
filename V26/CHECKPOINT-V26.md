# Cloudcourt VR v26 — sessions, feedback and venue identity

Baseline: delivered v25-trigger-fix, commit
2af9a34e7af73e50427ee1d0492c09a2fadc3b19. Recovery backup:
versions/cloudcourt-v25-antes-v26 (17 verified game files, 285 source files).
Previous delivered ZIPs are preserved. sources/ is read-only.

## Corrections

- Point and reason text activates the SDF material's OUTLINE_ON shader variant
  after font assignment. Merely setting width/color left that variant disabled.
  Each TMP instance owns its material; shared font assets remain untouched.
- Celebrating bots turn their decorative skeleton toward their chosen teammate,
  alongside the hand and head. Head yaw/pitch are bounded and diagonal bank is
  removed. Original poses restore before each IK pass and at the serve whistle.
  Gameplay transforms/colliders, recipient selection and wire format are retained.
- Indoor uses an original yellow/blue CloudCourt ball; Beach uses a distinct
  white/yellow/blue CloudCourt ball. The actual shared Resources ball binding has
  new original mesh/UV/art. An instance material selects its map's atlas half on
  every peer; a shared-material restore precedes instance cleanup.
- Graphics choices are saved for the next process. The menu explicitly requests
  restarting Cloudcourt. Rendering keeps one complete active preset until then,
  including after scene reloads, rather than mixing texture/AA/eye-buffer changes.
- Gym flags now carry an outlined vertical CloudCourt name, emblem and details.
  The standalone Indoor environment also carries visual net antennas, matching
  the separate GameRules net seen by peers. No antenna collision/rule is added.
- Changing face/outfit invalidates both CurvedUI caches and re-enters only the
  two noninteractive preview components. The panel/buttons/game lifecycle are
  never restarted. Selection preferences and live avatar appearance are retained.
- Lobby ball acquisition reuses the native serve Freeze RPC and the same
  placement above the palm. Native release/throw resumes physics. A fresh trigger
  still recalls the same owned ball; GRAB/A alone cannot create it.
- Beach's existing lobby net was missing its renderer. That renderer is restored
  and bound after environment readiness, shown only in practice, hidden at match
  start, and rebound when the environment changes. Its collider is retained.
- A symmetric world-space torso boundary now covers actual locomotion, teleport
  and room-scale motion on both online teams, including a freshly initialized
  client. Remote avatar updates cannot move the local player.
- A new online lobby/session clears stale waiting-ball/controller/roster/rally,
  jump/reception/spin, queued-team and practice state. Client rally setup binds
  fresh rules. Opening a menu over a live room preserves that match.

## Validation and limits

Focused native tests cover two ASLR bases, host/client eligibility, 2v2/4v4,
two consecutive sessions, controller/persistent-page reuse, delayed environment
readiness, material instance cleanup, gesture restoration and all 16 preset
transitions. Asset tests verify serialized references, geometry/UV/texture
readback, unchanged original scripts/transforms/physics/colliders and bounded
changes. Disposable Unity UI/material probes and final scene startups are
recorded separately from deterministic native fixtures.

Exact completed checks, package hashes, installation backup and public commit
are recorded in installation-status.json and analysis/v26-release-summary.json.
Those records, not this narrative alone, establish completed delivery.
Physical Quest 3 and real two-PC multiplayer confirmation remain pending.
No headset/FPS/real online test is claimed. Existing v24 room namespaces and
RPC layout are retained; friends should install the same v26 ZIP for all fixes.

Publish only scoped project source, own artwork and verification reports.
Do not publish base-game files, binary deltas, archives or backups to GitHub.
Keep the continuation automation active and avoid speculative changes after
delivery while waiting for physical playtests.
