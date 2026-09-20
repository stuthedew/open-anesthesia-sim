---
id: PL-NLP4
title: ROADMAP.md's Declined-to-Gate-2 closing paragraph says the subsection holds 66 dispositions and it now names 132 open debt items, which is PL-B8V1's stale-present-tense defect in a paragraph that item does not reach
priority: P2
effort: S
status: done
classes: defect, docs
feature: planning-cadence
milestone: v0.4.35
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-20
pr: 774
payoff: a reader sizing what a second Declined-to-Gate heading would cost stops being told it orphans the first one's dispositions, which PL-82B0 fixed
verify: grep -qF 'a convention rather than a constraint' ROADMAP.md
---

**Problem.** ROADMAP.md's Declined-to-Gate-2 closing paragraph says the subsection holds 66 dispositions and it now names 132 open debt items, which is PL-B8V1's stale-present-tense defect in a paragraph that item does not reach

**Where.** `ROADMAP.md` § "Declined to Gate 2 on the refilling-queue ground",
the closing paragraph opening "**It is inside this section rather than beside it
because the checker reads only one.**"

**Measured 2026-09-16**, while writing `PL-LPHT`'s gate dispositions into that
subsection. `tools/doc_check.py`'s `_declined_ids` reads the subsection and
returns every `PL-` id in it; intersected with the open items that are debt by
`docket.toml`'s `debt_classes` or sit at `needs-decision`, that is **132**, and
it was 132 before this pass as well as after. The paragraph says 66. Nothing
checks it: `check_gate_counts` holds the count-carrying *group headings* and the
`not-delegable` claims to the list, and this number is in a body paragraph.

**Why it is the same defect as `PL-B8V1` and not that item.** `PL-B8V1` is a
live count written in the present tense in the same subsection, and its
recommendation - date the claim in place rather than recompute it - is the
answer here too. But it is scoped to one paragraph, "The arithmetic is the
argument", and says so: it was found sweeping `PL-WSDY`'s done-when over release
narratives and filed because that paragraph is not one. So this paragraph is not
inside it, and the two are cheapest answered together.

**Why it matters.** The sentence exists to say what a second
`### Declined to Gate ...` heading would cost, which is `PL-82B0`'s defect - the
workflow lane's current top pick. A reader sizing that cost takes 66 from here
and is out by a factor of two, in the one paragraph written to make the cost
legible.

**Done when.** The paragraph states the figure in a form that does not go stale -
dated in place, per `PL-B8V1`'s recommendation, or expressed without a live
count - and `PL-B8V1`'s decision covers both paragraphs rather than one.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Follows `PL-B8V1` (date the gate arithmetic in place), and stays `blocked` on
it. The same clause 4 reading applies once that lands: this closing sentence is
a record of what the 2026-09-08 argument concluded, so it is dated rather than
recomputed.

## Closed 2026-09-20, in the same branch as `PL-B8V1` and `PL-82B0`

Unblocked by `PL-B8V1` landing, and overtaken in its own favour by `PL-82B0`
landing beside it: the paragraph did not only carry a stale figure, it also
described `_declined_ids`' single-subsection read in the present tense, and
that read is gone. So the paragraph now records the hazard as closed and says
what a second heading costs today, which is nothing.

**The count is expressed without a live figure rather than dated in place**,
which is the second branch `PL-B8V1`'s recommendation allows and the honest one
here. Dating 66 in place would have minted a false dated claim: the measurement
on 2026-09-16 found 132 and found that it had been 132 before that pass as well,
so there is no date at which 66 is known to have been right. `PL-0VFF` takes the
same branch for the open count in the same section, so one rule now covers both
numbers in it.

`verify:` written and run on 2026-09-20, watched to fail first (exit 1, the
phrase absent), and it is a bare `grep` for what the work adds - no
`doc_check.py check` clause ahead of it, per the skill's rule that a health
check passing before the work proves nothing.

