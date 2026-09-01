---
id: PL-BZCM
title: docket status shows no plan placement, so the feature survey a session leads with cannot say which work the current step includes
priority: P3
effort: S
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -k "status and scope"
status: ready
added: 2026-09-01
---

**Problem.** `render.format_status` receives the `plan` and uses it only for
the release offer at the bottom. The feature blocks above it are ordered by
progress and by name, and the `next:` item inside each is that feature's
highest-priority open item - neither asks `plan.scope` anything. So today's
output lists `numerical-domain 5/8 next: PL-9Y42` (validate wash-in against a
published human measurement, `v0.4.0` science scope) in the same undifferentiated
column as `delegation`, `parallel-sessions` and `dev-tooling`, which are what
`v0.2.8 - the workflow works` is about, with nothing distinguishing them.

**Why it matters.** This is the third surface of the seam `PL-1TPM` (`docket
next` ranked work the current milestone excludes), `PL-0RS6` (marking did not
reorder) and `PL-Q2BJ` (the digest's `Top:` line did not ask the plan at all)
have already been through, and it is the surface the `docket` skill tells every
session to *lead with*: "Answer at feature altitude first ... lead with `docket
status`".

It is a weaker case than the three before it, deliberately recorded as such.
`status` makes no project-altitude "do this next" claim - it is a survey, and
its one ranked block says in its own heading that it is "picked on priority
alone" - so nothing here contradicts the beat the way the digest's two lines
contradicted each other. What is missing is a mark, not a fix to an ordering.
The skill already mitigates it by requiring `docket wave` to be read first.

**Where.** `subprojects/docket/src/docket/render.py`, `format_status`. The
`plan: Wave | None` parameter is already threaded in, so `plan.scope` is at
hand; `Scope.placement` and `Scope.milestone` are the same two calls
`recommend` and `format_digest` make. The design question is where the mark
goes - per feature (a feature is placed by no structure the roadmap holds, so
it would have to be derived from its items) or on the `next:` item alone (a
fact `Scope` can answer directly, and the narrower claim).

Ordering is a separate question from marking, and `PL-0RS6` is the precedent
that they are separate items: reordering the `Underway` block away from
`-progress` would trade "finish what is nearly done" for "do what the step
names", which is a real trade rather than a fix, and wants its own decision.

**Found.** While closing `PL-Q2BJ` (2026-09-01), which named `status` as worth
checking at the same time. Not fixed there: `PL-Q2BJ`'s "Done when" is the
digest's `Top:` line, and adding a mark to `status` changes a second surface's
output budget and how the project's main survey reads - the project owner's
call rather than a widening of the item that found it.

**Done when.** A session reading `docket status` can tell which of the listed
work the current step includes, without running a second command.

**Triaged 2026-09-01, with the approach settled.** The project owner chose the
narrower of the two options in **Where.** above: the mark goes on the `next:`
item each feature row names, not on the row itself. A feature is placed by no
structure the roadmap holds, so a per-feature mark would have to be inferred
from its items and would claim more than `Scope` can prove; the `next:` item is
one id, and `Scope.placement` answers about an id directly. Build that, and
leave the row unmarked.

Ordering is still out of scope here, per **Where.**: the `Underway` block keeps
its `-progress` sort. Trading "finish what is nearly done" for "do what the
step names" is a real decision and wants its own item.

`P3` rather than `PL-Q2BJ`'s `P2`, and the brief above says why: this surface
makes no project-altitude claim to contradict, so what is missing is a mark
rather than a wrong answer. It sits with `PL-3576` and `PL-H8MQ`, the other
`P3` process defects of this family.

Not admitted to v0.2.8's frozen list. It was captured 2026-09-01, after the
2026-08-31 freeze, and admitting it is a decision about the release's size
rather than about the fix - `ROADMAP.md`'s "The gate is a snapshot, not a
moving target" is the rule, and the two reversals already recorded there were
written deliberately. Raise it for admission if v0.2.8 should carry the whole
family; otherwise it clears at the next gate.

The `verify:` selector matches no test today - `-k "status and scope"` exits 5
against `test_roadmap.py` on 2026-09-01 - so the new tests have to carry both
words, as `PL-Q2BJ`'s did.
