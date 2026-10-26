# V20 scene adjustments

`build_scene_v20.py` contains in-memory transforms only:

- `reorder_settings(level0)` arranges the existing controls into two columns,
  keeps the movement slider usable, places Back below the controls and retains
  the inactive Sets/Points widgets. Original controller references, button
  events, slider behavior and Cloudcourt font pointers are preserved.
- `relocate_banners(level3)` moves the existing banner bodies and gold hangers
  toward the interior of the gym. It modifies only Mesh 262 in the v19 base.
  Banner body centers become x=±11.25m; hanger centers become x=±11.13m.
  All UVs, normals, indices, materials and colliders remain unchanged.

The actual original banner components intersected the authored arena frame in
12 places. Bounds computed from the real mesh vertices and complete transform
chains are tested against 34 frame/roof boxes. The adjusted components have no
intersection and a minimum clearance above 0.27m. Exact IDs and before/after
bounds appear in `visuals-v20-scene/scene-report.json`.

Default command creates separate fixtures in `visuals-v20-scene`; it never
writes working/ or the Steam installation. The fixture preview is a layout
reference, not a headset screenshot. `test_scene_v20.py` checks the full object
and byte-field whitelist, unchanged font references/events/colliders and
idempotence. These helpers can be applied before the independent landing-marker
builder; they do not create new objects or depend on the final maximum ID.

## Runtime score outlines

The HUD/popup are TextMeshPro components in the GameRules prefabs; wall scores
are UI.Text. The existing runtime font replacement can discard an asset-only
TMP material outline, so use `score_outline_v20.c`:

1. Include it after `celebration_v15.c`, before `identity_v16.c`.
2. Call `score_outline_tmp_v20(text)` at the end of the existing `style_tmp`,
   after assigning the cartoon font and clearing `font_busy`.
3. Call `score_outline_text_v20(text)` at the end of `ui_text_enable_hook`,
   after assigning the cartoon font.

The helper scopes changes to ancestors named Scoreboard/CloudBoard0/CloudBoard1.
TMP gets opaque black outline color and width 0.18 through its own material APIs.
UI.Text receives UnityEngine.UI.Outline through AddComponent(Type), not a copied
MonoBehaviour schema. GetComponent(Type) prevents duplicates on repeated enable.
The outline distance is 2.5px and follows graphic alpha. Score graphics explicitly
ignore raycasts. Unrelated menu labels and the underlying cartoon fonts remain
untouched. `test_score_outline_v20.py` checks the compiled ABI, scope and repeated
enable behavior after the parent integrates/rebuilds the DLL.

No physical Quest 3 rendering or real two-PC session has been tested here.
