"""
test_genesis_v2.py — P5 Genesis v2 (strict layer) test suite

Function:
    Executable expression of SPEC_V2.md. Written before genesis_v2.py
    and run red first. Proves two things: (1) v2 mints the same genesis
    entry as the frozen v1 primitive, and its ledger verifies under P4
    v1 and v2; (2) v2 rejects, before touching the file, where v1
    crashed or accepted out-of-contract input (NOTES.md D1–D5).

Functions in this file (pytest-collected):
    1.  test_public_api                — one name, callable
    2.  test_entry_identity_with_v1    — same entry as v1, field for field
    3.  test_lf_only_on_disk           — D1: exact §2 bytes, no CR
    4.  test_verifies_under_p4_v1_v2   — ledger and ledger_v2 accept it
    5.  test_empty_file_is_new         — 0-byte file mints
    6.  test_refuses_non_empty         — v1 message kept, file unchanged
    7.  test_type_errors               — D3: file never created
    8.  test_non_finite_rejected       — P1 v2 rule, file never created
    9.  test_non_plain_json_rejected   — tuple record, file never created
    10. test_import_from_any_cwd       — D2

Fixtures:
    11. key  — fresh Ed25519 private key
    12. path — ledger path in a fresh temp directory (file absent)

Layer:    P5 — Genesis, v2 (strict)
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import os
import subprocess
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import genesis
import genesis_v2
import ledger
import ledger_v2

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = {"data": "genesis", "n": [1, 2.5, None], "é": "ü"}


# ---------------------------------------------------------------------------
# 11. key
# ---------------------------------------------------------------------------
@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()


# ---------------------------------------------------------------------------
# 12. path
#     A ledger path in a fresh directory; the file does not exist yet.
# ---------------------------------------------------------------------------
@pytest.fixture
def path(tmp_path):
    return str(tmp_path / "ledger.jsonl")


# ---------------------------------------------------------------------------
# 1. test_public_api
# ---------------------------------------------------------------------------
def test_public_api():
    assert callable(genesis_v2.mint_genesis)


# ---------------------------------------------------------------------------
# 2. test_entry_identity_with_v1
# ---------------------------------------------------------------------------
def test_entry_identity_with_v1(tmp_path, key):
    v1 = genesis.mint_genesis(str(tmp_path / "v1.jsonl"), RECORD, key)
    v2 = genesis_v2.mint_genesis(str(tmp_path / "v2.jsonl"), RECORD, key)
    assert v2 == v1
    assert v2["seq"] == 0 and v2["prev"] == "0" * 64


# ---------------------------------------------------------------------------
# 3. test_lf_only_on_disk
# ---------------------------------------------------------------------------
def test_lf_only_on_disk(path, key):
    entry = genesis_v2.mint_genesis(path, RECORD, key)
    with open(path, "rb") as f:
        data = f.read()
    assert b"\r" not in data
    assert data == json.dumps(entry, separators=(",", ":")).encode("ascii") + b"\n"


# ---------------------------------------------------------------------------
# 4. test_verifies_under_p4_v1_v2
# ---------------------------------------------------------------------------
def test_verifies_under_p4_v1_v2(path, key):
    genesis_v2.mint_genesis(path, RECORD, key)
    assert ledger.verify_ledger(path, key.public_key()) is True
    assert ledger_v2.verify_ledger(path, key.public_key()) is True
    # A genesis ledger can be extended by P4 v2 as normal.
    assert ledger_v2.append_entry(path, {"data": "next"}, key)["seq"] == 1
    assert ledger_v2.verify_ledger(path, key.public_key()) is True


# ---------------------------------------------------------------------------
# 5. test_empty_file_is_new
# ---------------------------------------------------------------------------
def test_empty_file_is_new(path, key):
    open(path, "wb").close()
    assert genesis_v2.mint_genesis(path, RECORD, key)["seq"] == 0


# ---------------------------------------------------------------------------
# 6. test_refuses_non_empty
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("prefill", [None, b"\n", b"junk"])
def test_refuses_non_empty(path, key, prefill):
    if prefill is None:
        genesis_v2.mint_genesis(path, RECORD, key)
    else:
        with open(path, "wb") as f:
            f.write(prefill)
    with open(path, "rb") as f:
        before = f.read()
    with pytest.raises(ValueError, match="Ledger already has entries"):
        genesis_v2.mint_genesis(path, {"data": "second"}, key)
    with open(path, "rb") as f:
        assert f.read() == before


# ---------------------------------------------------------------------------
# 7. test_type_errors
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("record, k", [
    ("str", "KEY"), (["list"], "KEY"), (None, "KEY"),
    ({"data": 1}, "not a key"), ({"data": 1}, None),
])
def test_type_errors(path, key, record, k):
    with pytest.raises(TypeError):
        genesis_v2.mint_genesis(path, record, key if k == "KEY" else k)
    assert not os.path.exists(path)


# ---------------------------------------------------------------------------
# 8. test_non_finite_rejected
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_rejected(path, key, bad):
    with pytest.raises(ValueError):
        genesis_v2.mint_genesis(path, {"x": bad}, key)
    assert not os.path.exists(path)


# ---------------------------------------------------------------------------
# 9. test_non_plain_json_rejected
# ---------------------------------------------------------------------------
def test_non_plain_json_rejected(path, key):
    with pytest.raises(TypeError):
        genesis_v2.mint_genesis(path, {"x": (1, 2)}, key)
    assert not os.path.exists(path)


# ---------------------------------------------------------------------------
# 10. test_import_from_any_cwd
# ---------------------------------------------------------------------------
def test_import_from_any_cwd(tmp_path):
    code = ("import sys; sys.path.insert(0, %r); import genesis_v2; "
            "print(genesis_v2.mint_genesis.__name__)" % HERE)
    out = subprocess.run([sys.executable, "-c", code], cwd=str(tmp_path),
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "mint_genesis"
