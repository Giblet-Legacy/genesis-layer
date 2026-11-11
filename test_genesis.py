"""
test_genesis.py — P5 Genesis test suite
"""
import os
import sys
import tempfile
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../ledger-layer'))

import genesis

@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()

@pytest.fixture
def temp_ledger():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    # Empty the file so it counts as "new"
    open(path, 'w').close()
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_mint_genesis_valid(temp_ledger, key):
    record = {"data": "genesis"}
    entry = genesis.mint_genesis(temp_ledger, record, key)
    assert entry["seq"] == 0
    assert entry["prev"] == "0" * 64

def test_mint_genesis_refuses_non_empty(temp_ledger, key):
    genesis.mint_genesis(temp_ledger, {"data": "genesis"}, key)
    with pytest.raises(ValueError, match="Ledger already has entries"):
        genesis.mint_genesis(temp_ledger, {"data": "second"}, key)
