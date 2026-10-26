# Cloudcourt bot roster v20

v20.1: BOT1's earlier middle-part hair geometry is restored at the user's
request. Its face, clothing and opaque BC1 texture remain unchanged. The other
eight characters retain their v20 hair improvements. The native roster and
online protocol still use v20.

Nine own procedural cartoon characters. The first seven faces preserve the
existing Cloudcourt drawings; continuous hair caps and curved hair strands
replace their previous geometry. BOT8 is the requested long black hair/curtain
bangs/blonde streak/septum character, in a black shirt and trousers. BOT9 is
the tall, slim young man with square black glasses, swept-back middle part,
black shirt and dark blue jeans. His visible model is 10% taller; gameplay
colliders, rig transforms, IK and animations are preserved.

`build_bots_v20.py` authors all meshes and artwork without copying original
game mesh vertices or texture samples. `bots-gallery.png` and the individual
front/back PNGs render those own meshes against the drawn atlases; they are
previews, not VR screenshots. `catalog.json` lists the nine styles.

The 48 inherited database variants bind to nine own meshes and textures.
Canonical database indices are 39,12,30,21,15,18,0,45,6. The host selects
without replacement through `bots_v20.c`; the existing assignment RPC carries
the selected index, so clients do not reroll. Roster reset happens on match
setup/clear, not on rally/rotation or a human team swap.

Textures use opaque BC1/DXT1 with nine mipmaps. Every pixel alpha in all 432
serialized mipmaps was checked. Texture data falls from 150,994,944 bytes to
33,554,304 bytes. Rig bindings retain compatibility with the separately
installed base game. This folder contains only our artwork and numeric
binding/catalog data; the game itself and its original assets are not included.
