# Cloudcourt VR — v20

Current checkpoint: **Cloudcourt-v27-avatar-elbow**. [Repair notes](CHECKPOINT-V27.md). Corrects the inward player elbow on the viewer-right side of a front-facing avatar. Keeps tracked wrists, the original analytic solve, outward poses and opposite arm. Both balls have no lettering; Beach follows broad white/blue/yellow reference panels with red/orange accents. Other v26 features and wire format retained. Physical Quest and two-PC confirmation remain pending.

- Fixed invisible customization previews: v19 BC7 compression corrupted alpha, especially in mipmaps. BC3 makes every mip opaque at the same 6 MB texture budget. Actual Unity desktop camera captures confirmed the before/after change. Avatar material binding now retries delayed and replaced materials; a native regression reproduces the old failure.
- Nine own cartoon bots, including the requested curtain bangs/blonde streak/septum character and the tall, slim young man with square glasses and dark blue jeans. Continuous hair coverage and curved strands replace the old hair geometry. The host picks without repetition and sends the chosen existing database index through the original assignment RPC. [Bot gallery and own art](assets/bots-v20/README.md).
- Character texture data reduced from 151 MB RGB24 to 33.6 MB opaque BC1 with verified mipmaps. Rig, IK and gameplay colliders preserved.
- Black score outlines, reordered Settings, and gym banners moved clear of structural beams (12 previous bound intersections reduced to zero).
- Floor points leave a green/red ring at the actual collision contact. The existing reliable EndRally RPC carries the mark and contact position to all peers. It clears at the next rally and has no collider or scoring effect.

All friends need **v20**, the same region and format. Room namespaces: **Cloudcourt-2v2-v20 / Cloudcourt-4v4-v20**. Earlier approved physics, assisted sets, 2v2/4v4, lobby and appearance options remain.

Build on a compatible local v19 working copy: compile `spin_mod.c`, run `build_patch.py`, then `build_cloudcourt_v20.py`. These apply narrow upgrades in place. Do not reconstruct old v16 assets over the current version. `package_cloudcourt_v20.py` builds/tests a reversible 17-file installer for the compatible original Steam build 9216628 or v19. Earlier ZIPs remain local.

`run_validation_v20.py` covers 27 native suites. `audit_assets_v20.py` compares the final assets with the v19 backup, including whitelist, colliders, alpha and geometry checks. The Unity preview probe restores PlayerPrefs and runs only in its disposable copy. The final package also passed reversible installer checks and controlled menu/Indoor/Beach startup. These checks do not establish live avatar appearance in Quest 3 or real two-PC multiplayer; those playtests remain pending.

Own compatible base game required. This repository includes mod sources, own art and previously included CC0 audio with its licenses. Game DLLs, extracted original assets, backups and distribution ZIPs are not published. A clean clone requires compatible local assets, backups and tools before it can build. The cleaned branch still excludes abandoned experimental files.

Earlier release: [v19](CHECKPOINT-V19.md). [Audio credits](assets/audio-v18/CREDITS.md).
