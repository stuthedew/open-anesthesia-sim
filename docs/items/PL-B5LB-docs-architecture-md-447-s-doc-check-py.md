---
id: PL-B5LB
title: docs/ARCHITECTURE.md:447's doc_check.py inventory and CONTRIBUTING.md:52's summary both describe the tool as validating documentation, but check_coverage_gate and check_ruff_cache hold the Makefile's own invocations, so the authoritative description of what the tool does is narrower than the tool
priority: P3
effort: S
status: ready
classes: docs
feature: doc-consistency-checks
touches: docs/ARCHITECTURE.md, CONTRIBUTING.md
added: 2026-09-15
verify: grep -q "the Makefile's own invocations" docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md:447's doc_check.py inventory and CONTRIBUTING.md:52's summary both describe the tool as validating documentation, but check_coverage_gate and check_ruff_cache hold the Makefile's own invocations, so the authoritative description of what the tool does is narrower than the tool

**Why it matters.** `docs/ARCHITECTURE.md:447` is the package map's own
description of what `tools/doc_check.py` is for, and `tools/doc_check.py` is the
tool that holds that map to the tree - so the one line nothing checks is the
line describing the checker. Both statements now understate it: the tool also
holds `make check`'s coverage invocation against CI's (`check_coverage_gate`,
`PL-D3M2`) and every `ruff check` recipe line against `--no-cache`
(`check_ruff_cache`, `PL-QSJM`), neither of which is documentation validation.

The cost is misrouting rather than falsehood. A session looking for where a
Makefile-invariant check should live reads "validates documentation", concludes
this is not the place, and builds a second tool beside it - which is how one
question ends up with two answers that can disagree. `CONTRIBUTING.md:52` says
the same thing to a contributor, who then reads a `doc_check` failure about a
ruff flag as a documentation problem.

**Done when.** Both lines describe the tool's two halves - the documentation it
holds to the tree, and the gate invocations it holds to each other - in a form
that does not need re-editing for the next check of either kind, and
`python3 tools/doc_check.py check` still passes.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Unchanged one-off: describe the tool without enumerating what the tree
enumerates. That is the same move `PL-GTSL` makes from the other side - the
enumeration is bound, the description is not.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** Both descriptions still omit the
two Makefile-invariant checks: `check_coverage_gate` at `tools/doc_check.py:3041`
("Hold the Makefile's coverage run and CI's to the same command") and
`check_ruff_cache` at `:3117`, neither of which is documentation validation, and
`grep -n 'coverage_gate\|ruff cache\|--no-cache' docs/ARCHITECTURE.md` returns
nothing. Both cited lines have drifted: `docs/ARCHITECTURE.md:447` is now
`:505`, and `CONTRIBUTING.md:52` is now `:53`.
