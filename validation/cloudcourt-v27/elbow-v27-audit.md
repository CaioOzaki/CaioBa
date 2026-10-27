# Player elbow correction v27

The affected arm is **anatomical left**, on the viewer's right when facing the avatar. The serialized `NetworkPlayer/PhysicalBody` component is resources.assets object 1283 (GameObject 441). Its left shoulder offset is (-.16,-.14,-.04), right is (+.16,-.14,-.04); both arm lengths are .6 m. Left upper/lower collider transform references are 807/802; right are 801/790. These fields were read from the immutable delivered v26 resources, not modified.

The player uses the game's procedural PhysicalBody two-bone IK, not the bot FinalIK skeleton. `UpdateArm` 0xeeea90 calls `GetBendNormal` 0xeeabe0 at 0xeeec75, computes `Cross(direction, normal)` at 0xeeeca8, then calls `GetDirectionToBendPoint` 0xeeb160 at 0xeeed12. GetBendNormal combines the hand target's world rotation, a handed ±90-degree correction derived from shoulderOffset.x, and the chest rotation. Neither PhysicalArm nor PhysicalBody serializes a bend normal or pole target. The serialized offsets and native handed sign are symmetric; the reproduced failure is an **unconstrained wrist-driven bend plane**, not a wrong serialized left/right sign.

`elbow_v27.c` wraps only GetBendNormal using its explicit Windows x64 structure-return ABI. After the original returns, it checks `body.leftArm == arm`. It projects torso-local -X onto the plane perpendicular to the shoulder-to-wrist direction. Only a negative (inward) component of the native bend vector is reflected outward in that plane. It preserves the bend-vector magnitude and original arm reach. An already outward result, the entire right-arm result, invalid/degenerate inputs and an outward axis parallel to the arm return unchanged. There are no new Unity calls, searches, caches, managed allocations or network fields.

The original UpdateArm still places and rotates the existing arm segments, collar/shoulder/elbow indicators and hand. Original capsule dimensions, masses, physics rules and tracked hand pose are unaffected. The solved segment transforms and their colliders move together; there is no detached cosmetic replacement. The method has no ownership or game-mode gate, so local tracking and remote Photon pose playback use the same correction.

## Numerical production readback

All coordinates below are metres in the chest-facing test frame. Shoulder=(-.16,1.46,-.04); tracked wrist=(-.22,1.05,.16). For a left wrist yaw of -90 degrees the delivered native elbow is (-.0429045,1.1838021,-.0418271), inside the torso's lateral envelope. The corrected native elbow is (-.3370955,1.2185792,-.0587915). Both shoulder-to-elbow and elbow-to-wrist lengths remain .3 m; wrist position and quaternion are byte-identical.

For the same target and neutral wrist, the native left elbow is already outward at (-.2362530,1.1785650,-.1105677) and is byte-identical after the hook. The opposite neutral right arm with mirrored target has elbow=(+.2362530,1.1785650,-.1105677); the hook leaves it identical. The bad left and good right differ in wrist orientation, as can occur with independently tracked controllers. No claim is made that the screenshot's exact tracking quaternion was recovered.

## Verification and limits

- `test_elbow_v27.py`: 144 production native pose cases, 60 torso-yaw covariance cases and 16 invalid/degenerate input guards. It runs the actual delivered GetBendNormal, GetDirectionToBendPoint and UpdateArm instructions plus the compiled production helper. All 72 right-arm cases and 60 already outward/straight left cases are unchanged; 12 left cases are corrected.
- `test_elbow_integrated_v27.py`: 112 cases against the full integrated working DLL and immutable v26, across two ASLR bases, both arms, standing/raised/crossbody/straight targets and seven wrist variants (three yaws, palms up, setting, thumbs up and high five). All 56 right-arm cases and 46 left cases are unchanged; 10 left cases are corrected. It verifies tracked wrist position and rotation, finite poses, outward left bend, .3-m segment lengths and segment collider midpoints.
- Engine APIs are deterministic math/transform fixtures; solver and helper instructions are production code. No live headset, Quest or two-PC online test was performed. This removes the inward elbow branch; it is not a general collision-avoidance solver for every physically impossible tracked pose.

Final source SHA256: e40910b9dcd84e44fb274e9ce5126c44df9b825a03c5a4dda709c57690362b1e

Integrated native SHA256: 2b7cd2d55d4e8f76e6a8c7bf02d18f1a55b1e3664bb8b457b1b123a95562346f

Evidence: elbow-v27-assets.json, elbow-v27-disassembly.txt, elbow-native-v26-readback.json, elbow-v27-results.json and elbow-v27-integrated-results.json in this analysis directory. No resources/scene assets changed for this correction.
