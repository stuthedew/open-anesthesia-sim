---
id: PL-554Q
title: Triage the 13 untriaged items left after #636, less the six that claude/gifted-fermi-m1cksg holds under PL-MQH0
priority: P2
effort: S
status: done
classes: planning
feature: queue-hygiene
milestone: v0.4.26
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 639
verify: bin/docket check && ! bin/docket triage | grep -qE '^PL-(7K8Y|7RYB|DMDF|NLP4|SH9Q|WXX8|ZLS5) '
---

**Problem.** Triage the 13 untriaged items left after #636, less the six that claude/gifted-fermi-m1cksg holds under PL-MQH0

**Why it matters.** Filed under `CLAUDE.md`'s housekeeping rule rather than for
its own sake: a triage pass takes commits of its own, so without an id it reads
as nobody's work to `flight`, `show`, `next` and `concurrent` alike, and goes on
reading that way after the push. `PL-LPHT` (#626) and `PL-LPHT`'s predecessors
set the precedent that a pass is filed.

**Six of the thirteen were left alone, and no ref could have said so.**
`PL-MQH0` - apply `feature: session-start-cost` to `PL-JH3T`, `PL-XD3C`,
`PL-0J9K`, `PL-MMVF` and `PL-RC86` - is being worked right now on
`claude/gifted-fermi-m1cksg`, which has pushed nothing, so
`branches_in_flight` cannot see it and `bin/docket triage` marked none of the six.
The session list is what saw it: a `RUNNING` session titled `PL-MQH0` whose
`task_summary` read "Checking field order and in-flight state of the six member
items". That is `.claude/skills/docket/SKILL.md`'s own rule working as stated -
it warns and never certifies - and the collision it avoided was direct, since
`feature:` sits two lines from `priority:` in the same front matter.

`PL-DMDF` is the seventh member of that diagnosis and `PL-MQH0` does not name it,
so it carries `feature: session-start-cost` from this pass instead.

**Done when.** The seven items not held elsewhere carry `priority`, `effort`,
`classes`, `touches` and a `feature` where one applies; every one set past
`untriaged` carries the full brief its status requires; every `ready` one names a
`verify:` command that was run first and failed on its `grep` half; and
`bin/docket check` reports zero errors.

---

**Done, 2026-09-16.** Seven triaged, six left to `claude/gifted-fermi-m1cksg`.
`PL-7K8Y` (P2/S/ready, `delegation`), `PL-DMDF` (P2/S/ready,
`session-start-cost`), `PL-SH9Q` (P2/M/ready, `parallel-sessions`), `PL-WXX8`
(P2/S/ready, `release-process`) and `PL-ZLS5` (P3/S/ready,
`worker-instructions`) each name a command that exits 1 today on its `grep` half
with the pytest half passing - the paired shape the skill prescribes, run before
it was written down. `PL-7RYB` went to `needs-decision` with a
`**Decision needed.**` naming three dispositions, because how a pre-2026-09-16
decision should be read is about what the owner's own past decisions meant.
`PL-NLP4` went to `blocked-by: PL-B8V1`, which is `needs-decision` on the same
question one paragraph over and which `PL-NLP4`'s own `Done when.` requires be
answered for both paragraphs at once.

`**Why it matters.**` was written for `PL-DMDF` and `PL-WXX8`, and
`**Done when.**` for `PL-WXX8` and `PL-7RYB`, since a status past `untriaged`
requires the full brief.

The four `pr` numbers the base was owed - `PL-FBXP` #633, `PL-N638` #632,
`PL-PHKP` #634, `PL-PX7V` #631 - rode this commit via `bin/docket record`, which
is what that advisory asks for rather than a commit of its own.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Six more arrived with the 2026-09-16 triage pass (`PL-554Q`). They are disposed of here rather than added to the list.** Four are `defect`s in the apparatus, found after the freeze. They are neither `safety` nor `science`, and their problems do not predate the freeze. So they are deferred for the ordinary snapshot reason. They are `PL-7K8Y` (`docket record` normalises front-matter key order as it writes `pr:`, so `docket verify` treats the backfill as a content edit), `PL-DMDF` (`docket digest` runs one `git diff` per item file, because `_superseded` is called with a one-element tuple inside a loop), `PL-SH9Q` (`docket stranded` misses an item that the base already carries and a branch has modified) and `PL-WXX8` (merged items owe a `pr` number, and the advisory's remedy addresses the one population that does not carry the debt). Each one lies entirely in the workflow lane, and none can affect a reader of the simulator.

> The other two wait on answers rather than on attention, as `PL-KQHN` does. `PL-7RYB` (nothing distinguishes a decision the owner ratified from one they specified, on anything recorded before 2026-09-16) is `needs-decision` on what the owner's own past decisions meant. That question belongs to the owner, not to a session. `PL-NLP4` concerns this subsection's own closing paragraph, whose figure of "66 dispositions" has not been true for some time. `PL-NLP4` is `blocked-by` `PL-B8V1`, which asks the same question one paragraph over. `PL-NLP4`'s `Done when.` requires one answer that covers both, not two answers that cover one each. That is also why the figure is left as it stands here. Correcting it in place would choose the form that `PL-B8V1` is open to decide.
