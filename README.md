# Cloudcourt VR — v19

Current checkpoint: **Cloudcourt-v19-customizacao**. [Changes and validation](CHECKPOINT-V19.md).

- Bots jump through the real inlined Update path, reaching a 2m apex and timing attacks for descending sets. The approved player set trajectory and target remain unchanged.
- Nine independent emoji faces and nine outfits, giving 81 combinations. Customize from the main menu or pause overlay; preferences persist and online peers receive each player's choice. [PNG previews and catalog](assets/customization-v19/README.md).
- Quest A and both digital/analog triggers feed the same menu submit state. Valid button clicks play a cached 2D sound. Clicking UI in the lobby does not request a practice ball.
- Beach sea/bird AudioSources disabled. Indoor and Beach are the available courts. The host chooses the online map before creating the room and all peers follow its Photon room property.
- Best of three sets with a two-point lead: Indoor25 / Beach21. Sets/points options and the night court are hidden.

Room namespaces: **Cloudcourt-2v2-v19 / Cloudcourt-4v4-v19**. All friends need v19, the same format and region. Earlier v18 beach, audio, lobby and gameplay fixes are preserved.

Build on a compatible local v18 working copy: compile `spin_mod.c`, run `build_patch.py`, then `build_cloudcourt_v19.py`. It applies only v19 UI/art/audio-source changes to existing assets. Do not run the old v16 assembly over this release. `package_cloudcourt_v19.py` builds and tests a reversible 17-file installer for the compatible original Steam build 9216628 or v18. Previous ZIPs remain local.

Validation: `run_validation_v19.py` covers 23 native suites, including original Bot.Update and scoring control flow. `audit_assets_v19.py`, `test_menu_v19.py`, `test_customization_art_v19.py` and `test_silence_beach_v19.py` cover the final serialized assets. Controlled menu/Indoor and Beach startup checks passed. Engine stubs, UV sampling and startup checks do not establish actual Quest 3 comfort/input or live two-PC behavior; those still need playtesting.

Own compatible base game required. This repository contains mod sources, own procedural artwork and previously included CC0 effects with their licenses. It does not contain game DLLs, extracted original meshes/textures/audio, backups or distribution ZIPs. A clean clone alone is not a complete game build; compatible local assets, backups and tool dependencies are required. The cleaned branch continues to exclude abandoned experimental files.

Visual identity: https://www.figma.com/design/1sIgjKcMItHmbLIu1dnch0?node-id=2-24

Earlier release: [v18](CHECKPOINT-V18.md). [Sound credits](assets/audio-v18/CREDITS.md).
