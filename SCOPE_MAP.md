# Scope map — Validator and Amendment Observability

Pinned postfiatd tree: `0085a1ff885d6a446369cf73a4430f75af22be55`
(tree: `/home/hatch/workspace/postfiatd-amendment/worktree-0085a1ff`).
All file:line citations were read from that tree; the verbatim excerpts are
vendored in `fixtures/pinned_tree_audit.json` under `snippets`.

## Validator onboarding

| Claim | Source | Checks |
| --- | --- | --- |
| Validator lists come from configured `[validator_list_sites]` URLs; a list is accepted only with manifest + version + non-empty blobs | `src/xrpld/core/ConfigSections.h:93`; `src/xrpld/app/misc/detail/ValidatorSite.cpp:372-402` | V03 |
| Validator keys and manifest come from `[validator_token]` config; empty when not a validator | `src/xrpld/core/ConfigSections.h:95-96`; `src/xrpld/app/misc/ValidatorKeys.h:32-70` | V04 |
| Lists are applied by `ValidatorList::applyListsAndBroadcast` / `applyLists` / `applyList`, validating publisher keys, sequence, expiry | `src/xrpld/app/misc/detail/ValidatorList.cpp:943-1244` | V05 |
| Quorum = max(ceil(0.67 * effective UNL), ceil(0.6 * UNL)); 67% for devnet/testnet, upstream 80% | `src/xrpld/app/misc/detail/ValidatorList.cpp:1845,1898-1935` | V02 |
| Negative-UNL water marks: 128 / 204 / 230 validations per flag-ledger period (50% / 80% / 90% of 256) | `src/xrpld/app/misc/NegativeUNLVote.h:56,62,68` | V06 |

## Amendment votes

| Claim | Source | Checks |
| --- | --- | --- |
| Pre-fix threshold 204/256; post-fix threshold 67/100 | `include/xrpl/protocol/SystemParameters.h:83,85` | V09 |
| Majority must hold 2 weeks | `include/xrpl/protocol/SystemParameters.h:88` | V10 |
| Flag ledgers every 256 ledgers; fee/amendment votes only then, gated on validations >= quorum | `src/xrpld/app/ledger/Ledger.h:426`; `src/xrpld/app/ledger/Ledger.cpp:981-984`; `src/xrpld/app/consensus/RCLConsensus.cpp:354-390` | V11 |
| Validations carry amendment choices in `sfAmendments` | `src/xrpld/app/misc/detail/AmendmentTable.cpp:187-189`; `src/xrpld/app/consensus/RCLConsensus.cpp:914` | V12 |
| Fee votes run at flag ledgers toward FeeSetup targets | `src/xrpld/app/misc/FeeVoteImpl.cpp` (`doVoting`) | V14 |

## Fees and burn

| Claim | Source | Checks |
| --- | --- | --- |
| Fees are destroyed (`dropsDestroyed_ += fee`); no account is credited | `src/libxrpl/ledger/ApplyStateTable.cpp:546-548` | V15 |
| Reference fee 10 drops; account reserve 10 XRP; owner reserve 2 XRP | `src/xrpld/core/Config.h:69,72,75` | V16 |
| Load fee: normal 256, max 256,000,000 | `src/xrpld/app/misc/LoadFeeTrack.h:141,147` | V16 |
| `median_fee` = `toDrops(escalationMultiplier, baseFee)` | `src/xrpld/app/misc/detail/TxQ.cpp:1793,1899` | V24 |

## Agent-integration surface (RPC handlers in the pinned tree)

| Method | Handler | Checks |
| --- | --- | --- |
| `server_info` | standard RPC surface (verified live) | V22 |
| `ledger` | standard RPC surface (verified live) | V23 |
| `feature` | `src/xrpld/rpc/handlers/Feature1.cpp` | V27, V28 |
| `fee` | `src/xrpld/rpc/handlers/Fee1.cpp` | V24, V28 |
| `account_info` | `src/xrpld/rpc/handlers/AccountInfo.cpp` | V26, V28 |
| `ledger_closed` | standard RPC surface (verified live) | V25 |

## Out of scope (stated, not measured)

- Per-validator participation (needs the validations WebSocket stream).
- Amendment-majority trends over time (needs repeated `feature` snapshots).
- WebSocket APIs (only JSON-RPC over HTTPS was probed).
- The cause of the 12-drop transaction and of the 500x median fee.
- Any live-network mutation; all observation was read-only.
