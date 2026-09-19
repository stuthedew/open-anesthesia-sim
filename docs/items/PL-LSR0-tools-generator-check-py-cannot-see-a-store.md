---
id: PL-LSR0
title: tools/generator_check.py cannot see a store-drift generator: clusters() partitions by a single touches path and STORE_PATHS excludes docs/items and docs/WORKING_NOTES.md, where 15 of PL-G424's 21 members sit
priority: P2
effort: M
status: done
classes: defect, infra
feature: generator-identification
milestone: v0.4.30
touches: tools/generator_check.py, tests/unit/test_generator_check.py
added: 2026-09-19
closed: 2026-09-19
pr: 726
verify: grep -q 'def test_the_store_clusters_like_any_other_path' tests/unit/test_generator_check.py
impairs-generators: clusters() partitions the store by a single touches path and STORE_PATHS excludes docs/items, docs/WORKING_NOTES.md and docs/dead-ends.md; 15 of PL-G424's 21 members sit on those excluded paths and the remaining 6 fall under MIN_OPEN, so no generator whose members share a kind of claim rather than a file can be surfaced by it
---

**Problem.** tools/generator_check.py cannot see a store-drift generator: clusters() partitions by a single touches path and STORE_PATHS excludes docs/items and docs/WORKING_NOTES.md, where 15 of PL-G424's 21 members sit

**Where it comes from.** A read-only survey of the open workflow lane,
2026-09-19, asked which mechanism is still generating items. `PL-G424`
(apparatus-side citation drift) is the one open generator head, and it was
found by a manual sweep. Running `python3 tools/generator_check.py` against the
same tree in the same sitting printed six clusters — `tests/integration`,
`src/anesthesia_sim/app`, `docs/MODEL.md`, `docs/ARCHITECTURE.md`,
`src/anesthesia_sim/app/controller.py`, `tools/doc_check.py` — and the line
"None of these is a generator". None of the six is the citation-drift family.

**The cause is structural, not a threshold.** `clusters()` partitions the store
by a single `touches` path, and excludes three of them outright:

```python
STORE_PATHS = {"docs/items", "docs/WORKING_NOTES.md", "docs/dead-ends.md"}
```

`PL-G424`'s own enumeration of where each member's wrong sentence sits maps
onto that exclusion almost exactly:

| Where the wrong sentence sits | Members | Visible to `clusters()` |
| --- | ---: | --- |
| `docs/WORKING_NOTES.md` | 8 | no — in `STORE_PATHS` |
| another item's brief (`docs/items`) | 7 | no — in `STORE_PATHS` |
| `.claude/skills/docket/SKILL.md` | 2 | under `MIN_OPEN = 3` |
| `CLAUDE.md` and `.claude/rules/` | 2 | under `MIN_OPEN = 3` |
| `Makefile` | 1 | under `MIN_OPEN = 3` |
| item briefs plus `ROADMAP.md` | 1 | under `MIN_OPEN = 3` |

15 of 21 are excluded by name; the other 6 scatter across four paths, each
below the floor. No threshold change reaches this family, because the members
share a *kind of claim* rather than a file.

**The exclusion is correct on its own terms, which is why this is a decision.**
The docstring states the reason: `docs/items` sits inside `workflow_paths`, so
"every capture made while doing something else would otherwise read as one
enormous cluster", and `docket trend` excludes store paths from its churn share
for the same reason. Deleting the exclusion would trade one blind spot for one
false cluster of ~300 items. The design work is finding an axis that partitions
the store by what an item *asserts about* rather than by which file it touches.

**Why it matters.** `CLAUDE.md` ranks a defect in the machinery that finds and
ranks generators above every band but `P0`, on the stated ground that "while
identification is broken a generator is never recorded, and an unrecorded
generator is ranked by nothing". This is that case with the mechanism named: a
whole family of generator — one whose members share a claim rather than a
path — cannot be surfaced by the only automated detector the project has.

**The count, run before proposing anything (`.claude/rules/expert-review.md`).**
Retiring the check is wrong if its clusters would have led to a recorded
generator at some worthwhile rate. The rate is **0 of 8**: every generator head
this store carries — `PL-4FBP`, `PL-G424`, `PL-6TP8`, `PL-4Q9B`, `PL-BHVM`,
`PL-L4YG`, `PL-2T03`, `PL-HWW1` — came from a manual sweep, and the tool's own
docstring records it reporting no cluster while `PL-6ZQY` had already named
six. `PL-4YJK` carries the other half of the trade, which is what a manual
sweep costs.

**Decision needed.** Three routes, and the choice is a session's rather than
the project owner's — it rests on measurement and on `CLAUDE.md`'s own "a check
earns its place every run, or it is retired", not on what the project is for:

1. **Add a second axis** that clusters store-path items by what their briefs
   cite — the path or id a brief asserts a fact about — leaving the existing
   `touches` axis untouched. Highest value, most design work.
2. **Keep the tool as a `touches`-axis detector** and say so in its docstring,
   accepting that claim-shaped generators are found by funded manual sweeps
   instead. Cheapest, and honest about what it covers.
