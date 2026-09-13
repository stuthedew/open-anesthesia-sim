---
id: PL-MS54
title: MODEL.md quotes mass-balance tolerance names that do not exist in the code
priority: P3
effort: S
status: done
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-08-30
closed: 2026-09-13
pr: 507
verify: grep -q 'AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L' docs/MODEL.md && ! grep -q 'MASS_BALANCE_ABSOLUTE_TOLERANCE' docs/MODEL.md
---

**Problem.** `docs/MODEL.md:502-503` presents a code block introduced as "The
release tolerance, as implemented in `core/agent_simulation_validation.py`",
naming `MASS_BALANCE_ABSOLUTE_TOLERANCE` and
`MASS_BALANCE_RELATIVE_TOLERANCE`. That module defines
`AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` and
`AGENT_ACCOUNTING_RELATIVE_TOLERANCE` (`:11-12`). The values quoted, 1e-12 L
and 1e-9, are correct; the identifiers are not.

**Why it matters.** The passage presents itself as a transcription of the
source — "as implemented in" — so a reader who greps for either name finds
nothing and cannot tell whether the constant was renamed, removed, or never
existed. The absolute tolerance also carries its unit in the real identifier
(`_L`) and loses it in the quoted one, which is the exact convention
`CLAUDE.md` requires for a quantity with a unit. `tools/doc_check.py` cannot
catch this: the names sit inside a fenced block rather than in a citation it
resolves.

**Where.** `docs/MODEL.md:502-503`;
`core/agent_simulation_validation.py:11-12`.

**Approach.** Correct the two names in the block, keeping the values. While
there, consider whether the block should also name `MINIMUM_RELATIVE_SCALE_L`
(`:13`), which is the 1e-15 L floor the prose beneath the block already
describes without naming.

**Scope note.** An instance of the class PL-036 describes; per that item's
Decided scope it is fixed here and cited there as evidence, not folded into it.

**Done when.** The quoted constant names in `docs/MODEL.md:502-503` match the
identifiers in `core/agent_simulation_validation.py`, units included.


**Closed 2026-09-13 with `PL-L7JB`, which is the same defect.** The block now
reads `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12`,
`AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9` and `MINIMUM_RELATIVE_SCALE_L =
1e-15`, with the prose beneath naming the scale floor rather than repeating its
value. This item's `verify:` command is what decided the direction between the
two: `PL-L7JB` left it open, and this one had already fixed it.
