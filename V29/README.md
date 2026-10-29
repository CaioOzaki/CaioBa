# Cloudcourt V29 — Refinement

V29 adds guided serve/receive/set/spike practice, cooperative bot coverage and
calls, distinct contact feedback, match summaries, small reactions and original
skill-unlocked outfits, expressions and cuff accents. It retains the V28 match,
customization and music behavior. [Release notes](CHECKPOINT-V29.md).

This folder is source for the separately owned compatible Volleyball Fever
Steam build 9216628. It contains original/verified licensed artwork, fonts and
sound inputs. No executable, extracted game mesh/texture, binary difference,
release ZIP, private report or machine-specific metadata is published here.
Physical Quest 3 and real two-PC gameplay confirmation remain pending.

## Relative layout and dependencies

Keep this folder intact. Older suffixes on shared C/Python helpers describe
where they originated; they are dependencies of this release. V28 and V27
remain separate matching snapshots in their own folders.

Python dependencies: UnityPy, Pillow, NumPy, fonttools, pefile, capstone and
fmod_toolkit (including its FMOD runtime for optional legacy audio generation).
Native fixtures/builds use Zig 0.14.1 for Windows x64 at
`tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe`; tool binaries and external
Python packages are supplied locally and are not vendored.

Font inputs and notices live in `assets/shared/fonts`; retained CC0 effect
inputs/credits live in `assets/shared/audio`. Original older face inputs used
by the atlas authoring helper live in `assets/shared/legacy-art`. New V29
artwork and licenses live in `assets/rewards-v29` and `assets/refinement-v29`.
The three V28 lofi tracks are reproducible original oscillator/noise synthesis
in `build_settings_audio_v28.py`; large generated WAVs are local outputs.

## Rebuilding and validation

Supply your own verified V28 game snapshot under
`versions/cloudcourt-v28-antes-v29/`, the compatible unmodified native DLL
under `backup/GameAssembly.dll`, and the complete compatible local game files
under `working/` as expected by the retained build/package scripts. These
inputs are excluded from source publication. Historical helper entry points
may require older separately owned local snapshots; the V29 composition uses
their imported authoring functions against V28.

Create `analysis/` and `tools/`. Build the release native helper without
`MODE_PROBE` using Zig's Windows x64 target, `-shared -O2 -ffreestanding
-fno-stack-protector -nostdlib -DPATCH_DELTA=0x194f000`, entry `DllMain`, source
`spin_mod.c`, output `tools/spin-native.dll`. Run `build_patch.py` to validate
original instruction bytes and merge the helper into the local working DLL.
Run `build_assets_v29.py --source versions/cloudcourt-v28-antes-v29 --output
visuals-v29` for the candidate asset composition; the working asset set must
be updated and verified by the maintainer before packaging.

Run the focused `test_*_v29.py` native/asset fixtures and the retained integrated
rules checks using your local tools and game inputs. `probe_release_v29.py`
uses a disposable desktop Unity copy for menu/runtime checks; it is not a
headset or two-PC test. `verify_cloudcourt_v29.py` requires local evidence and
verified final file hashes. `package_cloudcourt_v29.py` only accepts that
verified state; recovery/upgrade checks use local compatible V28 manifests and
preserved previous delivery files. Reports, installer fixtures and generated
binary differences stay local. Published package source uses flat original
ball/flag artwork for its older preview slots; no game-mesh preview is required.

## Installation and credits

The source folder is not an installer. Use the separately delivered V29 ZIP:
close the game, extract the whole ZIP and run `Instalar.cmd`. Keep its recovery
backup. Every online peer needs V29; standard/Bomb and 2v2/4v4 rooms remain
separate. Restore using the package's `Restaurar.cmd` when needed.

Retain [Baloo 2 OFL](assets/shared/fonts/Baloo2-OFL.txt),
[font origin](assets/shared/fonts/ORIGEM.md),
[base audio credits](assets/shared/audio/CREDITS.md),
[lofi license](assets/cloudcourt-v28/LOFI-LICENSE.txt),
[reward art license](assets/rewards-v29/LICENSE.txt) and
[V29 composition license](assets/refinement-v29/LICENSE.txt).
