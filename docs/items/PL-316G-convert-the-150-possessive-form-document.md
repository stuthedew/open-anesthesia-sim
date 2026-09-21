---
id: PL-316G
title: Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation
priority: P2
effort: M
status: done
classes: docs, infra
feature: dev-tooling
touches: docs/, src/anesthesia_sim/, tests/, tools/, CLAUDE.md, .claude/, ROADMAP.md, README.md, subprojects/docket/, docket.toml, Makefile
added: 2026-09-13
closed: 2026-09-21
pr: 874
payoff: every citation form the project writes is checked, so a renamed heading or a reworded sentence stops orphaning a pointer silently
verify: python3 tools/possessive_section_check.py
recurrences: 2026-09-21 PL-YSMV
---

**Problem.** Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation

**Why it matters.** `PL-V13T` made `doc_check` read the section-mark form, and
the possessive form was deliberately left out because this project writes
`` `CLAUDE.md`'s "..." `` to quote a *sentence* at least as often as to cite a
section - admitting it reported 28 quotations of correct prose as stale
headings. So 150 citations are unchecked by construction rather than by
oversight, and a section rename orphans every one of them silently. That is the
failure `PL-VZL0` exists to prevent, still live over a fifth of the tree's
citations.

**Decision needed.** Whether to convert, and how widely. Converting is not
mechanical: each of the 150 has to be read to say whether it cites a *section*
or quotes a *sentence*, and converting a sentence quotation to `§` would assert
something false. Three shapes:

1. **Convert the simulator half only** - `src/`, `tests/`, `docs/MODEL.md`,
   `docs/ARCHITECTURE.md`, `README.md`. That is where a stale pointer reaches a
   reader of clinical output, which is the whole argument for checking them.
   Smaller diff, and the apparatus keeps a form nobody checks. **This is the
   recommendation.**
2. **Convert everything**, apparatus included. Uniform, and the largest diff -
   it opens `CLAUDE.md` and the rules files, which sit in every session's cached
   prefix.
3. **Convert nothing, and adopt `§` for new citations only.** Costs no diff and
   leaves the 150 unchecked indefinitely; honest only if paired with saying so
   where a session would look.

Expect the conversion to surface stale citations, as `PL-V13T` did - that is
the point rather than a side effect, so budget for the repairs.

**Done when.** Every possessive-form reference inside the agreed scope that is
a section citation reads in the section-mark form:

```text
  `<document>.md` § "Section"
```

every one that quotes prose is left alone and is recognisable as prose, any
staleness the conversion surfaces is repaired, and `make check` is green.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and its count has
grown - but the recommendation's scope was already false when it was written.**
Re-measured today over `*.py` and `*.md`: **211** possessive-form citations
against 782 section-mark ones, where the comment at `tools/doc_check.py:354`
recorded 150 against 353 on 2026-09-13.

The scope this brief recommends - convert the simulator half, "`src/`,
`tests/`, `docs/MODEL.md`, `docs/ARCHITECTURE.md` and `README.md` … that is
where a stale pointer reaches a reader of clinical output" - is **five
occurrences**: `src/anesthesia_sim/app/formatting.py:210`,
`src/anesthesia_sim/core/uptake_system.py:473`,
`src/anesthesia_sim/core/governing_equations.py:66`,
`tests/unit/test_governing_equations.py:8` and
`tests/benchmarks/test_frame_cost.py:17`. `docs/MODEL.md`,
`docs/ARCHITECTURE.md` and `README.md` hold **zero** between them. At the
pre-filing commit `438808b` the same buckets read 3 / 1 / 0 / 0 / 0, because
`PL-VZL0` had already converted `src/core` - see
`src/anesthesia_sim/core/governing_equations.py:317-319`.

So the safety argument for the recommended scope does not hold: 184 of the 211
are in `docs/items/`, which no reader of clinical output opens. The decision
this item still owes should be taken on the queue, not on the simulator - and
whoever takes it should re-measure rather than reuse either number above.

## A fourth shape, measured 2026-09-21: widen the connective set, at one line

**The premise above is wrong, and it is wrong about the mechanism rather than
about the count.** The title and the problem statement both say the
section-mark form is "the only way doc_check can check them without reading
prose as a citation". It is not. Nothing about `§` makes a citation checkable:
`CITATION_CONNECTIVE` feeds exactly one pattern, `QUOTED_SOURCE_RE`, which
feeds exactly one function, `check_quoted_sources` - and that function tests
**containment**, not headings. Its own docstring already settles the question
this item proposes to settle by hand: whether a quotation is a section title or
a sentence "is a distinction this tool would have to guess at", and the
containment test does not guess, because "it is the same question in both
cases".

Positive control, run 2026-09-21 against a probe document holding the same text
in both forms:

```text
  `README.md` § "A heading no file has"    -> reported
  `README.md`'s "A heading no file has"    -> not matched at all
```

