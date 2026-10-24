---
id: PL-6VJ3
title: The resident instruction set grew from about 37,000 characters on 2026-09-01 to 90,700 on 2026-10-19: route CLAUDE.md's generator-tier, impairs-generators and pause paragraphs to the docket skill, where triage applies them
priority: P1
effort: M
status: ready
classes: session-cost
touches: CLAUDE.md, .claude/skills/docket/modes/triage.md, docs/resident-instructions.md
feature: defect-review-2026-10
added: 2026-10-19
payoff: every session loads about the generator rules only the two sentences it needs before triage, and reads their reasoning in the skill where triage applies it
not-delegable: the work is choosing what the two resident trigger sentences say and where they sit so that they still fire before triage; a command can count characters but not show that the rules still load at the right moment, and a headless worker cannot put that wording to the owner
---

**Problem.** The resident instruction set grew from about 37,000 characters on 2026-09-01 to 90,700 on 2026-10-19: route CLAUDE.md's generator-tier, impairs-generators and pause paragraphs to the docket skill, where triage applies them

**Why it matters.** The resident set loads in every session, and its growth is not matched by any fall in the defect rate. Prose that only triage needs costs context in every turn of every other session.

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** These sizes cover `CLAUDE.md` plus the `.claude/rules` files with no `paths:`, at the last `main` commit of each day:
- 2026-09-01: 37,305 characters
- 2026-09-22: 68,288
- 2026-10-08: 77,534
- 2026-10-19: 90,748, of which 8,700 were added in the week before

The falls in the defect rate lined up with specific code fixes in specific weeks. None lined up with a rule being added, though the rules grew steadily. `PL-LN69` (testing whether each rule changes behaviour) was dropped on 2026-09-21.

**Decided** (session, 2026-10-19; the owner asked why this was put to them, and it should not have been): route the reasoning and history in `CLAUDE.md`'s generator-tier, `impairs-generators` and pause paragraphs to `.claude/skills/docket/modes/triage.md`. Keep one resident trigger sentence for each of two rules that fire before any triage. The pause applies before building any workflow mechanism. The "fix it or end the reply with a fresh-session prompt" ending applies in the reply that finds a generator. Moving those wholesale would load them too late, the failure `PL-WWDT` and `PL-4S6C` record. `bin/docket generators` reported no head still generating on 2026-10-19.

**Done when.** The reasoning lives in the skill, `CLAUDE.md` keeps the two trigger sentences and a pointer, `docs/resident-instructions.md` records the move, and `make check`'s resident total shows the cut.

**Triage** (project owner, 2026-10-20, ratified, over leaving it eligible for a headless worker). P1, worked in the same interactive session as `PL-JRVV` (retiring `CLAUDE.md` rules a check already enforces), so that no paragraph is moved by one and deleted by the other.

**`PL-S2NL` went first, 2026-10-24.** It moved `CLAUDE.md`'s pull request procedure, the commit-and-push and base-merge bullets, into `.claude/skills/pull-request/SKILL.md`, and left one trigger bullet in their place. `docs/resident-instructions.md` § "The pull request procedure, routed to a skill 2026-10-24" records what stayed and why. Measure this item's cut against that smaller `CLAUDE.md`.
