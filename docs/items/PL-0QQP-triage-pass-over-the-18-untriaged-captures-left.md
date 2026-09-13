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
