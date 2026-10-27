# Cloudcourt VR v25 — analog trigger repair

Baseline: delivered v24-celebracao-graficos, commit 8a395739fe8b9627943f389232eb6b8daa6724df.
Recovery backup: versions/cloudcourt-v24-antes-v25 (17 game files, 276 source
files). Previous delivered ZIPs are preserved. sources/ remains read-only.
Only GameAssembly.dll changes in this release; the other 16 game files match v24.

## Cause and repair

v24's spawn filter accepted only IController.GetTrigger digital state. The
working menu also accepted GetTriggerAnalog pressure. On an analog-only input,
Hand.Update's original WantsToGrab returned false before it could ever request
FindClosestInteractable. Adding analog pressure solely to the spawn filter
would therefore still leave the ball inaccessible.

v25 adds per-hand digital/analog trigger state with .60 press / .35 release
hysteresis and controller identity/loss reset. The original WantsToGrab entry
has a verified six-byte detour, preserving its original method via a trampoline.
For local hands it adds trigger pressure to the native result; original ordinary
grip holding and native interaction/throw methods remain. Spawn/recall gates
separately require trigger input, so GRAB alone and A cannot create balls.
Network peers never sample or mutate the local analog latch. UI button intent
suppresses acquisition in both serve and lobby, without forcing held-ball release.

The sampler preserves original one-time method metadata initialization before
reading TypeInfo globals, including a first lobby polling frame. Original
initializer addresses were independently decoded from the original native
instructions. Missing controllers return safely; a replacement cannot inherit
an old pressed latch. Nonfinite pressure releases the analog state while an
explicit digital press remains supported.

## Evidence

The actual delivered v24 DLL (c718b7d6154d4786238a34d17aadacf7077861bc4104fc166c25015593990622)
reproduces the analog-only block under the same independent controller fixture.
The corrected final DLL passes 18 integrated cases at two relocated image bases:
both hands, solo/online 2v2/4v4 serve, original Hand.Update/WantsToGrab/
WantsToRelease, analog-only acquisition/hold/release, digital-only input, GRAB/A
exclusion, UI exclusion, single owned lobby recall/fresh transfer, controller
replacement, nonfinite release and remote-hand isolation. The native predicate
and interface invoker execute from the DLL; neither is replaced by a boolean
stub. Analog float results are independent from digital input and integer RAX.

An independent compiled-helper suite covers hysteresis boundaries, repeated
reads, cold/warm metadata setup, independent hands, disconnects, missing
interfaces/controllers and unsupported-session fallback. A controlled final
15-second no-headset Unity startup loaded Indoor without a native exception.
Reports: analysis/v25-pressure-tests.json, v25-trigger-integrated-tests.json
and v25-integration-audit.json. No physical Quest 3 or real two-PC test is claimed.
The hardware-specific input diagnosis remains subject to user confirmation.

No artwork, graphics presets, bot logic, physics or packet format changes.
Existing v24 room namespaces remain Cloudcourt-2v2-v24 / Cloudcourt-4v4-v24.
Friends should install the repair for working trigger input; each still needs
a compatible separately owned base game.

The new ZIP, installer recovery checks, local backup and public source commit
are recorded in installation-status.json and analysis/v25-release-summary.json.
Never stop a user's match to install. Publish only scoped sources/validation;
no original game files, binary deltas or ZIPs on GitHub. Keep the continuation
automation active. After delivery, only physical confirmation remains.
