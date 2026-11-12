# NOTES — genesis-layer (P5 Genesis)

NOTES.md — open questions, divergences and decisions for P5 Genesis.

Function:
    Records open questions and divergences between genesis.py v1.0.0
    and SPEC.md v1.0.0 / the Forge Stack rules. genesis.py is never
    edited (Immutable Rule), so a fix means a layer above P5 —
    genesis_v2.py, specified first in SPEC_V2.md.

## Open questions

- (none)

## Resolved questions

- **Q1 — What makes a ledger "the root"?** SPEC §1 says only the root
  ledger mints a genesis batch, but no spec defined "root". Raised
  2026-11-12. **Resolved 2026-11-12 — James delegated the decision;
  decided by the VS Code AI:**
  - A ledger is a **root ledger** if and only if its seq-0 entry has
    `prev = "0"*64`, i.e. it begins with a genesis entry. Its identity
    is the pair (genesis `hash`, genesis `signer`).
  - Minting a genesis *is* creating a root. P5 is the only layer that
    mints one, and only into an empty ledger (SPEC §2.1). P5 needs no
    registry and enforces nothing beyond that.
  - A **consumer ledger** never begins with a genesis entry: its first
    entry anchors to a root's head hash. Defining and checking that
    anchor is the job of the consuming layer (P6 Canon Verify and
    later), not P5.
  - Recorded as SPEC_V2.md §3.2. No code change: v1 and v2 already
    behave this way.
- **Q2 — Freeze v2.0.0?** Raised 2026-11-12. **Resolved 2026-11-12 —
  James: "yes".** Frozen at 20/20 on the laptop (Windows, Python
  3.13). The S24 run is still to be confirmed after the freeze.
- **Q3 — Move to ledger_v2 once P4 v2 freezes?** genesis_v2 depends
  only on frozen code (genesis.py v1.0.0 → ledger.py v1.0.0), as
  CLAUDE.md requires, and writes the P4 SPEC_V2 §2 line form so
  ledger_v2 accepts its ledgers (tested). Raised 2026-11-12.
  **Resolved 2026-11-12 — James: "yes".** P4 v2.0.0 was not frozen at
  that date (P4 NOTES Q1), so nothing changes yet. When P4 v2.0.0
  freezes, P5 adds a genesis_v3 layer that depends on ledger_v2
  (genesis_v2 is frozen and is not edited — Immutable Rule).

## Divergences — genesis.py v1.0.0 (all resolved in SPEC_V2 / genesis_v2)

- **D1 — CRLF on Windows.** genesis.py delegates the write to P4 v1
  ledger.append_entry, which writes in text mode. On the laptop the
  genesis line ends `\r\n`; on the S24 `\n`. Confirmed 2026-11-12: a
  genesis minted on the laptop verifies under ledger.verify_ledger
  but is **rejected by ledger_v2.verify_ledger** (P4 NOTES D1). v2
  writes LF only, in binary mode.
- **D2 — CWD-relative import.** genesis.py adds `../ledger-layer`
  relative to the *working directory*, and test_genesis.py adds
  `../envelope-layer` and `../ledger-layer` the same way. Confirmed
  2026-11-12: `python -m pytest genesis-layer` from the parent
  directory fails with `ModuleNotFoundError: No module named
  'ledger'`. genesis_v2.py and conftest.py resolve both siblings from
  their own file location.
- **D3 — No type checks.** SPEC §2.1 says record is a dict and the key
  is Ed25519. Confirmed 2026-11-12: v1 mints a genesis with
  `record="str"`, and raises AttributeError (not TypeError) on a
  non-key. v2 raises TypeError for both, before any file is touched.
- **D4 — Check-then-write race.** v1 checks the file is empty, then
  appends. A second writer between the two produces a ledger with two
  genesis-looking attempts; v1's post-write RuntimeError check fires
  only *after* the bad line is already on disk. v2 builds the entry
  in a private temp file, creates a missing ledger with exclusive
  create (`xb`), and re-checks the size on the open handle before it
  writes. Full concurrent-writer safety stays out of scope, as P4
  SPEC_V2 §3.2.
- **D5 — No fsync.** v1 returns before the genesis line is durable.
  v2 flushes and fsyncs.
- **D6 — Stale header.** genesis.py's header still reads
  "Version: 1.0.0 (on freeze; 0.0.0-dev until then)". Cosmetic; left
  as is (Immutable Rule).
- **D7 — test_genesis.py header.** It had no Function paragraph and no
  numbered function headers (Header Discipline). Fixed with comments
  only; no test logic changed.

## Divergences from the v1.2.1 stack document

- (none)

## Decisions

- Genesis simply wraps ledger.append_entry and asserts seq == 0.
- Refuses non-empty ledgers via ValueError.
- An existing but empty (0-byte) file counts as a new ledger, in v1
  and v2. A file holding anything at all — even a lone newline — is
  refused. v2 keeps v1's error text so callers matching on it work.
- genesis_v2 never builds an entry itself: it calls v1 mint_genesis on
  a private temp file and writes v1's entry, so v1 and v2 genesis
  entries are identical by construction — the same pattern as
  ledger_v2 over ledger and envelope_v2 over envelope.
