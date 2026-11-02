---
id: PL-B6YV
title: docs/MODEL.md states what the model computes in prose that no test computes, so a claim that was never true, or that lost its condition, is found only when a reviewer happens to read it: decide how such a claim names the test that holds it
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests/unit/test_doc_check.py, docs/items
deferred-from: v0.7.0 - recorded as a generator head on 2026-11-02 from PL-R4Y2's defect review; each member was placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-11-02
closed: 2026-11-02
pr: 1927
payoff: a specification sentence about what the model computes names the test that computes it, so a false claim, or one missing its condition, fails a check or a test instead of waiting for a reader
verify: grep -q 'def _numeric_paragraph_members' tools/doc_check.py && grep -q '_numeric_paragraph_members' tests/unit/test_doc_check.py
root-cause-of: PL-8YBS, PL-39KH, PL-5RPD, PL-M8F6, PL-MLPT, PL-GJYL, PL-SR8F
generator: spent - the rule is in docs/MODEL.md and check_bound_families now fails an unheld numeric paragraph in each section it holds; the remaining stock is filed as the model-claims-held-by-tests passes, led by PL-19W8
misread: Whether a docs/MODEL.md sentence about what the model computes matches what it computes
---

**Problem.** `docs/MODEL.md` states, in free prose, what the model computes
and what the interface displays. Two examples are a figure such as "fat's
whole first hour spans less than 4 px" and a behaviour such as "the
concentration displayed beside a halt is the height the learner marked".
Nothing ties such a sentence to a computation. So a claim that was never true,
or that holds only under a condition the sentence leaves out, stays in the
specification until a reviewer happens to read it against the code.

**Why it matters.** `docs/MODEL.md` is the authoritative specification, and
`CLAUDE.md` treats a wrong statement about what a value means as a safety
issue. A learner or a later session who trusts "the displayed value is the
marked height" reads a correct number wrongly. `PL-8YBS` sat in the queue for
37 days with its sentence still on the page.

**Generator check.** A new head, recorded 2026-11-02. The fact misread is
whether a `docs/MODEL.md` sentence about what the model computes matches what
the model computes. `PL-4FBP` (closed 2026-09-19) holds enumerated families
and restated data values to the tree, and it states the author's duty to name
what a sentence asserts. By decision, it left free prose outside those
families to review at close-out. These members show that review did not catch
them:

- `PL-8YBS` (open): a pixel figure true only at a 1 MAC dial, stated without
  the dial. Found by a measurement, 2026-09-26.
- `PL-39KH`: a benchmark called a 1 MAC case that reaches 0.84 MAC, with a
  wrong cause given for what the chart shows. Found by blind review,
  2026-10-25.
- `PL-5RPD`: two step sizes called two roundings of one solution, which is
  true only between setting changes. Blind review, 2026-10-25.
- `PL-M8F6`: the halt's displayed concentration called the marked height,
  when it can be one or two display counts past it. Blind review, 2026-10-25.
- `PL-MLPT`: the 24-hour run cap argued from an exposure range that a 1 MAC
  run passes. Blind review, 2026-10-25. This one is partly a reasoning error
  rather than a computed figure.
- `PL-GJYL` and `PL-SR8F`, both 2026-09-06, before `PL-4FBP` closed: a
  numerical claim that measurement contradicted, and "two orders milder" said
  of figures that span 0.8 to 1.3 orders.

`PL-1QL6` was matched to this cluster by the sweep that found it, and is left
out here. It named a removed method, which is a code-structure claim under
`PL-4FBP`'s clause 1, not a computed one. `PL-R4Y2` (the product-defect
generator sweep) matched 27 more items to `PL-4FBP`'s broader fact and left
them unrecorded. They are not re-examined here.

**What the fixes did.** A subagent read each member on 2026-11-02, and this
session checked the claims it relied on. Only one fix ties the sentence to a
computation. `PL-M8F6` added two tests in
`tests/integration/test_controller.py`, but the corrected sentence does not
name them. `PL-39KH`'s section now names
`tests/reference/test_mac_awake_washout_figures.py`. That test reads the
protocol and the printed figures from the section and runs the model, so the
page cannot drift from the model without the test failing. It is the strongest
form, and two other reference tests already use it:
`tests/reference/test_coupled_dynamics.py` and
`tests/reference/test_late_washout_against_published_fits.py`.

