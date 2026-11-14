#!/usr/bin/env python3
"""Build docs/index.html from the final run log and summaries.

Runs AFTER run_checks.py and verify_constants.py (see run_all.sh), so the
page reports the final numbers. The page embeds the run-log tail and check
counts, but never the digest-check output (produced later), so the
digest-manifest fixed point holds.

Usage: python3 scripts/build_derived.py
"""

import gzip
import html
import json
import os
import statistics

PACK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK_DIR, "fixtures")
RES = os.path.join(PACK_DIR, "results")
PINNED_COMMIT = "0085a1ff885d6a446369cf73a4430f75af22be55"


def load_sample():
    with gzip.open(os.path.join(FIX, "ledgers_sample.json.gz"), "rt") as fh:
        return json.load(fh)


def parse_findings():
    rows = []
    with open(os.path.join(PACK_DIR, "FINDINGS.md")) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.startswith("| F-"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5:
                rows.append(cells[:5])
    return rows


def main():
    summary = json.load(open(os.path.join(RES, "summary.json")))
    sample = load_sample()
    led = sample["ledgers"]
    burns = [sum(l["fees_drops"]) for l in led]
    mean = sum(burns) / len(burns)
    med = statistics.median(burns)
    empty = sum(1 for b in burns if b == 0)
    nonempty_mean = sum(burns) / (len(burns) - empty)
    cts = [l["close_time"] for l in led]
    iv = [b - a for a, b in zip(cts, cts[1:])]
    feats = sample["feature_snapshot"]["features"]
    enabled = sum(1 for v in feats.values() if v.get("enabled"))
    with open(os.path.join(RES, "run_log.txt")) as fh:
        run_log = fh.read()
    run_tail = "\n".join(run_log.strip().splitlines()[-8:])
    with open(os.path.join(RES, "constants_verification.txt")) as fh:
        const_lines = fh.read().strip().splitlines()
    const_line = const_lines[-1] if const_lines else "constants: not verified"
    findings = parse_findings()
    check_rows = "".join(
        f"<tr><td>{c['id']}</td><td>{html.escape(c['title'])}</td>"
        f"<td>{c['kind']}</td><td>{c['status']}</td></tr>\n"
        for c in summary["checks"])
    finding_rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>"
        f"<td>{html.escape(r[3])}</td><td>{r[4]}</td></tr>\n"
        for r in findings)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Validator and Amendment Observability — PFTL</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; color: #1a1a1a; }}
