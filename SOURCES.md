# Sources — Validator and Amendment Observability

Primary sources only. Every measured figure cites the fixture and method
that produced it; every spec claim cites the pinned-tree file:line.

## Pinned tree (primary source for all code claims)

- postfiatd tree at commit `0085a1ff885d6a446369cf73a4430f75af22be55`
  (worktree `/home/hatch/workspace/postfiatd-amendment/worktree-0085a1ff`).
  Verbatim excerpts are vendored in
  `fixtures/pinned_tree_audit.json` (`snippets`); grep outputs in the same
  file (`checks`).
- Upstream comparison: rippled 2.5.0
  (`~/workspace/postfiatd-amendment/rippled-2.5.0`). The 67% quorum and
  67/100 amendment threshold are postfiatd deviations; upstream uses 80%
  for both (ValidatorList.cpp comment, SystemParameters.h upstream value).
  Verified by diff during the governance-audit pack; re-stated here from
  the pinned tree's own comments, not re-diffed in this pack.

## Live public endpoints (primary source for all measured figures)

- `https://rpc.testnet.postfiat.org/` — public, unauthenticated, read-only
  JSON-RPC. No credentials, no session, no mutation. Used for:
  `server_info`, `ledger` (validated, transactions expanded),
  `ledger_closed`, `feature`, `fee`, `account_info` (error path only).
- Measurement window: 2026-11-14 19:14:59–19:21:41 UTC; ledgers
  8049400–8049599 (198 fetched, 2 failed after 4 attempts each).
  Raw compact extract vendored in `fixtures/ledgers_sample.json.gz`;
  probe snapshots in `fixtures/rpc_probes.json`.
- Fetch command (re-runnable): `python3 scripts/fetch_ledgers.py
  --count 200 --out fixtures/ledgers_sample.json.gz`

## Prior work (context, not evidence)

- PostFiat network-architecture and agent-integration reference pack
  (published 2026-11-13) — the source of the rounded "10 drops/ledger"
  fee-burn headline this pack corrects, and of the baseline figures quoted
  for comparison (ledger close ~3.036 s, quorum 17/25, 24 proposers).
  This pack re-measures every figure it reports; nothing is copied from
  the prior pack as evidence.
- Governance-audit framework pack (2026-11-14) pinned the same
  constants (67/100 threshold, 67% quorum, 10-drop reference fee); all were
  re-checked against the pinned tree in this pack
  (`scripts/verify_constants.py`, 20/20 OK).
