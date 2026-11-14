#!/usr/bin/env bash
# SHA-256 digest manifest for the pack.
# Usage:
#   bash verify_digests.sh          regenerate results/SHA256SUMS, then --check
#   bash verify_digests.sh --check  verify all digests, write results/digest_check_output.txt
#
# The manifest excludes ./.git/* plus results/SHA256SUMS,
# results/digest_check_output.txt, and results/reproduction_log.txt.
set -euo pipefail
cd "$(dirname "$0")"

if [ "${1:-}" = "--check" ]; then
    if [ ! -f results/SHA256SUMS ]; then
        echo "verify_digests.sh: results/SHA256SUMS missing" >&2
        exit 1
    fi
    set +e
    (cd . && sha256sum -c results/SHA256SUMS) > results/digest_check_output.txt 2>&1
    rc=$?
    set -e
    fails=$(grep -c ': FAILED' results/digest_check_output.txt || true)
    ok=$(grep -c ': OK' results/digest_check_output.txt || true)
    echo "verify_digests.sh: $ok files OK, $fails failed"
    exit $rc
fi

# Regenerate manifest (sorted, deterministic).
find . -type f \
  ! -path './.git/*' \
  ! -path './results/SHA256SUMS' \
  ! -path './results/SHA256SUMS.tmp' \
  ! -path './results/digest_check_output.txt' \
  ! -path './results/reproduction_log.txt' \
  -print0 | sort -z | xargs -0 sha256sum > results/SHA256SUMS.tmp
mv results/SHA256SUMS.tmp results/SHA256SUMS
echo "verify_digests.sh: manifest regenerated ($(wc -l < results/SHA256SUMS) files)"
bash verify_digests.sh --check