**Measured 2026-11-02, before recommending anything.** A paragraph-level
script over `docs/MODEL.md` (13,458 lines, 1,163 prose paragraphs) found 379
paragraphs that state a number with a unit. 150 carry a `provenance:`,
`derived:` or `absent:` marker, 25 name a test in a code span, and 56 carry a
date. That leaves about 148 held by nothing. The largest groups are "Known
limitations" (23), "Desflurane's residual" (11), "Where more than one trace
answers" (11), "Source hierarchy" (10) and "Displayed precision" (10). A
random sample of 16 of the 148 held about 6 computed claims, 6 published
figures restated beside their citation, and 4 definitions or conventions. So
roughly 55 to 60 numeric paragraphs state a computed result and name no test.
Qualitative claims, such as `PL-M8F6`'s, have no syntax that a script can
find, and are not counted. The script is a heuristic used once to size the
work. It is not a check.

**Decision needed.** Should a `docs/MODEL.md` sentence about what the model
computes or displays have to name the test that computes it, enforced section
by section? The alternative is the status quo, where such sentences are held
by review alone.

**Recommendation:** adopt it, as an extension of `PL-4FBP`'s clause 1 to
computed claims, built on the machinery that already exists.

1. **The rule.** A sentence that states what the model computes, or what the
   interface displays, names in a code span the test that computes it. Or it
   carries the declared-none form ``no test yet (`PL-XXXX`)``. Where the claim
   is a figure, the preferred form is the one
   `tests/reference/test_mac_awake_washout_figures.py` uses: the test reads the
   figure from the section and compares it with the model's output. Naming a
   test is the minimum.
2. **The trigger a script can enforce.** `check_bound_families` gains a
   member reader for "every prose paragraph in this section that states a
   number with a unit". Each such paragraph must carry one of the forms
   already in use: a `provenance:`, `derived:` or `not-restated:` marker, a
   code-spanned test, the declared-none form, a cited published source, or a
   date. A section joins the table when its annotation pass lands, so
   `make check` never goes red for work that is not yet done. This is
   `PL-4FBP`'s ramp, unchanged.
3. **What it does not reach.** A qualitative claim with no number is held by
   the author's duty and by review, through `tools/model_doc_review.py` and
   blind review. The check refuses only what its syntax shows.
4. **The annotation passes.** About 148 paragraphs in roughly 25 sections,
   filed as items under the `model-claims-held-by-tests` feature and grouped
   by section. They start with "Known limitations" and "Displayed precision".
   Each pass names an existing test where one computes the claim, adds a test
   where none does, and otherwise uses the declared-none form. `PL-8YBS` is
   the first instance and is fixed by its own item.

