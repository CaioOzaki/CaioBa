# Cloudcourt VR v27 — outward player elbow

Baseline: delivered v26-session-repair, commit
455aed7b3ca99c9b830362ef1bb7d9c789030068. Recovery backup:
versions/cloudcourt-v26-antes-v27 (17 verified game files and 315 source files).
Previous ZIPs remain intact; sources/ is read-only.

The affected arm is on the viewer's right in a front-facing avatar view:
anatomical left, with native PhysicalBody.leftArm at offset0x40. Its serialized
shoulder offset already mirrors the right arm correctly. The native wrist-driven
bend-plane choice could instead put the elbow toward the torso at certain wrist
rotations; changing the mesh or swapping arm labels would not address that cause.

v27 detours PhysicalBody.GetBendNormal at0xeeabe0, preserving its original result
and analytic UpdateArm/GetDirectionToBendPoint solve. Only an inward anatomical
left bend is reflected toward the shoulder's outward axis in chest space.
Already-outward left results and all right-arm results remain native. There is
no persistent state, allocation, Unity object search or network packet change.
Hand targets/rotations, arm lengths and collider definitions are preserved;
the original solver aligns the arm's transforms/colliders with its new elbow.
Other avatar hand poses, bot gestures, menus and v26 gameplay features remain.

Concrete standing example from the original native solver, in meters:
shoulder(-.16,1.46,-.04), wrist(-.22,1.05,.16). With a-90degree wrist yaw,
the old elbow was(-.04290,1.18380,-.04183), inside the lateral torso envelope;
the corrected elbow is(-.33710,1.21858,-.05879). Wrist position is unchanged,
and each arm segment remains0.30m. A neutral already-outward left elbow and the
opposite arm remain unchanged.

Validation uses actual delivered/final native UpdateArm, GetBendNormal and
GetDirectionToBendPoint instructions with deterministic Unity math/transform
fixtures at two image bases. It covers standing, raised, cross-body and straight
targets, controller rotations, torso orientation, unchanged tracked wrists,
segment lengths, collider midpoints and degenerate input guards. Isolated helper
checks and final integrated DLL checks are reported separately. Startup and
installer/recovery/package checks are recorded by the release audit.

The indoor ball retains its yellow/blue panels with all lettering and badges
removed. Beach follows the supplied broad perpendicular white/blue/yellow
panel reference with orange/red fades and dot accents, without writing or logos.
The own procedural artwork changes only pixel data of resources texture40;
dimensions, twelve mip levels, GPU bytes, mesh/UV, material bindings, physics
and colliders are identical. Reference photos are not redistributed.

Two of the17 game files change: GameAssembly.dll and resources.assets (texture40
pixels only). The other15 files match v26. Existing room namespaces/RPC layout are retained; both friends
should install v27 to see the same arm behavior. Physical Quest3 and real two-PC
confirmation remain pending; CPU emulation/startup are not headset playtests.

Exact package hashes, checks, installation backup and public commit are in
installation-status.json and analysis/v27-release-summary.json. Publish scoped
source/reports only, never base-game files, binary deltas or release ZIPs to
GitHub. Keep the continuation automation active after delivery.
