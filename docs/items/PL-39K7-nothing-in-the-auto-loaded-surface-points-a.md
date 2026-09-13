---
id: PL-39K7
title: Nothing in the auto-loaded surface points a session at docs/ARCHITECTURE.md's "Where new code belongs"
priority: P2
effort: S
status: done
classes: docs, session-cost
feature: documentation-standard
touches: .claude/rules/where-new-code-goes.md, .claude/rules/core-domain.md
added: 2026-09-13
closed: 2026-09-13
verify: python3 tools/rules_paths_check.py && grep -q 'Where new code belongs' .claude/rules/where-new-code-goes.md && grep -q 'core/tissue.py' .claude/rules/core-domain.md
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


**Closed 2026-09-13.** Two carriers, both path-scoped, so resident context is
unchanged at 49,802 characters — confirmed against `origin/main` by
`tools/doc_check.py`'s own report.

`.claude/rules/where-new-code-goes.md` is new, scoped to `/src/**` and
`/tests/**`, and does one thing: sends a session to `docs/ARCHITECTURE.md`
§ "Where new code belongs" and § "Tests (`tests/`)" and says to read one existing
instance end-to-end before writing a new one. It deliberately restates neither
section — a rule that paraphrases the document it cites goes stale while still
reading as current, and the map is already held to the tree in both directions by
`tools/doc_check.py`. It also names where the per-pattern instances live rather
than listing them, and says that an unnamed pattern means the codebase is silent
and that the silence is worth capturing rather than guessing past.

`.claude/rules/core-domain.md` gains the sharper half: `core/tissue.py` named as
the compartment to read end-to-end, with what makes it the fullest instance —
`TissueGroupState` saying why each parameter is excluded, `__post_init__` refusing
every field through `core/validation.py`'s named guards, properties carrying the
equation and citing the `docs/MODEL.md` section that defines it, and an
`advance()` separating this compartment's closed form from how a run steps. Its
`time_constant_s` is called out as the illustration of that file's own bar: a
property the step does not read, kept because it is the form a reader of the
specification is looking for.

**Scope held deliberately.** `ui-reader.md` was named as a candidate carrier in
the proposal and did not get the pointer: it governs what a clinician reading the
screen already knows, and structural routing bolted onto it would have been the
second copy this item exists to avoid. `/src/**` covers `app/` anyway.

**Found** reviewing an outside article on long AI projects against this
repository; its "point at a canonical instance from the instruction file" claim
was the half that landed. `PL-VV16`, in flight, adds the read-side instrumentation
that would answer whether this citation edge is ever actually traversed.
