"""
test_genesis.py — P5 Genesis test suite

Function:
    Executable expression of SPEC.md v1.0.0 for genesis.py: a genesis
    entry is seq 0 / prev 0*64, and a non-empty ledger is refused.

Functions in this file (pytest-collected):
    1. test_mint_genesis_valid            — seq 0, prev 0*64
    2. test_mint_genesis_refuses_non_empty — ValueError on second mint

Fixtures:
    3. key         — fresh Ed25519 private key
    4. temp_ledger — empty temp .jsonl file, removed afterwards

Layer:    P5 — Genesis
Spec:     SPEC.md 1.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""
import os
import sys
import tempfile
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../ledger-layer'))

import genesis

# ---------------------------------------------------------------------------
# 3. key
# ---------------------------------------------------------------------------
@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()

# ---------------------------------------------------------------------------
# 4. temp_ledger
# ---------------------------------------------------------------------------
@pytest.fixture
def temp_ledger():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    # Empty the file so it counts as "new"
    open(path, 'w').close()
    yield path
    if os.path.exists(path):
        os.remove(path)

# ---------------------------------------------------------------------------
# 1. test_mint_genesis_valid
# ---------------------------------------------------------------------------
def test_mint_genesis_valid(temp_ledger, key):
    record = {"data": "genesis"}
    entry = genesis.mint_genesis(temp_ledger, record, key)
    assert entry["seq"] == 0
    assert entry["prev"] == "0" * 64

# ---------------------------------------------------------------------------
# 2. test_mint_genesis_refuses_non_empty
# ---------------------------------------------------------------------------
def test_mint_genesis_refuses_non_empty(temp_ledger, key):
    genesis.mint_genesis(temp_ledger, {"data": "genesis"}, key)
    with pytest.raises(ValueError, match="Ledger already has entries"):
        genesis.mint_genesis(temp_ledger, {"data": "second"}, key)
