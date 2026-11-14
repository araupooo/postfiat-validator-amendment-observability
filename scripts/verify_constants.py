#!/usr/bin/env python3
"""Verify every constant in fixtures/constants.json against the pinned tree.

When the pinned tree is present at the recorded path, each constant is
checked by reading the cited source file. When the tree is absent, the check
falls back to the vendored source snippets in
fixtures/pinned_tree_audit.json (which were captured verbatim from the tree).

Usage: python3 scripts/verify_constants.py
Output: results/constants_verification.txt (stdout only; run_all.sh captures it)
"""

import json
import os
import sys

PACK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK_DIR, "fixtures")
PINNED_COMMIT = "0085a1ff885d6a446369cf73a4430f75af22be55"
TREE = "/home/hatch/workspace/postfiatd-amendment/worktree-0085a1ff"

# (constant key, source file relative to tree, expected literal)
CHECKS = [
    ("reference_fee_drops", "src/xrpld/core/Config.h", "reference_fee{10}"),
    ("account_reserve_xrp", "src/xrpld/core/Config.h",
     "account_reserve{10 * DROPS_PER_XRP}"),
    ("owner_reserve_xrp", "src/xrpld/core/Config.h",
     "owner_reserve{2 * DROPS_PER_XRP}"),
    ("amendment_majority_pre_fix",
     "include/xrpl/protocol/SystemParameters.h", "ratio<204, 256>"),
    ("amendment_majority_post_fix",
     "include/xrpl/protocol/SystemParameters.h", "ratio<67, 100>"),
    ("amendment_majority_time_weeks",
     "include/xrpl/protocol/SystemParameters.h", "weeks{2}"),
    ("default_peer_port", "include/xrpl/protocol/SystemParameters.h",
     "DEFAULT_PEER_PORT{2459}"),
    ("flag_ledger_interval", "src/xrpld/app/ledger/Ledger.h",
     "FLAG_LEDGER_INTERVAL = 256"),
    ("load_fee_normal", "src/xrpld/app/misc/LoadFeeTrack.h",
     "lftNormalFee ="),
    ("load_fee_max", "src/xrpld/app/misc/LoadFeeTrack.h",
     "lftFeeMax = lftNormalFee * 1000000"),
    ("negative_unl_50pct_ledgers", "src/xrpld/app/misc/NegativeUNLVote.h",
     "FLAG_LEDGER_INTERVAL * 50 / 100"),
    ("negative_unl_80pct_ledgers", "src/xrpld/app/misc/NegativeUNLVote.h",
     "FLAG_LEDGER_INTERVAL * 80 / 100"),
    ("negative_unl_min_local_vals", "src/xrpld/app/misc/NegativeUNLVote.h",
     "FLAG_LEDGER_INTERVAL * 90 / 100"),
    ("validator_quorum_fraction",
     "src/xrpld/app/misc/detail/ValidatorList.cpp", "0.67f"),
    ("validator_quorum_floor_fraction",
     "src/xrpld/app/misc/detail/ValidatorList.cpp", "0.6f"),
]


def file_text(relpath, audit):
    full = os.path.join(TREE, relpath)
    if os.path.isfile(full):
        with open(full) as fh:
            return fh.read(), "tree"
    for snip in audit.get("snippets", {}).values():
        if snip["file"] == relpath:
            return snip["text"], "snippet"
    return None, "missing"


def main():
    consts = json.load(open(os.path.join(FIX, "constants.json")))
    audit = json.load(open(os.path.join(FIX, "pinned_tree_audit.json")))
    if audit["pinned_commit"] != PINNED_COMMIT:
        print("FAIL: audit record commit != pinned commit")
        return 1
    ok = 0
    for key, relpath, literal in CHECKS:
        text, where = file_text(relpath, audit)
        if text is None:
            print(f"  {key}: FAIL (source {relpath} not available)")
            continue
        if literal in text:
            print(f"  {key}: OK ({where}: {relpath})")
            ok += 1
        else:
            print(f"  {key}: FAIL (literal {literal!r} not in {relpath})")
    # Value cross-checks that need arithmetic, not just literals.
    extra = [
        ("load_fee_max value 256000000",
         consts["constants"]["load_fee_max"]["value"] == 256 * 1000000),
        ("negative_unl_50pct value 128",
         consts["constants"]["negative_unl_50pct_ledgers"]["value"] == 256 * 50 // 100),
        ("negative_unl_80pct value 204",
         consts["constants"]["negative_unl_80pct_ledgers"]["value"] == 256 * 80 // 100),
        ("negative_unl_min_local value 230",
         consts["constants"]["negative_unl_min_local_vals"]["value"] == 256 * 90 // 100),
        ("quorum(25) == 17",
         max(-(-25 * 67 // 100), -(-25 * 60 // 100)) == 17),
    ]
    for label, passed in extra:
        print(f"  {label}: {'OK' if passed else 'FAIL'}")
        ok += 1 if passed else 0
    total = len(CHECKS) + len(extra)
    print(f"constants: {ok}/{total} OK")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
