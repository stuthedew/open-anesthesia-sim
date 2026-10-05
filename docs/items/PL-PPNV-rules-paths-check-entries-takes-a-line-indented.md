---
id: PL-PPNV
title: rules_paths_check.entries takes a - line indented past its sequence's dash for a new glob, where YAML continues the item's plain scalar, so the check passes while the harness reads one glob that matches nothing; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/rules_paths_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's YAML slice, 2026-10-05
added: 2026-10-04
payoff: a rule whose paths: list YAML joins into one glob is refused by name, so the check can no longer report sound a scope the harness reads as matching nothing
verify: grep -q 'rules paths, an over-indented dash is refused by name' tests/unit/test_doc_check.py
---

**Problem.** rules_paths_check.entries takes a - line indented past its sequence's dash for a new glob, where YAML continues the item's plain scalar, so the check passes while the harness reads one glob that matches nothing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 7.3.3: a line indented past the sequence's `- ` column continues the item's plain scalar, even when it opens with `- `. `entries` reads `paths:` over `  - /src/**` and `    - /tests/**` as two globs, where PyYAML 6.0.3 and ruamel read one, `/src/** - /tests/**`, and `problems` returns nothing on a tree holding both directories - the silent "Nowhere" the module exists to catch. The same continuation without its dash raises `Unreadable`, as the function's contract says this form should. Latent: all ten `.claude/rules` front matters write `paths:` at column 0 with one quoted glob per line.

**Why it matters.** `tools/rules_paths_check.py` exists to catch a `paths:`
entry that loads its rule nowhere or too widely, two failures that are both
silent. An over-indented `- ` line reads to it as a second glob, which it
checks and passes, while YAML hands the harness one glob, `/src/** -
/tests/**`, or, after a quoted glob as every rule here writes one, a front
matter PyYAML refuses to parse. The check reports the scope sound on a rule
whose scope YAML reads as nothing the tree holds. One keystroke of indentation
produces it, and it reads as correct in review.

**Reproduced 2026-10-05, at triage.** On Python 3.11.15, against `main` at
`a341dcd0`: `entries` read `paths:` over `  - /src/**` and `    - /tests/**`
as `['/src/**', '/tests/**']`, and the same lines without the second dash
raised `Unreadable`. PyYAML 6.0.3 read the first as one glob, `/src/** -
/tests/**`; refused it where the first glob is quoted or a comment line stands
between the two (`while parsing a block collection`); and refused a dash
shallower than the list's (`while parsing a block mapping`), which `entries`
also reads as a glob of its own.

**Done when.** `entries` refuses by name a `- ` line under `paths:` at any
other indentation than the list's first item, rather than reading it as a glob
of its own, as it already refuses the same continuation without its dash; and
`CONTINUED_STATEMENTS` in `tests/unit/test_doc_check.py` gains `rules paths,
an over-indented dash is refused by name`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
