"""
test_genesis_v3.py — P5 Genesis v3 (ledger_v2 layer) test suite

Function:
    Executable expression of SPEC_V3.md. Written before genesis_v3.py
    and run red first. Proves that v3 mints exactly as v2, that its
    ledgers are root ledgers under P4 ledger_v2, and that the root
    check refuses everything that is not one.

Functions in this file (pytest-collected):
    1.  test_public_api
    2.  test_same_entry_and_bytes_as_v2
    3.  test_identity_of_fresh_genesis
    4.  test_not_root_cases
    5.  test_root_survives_appends
    6.  test_identity_key_type
    7.  test_v2_errors_pass_through

Fixtures:
    8.  key  — fresh Ed25519 private key
    9.  path — ledger path in a fresh temp directory (file absent)

Layer:    P5 — Genesis, v3
Spec:     SPEC_V3.md 3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import genesis_v2
import genesis_v3
import ledger_v2


# 8. key
@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()


# 9. path
@pytest.fixture
def path(tmp_path):
    return str(tmp_path / "ledger.jsonl")


# 1. test_public_api
def test_public_api():
    for name in ("mint_genesis", "genesis_identity", "verify_genesis"):
        assert callable(getattr(genesis_v3, name))


# 2. test_same_entry_and_bytes_as_v2
def test_same_entry_and_bytes_as_v2(key, tmp_path):
    p2, p3 = str(tmp_path / "v2.jsonl"), str(tmp_path / "v3.jsonl")
    e2 = genesis_v2.mint_genesis(p2, {"root": True}, key)
    e3 = genesis_v3.mint_genesis(p3, {"root": True}, key)
    assert e2 == e3
    assert open(p2, "rb").read() == open(p3, "rb").read()


# 3. test_identity_of_fresh_genesis
def test_identity_of_fresh_genesis(key, path):
    entry = genesis_v3.mint_genesis(path, {"root": True}, key)
    ident = genesis_v3.genesis_identity(path, key.public_key())
    assert ident == {"hash": entry["hash"], "signer": entry["signer"]}
    assert genesis_v3.verify_genesis(path, key.public_key()) is True


# 4. test_not_root_cases
def test_not_root_cases(key, path, tmp_path):
    pub = key.public_key()
    assert genesis_v3.verify_genesis(path, pub) is False            # missing
    open(path, "wb").close()
    assert genesis_v3.verify_genesis(path, pub) is False            # empty
    os.remove(path)
    genesis_v3.mint_genesis(path, {"root": True}, key)
    other = Ed25519PrivateKey.generate()
    assert genesis_v3.verify_genesis(path, other.public_key()) is False  # wrong key
    good = open(path, "rb").read()
    open(path, "wb").write(good.replace(b"true", b"false"))
    assert genesis_v3.verify_genesis(path, pub) is False            # tampered
    open(path, "wb").write(good.replace(b"\n", b"\r\n"))
    assert genesis_v3.verify_genesis(path, pub) is False            # CRLF
    foreign = str(tmp_path / "foreign.jsonl")
    genesis_v3.mint_genesis(foreign, {"root": True}, other)
    assert genesis_v3.genesis_identity(foreign, pub) is None        # other signer


# 5. test_root_survives_appends
def test_root_survives_appends(key, path):
    entry = genesis_v3.mint_genesis(path, {"root": True}, key)
    ledger_v2.append_entry(path, {"n": 1}, key)
    ledger_v2.append_entry(path, {"n": 2}, key)
    ident = genesis_v3.genesis_identity(path, key.public_key())
    assert ident["hash"] == entry["hash"]


# 6. test_identity_key_type
def test_identity_key_type(key, path):
    genesis_v3.mint_genesis(path, {"root": True}, key)
    for bad in (key, None, b"\x00" * 32):
        with pytest.raises(TypeError):
            genesis_v3.genesis_identity(path, bad)


# 7. test_v2_errors_pass_through
def test_v2_errors_pass_through(key, path):
    genesis_v3.mint_genesis(path, {"root": True}, key)
    before = open(path, "rb").read()
    with pytest.raises(ValueError, match="already has entries"):
        genesis_v3.mint_genesis(path, {"root": True}, key)
    with pytest.raises(TypeError):
        genesis_v3.mint_genesis(str(path) + ".x", "not a dict", key)
    assert open(path, "rb").read() == before