So converting a possessive citation to `§` moves it into the identical test.
The conversion this item describes and the one-line widening buy the **same
guarantee**; they differ only in what they cost to reach it.

**What the widening reports, counted rather than estimated.** Admitting
`['’]s(?:\s+own)?` to `CITATION_CONNECTIVE` takes the citations
`check_quoted_sources` examines from **950 to 1,169** (+219) and produced
**40 errors** where the tree was otherwise clean. After the three repairs this
item's own commit makes, and rebased on `aff66dbb`, the same experiment reads
950 -> 1,167 and **37 errors** - that is the reproducible number today, and
the classification below is of the original 40. Each was then classified by
searching the cited file's own history on `origin/main` for the quoted text:

| Class | Count | What it is |
| --- | --- | --- |
| Genuine drift | 24 | Verbatim in an earlier version of the cited file, gone now |
| Never verbatim | 15 | A compression or paraphrase inside quotation marks |
| Path artifact | 1 | `v0.4.5.md` written bare, its directory only in the surrounding prose |

`PL-V13T` recorded the same experiment on 2026-09-13 as "28 errors, every one a
false positive". That is no longer what the tree shows: a **majority are real**,
and two of the 15 are real in a second way - the quoted text is verbatim in a
*different* file, so the citation sends a reader to the wrong document. The
clearest is `PL-SWP3:57`, which attributes "name the number that would change
your mind, then go and count it" to `CLAUDE.md`; it is a heading in
`.claude/rules/expert-review.md`, and moved there without the citation
following.

**Where the 40 sit, and it decides the design.** Exactly six are in text a
session acts on - `ROADMAP.md` twice, the docstring at
`tools/workflow_paths_check.py:47`, and the open briefs of `PL-FDMJ`,
`PL-BYMX` and `PL-4QCJ`. The other **34 are in briefs already `done` or
`dropped`**, and `.claude/rules/citation-drift.md` (project owner, 2026-09-19,
ratified) has already ruled on those: drift in a closed brief is not a finding,
not to be repaired, not to be filed against, not to be counted when sizing a
cluster. A closed brief says what was true when the work was done and is read
for provenance, where that is the correct meaning and the only one available.

So the widening has to exempt closed briefs - not as a concession bought to
shrink the diff, but as that ratified rule applied. With the exemption the
backlog is **6, not 40**, and the same rule already obliges the finding session
to repair the live ones in place. **Three of the six are repaired in this
item's commit**: the docstring above, which quoted a sentence `docs/worker.md`
no longer carries; `PL-FDMJ`, which sent a reader to `CLAUDE.md` for an
apparatus bar that has since moved to `.claude/rules/apparatus-standard.md`;
and `PL-4QCJ`, whose `docs/MODEL.md` pointer was reworded to name
`docs/references/`.

**The remaining three are one disposition question, and it belongs to this
decision rather than to a repair.** `ROADMAP.md` twice and `PL-BYMX` use the
possessive to *name* a rule by a compressed handle, not to point at a section.
The example is fenced because this brief would otherwise be its own
thirty-ninth finding, which is the convention `.claude/rules/citation-drift.md`
already sets for an item whose subject is a broken citation:

```text
  written    `CLAUDE.md`'s "prefer an obvious failure to a plausible-looking
             number"
  the rule   Prefer an obvious failure/error state to displaying a
             plausible-looking number when correctness cannot be established.
```

Nothing is stale: the rule is live and the handle is a fair compression of it. What the widening would demand is that
the handle be written out verbatim or lose its quotation marks. That is the
real cost of shape 4, it is a cost to how this project writes rather than a
backlog, and it is what the fifteen never-verbatim findings mostly are.

**The exemption is already built and has merged, which removes half of shape
4's cost** (`PL-ZM8P`, landed on `origin/main` in `#866` with the v0.5.1 tag,
re-verified 2026-09-21 against `origin/main` itself).
`check_quoted_sources` held closed briefs to current prose for every connective
in the set, and it passed here only because no `§` citation in a closed brief
had drifted yet. Cutting v0.5.1 hit it: `ROADMAP.md`'s `## Current baseline`
section is replaced wholesale at every release, so `PL-DL4M` - closed in that
same release - went red quoting two of its headings. `PL-ZM8P` is that item,
and it is `done`: `_quoting_sources` now yields `_live_item_briefs(root)`, the
same line `check_line_citations` already drew, with a second test holding the
exemption narrow. `PL-W8NH`, filed from this measurement while the collision
was still latent, is dropped as its duplicate.

So shape 4 no longer has to build the exemption, and no longer waits on
anything: it is startable now. Measured against `origin/main`'s own
`doc_check` with the possessive admitted: **3 errors**, and they are the three
handles named above.

