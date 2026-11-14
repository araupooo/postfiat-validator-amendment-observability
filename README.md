# Validator and Amendment Observability Evidence Pack

Public, inspectable observability evidence for the pinned postfiatd tree
(`0085a1ff885d6a446369cf73a4430f75af22be55`): validator onboarding paths,
amendment-vote observability, measured per-ledger fee burn, and
agent-integration conformance of the public read-only RPC surface.

Results page: `docs/index.html`.

## Headline numbers (measured, 2026-11-14)

| Metric | Value |
| --- | --- |
| Measured mean fee burn | **3.90 drops/ledger** (median 0, min 0, max 50) over 198 validated ledgers |
| Prior rounded headline corrected | 10 drops/ledger was the per-transaction base fee, not a per-ledger measurement (2.56x too high) |
| Empty ledgers | 164/198 (82.8%) |
| Ledger close interval | mean 3.046 s |
| Validation quorum / implied UNL | **17 / 25** (68%); proposers 24 in every sample |
| Amendments inventoried | 101 (64 enabled, 101 supported, 0 vetoed, 0 in majority) |
| Harness checks | 30 total — 30 passed, 0 failed |
| Constants verification | 20/20 OK |
| Digest manifest | all files OK, 0 failed |

## Layout

| Path | Contents |
| --- | --- |
| `docs/index.html` | Rendered results page (headline figures, failure-mode matrix, findings, checks) |
| `README.md` | This file |
| `SCOPE_MAP.md` | Pinned-tree claims mapped to file:line sources and checks |
| `FINDINGS.md` | Prioritized findings with mitigations and honest limitations |
| `claim_evidence_index.md` | Every material claim mapped to a runnable check or primary-source citation |
| `SOURCES.md` | Primary sources and fixture provenance |
| `REPRODUCTION.md` | Fresh-copy reproduction instructions |
| `scripts/run_checks.py` | The measurement/conformance harness (30 checks) |
| `scripts/fetch_ledgers.py` | The live fetch script (used once to build the fixture; not run by `run_all.sh`) |
| `scripts/verify_constants.py` | Constants verification against the pinned tree |
| `scripts/build_derived.py` | Rebuilds `docs/index.html` from the final run log |
| `fixtures/` | Pinned-tree constants + audit record, ledger sample, RPC probes |
| `results/` | Unedited run log, summaries, per-check outputs, digests |
| `results/outputs/` | Fresh clean-setup copies of the run log and per-check outputs |

## Reproduce

```sh
bash run_all.sh          # offline; exit 0, clean git status
bash verify_digests.sh --check
```

See `REPRODUCTION.md` for the exact expected output lines and for
re-fetching a current measurement window.

## Boundaries

- All ledger observation was read-only, from the public unauthenticated
  RPC `https://rpc.testnet.postfiat.org/`. No session, account, wallet,
  credential, or private surface was used.
- No live-network mutation; no changes to the pinned tree.
- No third-party chat-platform content anywhere in this pack.
