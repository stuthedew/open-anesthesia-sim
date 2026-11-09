---
id: PL-0QQP
title: Triage pass over the 18 untriaged captures left behind by the v0.4.14 range
priority: P2
effort: M
status: done
classes: infra
feature: queue-hygiene
milestone: v0.4.15
touches: docs/items
added: 2026-09-12
closed: 2026-09-12
pr: 503
not-delegable: A triage pass has no command that can prove it: 'bin/docket check reports no untriaged items' passes on any tree where nobody has captured anything, and the verify: commands this pass writes each prove their own item's work rather than this one's. The pass is judged by make docket, make check, and by whether each item's fields and brief survive being read by the session that starts it.
---

**Problem.** Triage pass over the 18 untriaged captures left behind by the v0.4.14 range

**Why it matters.** 18 captures arrived in the v0.4.14 range without fields or
briefs, which is the shape `docket.toml`'s `untriaged_stale_days` exists to stop
becoming permanent: an untriaged item is invisible to `bin/docket next`, so it is
neither ranked, counted into a debt gate, nor offered to any session, and a pile
of them is a second queue nobody reads. Several of these are upstream of work
already in flight - `PL-PQQ2` sits on the workflow lane's top pick, `PL-DZFJ`
sits on a `P1` `safety` item that is startable today - so leaving them
untriaged hides exactly the findings that should be changing what gets started
next.

**Done when.** Every untriaged capture carries `priority`, `effort`, `classes`,
`touches` and where it belongs a `feature`; each is at `ready` with a `verify:`
command that has been run and seen to fail, at `ready` with a `not-delegable`
reason where no command can prove it, or at `needs-decision` with the question
stated; each brief carries **Problem.**, **Why it matters.** and **Done when.**;
and `make docket` and `make check` pass.

**What this pass did not touch.** `PL-CSHL` (the pre-registered test of the
vcs.py batch closure) was skipped: its file is already edited on
`origin/claude/ready-vcs-batch-closure-xrvfya`, and a second answer here would be
a second resolution of the same file. It is left to that session.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it. Its paragraphs also dispose of entries that they count without naming: `PL-77SV`, `PL-H9GV`, `PL-JXVD`, `PL-LF2C`, `PL-PQQ2`, `PL-T8PT`, `PL-TTMF`, `PL-3V6C`, `PL-7XTS`, `PL-8T3Z`, `PL-BHVM` and `PL-LKGL`.

> **Fourteen more from the 2026-09-12 triage pass over what the v0.4.14 range left untriaged** (`PL-0QQP`). Twelve lie wholly in the workflow lane and sit exactly where the first thirty do. They were captured after the 2026-09-06 freeze, they are `P2` or `P3`, they are neither `safety` nor `science`, and they are apparatus held to `.claude/rules/apparatus-standard.md`'s deliberately lower bar. The refilling-queue arithmetic in the four paragraphs above is unchanged and is still the reason. This gate is not draining, and fourteen entries would add another tenth to it.
