# Forge Stack Context — P5 Genesis

CLAUDE.md — Context briefing for AI assistants working in this repository.

Function:
    Instructs the AI assistant on the strict architectural rules of the
    Forge Stack. Do not hallucinate external frameworks. Reason strictly
    within these boundaries.

## The Immutable Rule
Never rewrite a primitive. Add a layer.
If `genesis.py` needs a change, we do NOT edit it. We create a v2 layer above it.

## Dual-Device Workflow
We build on an S24 (Termux) and a laptop (VS Code). State is confirmed, never assumed. Always use LF line endings. Commit messages must be clear. We use the Good/Bad/Ugly CHANGELOG format (latest at top).

## Header Discipline
Every file MUST have a top header paragraph explaining its function.
Every function MUST have a numbered header.

## P5 Architecture Specifics
- genesis.py depends on `ledger` (P4 v1.0.0); genesis_v2 is frozen over it.
- genesis_v3.py (SPEC_V3.md, frozen 3.0.0) depends on genesis_v2 and `ledger_v2` (P4 v2.0.0). New code imports `genesis_v3`.
- Implements the Genesis rule: only the root ledger mints a genesis batch.
- Must refuse to run against a non-empty ledger.
