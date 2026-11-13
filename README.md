# genesis-layer — P5 Genesis

README.md — repository purpose and layer contract for P5 Genesis.

Function:
    This repository implements primitive layer P5 of the Forge Stack:
    minting a ledger's first immutable batch. It consumes P4 Ledger
    for the underlying ChronoSCRIBE append primitives.

Layer:    P5 — Genesis
Depends:  P4 Ledger v1.0.0 (ledger.py), checked out as the sibling
          directory `../ledger-layer`, which in turn needs P1
          Envelope v2 at `../envelope-layer`
Consumed: P6 Canon Verify
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   2.0.0 frozen (genesis_v2.py, SPEC_V2.md), a strict layer
          over 1.0.0 (genesis.py, SPEC.md), also frozen.

genesis_v3.py (SPEC_V3.md) is built over genesis_v2 and P4 ledger_v2,
not yet frozen (NOTES.md Q4). New code imports `genesis_v3`.

Tests: `python -m pytest` (needs `cryptography` and `pytest`). Runs
from the repo root or any other directory.