```text
  ROADMAP.md:86     CLAUDE.md  "prefer an obvious failure to a plausible-..."
  ROADMAP.md:6738   CLAUDE.md  "the correct number with the wrong label"
  PL-BYMX:35        CLAUDE.md  "one prune from unrecoverable"
```

**Recommendation: shape 4 - admit the possessive, on top of the exemption
v0.5.1 lands.** One alternative added to `CITATION_CONNECTIVE`, a test in
`tests/unit/test_doc_check.py` pinning a possessive citation of absent text as
reported (the existing
`test_a_possessive_quotation_of_prose_is_not_read_as_a_citation` inverts, and
is the regression this replaces), and three handle dispositions. It measures
3 errors on today's `main` rather than the 40 of the unexempted tree, and it
is unblocked: nothing is sequenced ahead of it.
It reaches shape 2's guarantee at a fortieth of shape 2's diff; it is strictly
wider than shape 1, whose scope the 2026-09-19 sweep had already reduced to
five occurrences; and unlike shape 3 it leaves nothing live unchecked. It is
also stronger than any of the three, because it checks the prose quotations
that a conversion would deliberately leave in the possessive form and therefore
outside the check forever.

**Stated against itself, per `.claude/rules/expert-review.md`.** The widening
is wrong if what it suppresses today is mostly writing that is correct as
written, because then it forces a rewording of correct prose - `PL-KJ63`'s
exact cost, and the reason `PL-V13T` refused. The number that decides it is how
many of the 40 are real: **24 genuine drift, 2 wrong-document and 1
unresolvable path against 13 handles**, and after the closed-brief exemption
the live residue is 3 repairs already made against 3 handles to disposition. `PL-V13T` recorded 28 of 28 as
false positives on 2026-09-13; that is not what the tree shows on 2026-09-21,
and the widening turns on that count rather than on the argument.

**Method, so it is not re-derived.** The classification was made by searching
each cited file's own history on `origin/main` for the quoted text, folded
through `doc_check`'s own `_comparable`. `git rev-list` was used without
`--follow`, so a quotation of a file that has since been renamed would be
misfiled as never-verbatim; none of the cited files has moved. The measurement
scripts were scratch and are not committed - the counts above are reproducible
by adding the possessive to `CITATION_CONNECTIVE` and running
`python3 tools/doc_check.py check`.

## Decided 2026-09-21: both steps, in this order (project owner)

The project owner took the fourth shape and the conversion **both**, on the
five-year test - "however much it costs to do it right once, it is still
cheaper than doing it twice" - and on the reading that these are sequential
rather than competing. The ordering is the substance of the decision: the
check has to exist first, because it is what makes the conversion safe. A
conversion done first is 49 hand edits with nothing underneath them, followed
by building the check anyway.

**Step 1 is done, in this item's branch.** `CITATION_CONNECTIVE` admits
`['’]s(?:\s+own)?`; the comment above it records why the 2026-09-13
exclusion was reversed and what the widening costs;
`test_a_possessive_quotation_of_prose_is_not_read_as_a_citation` is replaced by
a reporting test and a passing test, so the change cannot read as a ban on the
form; and the three findings it surfaced are repaired - `ROADMAP.md:86` became
a `§` section citation, `ROADMAP.md`'s colour-panel paragraph and `PL-BYMX`
now quote verbatim. `make check` green.

**Step 2 is the conversion, and a tool now names its sites.**
`tools/possessive_section_check.py` reports every possessive citation whose
quotation matches a heading or a `**Bold.**` marker in the file it names -
**29 sites** on the merged tree - and prints the exact `§` line each should
become. It is `PL-316G`'s `verify:`, and it fails today, which is what the
earlier `verify:` did not do: proving step 1 proved nothing about step 2, and
`docket check` was right to refuse it.

**Why a tool rather than the per-site judgment this brief first described.**
The decidable half is narrower than "is this a section citation" and it is the
half that matters: a quotation that *matches a heading* is one, as a fact about
the tree. A quotation matching no heading may still be a faithful quotation of
a sentence, which is correct as written, so the tool reports nothing about it.
That asymmetry is deliberate - `CLAUDE.md` refuses to script the judgment half,
and the half needing judgment is exactly the one left alone.

Scope is live text only. The 174 possessive citations in closed briefs are
exempt at `_quoting_sources` since `PL-ZM8P`, so the tool never sees them and
none must be edited.

**Step 2 ends by wiring the check into `make check`**, which is the part that
answers the standing question - a convention nothing enforces decays, and this
is what stops the next session writing a section citation in a form that says
nothing to its reader. It cannot be wired in before the conversion, because it
would hard-fail on the 29 sites it exists to find.

**Done when.** `python3 tools/possessive_section_check.py` exits 0, every
quotation it reported reads in the section-mark form, no quotation of prose was
converted, no closed brief was edited, the check runs inside `make check`, and
`make check` is green.
