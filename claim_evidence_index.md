# Claim-to-evidence index — Validator and Amendment Observability

Every material claim maps to a runnable check (results/checks/Vnn.txt) or a
primary-source citation. "TESTED" claims were recomputed by the harness
from the vendored fixtures; source citations point at the pinned tree.

## Validator onboarding

| Claim | Evidence |
| --- | --- |
| Pinned commit is 0085a1ff885d6a446369cf73a4430f75af22be55 | V01; `fixtures/pinned_tree_audit.json` |
| Quorum = max(ceil(0.67 * effective UNL), ceil(0.6 * UNL)); quorum(25) = 17 | V02; `src/xrpld/app/misc/detail/ValidatorList.cpp:1845,1898-1935` |
| Live validation_quorum is 17 | V02, V07; `fixtures/ledgers_sample.json.gz` (`server_info_start`) |
| Validator lists come from `[validator_list_sites]`; accepted only with manifest + version + non-empty blobs | V03; `src/xrpld/core/ConfigSections.h:93`; `src/xrpld/app/misc/detail/ValidatorSite.cpp:372-402` |
| Validator keys + manifest come from `[validator_token]` config | V04; `src/xrpld/core/ConfigSections.h:95-96`; `src/xrpld/app/misc/ValidatorKeys.h:32-70` |
| `applyList` validates publisher keys, sequence, expiry | V05; `src/xrpld/app/misc/detail/ValidatorList.cpp:943-1244` |
| Negative-UNL water marks 128 / 204 / 230 validations per flag-ledger period | V06; `src/xrpld/app/misc/NegativeUNLVote.h:56,62,68` |
| Proposers = 24 in every sample; quorum 17 stable across the window | V07; `fixtures/ledgers_sample.json.gz` |
| Probed node: build 1.0.9, network 2025, state full; sample inside complete_ledgers | V08; `fixtures/ledgers_sample.json.gz` |

## Amendment votes

| Claim | Evidence |
| --- | --- |
| Pre-fix threshold 204/256; post-fix threshold 67/100 | V09; `include/xrpl/protocol/SystemParameters.h:83,85` |
| Majority must hold 2 weeks | V10; `include/xrpl/protocol/SystemParameters.h:88` |
| Flag ledgers every 256 ledgers; fee/amendment votes only then, gated on validations >= quorum | V11; `src/xrpld/app/ledger/Ledger.h:426`; `src/xrpld/app/consensus/RCLConsensus.cpp:354-390` |
| Validations carry amendment choices in `sfAmendments` | V12; `src/xrpld/app/misc/detail/AmendmentTable.cpp:187-189` |
| Amendment inventory: 101 total, 64 enabled, 101 supported, 0 vetoed, 0 in majority | V13; `fixtures/ledgers_sample.json.gz` (`feature_snapshot`) |
| Fee votes run at flag ledgers toward FeeSetup targets | V14; `src/xrpld/app/misc/FeeVoteImpl.cpp` |

## Fees and burn

| Claim | Evidence |
| --- | --- |
| Fees are destroyed (`dropsDestroyed_ += fee`) | V15; `src/libxrpl/ledger/ApplyStateTable.cpp:546-548` |
| Reference fee 10 drops; reserves 10 XRP + 2 XRP/item | V16; `src/xrpld/core/Config.h:69,72,75` |
| Mean burn 3.90 drops/ledger over 198 ledgers (median 0, min 0, max 50, stdev 10.13) | V17; `fixtures/ledgers_sample.json.gz` |
| total_coins cross-check: 195/197 pairs exact; 2 mismatches explained by unfetched ledgers (implied burns 30 and 20 drops) | V18; `fixtures/ledgers_sample.json.gz` |
| 76/77 transactions at 10 drops; one at 12 drops | V19; `fixtures/ledgers_sample.json.gz` |
| Close interval mean 3.046 s; tx mix Payment 66, NFTokenMint 6, NFTokenBurn 5 | V20; `fixtures/ledgers_sample.json.gz` |
| Prior "10 drops/ledger" headline was the per-tx base fee; correction factor 2.56x | V21; V17; prior pack README (context only) |
| Load fee normal 256, max 256,000,000 | V16; `src/xrpld/app/misc/LoadFeeTrack.h:141,147` |
| median_fee = toDrops(escalationMultiplier, baseFee); observed 5000 drops vs base 10 | V24; `src/xrpld/app/misc/detail/TxQ.cpp:1793,1899` |

## Agent integration

| Claim | Evidence |
| --- | --- |
| server_info returns all fields agents need | V22; `fixtures/ledgers_sample.json.gz` |
| ledger method returns per-transaction Fee for every transaction | V23; `fixtures/ledgers_sample.json.gz` |
| fee method returns base/median/minimum/open-ledger fees and levels | V24; `fixtures/ledgers_sample.json.gz` |
| ledger_closed returns the validated ledger | V25; `fixtures/rpc_probes.json` |
| Malformed account returns actMalformed, code 35 | V26; `fixtures/rpc_probes.json` |
| Every feature entry carries enabled/supported flags | V27; `fixtures/ledgers_sample.json.gz` |
| RPC handlers exist in the pinned tree (Feature1, Fee1, AccountInfo) | V28; `fixtures/pinned_tree_audit.json` |
| Ledger chain linkage intact apart from the 2 one-ledger gaps | V29; `fixtures/ledgers_sample.json.gz` |
| Sample coverage 198/200; 2 failures recorded with errors | V30; `fixtures/ledgers_sample.json.gz` |

## Findings

| Finding | Evidence |
| --- | --- |
| F-01 (Medium): rounded fee-burn headline corrected to measured 3.90 drops/ledger | V17, V21 |
| F-02 (Low): 164/198 ledgers empty; median burn 0 | V17, V20 |
| F-03 (Low): no amendment in majority; single snapshot cannot show trends | V13 |
| F-04 (Low): participation observable only as aggregate proposers count (24) | V07 |
| F-05 (Low): median_fee 5000 drops = 500x base fee, reason not established | V24 |
| F-06 (Informational): 2/200 fetches failed after 4 attempts; retry + record | V30 |
| F-07 (Informational): one 12-drop transaction, reason not established | V19 |
