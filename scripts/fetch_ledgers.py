#!/usr/bin/env python3
"""Fetch a sample of consecutive validated ledgers from the public read-only
PFTL testnet RPC and store a compact, verifiable extract.

This is a LIVE fetch script. It is NOT run by run_all.sh: the harness
recomputes everything offline from the vendored fixture
(fixtures/ledgers_sample.json.gz). Re-run this script only to refresh the
sample; the shipped fixture is the measured evidence for this pack.

Endpoint: https://rpc.testnet.postfiat.org/ (public, unauthenticated,
read-only JSON-RPC; no credentials, no session, no mutation).

Method per ledger (fee burn):
  burn(ledger) = sum of the Fee field (drops) of every transaction in the
  ledger. Transaction fees are destroyed, not paid to anyone
  (ApplyStateTable::destroyXRP, src/libxrpl/ledger/ApplyStateTable.cpp:546),
  so the per-ledger burn is exactly the sum of the fees of that ledger's
  transactions. Cross-check: total_coins(ledger n) - total_coins(n-1) must
  equal -burn(ledger n) for consecutive validated ledgers.

Usage:
    python3 scripts/fetch_ledgers.py [--count N] [--out fixtures/ledgers_sample.json.gz]
"""

import argparse
import gzip
import json
import time
import urllib.request

RPC_URL = "https://rpc.testnet.postfiat.org/"
DEFAULT_COUNT = 200


def rpc(method, params, timeout=30):
    body = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(
        RPC_URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def rpc_retry(method, params, attempts=4):
    last = None
    for i in range(attempts):
        try:
            out = rpc(method, params)
            if out.get("status") == "success" or "result" in out:
                return out
            last = out
        except Exception as exc:  # noqa: BLE001 - retry on any transport error
            last = exc
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"RPC {method} failed after {attempts} attempts: {last!r}")


def fetch_ledger(seq):
    out = rpc_retry(
        "ledger",
        [{"ledger_index": seq, "transactions": True, "expand": True}],
    )
    return out["result"]["ledger"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT)
    ap.add_argument("--out", default="fixtures/ledgers_sample.json.gz")
    args = ap.parse_args()

    t0 = time.time()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    info_start = rpc_retry("server_info", [{}])["result"]["info"]
    end_seq = int(info_start["validated_ledger"]["seq"])
    start_seq = end_seq - args.count + 1

    ledgers = []
    failures = []
    for i, seq in enumerate(range(start_seq, end_seq + 1)):
        try:
            led = fetch_ledger(seq)
        except Exception as exc:  # noqa: BLE001
            failures.append({"seq": seq, "error": str(exc)})
            continue
        txs = led.get("transactions", [])
        fees = []
        types = []
        for tx in txs:
            try:
                fees.append(int(tx.get("Fee", 0)))
            except (TypeError, ValueError):
                fees.append(0)
            types.append(tx.get("TransactionType"))
        ledgers.append(
            {
                "seq": int(led["ledger_index"]),
                "hash": led["ledger_hash"],
                "parent_hash": led["parent_hash"],
                "close_time": int(led["close_time"]),
                "close_time_iso": led.get("close_time_iso"),
                "total_coins": led.get("total_coins"),
                "tx_count": len(txs),
                "fees_drops": fees,
                "tx_types": types,
            }
        )
        # Sample server_info last_close.proposers during the fetch window.
        if i % 8 == 0:
            try:
                info = rpc_retry("server_info", [{}])["result"]["info"]
                ledgers[-1]["proposers_sample"] = info.get("last_close", {}).get(
                    "proposers"
                )
            except Exception:  # noqa: BLE001 - best effort snapshot
                pass

    info_end = rpc_retry("server_info", [{}])["result"]["info"]
    feature = rpc_retry("feature", [{}])["result"]
    fee = rpc_retry("fee", [{}])["result"]
    ended_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    sample = {
        "endpoint": RPC_URL,
        "method": "per-ledger burn = sum of Fee (drops) over the ledger's transactions",
        "count_requested": args.count,
        "count_fetched": len(ledgers),
        "seq_range": [start_seq, end_seq],
        "started_utc": started_utc,
        "ended_utc": ended_utc,
        "duration_s": round(time.time() - t0, 1),
        "failures": failures,
        "server_info_start": {
            "build_version": info_start.get("build_version"),
            "network_id": info_start.get("network_id"),
            "server_state": info_start.get("server_state"),
            "validation_quorum": info_start.get("validation_quorum"),
            "complete_ledgers": info_start.get("complete_ledgers"),
            "validated_ledger": info_start.get("validated_ledger"),
            "peers": info_start.get("peers"),
        },
        "server_info_end": {
            "build_version": info_end.get("build_version"),
            "network_id": info_end.get("network_id"),
            "server_state": info_end.get("server_state"),
            "validation_quorum": info_end.get("validation_quorum"),
            "validated_ledger": info_end.get("validated_ledger"),
        },
        "fee_snapshot": fee,
        "feature_snapshot": feature,
        "ledgers": ledgers,
    }

    with gzip.open(args.out, "wt", encoding="utf-8") as fh:
        json.dump(sample, fh, sort_keys=True)
    total_burn = sum(sum(l["fees_drops"]) for l in ledgers)
    print(
        f"fetched {len(ledgers)}/{args.count} ledgers "
        f"{start_seq}..{end_seq} in {sample['duration_s']}s; "
        f"failures={len(failures)}; total burn={total_burn} drops; "
        f"mean={total_burn / max(len(ledgers), 1):.2f} drops/ledger"
    )


if __name__ == "__main__":
    main()
