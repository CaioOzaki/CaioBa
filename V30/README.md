# Cloudcourt V30 - Polish fixes

V30 repairs black launch fades, first Solo Extras visibility and customization
mirror atlas/lifecycle behavior. Bot captions sit above heads with slightly
louder cues; accepted-contact vibration uses the original controller behavior.
The match menu includes Game/Sound settings. Three new original lofi tracks
replace the previous music. [Release notes](CHECKPOINT-V30.md).

This source requires a separately owned compatible Volleyball Fever Steam build
9216628. No game binaries/assets, binary patches, ZIPs, private reports or local
machine metadata are included. Native/desktop checks do not establish physical
Quest 3 or real two-PC multiplayer validation; these remain pending.

V30/, V29/ and V28/ are separate matching release sources. Older suffixes on
shared helpers inside this folder identify dependencies, not retained versions.
Keep this folder's relative layout. Python tools: UnityPy, Pillow, NumPy,
fonttools, pefile, capstone, Unicorn and fmod_toolkit when a legacy helper needs
it. Native builds use Zig 0.14.1 for Windows x64; external tools are not vendored.

Supply a verified V29 snapshot in versions/cloudcourt-v29-antes-v30/, compatible
original GameAssembly.dll in backup/, and compatible local game files in working/.
These inputs remain private. Run build_assets_v30.py to compose visuals-v30.
Build spin_mod.c with Zig -target x86_64-windows-msvc -shared -O2 -ffreestanding
-fno-stack-protector -nostdlib -DPATCH_DELTA=0x194f000 and entry DllMain, without
MODE_PROBE, to tools/spin-native.dll. Run build_patch.py to validate original
instructions and construct the working DLL. Native rules/ball, visual, haptic,
settings and music checks are maintained with source; run probe_launch_v30.py
--fixed --all for actual desktop Button.OnPointerClick launch/fade/settings checks
in a disposable game copy. Finalize and verify evidence before packaging with
package_cloudcourt_v30.py. Reports and generated binaries remain local.

Music is reproducible original oscillator/noise synthesis in build_music_v30.py.
Its WAV outputs are local; retain [CC0 notice](assets/audio-v30/CC0-NOTICE.txt).
Retained font notices are in assets/shared/fonts, base sound licenses in
assets/shared/audio and original legacy face art in assets/shared/legacy-art.
Retained reward/startup art and notices remain in assets/rewards-v29 and
assets/refinement-v29. No new bitmap or third-party song is introduced by V30.

Install with the separately delivered V30 ZIP, game closed. Extract the whole
ZIP and run Instalar.cmd. Keep ZIPs/backups. Every online peer needs V30; standard
and Bomb 2v2/4v4 use separate rooms. The source folder itself is not an installer.
