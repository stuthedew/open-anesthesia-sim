---
id: PL-7922
title: The fixture-id guard reaches subprojects/docket/tests only, so the apparatus fixtures under tests/unit are held to no id grammar at all
priority: P2
effort: M
status: done
feature: one-id-grammar
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py, subprojects/docket/tests/test_store.py, Makefile, .github/workflows/quality.yml, tests/unit/test_tools_portability.py, tests/unit/test_contrast_check.py, tests/unit/test_doc_check.py, tests/unit/test_generator_check.py, tests/unit/test_item_read_log.py, tests/unit/test_workflow_paths_check.py, .claude/rules/citation-drift.md, .claude/skills/docket/modes/ideas.md
added: 2026-09-21
closed: 2026-09-21
payoff: an unmintable PL- literal cannot reach any apparatus tree or any .claude document without make check naming the file and line
verify: uv run python tools/fixture_id_check.py
---

**Problem.** The fixture-id guard reaches subprojects/docket/tests only, so the apparatus fixtures under tests/unit are held to no id grammar at all

**Two instances, measured 2026-09-21 while doing `PL-DPY6`.**

- `tests/unit/test_generator_check.py` carried `PL-AAAA` as a fixture id in 20
  places - the file asserting the advisory's behaviour reproducing the defect it
  asserts about. `PL-DPY6` renamed them to `PL-8888`, so the instance is gone
  and the gap that let it stand is not.
- The gap is wider than `tests/unit`. Nothing scans `tools/` or `.claude/`
  either, which is how `tools/generator_check.py` printed `PL-AAAA` as the
  example to copy (`PL-DPY6`) and how `PL-A1B2` still stands in two `.claude/`
  files (`PL-3BZS`).

**Worth deciding when this is worked:** whether the guard moves out of
`subprojects/docket/tests/test_store.py` into a `tools/` check wired into
`make check`, which is the only tier that reaches `.claude/` and `tools/` as
well as both test trees. The AST walk it uses reads Python only, so a markdown
scanner is a second mechanism rather than a wider glob - and `citation-drift.md`
and `modes/ideas.md` are markdown. The recommendation is the `tools/` check over
a wider glob: same code, three more trees, one tier.

**Why it matters.** `read_items` takes the `id` field verbatim, so an id outside
`store.ID_ALPHABET` parses and behaves like any other fixture right up to the
moment it reaches something that applies `ID_PATTERN` - and then it matches
nothing at all. A test asserting that an id is absent from a listing, excluded
from a pick, or unrecognised in prose then passes against a broken
implementation as readily as a correct one. `PL-GXPP` is what that costs once it
has spread: 261 substitutions across 9 test files, after `test_roadmap.py` spent
seventeen days asserting a placement rule while naming an id the parser could
never have placed. The same literal reached `tools/generator_check.py`'s printed
advisory (`PL-DPY6`) and `.claude/rules/citation-drift.md`'s documented
placeholder set (`PL-3BZS`), because an example is copied.

**Done when.** One mechanism refuses an unmintable `PL-` literal everywhere the
project can carry one, and `make check` names the file and the line.

**Decided while working it, 2026-09-21.**

- **A `tools/` check, not a wider glob on the pytest guard.** Every repo-wide
  grammar or structure guard here is already a `tools/` script -
  `branch_id_check.py`, `rules_paths_check.py`, `workflow_paths_check.py`,
  `core_vocabulary_check.py`, `glyph_check.py`, `agent_identity_check.py`,
  `import_boundary_check.py` - with its own `tests/unit/test_*.py`. A pytest
  test could reach the same trees, so the deciding argument is consistency with
  that established group and a purpose-built failure message, not reach.
- **The pytest guard is removed rather than kept beside it.** Two spellings of
  one grammar drift, which is the hazard `store.ID_PATTERN` is exported
  unanchored to avoid. What it gives up: an extracted `subprojects/docket/`
  would carry no fixture-id guard of its own until it took a copy.
- **The markdown half is built, scoped to `.claude/` and to nothing else.**
  Measured 2026-09-21: every `PL-` token under `.claude/` that fails the grammar
  is a defect - 2 of 2, both `PL-A1B2`, both `PL-3BZS`'s - so the rule is exact
  there and needs no judgment. Under `docs/` it is the reverse: prose *about*
  malformed ids is the norm (`PL-GXPP`'s brief alone names 17), so `docs/`,
  `ROADMAP.md` and the item store stay out of scope. `PL-3BZS` closes with this
  item, because a hand-fix its "Done when" would accept is exactly what this
  item exists to stop recurring.
- **Two corrections to the walk being moved.** The candidate pattern grows a
  `(?<![A-Za-z0-9])` lookbehind, so `GPL-3.0` and `LGPL-2.1` stop reading as
  `PL-3` and `PL-2` - latent in Python today, live the moment the markdown scan
  runs, and `docs/ARCHITECTURE.md` carries three. And the `not-an-id` marker is
  looked for across a literal's whole `lineno..end_lineno` span rather than its
  first line only, because the parser folds implicitly concatenated strings into
  one node reported at the opening line - `tests/unit/test_workflow_paths_check.py`
  has two, where the marker could not have been placed where it was read.
