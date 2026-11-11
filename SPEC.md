# SPEC — genesis-layer (P5 Genesis)

SPEC.md — the complete layer specification for P5 Genesis.

Function:
    This document is the authoritative specification for primitive
    layer P5 of the Forge Stack. It enforces the Genesis rule.

Layer:     P5 — Genesis
Depends:   P4 Ledger (ledger.py)
Consumed:  P6 Canon Verify
Version:   SPEC 1.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

## 1. The Genesis Rule

Only the root ledger mints a genesis batch. A genesis batch is an
entry with seq=0 and prev="0"*64. Consumer ledgers must anchor to
the root's head, not create their own genesis.

## 2. Function Contracts

### 2.1 mint_genesis(ledger_path: str, record: dict, private_key) -> dict
- Input: Path to a ledger file, a record, an Ed25519 private key.
- Output: The genesis entry (seq 0, prev 0*64).
- Raises: ValueError if the ledger already has entries.
- Purity: Impure (file I/O).
