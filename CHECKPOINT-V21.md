# Cloudcourt VR v21 — Orla, hands and lobby practice

Base: Cloudcourt-v20-1-middle-part. A verified backup of the 17 game files and
175 source files is preserved in versions/cloudcourt-v20-1-antes-v21. Previous
release ZIPs are preserved. sources/ remains read-only.

## Changes

- CUSTOMIZE refreshes face/outfit previews immediately, invalidating both the
  CurvedUI UV cache and Graphic vertices; a controlled Unity click probe
  confirmed changing choices without closing the panel.
- Six independently saved hand tones; separate left/right thumbs-up and open
  setting meshes. A single GRAB gives thumbs-up. Both GRABs give two thumbs,
  except an eligible second team touch uses the open setting gesture. Existing
  tracking, ball holding, hitboxes and the approved set trajectory are retained.
- Hand tones/poses travel with each player's reliable appearance update in both
  online formats. Initialized hands cache leaves/materials and toggle only when
  needed; ordinary frames do not search the hierarchy or allocate path strings.
- Winning-team bots direct a short thumbs-up toward the nearest human on their
  own team. Losing teams and teams without human teammates do not celebrate.
- A point's exact contact circle stays visible until the next serve ball appears.
  The new referee whistle is original procedural audio, generated once/reused.
  Human serve feedback uses the actual synchronized serving player, avoiding a
  stale host-only field on invited clients. Practice balls do not consume it.
- Online practice keeps one owned ball per player. Either trigger recalls it to
  that hand, including transfer while held; release/throw remains native.
  The team selector can close/reopen using the menu/Change Team controls.
  Pre-match movement/jump uses the match speed and original jump coroutines.
  The existing aligned solid scene net is retained without duplicate colliders.
- Beach becomes an urban seaside with a promenade and 17 landward buildings.
  The skyline uses 1,572 triangles and one opaque draw. Palms use a static
  shader; sand and palms retain the previously authored replacement geometry.
- Indoor flags moved away from beams, black beams, filled double-sided upper
  gable/roof visual, square white scoreboard boards with black borders.
  The original collision roof is byte-identical and separate from the new visual.
- Plain black unbranded posts, plain white net tapes and an original yellow/blue
  panel ball texture without text or logos.
- Curly, Nerd, Grandpa and Side Quiff regain their earlier authored facial style.
  Nerd wears scout clothing; Side Quiff wears a black tee/beige trousers; Grandma
  has almost-black dark wine hair. BOT1's restored middle-part remains exact.
- Black outlines on the menu title, tagline, scoreboards and point/reason popup.
  All authored visible game text uses English, including runtime point reasons.

## Verification

- Compiled x64 native hooks tested at two relocated addresses, solo and online
  2v2/4v4: serve rules, formation, movement, assist, original bot attack/jump flow,
  point/set logic, menu input, appearances, team changes, pause and finite motion.
- Final asset audit: exact authorized object unions across eight files; 144
  unchanged colliders and 19 unchanged collider-referenced meshes. All nine bot
  meshes and BOT1 texture aliases preserved. No missing introduced references;
  opaque avatar mipmaps; 119 English serialized text fields.
- Native codec/menu: 9,720 appearance packet roundtrips, 486 initial choice
  combinations, mirrored hand anatomy and conditional gestures.
- Dedicated integrated tests cover contact persistence, cached whistle, actual
  native trigger/attachment, lobby ownership/recall/cleanup/jump, and own-team
  bot celebrations. Reports are saved under analysis/v21-*.json.
- Controlled startup of the real Unity menu/Indoor and Beach stayed active for
  15 seconds each without a new crash. No headset was connected; the existing
  HmdNotFound and terrain utility shader warnings remain baseline limitations.
- Complete installer passed 13 isolated install/reinstall/restore/upgrade/error
  cases, verified seven recovery backups, preserved the prior ZIP and rejected
  incompatible/corrupt/path-invalid/incomplete input without partial writes.

No physical Quest 3, FPS benchmark or real two-PC multiplayer playtest is
claimed. Those remain user playtests. Friends need the same v21 package and
compatible separately owned base game. Rooms: Cloudcourt-2v2-v21 and
Cloudcourt-4v4-v21. Steam launch remains the same.

## Delivery record

The package builder records ZIP path/hash in analysis/complete-package-v21-validation.json.
Installation and public commit are recorded in installation-status.json after
successful verification. Only sources, own art and validation summaries are
published to CaioOzaki/CaioBa; game binaries, extracted assets, backups and ZIPs
remain local. The continuation automation stays active as requested.
