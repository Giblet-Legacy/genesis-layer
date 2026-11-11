"""
genesis.py — P5 Genesis primitive layer

Function:
    Implements the Genesis rule: only the root ledger mints a genesis
    batch. Delegates to P4's append_entry.

Public API:
    1. mint_genesis — Mints the first entry (seq 0, prev 0*64).

Layer:    P5 — Genesis
Depends:  P4 Ledger (ledger.py)
Consumed: P6 Canon Verify
Version:  1.0.0 (on freeze; 0.0.0-dev until then)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

sys.path.insert(0, os.path.abspath('../ledger-layer'))
import ledger

# ---------------------------------------------------------------------------
# 1. mint_genesis
#    Refuses non-empty ledgers. Otherwise, delegates to P4.
# ---------------------------------------------------------------------------
def mint_genesis(ledger_path, record, private_key):
    if os.path.exists(ledger_path) and os.path.getsize(ledger_path) > 0:
        raise ValueError("Ledger already has entries — genesis refused")
        
    entry = ledger.append_entry(ledger_path, record, private_key)
    
    if entry.get("seq") != 0 or entry.get("prev") != "0" * 64:
        raise RuntimeError("append_entry did not produce a genesis entry")
        
    return entry
