# Cloudcourt VR

Current checkpoint: **Cloudcourt-v28-extras-customization**. [Release notes](CHECKPOINT-V28.md).

Cloudcourt VR is a PC VR modification for the separately owned compatible
Volleyball Fever Steam build9216628. This source repository is not a standalone
playable game and does not redistribute the base game's executables or assets.

## v28

- Newly spawned Indoor/Beach volleyballs retain their artwork and serve transparency.
- Indoor blocks preserve three team hits; Beach blocks use one. The blocker may
  take the next contact. Near-net airborne interception is the supported VR proxy.
- Bomb uses its compact court bounds, corrected roster/serve and 2v2/4v4, offline
  and online, through Extras.
- Customization adds a camera-free same-avatar live preview, cap/fedora/cowboy/
  motorcycle helmet/beanie/crown/visor, and transparent or outfit-colored arms.
- Settings groups Game, Graphics and Sound. Master/Music/Game/Interface volumes
  are separate. Music toggles a three-track original CC0 lofi playlist.
- The original indoor flag emblem appears beside the startup game title.

Install v28 on every peer. The four room namespaces are Cloudcourt-2v2-v28,
Cloudcourt-4v4-v28,Cloudcourt-Bomb-2v2-v28 and Cloudcourt-Bomb-4v4-v28.
Graphics changes apply after restarting Cloudcourt, as stated in Settings.

## Delivery and validation

The local release ZIP contains an installer, backup/recovery support, credits
and binary differences for a compatible separately owned installation. It can
upgrade v27 or patch the compatible original. Previous release ZIPs are preserved.
The ZIP and base-game files are deliberately excluded from this GitHub repository.

Local validation checks cover
native rules, spawning, session reset, assets, real desktop Unity UI clicks,
streaming playlist playback and13 installer/recovery cases. These checks are not
physical Quest3 or real two-PC gameplay tests; those remain pending.

## Source and assets

Native hooks target this exact Windows x64 IL2CPP build. build_patch.py validates
original instruction bytes and emits the patched image with ASLR/unwind metadata.
build_assets_v28.py composes only the authorized changes from an immutable local
v27 snapshot; all referenced base-game input must be supplied locally.
Source generators and original assets are provided here; see
[original lofi licensing](assets/cloudcourt-v28/LOFI-LICENSE.txt),
[art notes](assets/cloudcourt-v28/README.md) and retained dependency credits.
The game's standard matches retain best-of-three Indoor25/Beach21 scoring.
