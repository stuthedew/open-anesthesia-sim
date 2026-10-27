---
id: PL-K5CX
title: Triage's generator check and docket inflow ask only items on apparatus paths, so a product defect is never asked which fact it misread and a product head whose fix did not hold is never listed
priority: P1
effort: M
status: ready
classes: defect
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - apparatus work on the machinery that finds generators, taken now at the project owner's request rather than held by the schematic's gate
added: 2026-10-27
payoff: a simulator defect is asked which fact it misread when it is triaged, and a product head whose fix did not hold is listed, without waiting for the owner to ask for a sweep
verify: grep -q 'def test_triage_marks_a_product_defect_as_owing_a_generator_check' subprojects/docket/tests/test_cli.py && grep -q 'def test_product_lane_counts_a_product_reentry' subprojects/docket/tests/test_inflow.py
impairs-generators: render._generator_check and inflow.analyze key on workflow_paths alone, so triage never asks a product defect which fact it misread and inflow never counts a product re-entry
---

**Problem.** The project owner asked on 2026-10-27 for the generator checks to
reach product code, so that the simulator's common failure modes are found as
mechanisms rather than patched one item at a time. Two parts of the machinery
that finds generators stop at `workflow_paths`:

- `render._generator_check` and `render.generator_check_on_set` mark an item as
  owing triage's generator question only when a `touches` path is under
  `workflow_paths`. A product defect is never asked which fact it misread.
- `inflow.analyze` counts only filings with an apparatus path. A product
  filing's `reenters:` is never counted, so a product head re-entered by three
  filings is never listed as "a generator whose fix did not hold".

`PL-R4Y2` (the sweep of product defects for generators) measured the cost. A
recorded head explained 35 of 222 product defects (16%) on 2026-10-19, against
44% in the workflow lane. Its two passes then found seven heads and two more,
each by an owner-requested sweep. The second pass says why it was needed:
"Product items are not asked the generator question at triage, so none of the
43 had been asked." Product defect filings are not falling either: 174 in
September and 157 in the first 27 days of October.

**Which product items are asked.** An item owes the question when a `touches`
path is a product path and its `classes` are not all in `new_work_classes`
(`feature`, `planning`). An item with no classes is asked, so the rule fails
closed. Two narrower keys were measured on 2026-10-27 against the 75 product
members of heads that touch product paths, and the 230 product filings since
2026-09-28:

| Key | Members it would have asked | Filings asked in 4 weeks |
| --- | --- | --- |
| Not new work | 75 of 75 | 226 of 230 |
| A `debt_classes` class | 69 of 75 | 160 of 230 |
| `defect`, `safety` or `science` | 66 of 75 | 158 of 230 |

The debt-class key misses four `docs` items of `PL-4FBP`'s fact, a document
sentence diverged from the tree fact it restates, which is the largest product
family `PL-R4Y2` found (27 unrecorded matches). So the key is "not new work",
read from `new_work_classes`, the gate's own definition of work owed.

**The number that would make this wrong.** The extension costs one judgment
per product filing at triage. It is wrong if nearly every product answer is
"a one-off", say more than nine in ten. `PL-R4Y2`'s passes place about a third
of product defects under a head or a head's fact, so the yield is far above
that.

**What to build.**

1. One predicate in `docket.model` for the paths that make an item owe the
   question, read by the triage mark, by `set`'s line and by `inflow`.
2. The triage mark and `set`'s line name product paths as well as apparatus
   ones, and say "undecided" where a product item has no `touches`.
3. `bin/docket inflow --lane product` counts the product filings that owe the
   question, with their re-entries and the re-entered list. The default stays
   the apparatus, and `PL-04KR`'s release-time predictions stay apparatus-only.
4. `.claude/skills/docket/modes/triage.md` and `subprojects/docket/README.md`
   say which product items are asked and why.

**Done when.** `bin/docket triage` marks an untriaged product defect as owing
the generator check, `bin/docket inflow --lane product` lists product
re-entries, and tests pin both.

**Generator check.** This item is a defect in the machinery that finds
generators, recorded as `impairs-generators:`. It misreads no fact itself.

**Why it matters.** Product defects are the ones a learner can see. While
triage never asks one where it came from, a recurring cause is found only when
the owner asks for a sweep, and each instance in between is patched alone.