3. **Retire it** under the check-earns-its-place rule, and fund the sweep.

Route 1 is the recommendation if `PL-4YJK` shows sweeps are expensive enough to
be worth automating away; route 2 if they are not. Do not take route 3 without
`PL-4YJK`'s number — an 0-for-8 record alone cannot distinguish a broken
detector from one whose cluster shape is simply rarer than the other kind.

**Done when.** One of the three routes above is taken and recorded as a
decision with what it was chosen over; `tools/generator_check.py`'s docstring
states which shapes of generator it can and cannot surface, so the next session
reading a clean run knows what that silence covers; and if route 1 was taken,
`python3 tools/generator_check.py` names the citation-drift family on a tree
where `PL-G424`'s members are still open.

**This item's gate disposition is written: declined to Gate 2 on the
refilling-queue ground.** Classing it `defect` and triaging it to
`needs-decision` is what made it debt, so the capture created the failure it
then had to answer — the lesson `PL-2P9L` paid for on 2026-09-19. `make
doc-check` reported it as an advisory (`ROADMAP.md:2036`); `make check` reported
it as a **failing test**, `test_this_repository_records_a_disposition_for_every
_open_debt_item`, which is what forced it to be written rather than deferred.

**Recommended disposition: decline to Gate 2 on the refilling-queue ground**,
written into `ROADMAP.md`'s `### Declined to Gate 2 on the refilling-queue
ground` subsection with its entry count incremented. The grounds, against
`ROADMAP.md` § "The gate is a snapshot, not a moving target": captured
2026-09-19 where the gate froze 2026-09-06; neither `safety` nor `science`; not
`P0`; wholly in the workflow lane. The one argument the other way is that the
*problem* predates the freeze — `STORE_PATHS` is long-standing code — but
v0.5.0's gate stands at 173 of 175 cleared, and admitting an `M` design
decision to a gate two entries from draining is the refilling shape Phase 0 was
retired for.

The entry sits in `ROADMAP.md`'s `### Declined to Gate 2 on the
refilling-queue ground` subsection, whose count went 192 to 193, and it records
the closest call in that section: the *blind spot* predates the 2026-09-06
freeze, but the `impairs-generators:` field that makes it debt did not exist
until 2026-09-19 (`PL-G5ZH`). Nothing further is owed to the gate here.

**Decided 2026-09-19, by this session under the delegation above: the
exclusion is removed and the sort breaks a tie on citations before size.** A
fourth route, and the cheapest that reaches route 1's end state. Chosen over
route 1 as written — a second axis clustering store items by what their briefs
cite — because the constant was the blind spot, not the axis, and a citation
axis would not have gathered these 21 anyway: each asserts a fact about a
different subject. Over route 2, because documenting a blind spot a one-line
change removes is the wrong trade. Over route 3, because 0-for-8 was measured
with the exclusion in place and says nothing about the tool without it, and
`PL-4YJK`'s figures (~$95–100 and ~400,000 tokens per manual sweep) are the
cost of the alternative; a retire-or-keep count is worth running again once
the corrected tool has had time to be 0-for-N or not.

**The count that decided it.** The exclusion's ground — "every capture made
while doing something else would otherwise read as one enormous cluster" — is
true of `docket trend`'s churn share, a commit-diff axis on which `docs/items`
is in every capture commit, and false of the declared-`touches` axis
`clusters()` partitions on: 24, 18 and 0 open items declare `docs/items`,
`docs/WORKING_NOTES.md` and `docs/dead-ends.md`. This brief's own "~300" was
the same conflation. Un-excluded, both store clusters carry a signal:
`docs/WORKING_NOTES.md` has 18 open, 5 sharing `dev-tooling`, 6 cited by three
or more open items and 8 of `PL-G424`'s members; `docs/items` has 24 open, 5
sharing `queue-hygiene` and 5 members. With the sweep's own products
(`PL-G424`, `PL-LSR0`, `PL-4YJK`) removed as citing sources, three members were
already cited by three or more others (`PL-38PN`, `PL-60CQ`, `PL-JXVD`), so the
citation signal predates the head. Under the old sort the `docs/WORKING_NOTES.md`
cluster ranked 9th of 43 signalled clusters — behind `docs/items`,
`tools/doc_check.py` and `subprojects/docket/tests/test_cli.py`, each larger
and cited less — and `SHOW = 6` hid it. Breaking the feature-count tie on the
citation count before open count puts it 6th and leaves the top five as they
were.

**What it still cannot see, now stated in its docstring.** 6 of the 21 declare
a single item file each and are singleton clusters; 6 more scatter across four
apparatus paths under `MIN_OPEN`. A family visible only by reading the briefs
stays a sweep's to find, and `PL-4YJK` records what a sweep costs so the next
count has both halves. Gathering the single-file declarations into the
`docs/items` cluster would need a directory-containment rule this tool applies
nowhere else — `concurrent`'s "same area" reading is the general form — and is
captured as `PL-FH61` rather than special-cased here.
