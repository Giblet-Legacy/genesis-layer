# SPEC V3 — genesis-layer (P5 Genesis, ledger_v2 layer)

SPEC_V3.md — specification for genesis_v3.py, the layer above P5 v2.0.0.

Function:
    Specifies genesis_v3.py, the layer promised by NOTES.md Q3: once
    P4 ledger_v2 froze (2.0.0, 2026-11-13), P5 gains a layer that
    depends on it. genesis_v3 mints exactly as genesis_v2 does, then
    confirms the result under ledger_v2, and adds the root-ledger
    check that SPEC_V2.md §3.2 defined but no function exposed.

    SPEC_V2.md 2.0.0 remains authoritative for everything this
    document does not change.

Layer:     P5 — Genesis, v3
Depends:   genesis_v2.py (P5 v2.0.0), ledger_v2.py (P4 v2.0.0)
Consumed:  The Cockpit (`forge health`, P5 probe), The Legacy
Version:   SPEC V3 3.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Compatibility guarantee

- mint_genesis writes the same bytes and returns the same entry as
  genesis_v2.mint_genesis for every input genesis_v2 accepts.
- Every ledger genesis_v2 mints is a root ledger under §3.

## 2. mint_genesis(ledger_path, record, private_key) -> dict

1. Delegate to genesis_v2.mint_genesis. Its errors (TypeError,
   ValueError, the v1 "already has entries" text) pass through
   unchanged, with the file untouched.
2. Confirm `ledger_v2.verify_ledger(ledger_path, public_key)` is True
   for the key's public half. If not, raise RuntimeError. This cannot
   happen for a correct genesis_v2; it is a tripwire, not a path.
3. Return the entry.

## 3. Root ledgers (SPEC_V2.md §3.2, made callable)

A **root ledger** is a ledger that ledger_v2 verifies under the given
public key and whose first line has `seq == 0` and `prev == "0"*64`.
Its identity is the pair (genesis `hash`, genesis `signer`).

### 3.1 genesis_identity(ledger_path, public_key) -> dict | None

- Returns `{"hash": <genesis hash>, "signer": <did:key>}` for a root
  ledger, else None.
- Never raises for file content: a missing, empty, CRLF, tampered or
  foreign-signed ledger returns None.
- Raises TypeError if public_key is not an Ed25519PublicKey (stack
  convention: a wrong key type is a caller bug).

### 3.2 verify_genesis(ledger_path, public_key) -> bool

`genesis_identity(...) is not None`.

## 4. Public API

1. mint_genesis      — v2, then a ledger_v2 confirmation
2. genesis_identity  — root identity pair, or None
3. verify_genesis    — bool form of 2

## 5. Tests (test_genesis_v3.py)

- Public API: three names, all callable.
- mint_genesis returns the same entry as genesis_v2 and writes the
  same bytes.
- genesis_identity on a fresh v3 genesis returns its hash and signer.
- verify_genesis False for: missing file, empty file, tampered line,
  wrong key, CRLF line ending, a second genesis-shaped chain signed
  by another key.
- verify_genesis still True after further ledger_v2 appends.
- genesis_identity raises TypeError for a private key or None.
- Errors from genesis_v2 pass through (non-empty ledger refused).

---

## Document control

- **SPEC V3 3.0.0** — decided 2026-11-13 by the VS Code AI on James's
  delegation ("fix all 11 issues"), resolving NOTES.md Q3's follow-up.
