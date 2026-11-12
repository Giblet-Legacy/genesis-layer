"""
genesis_v2.py — P5 Genesis v2, strict layer over the frozen v1 primitive

Function:
    The layer new code imports instead of genesis.py. It mints the
    genesis entry of an empty ledger exactly as genesis.py v1.0.0 does,
    but writes it as one LF-terminated compact line (SPEC_V2.md §2),
    type-checks its inputs, leaves the file untouched on any error, and
    fsyncs (SPEC_V2.md §3). It never reimplements the primitive: the
    entry it writes is the dict returned by genesis.mint_genesis, run
    against a private temp file (SPEC_V2.md §1).

    genesis.py is not edited (Immutable Rule). This file is the
    "add a layer" half of that rule.

Public API (same name and numbering as P5 v1.0.0):
    1. mint_genesis — type checks, v1 entry, exclusive LF write

Internal helpers (not exported):
    2. _refuse      — the v1 "already has entries" ValueError
    3. _v1_genesis  — v1 mint_genesis on a private temp file
    4. _compact     — the SPEC_V2 §2 line bytes for an entry
    5. _open_empty  — open the ledger for writing only if it is empty

Layer:    P5 — Genesis, v2 (strict)
Depends:  genesis.py (P5 v1.0.0), ledger.py (P4 v1.0.0)
Consumed: P6 Canon Verify
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Version:  2.0.0 (frozen 2026-11-12)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import os
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Resolve P1, P4 and P5 v1 from this file's location, not the CWD (SPEC_V2 §4).
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _path in (os.path.join(_PARENT, "envelope-layer"),
              os.path.join(_PARENT, "ledger-layer"),
              _HERE):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import genesis as _v1  # noqa: E402


# ---------------------------------------------------------------------------
# 2. _refuse
#    Same exception type and text as v1, so callers matching on it work.
# ---------------------------------------------------------------------------
def _refuse():
    return ValueError("Ledger already has entries — genesis refused")


# ---------------------------------------------------------------------------
# 3. _v1_genesis
#    Runs v1 mint_genesis against a fresh private file and returns v1's
#    entry. The real ledger is not touched. v1 raises for NaN/±Infinity
#    (via P1 v2) and checks seq 0 / prev 0*64 itself.
# ---------------------------------------------------------------------------
def _v1_genesis(record, private_key):
    with tempfile.TemporaryDirectory() as tmp:
        return _v1.mint_genesis(os.path.join(tmp, "ledger.jsonl"), record, private_key)


# ---------------------------------------------------------------------------
# 4. _compact
#    One ledger line: compact JSON, ASCII, LF-terminated (SPEC_V2 §2).
# ---------------------------------------------------------------------------
def _compact(entry):
    return json.dumps(entry, separators=(",", ":")).encode("ascii") + b"\n"


# ---------------------------------------------------------------------------
# 5. _open_empty
#    Missing file: exclusive create, so a file that appears meanwhile is
#    refused. Existing file: open for append and re-check its size on
#    the handle. Raises the v1 ValueError if the ledger is not empty.
# ---------------------------------------------------------------------------
def _open_empty(ledger_path):
    try:
        return open(ledger_path, "xb")
    except FileExistsError:
        pass
    f = open(ledger_path, "ab")
    if os.fstat(f.fileno()).st_size > 0:
        f.close()
        raise _refuse()
    return f


# ---------------------------------------------------------------------------
# 1. mint_genesis
#    SPEC_V2 §3.1. Checks types and emptiness, takes the entry from v1,
#    writes it as one LF line, fsyncs. On any error the ledger file is
#    unchanged, and not created if it was missing.
# ---------------------------------------------------------------------------
def mint_genesis(ledger_path, record, private_key):
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError(f"private_key must be Ed25519PrivateKey, got {type(private_key).__name__}")
    if not isinstance(record, dict):
        raise TypeError(f"record must be dict, got {type(record).__name__}")
    if os.path.exists(ledger_path) and os.path.getsize(ledger_path) > 0:
        raise _refuse()

    entry = _v1_genesis(record, private_key)
    line = _compact(entry)
    if json.loads(line) != entry:
        raise TypeError("record must be plain JSON: str keys, lists not tuples")

    with _open_empty(ledger_path) as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    return entry
