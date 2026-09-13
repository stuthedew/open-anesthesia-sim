---
id: PL-BZCM
title: docket status shows no plan placement, so the feature survey a session leads with cannot say which work the current step includes
priority: P3
effort: S
status: done
classes: defect, infra
feature: planning-cadence
milestone: v0.4.21
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_release.py
added: 2026-09-01
closed: 2026-09-13
pr: 544
verify: uv run pytest subprojects/docket/tests/test_release.py && grep -q 'def test_status_marks_the_next_item_the_open_gate_names' subprojects/docket/tests/test_release.py
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

**Done.** The mark goes on the id, as triage settled, and on the loose block's
ids as well as each feature row's `next:` — marking only the feature rows would
have made an unmarked entry under `Outside any feature` read as unplaced when
three of the five there are on the gate, which is a wrong inference the fix
itself would have created. The feature rows are unmarked and unreordered, per
**Where.**

Four answers rather than three, because `Scope` already draws a distinction
`placement()`'s three constants flatten: while a gate is open, the anchor's own
`Required scope` sits in `later` under the anchor's own version, which is
`OUT_OF_SCOPE` but is not "a later milestone names this". `placement_line`
already handles that case in prose, and the tag mirrors it:

| Tag | What it says |
| --- | --- |
| `[gate]` | on the anchor's frozen list, which is the current step |
| `[after the gate]` | in the anchor's own `Required scope`, which clearing its gate comes before |
| `[in scope]` | in the anchor's `Required scope`, its gate already clear |
| `[v0.5.1]` | a later milestone's section places it |
| unmarked | no section of the roadmap places the id |

**The legend is the load-bearing half, and it is why no tag is drawn for the
common case.** Twenty-four of this store's feature rows print a `next:` item and
five of them are on the gate, so a tag on every row would bury the ones that
matter; but an untagged row is then indistinguishable from one nobody looked at,
which is exactly the silence `PL-J790` named in `docket next`'s reason lines and
fixed there with a sentence per item. A sentence does not fit two dozen rows, so
`_plan_header` defines the blank once, in two lines above the survey, naming
only the tags the render actually drew.

**Where it landed.** `placement_mark` and `PLACEMENT_MARKS` in
`subprojects/docket/src/docket/plan.py`, beside `placement_line` rather than in
`render.py`, because the two must agree on the *relation* and that is
`scope.placement` in both — the same argument `placement_line`'s own docstring
makes for not sharing its wording. `_plan_header` and the call sites are in
`format_status`. `plan.py` is added to `touches`, which named only `render.py`
and `test_roadmap.py`; the tests went to `test_release.py`, where the existing
`format_status`-with-a-plan tests already live.

**The `verify:` command was one of the broken ones.** `-k "status and scope"`
selected nothing and exited 5, which reads as a command failing as intended and
would have gone on reading that way after the work. Replaced with the paired
shape the skill prescribes — the file's whole suite, and a `grep` for the test
the work adds — run and watched fail first: five of the seven new tests fail
against the unpatched `render.py`.
