"""
genesis_v3.py — P5 Genesis v3, the ledger_v2 layer over genesis_v2

Function:
    The layer new code imports instead of genesis_v2.py. It mints a
    genesis exactly as genesis_v2 does, confirms the result under P4
    ledger_v2 (frozen 2.0.0), and exposes the root-ledger check that
    SPEC_V2.md §3.2 defined but no function offered (SPEC_V3.md).

    genesis.py and genesis_v2.py are not edited (Immutable Rule).

Public API:
    1. mint_genesis     — genesis_v2, then a ledger_v2 confirmation
    2. genesis_identity — (hash, signer) of a root ledger, or None
    3. verify_genesis   — bool form of genesis_identity

Internal helpers (not exported):
    4. _first_line      — the first line of a ledger file, or None

Layer:    P5 — Genesis, v3
Depends:  genesis_v2.py (P5 v2.0.0), ledger_v2.py (P4 v2.0.0)
Consumed: The Cockpit, The Legacy
Spec:     SPEC_V3.md 3.0.0
Version:  3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _path in (os.path.join(_PARENT, "envelope-layer"),
              os.path.join(_PARENT, "ledger-layer"),
              _HERE):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import genesis_v2 as _v2  # noqa: E402
import ledger_v2 as _ledger  # noqa: E402

_ZERO = "0" * 64


# ---------------------------------------------------------------------------
# 4. _first_line
#    Raw first line of the file (without its LF), or None if the file is
#    missing or unreadable. Content is judged by ledger_v2, not here.
# ---------------------------------------------------------------------------
def _first_line(ledger_path):
    try:
        with open(ledger_path, "rb") as f:
            return f.readline().rstrip(b"\n")
    except OSError:
        return None


# ---------------------------------------------------------------------------
# 1. mint_genesis
#    SPEC_V3 §2. genesis_v2 does all the work; v3 only confirms that the
#    file it wrote is a ledger_v2-valid chain under the same key.
# ---------------------------------------------------------------------------
def mint_genesis(ledger_path, record, private_key):
    entry = _v2.mint_genesis(ledger_path, record, private_key)
    if not _ledger.verify_ledger(ledger_path, private_key.public_key()):
        raise RuntimeError("genesis written but not valid under ledger_v2")
    return entry


# ---------------------------------------------------------------------------
# 2. genesis_identity
#    SPEC_V3 §3.1. Never raises for file content; TypeError for a wrong
#    key type, before the file is read.
# ---------------------------------------------------------------------------
def genesis_identity(ledger_path, public_key):
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError(f"public_key must be Ed25519PublicKey, got {type(public_key).__name__}")
    try:
        if not _ledger.verify_ledger(ledger_path, public_key):
            return None
    except RecursionError:  # P4 NOTES Q3: deep nesting is not a valid ledger
        return None
    line = _first_line(ledger_path)
    if not line:
        return None
    first = json.loads(line)
    if first.get("seq") != 0 or first.get("prev") != _ZERO:
        return None
    return {"hash": first["hash"], "signer": first["signer"]}


# ---------------------------------------------------------------------------
# 3. verify_genesis
#    SPEC_V3 §3.2.
# ---------------------------------------------------------------------------
def verify_genesis(ledger_path, public_key):
    return genesis_identity(ledger_path, public_key) is not None
