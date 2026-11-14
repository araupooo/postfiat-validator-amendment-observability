#!/usr/bin/env bash
# Validator and Amendment Observability Evidence Pack — full run.
# Offline recomputation from vendored fixtures; no network access.
# Exit 0 only when every battery passes.
set -euo pipefail
cd "$(dirname "$0")"

echo "== run_checks =="
python3 scripts/run_checks.py | tee /tmp/observability_run_checks.log
echo "== verify_constants =="
python3 scripts/verify_constants.py | tee results/constants_verification.txt
echo "== build_derived =="
python3 scripts/build_derived.py
echo "== outputs (fresh-run copies) =="
mkdir -p results/outputs
cp results/run_log.txt results/outputs/run_log.txt
cp results/summary.json results/outputs/summary.json
cp results/summary.txt results/outputs/summary.txt
cp results/constants_verification.txt results/outputs/constants_verification.txt
rm -f results/outputs/V*.txt
cp results/checks/V*.txt results/outputs/
echo "== digests =="
bash verify_digests.sh
echo "run_all.sh: OK"