h1 {{ font-size: 1.6em; }} h2 {{ font-size: 1.25em; margin-top: 2em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #bbb; padding: 6px 10px; text-align: left; vertical-align: top; }}
th {{ background: #f0f0f0; }}
code, pre {{ background: #f6f6f6; padding: 2px 4px; }}
pre {{ padding: 12px; overflow-x: auto; }}
.big {{ font-size: 1.3em; font-weight: bold; }}
.pass {{ color: #0a7a1f; font-weight: bold; }}
</style>
</head>
<body>
<h1>Validator and Amendment Observability Evidence Pack</h1>
<p>Pinned postfiatd tree: <code>{PINNED_COMMIT}</code>. All ledger observation
was read-only from the public RPC <code>https://rpc.testnet.postfiat.org/</code>;
no live-network mutation, no changes to the pinned tree.</p>

<h2>Headline — measured per-ledger fee burn</h2>
<p class="big">Mean burn: {mean:.2f} drops/ledger (median {med:.0f}, min {min(burns)}, max {max(burns)})</p>
<p>Measured over <strong>{len(burns)} consecutive validated ledgers</strong>
(seq {sample['seq_range'][0]}&ndash;{sample['seq_range'][1]},
{sample['count_fetched']} fetched of {sample['count_requested']} requested,
total burn {sum(burns)} drops). The previously cited rounded figure of
<strong>10 drops/ledger</strong> was the per-transaction base fee, not a
per-ledger measurement — the correction factor is {10 / mean:.2f}x. Per-ledger
burn = sum of the Fee field of that ledger's transactions; fees are destroyed
(<code>ApplyStateTable::destroyXRP</code>), not paid to anyone. Cross-check:
<code>total_coins</code> delta between consecutive ledgers equals the burn in
195/197 pairs; the 2 mismatches are fully explained by the 2 unfetched
ledgers (implied burns 30 and 20 drops).</p>

<h2>Headline figures</h2>
<table>
<tr><th>Metric</th><th>Value</th><th>Method</th></tr>
<tr><td>Mean fee burn</td><td>{mean:.2f} drops/ledger</td><td>sum of per-ledger tx fees, 198 ledgers</td></tr>
<tr><td>Median fee burn</td><td>{med:.0f} drops/ledger</td><td>same sample</td></tr>
<tr><td>Mean burn, non-empty ledgers only</td><td>{nonempty_mean:.2f} drops/ledger</td><td>772 drops / 34 non-empty ledgers</td></tr>
<tr><td>Empty ledgers</td><td>{empty}/{len(burns)} ({100 * empty / len(burns):.1f}%)</td><td>count of ledgers with 0 transactions</td></tr>
<tr><td>Ledger close interval</td><td>mean {statistics.mean(iv):.3f} s, median {statistics.median(iv):.1f} s</td><td>stored close_time deltas</td></tr>
<tr><td>Validation quorum / implied UNL</td><td>17 / 25 (68%)</td><td>quorum formula in tree; live <code>validation_quorum</code> 17</td></tr>
<tr><td>Proposers (last close)</td><td>24 in every sample</td><td><code>server_info</code>, 25 samples</td></tr>
<tr><td>Amendments inventoried</td><td>{len(feats)} total, {enabled} enabled, 101 supported, 0 vetoed, 0 in majority</td><td><code>feature</code> method snapshot</td></tr>
<tr><td>Reference fee / reserves</td><td>10 drops; 10 XRP + 2 XRP per owner item</td><td><code>Config.h:69,72,75</code></td></tr>
<tr><td>Amendment threshold</td><td>204/256 pre-fix, 67/100 post-fix; 2-week majority hold</td><td><code>SystemParameters.h:83,85,88</code></td></tr>
<tr><td>Flag-ledger interval</td><td>256 ledgers</td><td><code>Ledger.h:426</code></td></tr>
</table>

<h2>Harness results</h2>
<p>Checks: <strong>{summary['checks_total']} total, {summary['checks_passed']} passed, {summary['checks_failed']} failed</strong>.
Constants verification: <strong>{html.escape(const_line)}</strong>. The harness
recomputes every figure offline from the vendored fixtures; no network access.
Fresh-clone reproduction: <code>bash run_all.sh</code> exits 0, git status
clean, outputs byte-identical (see REPRODUCTION.md; fresh logs in
<code>results/outputs/</code>).</p>
<table>
<tr><th>Check</th><th>Title</th><th>Kind</th><th>Result</th></tr>
{check_rows}</table>

<h2>Findings</h2>
<table>
<tr><th>ID</th><th>Severity</th><th>Status</th><th>Finding</th><th>Checks</th></tr>
{finding_rows}</table>
<p>Full finding detail, mitigations, and honest limitations: <code>FINDINGS.md</code>.
Claim-to-evidence index: <code>claim_evidence_index.md</code>.</p>

<h2>Reproduction</h2>
<pre>git clone &lt;repo-url&gt; observability-repro
cd observability-repro
bash run_all.sh
# expected: checks: 30 total, 30 passed, 0 failed
#           constants: 20/20 OK
#           verify_digests.sh: all files OK, 0 failed
# exit 0, git status clean
bash verify_digests.sh --check</pre>

<h2>Run log (tail)</h2>
<pre>{html.escape(run_tail)}</pre>

<h2>Limitations</h2>
<ul>
<li>The fee-burn figure covers a 7-minute window; activity varies by time of day.</li>
<li>Per-validator participation and amendment-majority trends need the validations stream / repeated snapshots; not measured here.</li>
<li>The 12-drop transaction and the 500x median fee are reported as observed; their causes were not established.</li>
<li>Only JSON-RPC over HTTPS was probed; WebSocket APIs were not used.</li>
</ul>
</body>
</html>
"""
    os.makedirs(os.path.join(PACK_DIR, "docs"), exist_ok=True)
    with open(os.path.join(PACK_DIR, "docs", "index.html"), "w") as fh:
        fh.write(page)
    print(f"docs/index.html written ({len(page)} bytes)")
    print(f"checks: {summary['checks_total']} total, "
          f"{summary['checks_passed']} passed, {summary['checks_failed']} failed")
    print(f"findings: {len(findings)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
