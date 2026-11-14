# Findings — Validator and Amendment Observability

Pinned postfiatd tree: `0085a1ff885d6a446369cf73a4430f75af22be55`.
Measured window: 198 consecutive validated ledgers, seq 8049400–8049599
(2 requested ledgers failed to fetch; see V30), fetched 2026-11-14
19:14:59–19:21:41 UTC from the public read-only RPC
`https://rpc.testnet.postfiat.org/`.

Headline: **measured mean fee burn is 3.90 drops/ledger** (median 0,
min 0, max 50, stdev 10.13) over 198 ledgers — not the previously cited
rounded 10 drops/ledger, which was the per-transaction base fee.

## Findings

| ID | Severity | Status | Finding | Checks |
| --- | --- | --- | --- | --- |
| F-01 | Medium | CONFIRMED | Prior "10 drops/ledger" headline was the per-transaction base fee, not a per-ledger measurement; measured mean is 3.90 drops/ledger | V17, V21 |
| F-02 | Low | CONFIRMED | 164 of 198 ledgers (82.8%) are empty, so the mean burn is dominated by idle ledgers; the median burn is 0 | V17, V20 |
| F-03 | Low | CONFIRMED | No amendment is currently in majority and the feature snapshot is point-in-time; a single snapshot cannot show whether an amendment is trending toward majority | V13 |
| F-04 | Low | CONFIRMED | Validator participation is observable only as an aggregate proposers count (24); no per-validator participation is exposed by the public read-only API | V07 |
| F-05 | Low | CONFIRMED | median_fee (5000 drops) was observed at 500x the base fee (10 drops) with an empty queue; the reason the escalation multiplier sat at 500x was not established | V24 |
| F-06 | Informational | CONFIRMED | 2 of 200 requested ledgers failed to fetch after 4 attempts each (connection dropped mid-response); measurement scripts must retry and record failures | V30 |
| F-07 | Informational | CONFIRMED | One transaction paid 12 drops instead of the 10-drop reference fee; the reason was not established | V19 |

## Detail

### F-01 — Medium, CONFIRMED: the rounded fee-burn figure was wrong

The prior pack's headline "10 drops/ledger" was derived from a supply
observation (supply −60 drops in 31 s) and equals the per-transaction
reference fee, not a per-ledger burn. This pack measured the burn directly:
for each of 198 consecutive validated ledgers, burn = sum of the Fee field
of that ledger's transactions (fees are destroyed, not paid to anyone —
`ApplyStateTable::destroyXRP`, `src/libxrpl/ledger/ApplyStateTable.cpp:546`).
Total burn 772 drops over 198 ledgers = mean 3.90 drops/ledger; median 0;
max 50 (one 5-transaction ledger). The correction factor is 2.56x.

**Mitigation:** report fee burn per ledger from measured ledger data only;
never quote the base fee as a burn rate; always publish the sample size,
window, median, and empty-ledger fraction alongside the mean.

### F-02 — Low, CONFIRMED: most ledgers are empty

164 of 198 ledgers contain no transactions. A mean over all ledgers (3.90)
and a mean over non-empty ledgers only (772 / 34 = 22.71 drops/ledger)
describe different things; quoting either without the other misleads.

**Mitigation:** always report the empty-ledger fraction and both means, or
report the median (0) with the mean.

### F-03 — Low, CONFIRMED: amendment majority trend is not observable from one snapshot

The `feature` snapshot lists 101 amendments (64 enabled, 101 supported,
0 vetoed, 0 in majority). A single snapshot cannot show whether an
amendment's support is rising toward the 67% threshold or how long it has
held a majority (2-week hold required). The vote data exists (validations
carry `sfAmendments`), but no public read-only endpoint aggregates it over
time.

**Mitigation:** poll the `feature` method over days and record
majority-timestamp transitions; or subscribe to the validations stream and
tally `sfAmendments` per flag-ledger period.

### F-04 — Low, CONFIRMED: participation is aggregate-only

The only validator-participation figure the public read-only API exposes is
`server_info.last_close.proposers` (24 in all 25 samples) plus
`validation_quorum` (17). Per-validator participation (which validators
proposed/validated in each ledger) requires the validations WebSocket
stream, which was not used here.

**Mitigation:** document the limitation; use the validations stream for
per-validator participation.

### F-05 — Low, CONFIRMED: median fee 500x base fee, unexplained

At snapshot time the `fee` method reported `median_fee` 5000 drops while
`base_fee` was 10 drops and the queue was empty. The code defines
`median_fee = toDrops(escalationMultiplier, baseFee)`
(`src/xrpld/app/misc/detail/TxQ.cpp:1793,1899`), so the escalation
multiplier was 500x the reference level (128000 vs 256) at that moment.
Why it sat at 500x with an empty queue was not established from the
available data.

**Mitigation:** agents should budget by `open_ledger_fee`/`median_fee`,
not by `base_fee`, and the multiplier's behaviour under load should be
measured over a longer window before relying on it.

### F-06 — Informational, CONFIRMED: the public RPC drops connections under load

2 of 200 ledger fetches failed after 4 attempts each
(`IncompleteRead` — remote end closed the connection mid-response). Both
ledgers' burns were recovered indirectly (30 and 20 drops) from the
`total_coins` delta of the following ledger (V18), but they are excluded
from every statistic.

**Mitigation:** fetch with retries and backoff; record every failure with
its error; never silently skip a ledger.

### F-07 — Informational, CONFIRMED: one 12-drop transaction

76 of 77 transactions paid exactly 10 drops; one paid 12 drops. The reason
was not established (multi-signing and load are candidates, not verified).

**Mitigation:** none required; record the outlier rather than smoothing it.

## Checked and cleared (no finding)

- Quorum formula matches live quorum: `quorum(25) = 17` = live
  `validation_quorum` 17 (V02).
- Amendment thresholds 204/256 pre-fix and 67/100 post-fix, 2-week majority
  hold, 256-ledger flag cadence with quorum gate (V09–V11).
- All six RPC methods an agent needs respond correctly; the malformed
  account error path is structured (`actMalformed`, code 35) (V22–V27).
- Ledger chain linkage is intact across the sample apart from the two
  unfetched ledgers (V29).
- `total_coins` cross-check: 195/197 consecutive pairs match exactly; the
  2 mismatches are fully explained by the unfetched ledgers (V18).

## Limitations (honest)

- The fee-burn figure is a 7-minute window (198 ledgers); activity varies
  by time of day and the mean will drift. Re-fetch with
  `scripts/fetch_ledgers.py` for a current window.
- Per-validator participation and amendment-majority trends need the
  validations stream / repeated snapshots; not measured here.
- The 12-drop transaction and the 500x median fee are reported as observed;
  their causes were not established.
- WebSocket APIs were not probed; only JSON-RPC over HTTPS was used.
- No live-network mutation was performed; all observation was read-only.
