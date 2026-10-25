# Native gameplay audit

## Confirmed and corrected

1. **An appearance packet could corrupt team membership after changing teams.** The previous `client_choose_hook` wrote the packet's team value into `NetworkPlayer.team` for every skin refresh. Those refreshes run every three seconds. A delayed refresh from before a completed swap could set that field back while the human remained in the new team's member/player lists. The revised receiver applies lobby assignments only before a player has match membership; in a match, only an explicit team-change request can alter membership and team together.

2. **Periodic appearance updates and team changes accumulated in Photon's room cache.** The original `NetworkPlayer.InvokeRpc_ChooseTeam` calls `PhotonView.RPC` with target 6, `AllBufferedViaServer`. The periodic refresh therefore created about 1,200 cached events per player per hour. The mod now invokes the same `Client_ChooseTeam(int)` RPC with target 5, `AllViaServer`, keeping reliable server ordering without buffering historical appearance or swap events. Original lobby selection still uses its original buffered route.

The packet layout is unchanged. An updated sender and receiver are needed to obtain both fixes. The release room namespace is managed separately by the parent task.

## Reproduction and validation

`test_identity_rpc_v16.py` executes the compiled hooks with actual field/list layouts and engine stubs, under two relocated memory bases. It checks stale appearance packets, a delayed packet after a queued swap, RPC target/payload, lobby selection before membership, and refusal when the destination has no bot slot. The old compiled release failed the stale-packet and RPC cases; `v16-identity-rpc-before.json` preserves that result. The current test report is `v16-identity-rpc-tests.json`.

## Other audited paths

The wall scoreboard and popup calls use the correct `UnityEngine.UI.Text.set_text` and `TMPro.TMP_Text.set_text` signatures. The high-five path uses `PhysicalArm.hand` at offset 0x28, correct Transform and AudioSource/AudioClip APIs, and unscaled delta time. No additional confirmed bug was found in these paths. Deterministic engine stubs do not establish real Quest 3 input behavior or two-PC Photon behavior.

## Original build evidence

- `NetworkPlayer.InvokeRpc_ChooseTeam`: RVA 0x31B1B0; target 6 at RVA 0x31B24F.
- `PhotonView.RPC`: RVA 0xE6BB50; `(view, methodName, target, object[] parameters, MethodInfo*)`.
- `RpcTarget` enum in `dump.cs`: `AllViaServer = 5`, `AllBufferedViaServer = 6`.
- Original metadata-init token: RVA 0x1294F48; Object[] class reference: 0x15260B8; Int32 class reference: 0x15269D0.

## Late join / rejoin review

The original `InRoomPageController.TransitionIntoGame` host branch closes and hides the room before creating the match: `Room.set_IsOpen(false)` at RVA 0x315593, then `Room.set_IsVisible(false)` at 0x3155BA. Only after those operations does it instantiate the match objects and call `GameRules.Go`. Room creation sets the maximum player count but does not configure an inactive-player rejoin mechanism. If a player leaves a match, `InGamePageController.HandlePlayerLeftRoom` calls `NetworkManager.Disconnect` at 0x3143B5, ending that session on the remaining clients.

Consequently, the supported match flow has no mid-match join/rejoin path that requires historical team changes. No additional snapshot mechanism is needed for this correction. Future support for joining active matches would require an authoritative roster/score snapshot; old swap events must not serve as that snapshot. Evidence is recorded in `v17-latejoin-flow.txt`.