**Why adopt rather than keep review alone.** Six of the seven members were
found by a measurement or a blind review weeks after the sentence was
written, and five of them in one review on one day. That review found the
existing stock, not the new arrivals, and nothing stops the next sentence. The
practice is the one the document already cites for its required tests:
traceability from a requirement to the test that verifies it (IEC 62304
§ 5.1.1; FDA, *General Principles of Software Validation*, 2002, § 5.2.2). For
figures, a test that reads the document is an executable specification. That
is the sense of Adzic, *Specification by Example*, Manning 2011, chapter 3,
"Living documentation" (https://www.manning.com/books/specification-by-example).
Python's `doctest` exists for the same reason, to check that documented
examples "still work as documented"
(https://docs.python.org/3/library/doctest.html).

**What it costs, and why this is the owner's decision.** On the page, about
148 paragraphs gain a test name, a marker or a declared absence, as the hazard
table's "Held by" column already does. In the queue, it costs one item per
section group, each S or M. It also reopens part of a ratified decision:
`PL-4FBP` left free prose to review at close-out, and the members above are
the ordinary evidence that reopens it.

**What would make this wrong.** The sample puts about 60% of the 148 as
published figures or definitions. Those pass on the citation or date form
with little or no edit, so they cost little. The rule earns its cost only if
the remaining computed claims turn out wrong when a test is written for them.
The first annotation pass counts how many of its computed claims were wrong
or missing a condition. If it finds none in "Known limitations" and
"Displayed precision" together, the remaining passes are dropped and the
check stays on those sections alone.

**Decided 2026-11-02 (project owner, 2026-11-02, ratified).** Adopted as
recommended above: the rule, the numeric-paragraph trigger enforced section by
section through `check_bound_families`, the limit for qualitative claims, and
the annotation passes with the stop condition in "What would make this wrong".
It was chosen over keeping such sentences held by review alone. The answer was
"agree", so the decision reopens on ordinary evidence. It also reopens, for
computed claims only, `PL-4FBP`'s 2026-09-19 decision to leave free prose to
review at close-out. That decision still applies to every other kind of free
prose.

**Done when.** The build lands these, in order:

1. `docs/MODEL.md` § "How this document is held to the tree" states the rule
   for computed claims beside clause 1, with the preferred form for figures
   and the limit for qualitative claims.
2. `tools/doc_check.py` gains `_numeric_paragraph_members`, a member reader
   for `BOUND_FAMILIES` that yields each prose paragraph stating a number with
   a unit. Each must carry a `provenance:`, `derived:` or `not-restated:`
   marker, a code-spanned test, the declared-none form, a cited published
   source, or a date. Unit tests in `tests/unit/test_doc_check.py` cover each
   accepted form, a paragraph that carries none, and a number with no unit,
   which is not a member. If the reader lands under another name, update this
   item's `verify:` in the same commit.
3. One section joins the table and conforms when it lands: "Displayed
   precision" is the first choice, because a learner reads its values
   directly.
4. The remaining annotation passes are filed under
   `model-claims-held-by-tests`, grouped by section, starting with "Known
   limitations". The first pass records how many of its computed claims were
   wrong or missing a condition, and applies the stop condition above.

**Built 2026-11-02, as decided.** `tools/doc_check.py` gained
`_numeric_paragraph_members`, a fourth member shape for `BOUND_FAMILIES`,
and `FIGURE_ENTITY`, the kind its members are held to. A member is each
paragraph in the section that states a figure in a unit. A figure is read as
`_untied_figures` reads one, so the units are the ones `PROSE_UNITS` lists and
"a number with a unit" has one meaning in the file. A paragraph passes on any
of these, each a syntax the writer adds on purpose, as
`.claude/rules/apparatus-standard.md` requires of a hard check:

- a `provenance:`, `derived:` or `not-restated:` marker that speaks for it,
  read with `_marked_scope`, so a marker under a list holds each entry;
- a test named in a code span, read by `_names_a_test`, the predicate the
  other families use;
- the declared-none form, resolved against the queue by
  `check_bound_families` as before;
- an ISO date, which makes it a record under clause 4;
- a published source in a form `PUBLISHED_SOURCE_RE` reads: a DOI, a PubMed
  id, an ISBN, or a journal locator such as "Anesth Analg 1991;72:316-324".

**How a cited source is recognised, decided in the build.** Only by an
identifier or a locator. An author and a year alone, such as "Mapleson 1963",
is refused, because "Until 2026" and "The 2019" have the same shape and no
pattern can tell them apart. A paragraph that cites a source that way adds
the locator or the identifier, which `docs/MODEL.md` already writes for most
of its sources. A date or a source inside a code span does not count. This
was a choice with one clearly correct option under the apparatus standard,
so it was taken rather than offered.

"Displayed precision" joined the table and conforms. Of its 22 numeric
paragraphs, 9 carried no form. Three now name the test that holds them. Seven
declare ``no test yet (`PL-19W8`)``, and `PL-19W8` owes those tests. The pass
found one computed claim that is wrong or missing a condition: the section
gives desflurane's fat 236 s in one paragraph and 237 s in another. It also
found one status claim gone stale, "which `PL-2881` writes", after `PL-2881`
closed. That one was corrected here.

Counted with the reader over the whole document: 383 numeric paragraphs, 96
of them carrying no form. The passes are filed under
`model-claims-held-by-tests`: `PL-19W8` first ("Known limitations", and the
tests "Displayed precision" owes), then `PL-JP7P`, `PL-MCQ5`, `PL-5C1H` and
`PL-H94Q`, each blocked on it under the stop condition. `PL-XQXK` records the
unit vocabulary's limit: a figure in px, mL, mmHg or percentage points makes
no member, and `PL-8YBS`'s own figure is in px.
