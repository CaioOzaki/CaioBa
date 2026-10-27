# v26 bot thumbs-up pose

Production change: `hand_visuals_v21.c`, bot celebration section only.

The decorative `Root_jnt` now faces the selected teammate during the gesture, so torso, legs and idle arm follow the head. This changes only skeletal bone rotations; the bot/model gameplay transforms, collider hierarchy and movement state are untouched. The right arm and thumb still point toward the same selected human. Recipient attribution, stable network rank, fallback rules and whistle lifetime remain unchanged.

The calibrated head starts from the verified neutral bind rotation and limits gaze relative to the turned body to 60 degrees sideways and 35 degrees up/down. The previous ball-look roll cannot survive into the gesture. Calibrated horizontal yaw is applied before vertical pitch so their combination does not introduce shortest-arc neck banking. Saved skeleton-root, head and three arm-bone local rotations plus hand scale are restored before each native IK pass and on hide/reset.

Whistle/menu resets now release cached bot/IK/look/skeleton references. Destroyed Unity bots/components/bones are checked before display operations, and an invalid binding can rebind the same bot with a replacement visual rig.

Validation:

- `test_bot_pose_v26.py`: 607 compiled production-C checks pass (129 recipient, 60 wire, 9 ace, 409 pose/lifecycle), including a recipient behind the bot, changed target position, rotated gameplay/model parents, both hostile IK passes, independent peer/format fixtures, reverse roster ordering, constrained head/up direction, original pose restoration, destroyed rig and replacement rig.
- `analysis/v26-bot-pose-asset-safety.json`: all 48 SimpleCitizens model skeleton hierarchies in the v25 backup contain Transform components only; all heads have identity bind rotation. No collider, Rigidbody or gameplay component is beneath Root_jnt.
- `test_bot_pose_integrated_v26.py`: PASSES on final DLL SHA256 `2c860f7a8f9a74fc1ce1cc09ece86653eebbdc54796edfc2f5ea72f1f8fbd65b`. Actual x64 hooks execute through Unicorn at two ASLR bases, two peers and both formats, including behind/moving recipients, extreme tracked-head pitch/yaw without neck banking, whistle restoration and a new rig on the same bot. The DLL remained unchanged throughout.

Native test command (Zig requires sandbox escalation on this machine):

```powershell
& 'C:/Users/Usuario/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' test_bot_pose_v26.py
```

Integrated test command:

```powershell
& 'C:/Users/Usuario/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' test_bot_pose_integrated_v26.py
```

No shipped game DLL, asset or publish output was modified by this subtask. Native hierarchical stubs and offline asset inspection do not establish live headset/two-PC visual results.

Ball material independent review and integrated validation:

- Identified and root agent corrected the atlas-offset ABI: RVA `0x9566d0` is `set_mainTextureOffset(Material*, Vector2, MethodInfo*)`; its Vector2 must pass by value in RDX, with no property-string argument.
- Identified and root agent corrected live-ball material release: restore cached original sharedMaterial to a live renderer before destroying its owned clone.
- `test_ball_style_integrated_v26.py` PASSES on the same final DLL, four independent ASLR/peer cases. Checks both atlas offsets and maps, eight-ball cache bound, stable warm frames, dead slot reuse, reset/root release, live ball rebind, externally destroyed instance recovery, late-ready retry and shared asset preservation. The DLL remained unchanged throughout.
- Ball report: `analysis/v26-ball-style-integrated-tests.json`.
