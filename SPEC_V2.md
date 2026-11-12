# SPEC V2 — genesis-layer (P5 Genesis, strict layer)

SPEC_V2.md — specification for genesis_v2.py, the layer above P5 v1.0.0.

Function:
    Specifies genesis_v2.py, a strict layer over the frozen P5 v1.0.0
    primitive (genesis.py). It closes the divergences D1–D5 recorded
    in NOTES.md without editing genesis.py (Immutable Rule).

    SPEC.md v1.0.0 remains authoritative for everything this document
    does not change. Where this document is silent, SPEC.md v1.0.0
    applies unchanged.

Layer:     P5 — Genesis, v2 (strict)
Depends:   genesis.py (P5 v1.0.0), ledger.py (P4 v1.0.0)
Consumed:  P6 Canon Verify — new code imports genesis_v2, not genesis
Version:   SPEC V2 2.0.0 (frozen 2026-11-12)
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Compatibility guarantee

- **Entries.** For the same record and key, genesis_v2 returns the
  same genesis entry as genesis.py v1.0.0: the same seq, prev, record,
  signer, hash and signature (Ed25519 is deterministic). v2 obtains
  the entry by calling v1's mint_genesis, so this holds by
  construction.
- **Ledgers.** The file v2 writes verifies under P4
  ledger.verify_ledger (v1) and ledger_v2.verify_ledger (v2).

v2 differs from v1 only by **rejecting** inputs that v1 accepted or
crashed on, and by the bytes of the line ending. That is why the
major version is 2.

## 2. On-disk form (resolves D1)

The genesis ledger file is exactly

    json.dumps(entry, separators=(",", ":")).encode("ascii") + b"\n"

— one LF-terminated compact line, the P4 SPEC_V2 §2 form. No `\r`
byte is ever written, on any device.

## 3. Function contract

### 3.1 mint_genesis(ledger_path, record, private_key) -> dict (resolves D3–D5)

- Raises TypeError if private_key is not an Ed25519PrivateKey.
- Raises TypeError if record is not a dict.
- Raises ValueError if record contains NaN or ±Infinity (P1 v2).
- Raises TypeError if record is not plain JSON, i.e. if the written
  line would not read back equal to the returned entry (non-str keys,
  tuples).
- Raises ValueError with a message beginning "Ledger already has
  entries" if the file exists and is non-empty (SPEC.md §2.1, same
  text as v1).
- A missing file is created with exclusive create; if it appears in
  the meantime, ValueError as above. An existing 0-byte file is
  re-checked for size on the open handle immediately before writing.
- On any error the file is unchanged (and not created, if it was
  missing).
- Otherwise it writes the §2 line, flushes and fsyncs, and returns the
  entry: seq 0, prev "0"*64.

Concurrent writers are out of scope beyond the checks above: one
process mints a given ledger.

### 3.2 Root and consumer ledgers (resolves NOTES.md Q1)

- A **root ledger** is a ledger whose seq-0 entry has
  `prev = "0"*64` — a genesis entry. Its identity is the pair
  (genesis `hash`, genesis `signer`).
- mint_genesis is the only way a genesis entry is created, and it
  only writes into an empty ledger (§3.1). Minting a genesis therefore
  *is* creating a root ledger; P5 keeps no registry of roots.
- A **consumer ledger** never begins with a genesis entry. Its first
  entry anchors to a root's head hash. That anchor is defined and
  checked by the consuming layers (P6 Canon Verify onward), not P5.

## 4. Import path (resolves D2)

genesis_v2 finds P4 at the `ledger-layer` directory and P1 at the
`envelope-layer` directory that are siblings of this repository's
directory, resolved from the location of genesis_v2.py, not from the
current working directory.

## 5. Tests

test_genesis_v2.py is the executable form of §1–§4. It is written
before genesis_v2.py and run red first.
