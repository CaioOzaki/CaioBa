# Cloudcourt VR v22 — corrective release

Base: delivered Cloudcourt-v21-orla-gestos, commitde12441563c33767af79834700f5dd7ec3cbc3d9.
Verified recovery backup: versions/cloudcourt-v21-antes-v22 (17 gamefiles and208
sourcefiles). v21ZIP preserved; sources/ never edited.

## Corrections

- CUSTOMIZE Done: the v21 button was below the unchanged800x400 canvas raycast
  bounds. The modal and controls now fit within that actual interactive region.
  Real CurvedUI.GetObjectsHitByRay + Unity Button.OnPointerClick reproduced the
  old0-hit failure and verified closing, reopening and closing the fixed panel.
  No page re-entry, scene restart or close-button input workaround is used.
- Black tagline outline reduced to.75px, title1.25px; score outlines retained.
- New anatomical thumbs-up has four curled fingers and a proportionate thumb
  on the real thumb axis (+Y), not the old finger axis (+Z). Separate cupped,
  spread/flexed setting hands follow the user's volleyball-setting reference.
  Both GRABs on the eligible second team touch show the set pose; otherwise
  one/both GRABs show the respective thumbs. Original tracking/ball physics and
  approved aim-assist trajectory retained; hand colors/cache remain perplayer.
- Winning bots raise their existing skinned right arm toward a human teammate.
  A matching-skin thumb is connected to that moved wrist. A post-IK visual
  override restores before the next solver pass. The gesture remains through
  NewRally/serve delay and is restored at the actual serve whistle event.
  Losing bots/teams without human teammates do not perform this gesture.
- Curly, Nerd, Grandpa and SideQuiff recover exact pre-v20 authored hair meshes
  and historical facial artwork/palette. The v21 head pixels already matched
  history, but the new scalp silhouette still changed their appearance. The
  restoration therefore recovers the actual prior look, rather than redrawing
  the same face again. Common6194 body/head vertices, bones and rig preserved.
  Nerd's scout outfit and SideQuiff's black tee/beige trousers remain; BOT1 and
  the other requested bot identities are preserved.
- Gray indoor beams; silver post hardware with dark gray padding, no branding.
  Wall boards are fitted rectangles around actual score/title/set glyph bounds,
  replacing oversized square backings. Existing score UI remains functional.
- Beach skyline grows55% in height and30% in width, same1572triangles/one draw.
  An opaque dry sand surface isolates the flat gameplay region from the old
  terrain/probe/gloss contribution:2triangles/one draw,4mm above unchanged
  physics terrain. Existing court line tops clear it. Real Sun/bot/ball/palm
  shadow settings are retained; no global shadow/lighting disable.
- Landing markers use one short downward ground raycast at the point event,
  preserving exact X/Z and in/out status. A2mm visual clearance replaces the
  old14mm hover (Beach6mm over original physical ground to clear its4mm visual
  sand layer). The ring remains until the next actual serve spawn.

## Validation / release status

Isolated UI, hand/native pose, exact historical restoration and combined asset
checks are saved in analysis/v22-*.json. The combined asset audit preserves144
colliders,76collider-referenced meshes, all physics/terrain/tracking/animation
components and original rig transforms. All introduced references resolve.

The actual controlled Unity UI pointer test is distinct from a direct callback
unit test. Mesh previews decode authored serialized geometry and are not Quest
screenshots. No physical Quest3, live two-PC multiplayer or FPS benchmark is
claimed. Final native regressions, installer roundtrips, package and installation
records are kept in installation-status.json and analysis/v22-release-summary.json.

Online rooms: Cloudcourt-2v2-v22 and Cloudcourt-4v4-v22. Each friend needs the
same newZIP and compatible separately owned base game; launch through Steam.
Only sources, original art and validation summaries are pushed to CaioOzaki/CaioBa.
No game binaries, extracted assets, ZIPs or backups are published there.

Automation remains active as requested. Once installation/push are recorded,
only the external headset/FPS/two-PC playtest remains; no speculative changes.
