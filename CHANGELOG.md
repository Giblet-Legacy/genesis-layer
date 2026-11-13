# CHANGELOG — genesis-layer (P5 Genesis)

CHANGELOG.md — build history for P5 Genesis, latest entry at top.

Function:
    Records the Good / Bad / Ugly of every build step for this layer.
    Updated at every sign-off. Format never changes shape, even when a
    section is empty.

## [Unreleased]

### Good

- `SPEC_V3.md`, `test_genesis_v3.py` (7 tests, run red first) and `genesis_v3.py`: the layer NOTES Q3 promised once P4 ledger_v2 froze (2.0.0, 2026-11-13). Mints via genesis_v2, confirms under ledger_v2, and adds `genesis_identity` / `verify_genesis`, the callable form of SPEC_V2 §3.2's root-ledger definition. 27/27 pass from the repo root and from the parent directory.
- Built on James's delegation ("fix all 11 issues"). Not frozen: VERSION stays 2.0.0 until James says freeze (NOTES Q4).

### Bad

- (none)

### Ugly

- genesis_identity catches RecursionError itself, because frozen ledger_v2 can raise it on a deeply nested line (P4 NOTES Q3).

## [v2.0.0] — 2026-11-12

### Good

- `SPEC_V2.md`: strict layer over P5 v1.0.0, written before any code.
- `test_genesis_v2.py`: 18 tests, written before genesis_v2.py and run
  red first. 20/20 pass (v1 2/2, v2 18/18) on the laptop (Windows,
  Python 3.13) — from the repo root and from the parent directory.
- `genesis_v2.py`: resolves NOTES D1–D5 (LF-only write, import from
  any CWD, type checks, file untouched on error, exclusive create,
  fsync). The entry is delegated to genesis.py, so v1 and v2 genesis
  entries are identical (tested). Its ledgers verify under P4 v1 and
  P4 ledger_v2 (tested).
- `conftest.py`: both suites now run from any working directory.
- `NOTES.md`: divergences D1–D7 recorded. Q1–Q3 raised and resolved
  with James: Q1 root/consumer definition decided (SPEC_V2 §3.2);
  Q2 freeze v2.0.0; Q3 move to ledger_v2 via genesis_v3 once P4
  v2.0.0 freezes.
- Header paragraph and numbered headers added to test_genesis.py
  (comments only); header paragraphs added to .gitattributes and
  .gitignore; `.pytest_cache/` ignored; `requirements.txt` added.
- README status corrected (it still said 0.0.0-dev after freeze).
- Missing `[v0.0.0-dev]` heading restored below (it was dropped when
  v1.0.0 was added, merging the scaffold entry into v1.0.0).
- genesis.py untouched (Immutable Rule).

### Bad

- genesis.py v1.0.0 writes CRLF on Windows (via P4 v1), so a genesis
  minted on the laptop is rejected by P4 ledger_v2 (NOTES D1). It
  only imports from the repo root (D2) and accepts a non-dict record
  (D3). Shipped in v1.0.0 because the two v1 tests never covered them.
- Frozen on the laptop run alone; the S24 run of the v2 suite is
  still to be confirmed.

### Ugly

- Genesis ledgers already minted by v1 on the laptop have a CRLF line
  ending and fail P4 ledger_v2 until converted to LF (P4 NOTES D1).
- P5 still depends on P4 v1 (CRLF on Windows), with an LF rewrite
  on top, because P4 v2.0.0 is not frozen yet (NOTES Q3).

## [v1.0.0] — 2026-11-11

### Good

- `genesis.py` implemented to SPEC v1.0.0.
- 2/2 pytest tests pass.
- Enforces the Genesis rule: refuses to mint into a non-empty ledger.

### Bad

- (none)

### Ugly

- (none)

## [v0.0.0-dev] — scaffold

### Good

- Repository scaffolded: `Giblet-Legacy/genesis-layer` created for P5.
- Depends on P4 Ledger v1.0.0.

### Bad

- (none)

### Ugly

- (none)
