---
id: PL-3Y96
title: The docket skill routes every undecided item to needs-decision, so a session triaging one that waits on an unscoped milestone will not reach for the blocked-by entry PL-W8XP added
priority: P2
effort: S
status: done
classes: docs, infra
feature: dev-tooling
milestone: v0.4.11
touches: .claude/skills/docket/SKILL.md
added: 2026-09-08
closed: 2026-09-08
pr: 477
verify: python3 tools/doc_check.py check && grep -qF 'the decision is a milestone being scoped' .claude/skills/docket/SKILL.md
---

**Problem.** The docket skill routes every undecided item to needs-decision, so a session triaging one that waits on an unscoped milestone will not reach for the blocked-by entry PL-W8XP added

**Why it matters.** `PL-W8XP` (blocked-by may name a milestone) built the
representation and documented it in `subprojects/docket/README.md`, which is
the reference a session reads when it already knows the field exists. The
skill is what a session reads when it is deciding *which* status to write, and
its triage mode says only this:

> **An item whose next step is a decision is triaged to `needs-decision`, not
> answered.**

That was the whole truth before and is now half of it. Two cases hide under
"its next step is a decision", and they want opposite statuses: a question
this project can answer — which is `needs-decision`, and is debt by
`docket.toml`'s `debt_classes` rule because somebody can go and resolve it —
and a milestone that has not been scoped, which is `status: blocked` with
`blocked-by: v0.6.0` and is not debt, because the only thing that resolves it
is a scoping round nobody can bring forward by working the item.

A mechanism nobody is routed to does not run. `PL-B9PY` is what the first
case cost: parked at `needs-decision` because that was the only shape
available, counted into Gate 1 as though it were resolvable, and then left
two days at a status that hid it from `bin/docket next` after the milestone
was scoped (`PL-MKFG`). The next item deferred into v0.6.0 gets the same
treatment unless the skill says otherwise, because the skill is what the
triage pass reads.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: triage" — the
`needs-decision` paragraph. Outside `PL-W8XP`'s declared `touches`, which is
why this is an item rather than a fix riding that branch.

**`PL-W8XP` shipped in `#478`, written by a different session than the one
that found this** (`PL-HX5C` records how both sessions came to implement it).
That changes nothing here: the four claims this edit makes were re-verified
against the merged implementation rather than the one they were written
beside — a scoped version raises the promotion advisory, a named-but-unscoped
one stays silent, a version the roadmap names nowhere is an error, and a patch
track is refused. The wordings differ slightly between the two; the edit cites
none of them, deliberately, because a skill paragraph quoting an error string
goes stale the first time somebody rewords it.

**Done when.** The skill's triage mode distinguishes the two cases and names
`blocked-by: <version>` for the second, so a session triaging an item that
waits on an unscoped milestone writes the status that says so.

**A skill edit rather than a check, and the reason is timing rather than
decidability.** `CLAUDE.md`'s routing rule asks at what moment a session needs
the rule and what is cheapest to deliver it then. A check is available here —
`_check_prose_dependencies` already matches "blocked on X" cues, and extending
it to versions would catch a brief saying "blocked on v0.6.0 being scoped"
while sitting at `needs-decision`. It was declined because it fires one step
too late: the session has by then already written the wrong status and moved
on, and somebody has to come back. The triage pass is the moment the status is
chosen, and the skill is what that pass reads, so disposition 2 lands the rule
where it is used. The two are not exclusive and the check stays available if
the skill alone proves not to hold.

**Found.** Building `PL-W8XP`, 2026-09-08.
