---
id: PL-Z90G
title: Move CLAUDE.md's context-budget reset procedure and its housekeeping-filing rule into the docket skill, keeping one always-loaded trigger sentence for each
priority: P2
effort: S
status: ready
classes: session-cost
feature: skill-routing
touches: CLAUDE.md, .claude/skills/docket/modes, docs/resident-instructions.md
added: 2026-10-24
payoff: every session loads about 4,000 fewer resident characters, and the reset and housekeeping procedures arrive when a session starts an item or files unnamed work
verify: ! grep -q 'That floor measured 81,048' CLAUDE.md && ! grep -q 'Every in-flight guard matches a' CLAUDE.md
---

**Problem.** Move CLAUDE.md's context-budget reset procedure and its housekeeping-filing rule into the docket skill, keeping one always-loaded trigger sentence for each

**Why it matters.** `CLAUDE.md` § "Session and tool-use efficiency" carries the context-budget reset procedure, about 2,900 characters by a rough split on 2026-10-24. `CLAUDE.md` § "The queue, and how the project owner works" carries the rule to file housekeeping before doing it, about 1,300 characters. Both apply at moments the docket skill already covers: starting an item, and filing repository work that no item names. `.claude/skills/docket/modes/capture.md` § "Mode: housekeeping nobody filed" already holds most of the housekeeping rule, so for that rule the move is mostly cutting the copy in `CLAUDE.md`.

**What `PL-SN2Z` found, 2026-10-24.** A skill named by a resident trigger started first in 8 of 8 sessions whose request named its moment, including starting a named item, which is when the reset check fires. The housekeeping rule fires mid-task, at the first edit to unfiled work, and `.claude/hooks/docket-branch-guard.sh` already fires there. Keep a resident sentence for each that names its moment.

**Waited on** `PL-6VJ3` and `PL-JRVV`, which also edited `CLAUDE.md`, so that no paragraph was moved by one item and deleted by another. Both closed on 2026-10-24. `PL-6VJ3` moved `CLAUDE.md`'s generator rules into `.claude/skills/docket/modes/triage.md`. `PL-JRVV` retired two sentences that a check enforces and kept both paragraphs this item moves. `CLAUDE.md` is now 48,842 characters.

**What stays always loaded.** One sentence for each rule: check spend with `python3 tools/context_reading.py` before starting an item, and file an item before doing work that no item names. The moved text goes into the mode files rather than the skill's front page. The front page is sized to come back whole after compaction, which keeps only the first 5,000 tokens of a skill.

**Done when.** Each procedure lives in one docket mode file. `CLAUDE.md` keeps one trigger sentence for each. `docs/resident-instructions.md` records the move, and `make check`'s resident total shows the cut.

**Generator check.** None. The owner asked for this work after the comparison with testdouble/han, and no fact was misread to produce it.
