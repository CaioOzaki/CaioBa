# Cloudcourt avatar art v19

Nine independently selectable faces and nine outfits, allowing 81 combinations.
The first four faces preserve the existing original Cloudcourt emoji PNGs.
The five additional expressions and every garment are drawn from geometric
marks by `build_customization_art_v19.py`; they use no base-game texture sample.
The preview labels use the project's existing OFL-licensed Cloudcourt Bubble font.

`faces-atlas.png` and `outfits-atlas.png` are separate 1536 by 1536 images, each
with nine 512 by 512 cells. Runtime textures use BC7 with nine mip levels,
requiring 6,291,488 encoded bytes in total. Existing avatar meshes, renderers,
positions, normals, triangle indices, bounds and colliders are preserved.

The face material uses a complete cell; the outfit material uses the inherited
UV layout, whose clothing front is in the bottom-left quarter of each cell.
Mesh UVs are baked into a single cell. Runtime material scale stays `(1, 1)`
and each selection changes the offset to:

`(index % 3 / 3, (2 - index // 3) / 3)`

RawImage thumbnail UV rectangles:

- Face: `(column / 3, (2 - row) / 3, 1 / 3, 1 / 3)`.
- Outfit front: `(column / 3, (2 - row) / 3, 1 / 6, 1 / 6)`.

`catalog.json` lists stable selection IDs. `unity-bindings.json` records the
actual dynamically allocated Unity IDs. Default clothing is ID 2, Black Suit.
The head and body use distinct material objects and independent selection.

The builder exposes `create_art()` and `apply_customization_assets(resources)`.
It only modifies avatar mesh UVs, their two renderer material pointers, and four
new objects (two atlases plus two materials). Reapplying the upgrade reuses those
objects. Running the command-line builder requires a separate output path.

`test_customization_art_v19.py` validates the independent combinations, decoded
atlas sampling, preserved legacy drawings, compressed data, mip levels, mesh
invariants, unchanged unrelated objects and idempotence. These checks do not
replace real headset and multiplayer review.
