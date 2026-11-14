# Reproduction — Validator and Amendment Observability

## Fresh-copy reproduction (offline, deterministic)

From a fresh clone of the repository:

```sh
git clone <repo-url> observability-repro
cd observability-repro
bash run_all.sh
```

Expected output (exact lines):

```text
checks: 30 total, 30 passed, 0 failed
constants: 20/20 OK
verify_digests.sh: <N> files OK, 0 failed
run_all.sh: OK
```

Exit code 0. `git status` clean after the run. `results/` and
`docs/index.html` byte-identical to the shipped pack. The fresh run log is
shipped at `results/reproduction_log.txt` and the fresh per-check logs at
`results/outputs/` (all batteries re-run in the clean setup).

What `run_all.sh` does, in order:

1. `python3 scripts/run_checks.py` — recomputes every figure offline from
   the vendored fixtures; writes `results/run_log.txt`,
   `results/summary.json`, `results/summary.txt`, `results/checks/V*.txt`,
   `results/env.txt`. No network access.
2. `python3 scripts/verify_constants.py` — checks every constant in
   `fixtures/constants.json` against the pinned tree when present, else
   against the vendored source snippets; writes
   `results/constants_verification.txt`.
3. `python3 scripts/build_derived.py` — rebuilds `docs/index.html` from the
   final run log and summaries.
4. Copies the fresh run log, summaries, and per-check outputs to
   `results/outputs/` (the clean-setup copies).
5. `bash verify_digests.sh` — regenerates `results/SHA256SUMS` over every
   pack file except `.git`, `results/SHA256SUMS` itself,
   `results/digest_check_output.txt`, and `results/reproduction_log.txt`;
   then `bash verify_digests.sh --check` verifies all digests and writes
   `results/digest_check_output.txt`.

Verify digests at any time with:

```sh
bash verify_digests.sh --check
```

## Re-fetching a current measurement window (live, optional)

The shipped fixture is the measured evidence for this pack. To measure a
current window instead:

```sh
python3 scripts/fetch_ledgers.py --count 200 --out fixtures/ledgers_sample.json.gz
bash run_all.sh
```

This needs network access to `https://rpc.testnet.postfiat.org/` once.
Ledger heights move (~20 ledgers/min), so figures will differ from the
shipped window; the methods and cross-checks are the same. The two
ledgers that failed in the shipped window (8049459, 8049590) are
re-fetchable the same way.

## Requirements

- Python 3.11+ with only the standard library (no third-party packages).
- `git` (only for the fresh-clone step and the optional live tree re-check).
- No network access is needed for `bash run_all.sh`.
