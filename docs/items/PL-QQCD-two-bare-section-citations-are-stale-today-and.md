---
id: PL-QQCD
title: Two bare section citations are stale today and nothing checks a bare citation: ROADMAP.md cites a Current baseline v0.4.26 heading that is now v0.5.10, and docs/MODEL.md cites Published wash-in validation test, now Published wash-in and elimination validation test
status: untriaged
feature: exact-gates
touches: ROADMAP.md, docs/MODEL.md
added: 2026-09-25
---

**Problem.** Two bare section citations are stale today and nothing checks a bare citation: ROADMAP.md cites a Current baseline v0.4.26 heading that is now v0.5.10, and docs/MODEL.md cites Published wash-in validation test, now Published wash-in and elimination validation test

`ROADMAP.md:1960` cites § "Current baseline: v0.4.26"; the heading is now v0.5.10 and the cited subsection exists nowhere. `docs/MODEL.md:2333` cites § "Published wash-in validation test"; the heading is now "Published wash-in and elimination validation test". doc_check checks a quoted heading only after see/under or before above/below, so a bare `§ "X"` with no document named is read by nothing - 264 such citations across documents (182) and live items (82).

**Why it matters.** A reader of `docs/MODEL.md`, the simulator's authoritative specification, following a citation lands nowhere. Small, but it is the authoritative document, and the class is unchecked.

**Done when.** Both citations name headings that exist; the check that makes bare `§` citations checked is the `exact-gates` head's work, not this item's.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
