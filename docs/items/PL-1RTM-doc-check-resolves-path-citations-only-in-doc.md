---
id: PL-1RTM
title: doc_check resolves path citations only in DOC_GLOBS, so the queue - most of this project's prose - has its citations unchecked
priority: P2
effort: M
status: done
classes: defect, infra
feature: doc-consistency-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md, .claude/rules/citation-drift.md, docs/items/PL-5B1N-simulated-traces-should-be-solid-and-a-dotted.md, docs/items/PL-5N7T-nothing-checks-a-prose-enumeration-of-quality.md, docs/items/PL-CNCF-controller-drawn-window-costs-6-2-ms-a-frame-at.md, docs/items/PL-DBGT-desflurane-json-points-at-the-five-other.md, docs/items/PL-H2K2-nothing-signals-a-run-approaching-the-supported.md, docs/items/PL-MBP6-the-readme-has-no-image-of-the-interface-which.md, docs/items/PL-PGZF-pl-gs3r-made-the-chart-s-column-budget-follow.md, docs/items/PL-S5YM-doc-check-s-covered-directory-branch-now-has-no.md, docs/items/PL-W4M9-write-the-flet-interface-s-parity-inventory-the.md, docs/items/PL-X5L4-app-chart-series-py-s-wash-in-docstrings-still.md
blocked-by: PL-H0CF
added: 2026-09-15
closed: 2026-10-03
pr: 1300
verify: grep -q 'def test_a_path_citation_in_an_item_brief_is_resolved' tests/unit/test_doc_check.py && uv run pytest tests/unit/test_doc_check.py
recurrences: 2026-09-25 PL-HJ8G
---

**Problem.** doc_check resolves path citations only in DOC_GLOBS, so the queue - most of this project's prose - has its citations unchecked

[superseded 2026-10-03] **Blocked by `PL-H0CF`** (doc_check resolves an absolute-path citation against
the container filesystem), added 2026-09-21 at triage. `PL-H0CF` measured the
queue and found 22 open and closed briefs carrying 14 distinct absolute tokens
that `_is_path_citation` already accepts. Handing the item files to
`check_citations` admits all 22 at once: the repo-anchored spellings
(`/docs/worker.md`, `/subprojects/docket/uv.lock`) as false errors on files
that exist, and the container paths (`/root/.ccr/README.md`) as verdicts that
differ between root and the CI runner on one commit. So the absolute-token
reading has to be settled first, or this item's first run is 22 wrong answers.

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

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** The mechanism is unchanged -
`check_citations` is still handed `read_docs(root)`, which iterates `DOC_GLOBS`
(`tools/doc_check.py:141-149`), and `docs/items/` is not in it, while
`_quoting_sources` at `:2812` already reaches those files for
`check_quoted_sources` alone. Three numbers moved: the comment at `:2807` says
widening would hand over "687 item files" and the tree holds **1258**; the
brief's "252 open items" is **317**; and `docs/ARCHITECTURE.md:447` is now
`:505`. The measurement the brief asks for - how many path citations the queue
holds, and how many are stale - has still not been taken.

**A slice of that measurement was taken 2026-09-21, under `PL-D1NT`, and it
names a prerequisite: `PL-H0CF`.** Counting only the tokens beginning `/`,
`CODE_SPAN_RE` plus `_is_path_citation` over `docs/items/*.md` returns **22
briefs carrying 14 distinct absolute tokens**. They are not one class:

- container paths (`/root/.ccr/README.md` in 3 briefs, `/opt/pw-browsers/...`,
  `/usr/lib/x86_64-linux-gnu/`) resolve against the machine, so root and the
  CI runner disagree about the same line;
- repo-anchored spellings (`/docs/worker.md` in 2, `/README.md`,
  `/subprojects/docket/uv.lock`, `/out/`) - the form `.claude/rules/*.md` uses
  in its `paths:` frontmatter - resolve against the filesystem root, so a file
  that *is* there would be reported dangling;
- a bare `/`, in 12 briefs, is accepted by `_is_path_citation` because it ends
  in a slash, and always resolves.

So widening the check to the queue admits all 22 at once, and roughly half
would be false errors on files that exist. `PL-H0CF` is that resolver defect,
and landing it first is what makes this widening's output trustworthy; it also
owes these briefs the escape `check_line_citations` already has, since an item
reporting a bad citation has to be able to show it. The rest of the
measurement this brief asks for - relative path citations in the queue, and
how many are stale - is still untaken.

**Built 2026-10-03, in #1300, after `PL-H0CF`; the measurement first.** Live
briefs held 1,843 path citations, 95 resolving to nothing and 2 more covered by
`.gitignore`; closed briefs held 12,237 with 459 unresolved, and stay exempt
under `.claude/rules/citation-drift.md`. Of the 95: 11 named a path the citing
item's own `touches` declares, 12 were absolute tokens, and 22 named a path git
history shows the tree once held. Read one by one, 5 of those 22 were drift -
two Done-when lines naming the Flet view's test module the Qt port removed
(`PL-5B1N`, `PL-H2K2`), `PL-CNCF`'s `touches` as they stood before their
re-point (`PL-PGZF`), and `PL-MBP6`'s two lines on `assets/branding/` - and 17
named a removal on purpose ("renamed from", "is gone", "does not exist"). The
other 73 named nothing the tree ever held: planned files, examples
(`tools/x_check.py`), another repository's paths, container paths.

**So the check is narrower than "resolves path citations in `docs/items/*.md`",
by that count.** `_check_brief_paths`, called from `check_citations`, holds a
live brief's unresolved path citation to an error only where history shows the
tree once held it - one `git log --no-renames --diff-filter=D` walk, 0.2 s on
this repository - so a record separates drift from specification where the
`touches` exemption `PL-3NKZ` proposed excuses 11 of 95. The 5 drifts are
repaired in place and the 17 deliberate mentions carry the `absent:` marker
`PL-HJ8G` built for the documents; a fence also escapes, as for line
citations. The trade: a misspelt path no commit ever held is not reported. A
checkout whose history git cannot read, or holds only part of, says so in
`declined`. `docs/ARCHITECTURE.md`'s tools-map sentence now states both halves
of the citation check.

