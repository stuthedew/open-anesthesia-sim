---
id: PL-39K7
title: Nothing in the auto-loaded surface points a session at docs/ARCHITECTURE.md's "Where new code belongs"
status: untriaged
added: 2026-09-13
---

**Problem.** Nothing in the auto-loaded surface points a session at docs/ARCHITECTURE.md's "Where new code belongs"

**Notes.** `grep -rn "ARCHITECTURE"` over `CLAUDE.md`, `.claude/rules/*.md`,
`.claude/skills/docket/SKILL.md`, `docs/worker.md` and `AGENTS.md` returns
nothing. `README.md`:143 and `CONTRIBUTING.md`:64 do point at it, and neither is
auto-loaded, so a human contributor is routed to it and a session is not. What
the session is missing is § "Where new code belongs" (line 713), which answers
per pattern the question asked before writing new code, and § "Tests (`tests/`)"
(line 697), which says which of the three trees a new test belongs in and why a
`tests/reference/` case must not reach a solver in `core/`.

The exemplar technique is already established here, just not at this pattern:
`.claude/rules/sources-and-docstrings.md` names
`AlveolarCompartment.set_alveolar_ventilation` as "the shape" and
`core/supported_ranges.py` as the worked example against `core/validation.py` as
the contrast, and `.claude/rules/ui-reader.md` names `_mac_reference_text` as the
in-source pattern. `.claude/rules/core-domain.md` fires on exactly the path where
a new compartment is written and names no instance at all, which is the sharper
half of this finding.

`PL-007` is the precedent worth copying rather than restating: it put the
rationale on `_StrictPayload` and added
`test_every_payload_model_documents_why_it_exists`, which walks
`__subclasses__()` and fails on a payload with no docstring while deliberately
not checking what the docstring says. `PL-FZ6T` (blocked on `PL-H46J`, which
merged as #519) is adjacent and may subsume part of this.

**Where.** `.claude/rules/core-domain.md` (`paths: /src/anesthesia_sim/core/**`)
and `.claude/rules/ui-reader.md` (`paths: /src/anesthesia_sim/app/**`), or one
new path-scoped rule — disposition 3, not resident prose. `tools/doc_check.py`'s
citation check already guards a cited path from rot.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository.
