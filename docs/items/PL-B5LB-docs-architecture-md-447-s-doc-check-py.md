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
