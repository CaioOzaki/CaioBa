# Cloudcourt VR — v18

Current checkpoint: **Cloudcourt-v18-praia-lobby**. [Changes and validation](CHECKPOINT-V18.md).

- All 22 AudioClips replaced: Kenney CC0 impacts/menu click and original synthesized music, chimes and beach ambience. [Credits and licenses](assets/audio-v18/CREDITS.md).
- Original curved fan palms (261 vertices / 512 triangles, previously 831), shared material and 512px mipmapped atlas. New sand texture, normals, crescent shore and dunes; flat court/runoff and collider components preserved.
- Assisted second-touch set follows the intended teammate's lateral position at the near-net attack strip, in solo and online 2v2/4v4. Both GRAB buttons remain required.
- Online pre-match room permits walking across both sides and trigger-to-hand practice balls. Photon owns each ball per spawning client. Up to four live balls per client are recycled; practice objects are disabled/destroyed before match transition. Practice contacts do not update rally touch tracking.

Room namespaces: **Cloudcourt-2v2-v18 / Cloudcourt-4v4-v18**. All friends must use v18, the same format and region. Existing v17 fixes are preserved. Original networking has no mid-match late join.

Build order on an existing compatible local v17 working copy: compile `spin_mod.c`, run `build_patch.py`, then `build_audio_v18.py` and `build_beach_v18.py`. The latter scripts edit current assets in place and preserve unrelated data. Do not run the old v16 visual assembly over a v18 copy. `package_cloudcourt_v18.py` builds and tests a 17-file reversible installer for compatible original Steam build 9216628 or v17. Previous ZIPs remain local.

Run `run_validation_v18.py` for native regression and asset checks. Compiled x64 tests use deterministic Unity/Photon stubs; FSB banks are decoded through FMOD and compared sample-for-sample. These checks do not establish real Quest 3 visuals/input or real two-PC behavior, which still require playtesting.

Own compatible base game required. This repository contains mod sources, original procedural artwork and selected third-party CC0 source effects with their licenses. It does not contain game DLLs, extracted original meshes/textures/audio, backups or installer ZIPs. A clean clone alone is not a complete game build; local `working`, `backup`, `versions` and tool dependencies are needed. Procedural sound/music WAVs and art previews can be regenerated from the supplied sources. The current branch continues to exclude abandoned experimental files.

Visual identity: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24
Earlier release: [v17 review](CHECKPOINT-V17-REVISAO.md).
