---
id: PL-4FBP
title: Fifteen items repair a document sentence whose link to the tree lives only in the reader's head: decide whether an assertion must name what it asserts
priority: P2
effort: M
status: needs-decision
classes: docs, infra
feature: generator-heads
touches: tools/doc_check.py, docs/MODEL.md, docs/items
added: 2026-09-17
root-cause-of: PL-8LDF, PL-2M9N, PL-41YP, PL-GQWP, PL-5N7T, PL-9LXK, PL-T9XJ, PL-4RHP, PL-DHJ7, PL-B8V1, PL-NLP4, PL-LM8P, PL-NWTM, PL-B5LB, PL-GTSL
---

**Problem.** The project's authoritative documents were written as prose for a
human reader and only later became the specification the code is judged
against. The link from a sentence to the identifier, test, constant or count it
names therefore exists only in the reader's head, so nothing can tell a
statement that is still true from one the tree has moved past. Fifteen open
items repair one such sentence each, or ask for one more check over one more
family of them.

**Why it matters.** `CLAUDE.md` calls a stale statement about what a value
means a safety issue rather than tidiness, and this is the cluster that
produces them. The instances already run from a count that misleads a session
sizing the debt gate (`PL-B8V1`, `PL-NLP4`, `PL-4RHP`, `PL-DHJ7`) to a
`docs/MODEL.md` guarantee that exists as prose and nowhere else - `PL-NWTM`,
which is `safety`-classed and says the unconditional displayed set has no
structural home in the code at all.

The self-generating half is that every document maintained correctly produces
more of them. `docs/MODEL.md`'s eighteen "Required invariants" and fifteen
"Required tests" name things without naming *which* things (`PL-8LDF`,
`PL-2M9N`); `README.md` states three capability facts whose authority is a
Python constant with nothing comparing the two (`PL-GQWP`); two documents
hand-enumerate the CI floor job (`PL-5N7T`). Each is found by a session reading
the files rather than by anything that runs, one at a time, and each becomes
its own item.

**Why this item is the head - and this one is a refusal rather than a gap.**
Confirmed against the store on 2026-09-18. `PL-036` is the only other open item
whose subject is the mechanism, and its own `Decided` section closes the
general case: *"Recorded, and not to be revisited by tooling: whether a
documented statement is still true stays human."* Its `Done when` implements
one link - fifteen bullets under `docs/MODEL.md` "Minimum displayed outputs"
named against `SimulationSnapshot` fields. Writing `root-cause-of:` onto it
would record a claim its own brief contradicts and promote a narrow item above
every band but `P0`, where nobody could work the cluster from it. `PL-9LXK`
carries the owner's decision for the *count* half only.

**Decision needed.** Whether the annotation convention is adopted - and note
that this is a decision about scope rather than about truth. `PL-036`'s recorded
principle - the tool checks **linkage, not truth** - is not in question and is
not reopened here. What is unsettled is whether the *convention* is adopted:
that an assertion in an authoritative document names the tree entity it
asserts, so `doc_check` can resolve the link without deciding the sentence.
That is the annotation pass `PL-036` itself calls "eighteen judgments, not the
forty lines of checking", and it is what would close the cluster rather than
one bullet list of it. Two sub-questions come with it: which documents the
convention binds - `docs/MODEL.md` and `README.md` are held to the specialist
standard, the apparatus files are not - and what an assertion that legitimately
names nothing looks like, so the convention has an escape that is declared
rather than assumed.

**The items this explains (15, confirmed 2026-09-18 against each brief).**
`PL-8LDF`, `PL-2M9N`, `PL-41YP`, `PL-GQWP`, `PL-5N7T`, `PL-9LXK`, `PL-T9XJ`,
`PL-4RHP`, `PL-DHJ7`, `PL-B8V1`, `PL-NLP4`, `PL-LM8P`, `PL-NWTM`, `PL-B5LB`,
`PL-GTSL`. This is the 2026-09-17 candidate list, each re-read and still open;
`PL-NLP4` and `PL-NWTM` are `blocked` and stay members, since a root cause
explains an item whatever its status.

Four of them - `PL-LM8P`, `PL-B5LB`, `PL-GTSL`, `PL-T9XJ` - are one-off repairs
of one stale sentence each, which the head would re-point rather than close.
`PL-6ZQY` lists `PL-LM8P` as a drop candidate; being a drop candidate is a
question about whether that instance still reproduces, not about what caused
it, so it is named here and the drop stands or falls on `PL-6ZQY`'s own sweep.

**A confirmed floor rather than a census.** The store holds further instances
of the same sentence-to-tree link that this list does not name - `PL-0VFF`,
`PL-C25K`, `PL-N32Y` and `PL-FV7G` in `ROADMAP.md`, `PL-BHJW`, `PL-C7XV` and
`PL-0R06` in `docs/WORKING_NOTES.md`, `PL-DBGT` in the agent data files. They
are left out because they were read from their titles today and not from their
briefs, and the field is a recorded fact rather than an inference. A later
session working this head should expect the cluster to be larger than fifteen.

**Done when.** Either the convention above is adopted and recorded, with
`doc_check` resolving the links it creates, or it is refused with the reason
written where the next session meets it; and the fifteen members are re-pointed
at that decision or dropped against it. If the convention is adopted, `PL-036`
becomes its first instance rather than its statement.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none, and that
`PL-036` refuses to be one. On 2026-09-18 it became the head itself - the
second of the two endings its own `Done when` offered, since the first would
have meant widening `PL-036` against its own recorded decision.
