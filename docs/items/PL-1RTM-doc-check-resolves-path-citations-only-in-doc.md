---
id: PL-1RTM
title: doc_check resolves path citations only in DOC_GLOBS, so the queue - most of this project's prose - has its citations unchecked
priority: P2
effort: M
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md
added: 2026-09-15
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_path_citation_in_an_item_brief_is_resolved' tests/unit/test_doc_check.py
---

**Problem.** doc_check resolves path citations only in DOC_GLOBS, so the queue - most of this project's prose - has its citations unchecked

**Where.** `tools/doc_check.py:2323`, inside `check_citations`, is the only
call site of `_is_path_citation` - and `check_citations` is handed
`read_docs(root)`, which reads `DOC_GLOBS` alone. `_quoting_sources` already
reaches `docs/items/*.md` and every docstring, but only for
`check_quoted_sources`, which checks *quotations*.

**Found 2026-09-15** while measuring for `PL-MXSL` (the `.gitignore` exemption
for cited directories). The queue is where this project writes most of its
prose and most of its path references, and a citation that goes stale there is
exactly the kind an item's reader acts on.

**Not simply widening `DOC_GLOBS`**, which the comment at `_quoting_sources`
rules out for a stated reason: it would hand 687 item files to
`check_make_targets` and to `candidates`, neither of which wants them. The
shape to consider is passing the item files to `check_citations` only, the way
`_quoting_sources` already does for quotations.

**Worth measuring before building**: how many path citations the queue holds
and how many of them are already stale. A large stale count is a reason to
scope the check to newly-written items rather than to fail the whole store at
once.

**And one document overclaims because of it.** `docs/ARCHITECTURE.md:447`
describes `doc_check.py` as validating "citations - in the documentation, in
every `docs/items/` brief and in every source docstring, since those last two
are where this project writes most of them". That is true of the *quoted*
citations `check_quoted_sources` reads and false of the path citations
`check_citations` does not, and a reader has no way to tell the two apart from
the sentence. Fix the code rather than the sentence where the answer is to
widen the check; narrow the sentence only if the decision goes the other way.

**Why it matters.** `docs/items/` is where this project writes most of its prose
and most of its path references - 252 open items and several hundred closed
ones, each citing the files its work touches - and a citation that goes stale
there is exactly the kind a reader acts on. `PL-3GSZ` is a live instance from
the same week: `PL-5K5C` and `PL-T691` both point at `app/controller.py` for
`ControlInput` and `ControlChange`, which `PL-RD3B` moved to
`app/control_record.py`, and nothing reported it. Meanwhile
`docs/ARCHITECTURE.md:447` tells a reader the check already covers every
`docs/items/` brief, which is true of the *quoted* citations
`check_quoted_sources` reads and false of the *path* citations
`check_citations` does not - so the one document that would warn a reader off
relying on this instead assures them of it.

**Done when.** `check_citations` resolves path citations in `docs/items/*.md`,
by the route `_quoting_sources` already uses rather than by widening
`DOC_GLOBS` - the comment there rules that out for a stated reason, and it
would hand 687 item files to `check_make_targets` and to `candidates`, neither
of which wants them. The measurement the brief asks for is recorded here first:
how many path citations the queue holds and how many are already stale, since a
large stale count is the argument for scoping the check to newly-written items
rather than failing the whole store at once. `docs/ARCHITECTURE.md:447` is then
true of both halves of the check, and a test pins a stale path citation in an
item brief being caught.
