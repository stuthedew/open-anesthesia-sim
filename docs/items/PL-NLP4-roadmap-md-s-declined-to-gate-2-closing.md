---
id: PL-NLP4
title: ROADMAP.md's Declined-to-Gate-2 closing paragraph says the subsection holds 66 dispositions and it now names 132 open debt items, which is PL-B8V1's stale-present-tense defect in a paragraph that item does not reach
status: untriaged
added: 2026-09-16
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
