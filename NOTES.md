# NOTES — genesis-layer (P5 Genesis)

NOTES.md — open questions, divergences and decisions for P5 Genesis.

## Decisions
- Genesis simply wraps ledger.append_entry and asserts seq == 0.
- Refuses non-empty ledgers via ValueError.
