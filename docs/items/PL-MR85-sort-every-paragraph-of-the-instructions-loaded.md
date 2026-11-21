---
id: PL-MR85
title: Sort every paragraph of the instructions loaded at launch into four groups (enforced by a named check, procedure for a skill, history, judgment no check can carry) and bring the table to the owner before any text moves
priority: P2
effort: M
status: needs-decision
classes: session-cost, planning
feature: standing-weight
touches: docs/items/PL-MR85-sort-every-paragraph-of-the-instructions-loaded.md
deferred-from: v0.7.0 - the sort changes how sessions are instructed, not the schematic, so the release does not wait on this answer
added: 2026-11-20
---

**Problem.** Sort every paragraph of the instructions loaded at launch into four groups (enforced by a named check, procedure for a skill, history, judgment no check can carry) and bring the table to the owner before any text moves

**Why it matters.** Every session loads 1,332 lines of instructions before it reads anything, as `python3 tools/doc_check.py check` reports. The instruction files grew from 60,199 characters on 2026-09-19 to 92,660 on 2026-11-20. The rule that every edit names what it replaces dates from 2026-09-19, so that rule has not stopped the growth. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to the sort, and to a line cap after it (project owner, 2026-11-20, ratified, "Agree with recs", over leaving the size to the rule that each edit names what it replaces).

**What to do.**

1. Take each paragraph of `CLAUDE.md`, `.claude/rules/expert-review.md`, `.claude/rules/instruction-writing.md` and `.claude/rules/plain-writing.md`.
2. Put it in one of four groups. A paragraph that a named check enforces keeps one line, which names the check. A procedure moves to a skill. History moves to `docs/resident-instructions.md`. Judgment that no check can carry stays.
3. For each paragraph in the first group, confirm that its check runs in `make check` or in CI. A hook alone does not count, because project threads do not run the repository's hooks.
4. Bring the table to the owner. Move no text before the owner approves it.

**Sorted 2026-11-21, at `origin/main` `2b17061`.** Nothing has moved. Each row below is a paragraph, a bullet, or a run of one-line bullets of the same kind. "Lines" counts its non-blank lines, and "Keep" counts how many would still load at launch after the move. The four files hold 1,171 non-blank lines, and about 639 would stay:

| Group | Lines now | Lines that stay |
| --- | --- | --- |
| Judgment that no check can carry | 755 | 584 |
| Procedure for a skill or a path-scoped rule | 275 | 35 |
| History | 104 | 11 |
| Enforced by a named check | 37 | 9 |

With headings, blank lines, the skill descriptions and the session-start digest, about 760 of the 1,332 lines loaded at launch would remain.

The sort adds path-scoped rules as a destination beside skills. A path-scoped rule loads when a session reads a matching file, and the thread that made this sort saw one load. Each check named in the table runs in `make check`, in CI, or in both, which was read from the `check` target of the `Makefile` and from `.github/workflows/quality.yml`. The co-author line in row 72 has no check, so it stays.

The 584 lines of judgment alone are almost three times the target in Claude Code's memory documentation: "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). Getting below that target would mean rewording the judgment itself, which is work for the `prose-quality` feature.

**Decision needed.** Do you approve the table, or which rows should change? **Recommendation: approve it as it stands.** The cap is then set at the total after the moves, and it can only go down.

| Row | File | Lines in file | Lines | Group | Keep | Goes to, or the check | What it says |
|---|---|---|---|---|---|---|---|
| 1 | CLAUDE.md | 3 | 1 | Judgment | 1 | stays | Scope: applies to all agents |
| 2 | CLAUDE.md | 5-18 | 14 | History | 3 | ledger | Map of where each rule lives; keep a 3-line map, move the routing story |
| 3 | CLAUDE.md | 22-32 | 11 | Judgment | 11 | stays | What the project is: solo, multi-year horizon |
| 4 | CLAUDE.md | 34-41 | 8 | Judgment | 8 | stays | The apparatus is not judged by its share of the queue |
| 5 | CLAUDE.md | 43-52 | 10 | History | 2 | ledger | Level versus trend (2026-09-19); keep the 2-line expectation, move the history |
| 6 | CLAUDE.md | 54-67 | 14 | Skill or path rule | 3 | docket triage mode (already holds it) | Generator pause; keep the 3-line rule, the full rule is already in triage.md |
| 7 | CLAUDE.md | 69-81 | 13 | Judgment | 4 | stays; trial clauses to coordinator mode | Product focus; keep the rule, move the Projects-trial clauses |
| 8 | CLAUDE.md | 85-90 | 6 | Judgment | 6 | stays | The outcome is the requirement |
| 9 | CLAUDE.md | 92-97 | 6 | Judgment | 6 | stays | Explain the approach whoever proposed it |
| 10 | CLAUDE.md | 99 | 1 | Judgment | 1 | stays | So, before building what was described: |
| 11 | CLAUDE.md | 101-102 | 2 | Judgment | 2 | stays | Goal wins over stated method |
| 12 | CLAUDE.md | 103-106 | 4 | Judgment | 4 | stays | Say when a better route exists |
| 13 | CLAUDE.md | 107-113 | 7 | Judgment | 7 | stays | Then stop and wait for the answer |
| 14 | CLAUDE.md | 114-123 | 10 | Judgment | 8 | stays | The gate's one trigger; drop the sentence explaining why the list is here |
| 15 | CLAUDE.md | 124-126 | 3 | Judgment | 3 | stays | Put the case in one read |
| 16 | CLAUDE.md | 127-129 | 3 | Judgment | 3 | stays | Do the shared parts while waiting |
| 17 | CLAUDE.md | 130-131 | 2 | Judgment | 2 | stays | Ask first when the goal is ambiguous |
| 18 | CLAUDE.md | 133-136 | 4 | Judgment | 4 | stays | A proposal is an invitation to think |
| 19 | CLAUDE.md | 138-141 | 4 | Judgment | 4 | stays | Clearly weaker: say so and wait |
| 20 | CLAUDE.md | 142-147 | 6 | Judgment | 6 | stays | Close call: build theirs, note trade-offs |
| 21 | CLAUDE.md | 148-149 | 2 | Judgment | 2 | stays | No approach proposed: choose and explain |
| 22 | CLAUDE.md | 151-155 | 5 | Judgment | 5 | stays | Ratified and specified decisions differ |
| 23 | CLAUDE.md | 157-166 | 10 | Skill or path rule | 1 | citation-drift path rule (docs/items/**) | How to write "(project owner, DATE, ratified)"; fires when writing an item |
| 24 | CLAUDE.md | 167-170 | 4 | Judgment | 4 | stays | Reopen a ratified decision on ordinary evidence |
| 25 | CLAUDE.md | 171-172 | 2 | Judgment | 2 | stays | Reopen a specified one only on a compelling argument |
| 26 | CLAUDE.md | 173-174 | 2 | Judgment | 2 | stays | Safety standard overrides both |
| 27 | CLAUDE.md | 176-187 | 12 | Judgment | 4 | stays; rationale to ledger | instruction-writing decides shape; move why this file states no format |
| 28 | CLAUDE.md | 189-195 | 7 | Judgment | 3 | stays | Ask-gate governs the deliverable, not the session; overlaps row 14 |
| 29 | CLAUDE.md | 197-205 | 9 | Judgment | 5 | stays | Ask-gate is not a licence to widen the goal |
| 30 | CLAUDE.md | 209 | 1 | Check | 1 | tools/import_boundary_check.py (CI) | Simulation time is explicit state: core may not import time or datetime |
| 31 | CLAUDE.md | 210 | 1 | Check | 0 | tools/import_boundary_check.py (CI) | Determinism: core may not import random, secrets or uuid; duplicates row 94 |
| 32 | CLAUDE.md | 211 | 1 | Check | 1 | pytest --cov-fail-under=100 on core (make check, CI) | Tests with every core change; the check holds coverage, not behaviour |
| 33 | CLAUDE.md | 212-236 | 25 | Judgment | 8 | stays; quotes and dates to ledger | One source of truth; names literal_home_check (CI) and fact_home_check (make check, CI) |
| 34 | CLAUDE.md | 237 | 1 | Check | 1 | tests/unit/test_parameters.py (pytest) | Parameters in validated, versioned data files |
| 35 | CLAUDE.md | 238-239 | 2 | Check | 1 | core/parameters.py typed payloads, tests/unit/test_parameters.py | No executable equations in data files |
| 36 | CLAUDE.md | 240-244 | 5 | Judgment | 5 | stays | Do not implement beyond the milestone |
| 37 | CLAUDE.md | 248-252 | 5 | Judgment | 2 | stays | Session cost is turns times context |
| 38 | CLAUDE.md | 254-261 | 8 | Skill or path rule | 1 | docket start mode (already holds it) | Reset at 150,000 tokens; this project's threads are exempt |
| 39 | CLAUDE.md | 262 | 1 | Judgment | 1 | stays | Batch questions and edits |
| 40 | CLAUDE.md | 263-264 | 2 | Judgment | 2 | stays | Targeted reads |
| 41 | CLAUDE.md | 265-267 | 3 | Judgment | 3 | stays | Delegate broad search to subagents |
| 42 | CLAUDE.md | 268-272 | 5 | History | 0 | ledger | Editing a resident file mid-session invalidates no cache |
| 43 | CLAUDE.md | 273-276 | 4 | Check | 1 | CI quality.yml runs ruff format, ruff check, mypy, pytest | Run the full suite before committing; keep the "pytest -q while iterating" line |
| 44 | CLAUDE.md | 277-284 | 8 | Judgment | 4 | stays; incident detail to ledger | Wait on a long run only through the harness |
| 45 | CLAUDE.md | 285-290 | 6 | Skill or path rule | 0 | coordinator mode | Fill a long wait with work; applies to Projects threads only |
| 46 | CLAUDE.md | 292-293 | 2 | History | 0 | ledger | Which model a session runs lives in maintainer.md |
| 47 | CLAUDE.md | 297-301 | 5 | Judgment | 2 | stays | Deterministic tooling: why it pays |
| 48 | CLAUDE.md | 303-308 | 6 | Judgment | 4 | stays | Put the decidable part in code |
| 49 | CLAUDE.md | 309-312 | 4 | Judgment | 4 | stays | Do not script the judgment |
| 50 | CLAUDE.md | 313-316 | 4 | Judgment | 3 | stays | Cheapest sufficient tier |
| 51 | CLAUDE.md | 317-319 | 3 | Judgment | 2 | stays | Summarizing counts |
| 52 | CLAUDE.md | 320-323 | 4 | Judgment | 4 | stays | Build only where it will run again |
| 53 | CLAUDE.md | 324-335 | 12 | Skill or path rule | 2 | apparatus-standard path rule (tools/**) | A check earns its place every run; the retirement test fires when editing a check |
| 54 | CLAUDE.md | 337-339 | 3 | History | 0 | ledger | A script answers identically every run |
| 55 | CLAUDE.md | 343-350 | 8 | Judgment | 3 | stays | The queue is docs/items; use the docket skill |
| 56 | CLAUDE.md | 352-354 | 3 | Judgment | 3 | stays | Two modes with opposite costs |
| 57 | CLAUDE.md | 356-359 | 4 | Judgment | 4 | stays | Ideation stays cheap |
| 58 | CLAUDE.md | 360-361 | 2 | Judgment | 2 | stays | Implementation goes deep |
| 59 | CLAUDE.md | 363-365 | 3 | Judgment | 3 | stays | Do not turn ideation into work |
| 60 | CLAUDE.md | 367-373 | 7 | Judgment | 7 | stays | The owner sets direction; sessions do the rest |
| 61 | CLAUDE.md | 375-389 | 15 | Judgment | 7 | stays; refused hard count to ledger | Involve the owner on a real trade-off, not size |
| 62 | CLAUDE.md | 391-406 | 16 | Skill or path rule | 4 | docket capture mode | Capture always; the how (feature grouping, WORKING_NOTES) moves |
| 63 | CLAUDE.md | 407-411 | 5 | Judgment | 3 | stays | Fix a small defect in place |
| 64 | CLAUDE.md | 413-434 | 22 | Skill or path rule | 0 | docket skill, building an item | The four fix-in-place conditions |
| 65 | CLAUDE.md | 436-455 | 20 | Skill or path rule | 0 | docket skill, building an item | Two per branch, commit form; the eleven-repairs history to ledger |
| 66 | CLAUDE.md | 456-462 | 7 | Skill or path rule | 1 | docket capture mode (already holds it) | File housekeeping before doing it |
| 67 | CLAUDE.md | 463-475 | 13 | Skill or path rule | 2 | docket triage mode (already holds it) | A generator's two endings |
| 68 | CLAUDE.md | 476-482 | 7 | Judgment | 7 | stays | A behavior change takes effect in the same session |
| 69 | CLAUDE.md | 484-486 | 3 | Judgment | 2 | stays | Route it; ask at what moment it is needed |
| 70 | CLAUDE.md | 488-498 | 11 | Skill or path rule | 1 | new path rule on CLAUDE.md and .claude/** | The four dispositions; needed only when editing an instruction file |
| 71 | CLAUDE.md | 500-513 | 14 | Check | 1 | tools/doc_check.py resident total (make check); the cap to be filed | Growth figures to ledger; the cap replaces "name what it replaces" |
| 72 | CLAUDE.md | 514-526 | 13 | Check | 3 | tools/branch_id_check.py, tools/pr_title_check.py (make check, CI) | Leading id is checked; claim and rename go to docket start; Co-authored-by line has no check and stays |
| 73 | CLAUDE.md | 527-537 | 11 | Skill or path rule | 3 | pull-request skill (already holds it) | Commit and push as you go; read the pull-request skill |
| 74 | CLAUDE.md | 538-548 | 11 | Judgment | 6 | stays; #1213 story to ledger | Read only means read only |
| 75 | CLAUDE.md | 549-555 | 7 | Skill or path rule | 2 | docket capture mode | Route intent by readiness |
| 76 | CLAUDE.md | 556-572 | 17 | Judgment | 9 | stays; the 20-day example to ledger | Friction that compounds is raised at once; four tests |
| 77 | CLAUDE.md | 574-580 | 7 | Judgment | 4 | stays; procedure is docket close-out | Sweep the docs before calling an item done |
| 78-108 | CLAUDE.md | 584-621 | 31 | Judgment | 31 | stays | Safety-critical clinical-output standard, every line |
| 109-115 | CLAUDE.md | 625-634 | 7 | Judgment | 7 | stays | Proactive expert review; never cite from memory |
| 116 | CLAUDE.md | 638-643 | 6 | Judgment | 6 | stays | Compact Instructions (the harness reads this heading) |
| 117 | expert-review.md | 3-7 | 5 | History | 0 | ledger | Why the file has no paths: |
| 118 | expert-review.md | 9-18 | 10 | Judgment | 3 | stays | Scope: simulator only |
| 119 | expert-review.md | 20-23 | 4 | Judgment | 1 | stays | Specialist standard, restated |
| 120-132 | expert-review.md | 25-54 | 26 | Judgment | 26 | stays | The 12 review domains |
| 133-140 | expert-review.md | 56-80 | 24 | Judgment | 20 | stays | Design principles; parse-don't-validate history to ledger |
| 141 | expert-review.md | 84-88 | 5 | Judgment | 5 | stays | Name the number that would change your mind |
| 142 | expert-review.md | 90-98 | 9 | History | 1 | ledger | Chang et al. 2024 (quantification fixation); keep a one-line citation |
| 143 | expert-review.md | 100-109 | 10 | History | 1 | ledger | OMB Circular A-4 threshold analysis |
| 144 | expert-review.md | 111-116 | 6 | History | 0 | ledger | Worked example, 2026-09-12 |
| 145 | expert-review.md | 120-125 | 6 | Judgment | 3 | stays | Count what undoing the cheap route costs |
| 146 | expert-review.md | 127-132 | 6 | Judgment | 6 | stays | Name what would change; count what is downstream |
| 147 | expert-review.md | 134-147 | 14 | History | 4 | ledger | Count runs both ways; Bezos 2015 and Cunningham 2009 citations move |
| 148 | expert-review.md | 149-161 | 13 | Judgment | 4 | stays; Fowler and PL-51B7 history to ledger | Waiting for another instance is the cheap route |
| 149 | expert-review.md | 163-167 | 5 | Judgment | 4 | stays | The five-year horizon breaks a tie |
| 150 | expert-review.md | 171-177 | 7 | Judgment | 7 | stays | Narrowest rule; instance, not rule |
| 151 | expert-review.md | 179-181 | 3 | Judgment | 2 | stays | It fails quietly |
| 152 | expert-review.md | 183-190 | 8 | History | 0 | ledger | PL-GDB0's three instances |
| 153 | expert-review.md | 192-196 | 5 | Judgment | 1 | stays | Pointer to the safety standard |
| 154 | expert-review.md | 198-210 | 13 | Skill or path rule | 3 | sources-and-docstrings path rule | A reference implementation measured nothing |
| 155 | instruction-writing.md | 1-7 | 7 | Judgment | 4 | stays | Precedence over other instructions |
| 156 | instruction-writing.md | 9-12 | 4 | History | 0 | ledger | Resident by necessity |
| 157 | instruction-writing.md | 14-18 | 5 | Judgment | 5 | stays | Scope of rules 1-9, 10-13 |
| 158-166 | instruction-writing.md | 20-45 | 26 | Judgment | 26 | stays | Rules 1-9, procedures the owner runs |
| 167 | instruction-writing.md | 47-65 | 19 | Judgment | 10 | stays; screenshot steps to run-the-app, coordinator clause to coordinator mode | Rule 10, decision first |
| 168-170 | instruction-writing.md | 66-73 | 8 | Judgment | 8 | stays | Rules 11-13 |
| 171 | instruction-writing.md | 75-79 | 5 | Judgment | 5 | stays | Rule 14, close with what the reader has to do |
| 172a | instruction-writing.md | 81-83 | 3 | Judgment | 3 | stays | Only what needs them |
| 172b | instruction-writing.md | 84-85 | 2 | Judgment | 2 | stays | Mark the recommendation |
| 172c | instruction-writing.md | 86-95 | 10 | Judgment | 7 | stays | Order the block |
| 172d | instruction-writing.md | 96-103 | 8 | Skill or path rule | 2 | pull-request skill | A line whose answer makes a commit; the draft and claim mechanics move |
| 172e | instruction-writing.md | 104-113 | 10 | Judgment | 10 | stays | Outside actions carry exact steps |
| 172f | instruction-writing.md | 114-115 | 2 | Judgment | 2 | stays | Keep it short |
| 172g | instruction-writing.md | 116-117 | 2 | Judgment | 2 | stays | Nothing to act on: say so |
| 172h | instruction-writing.md | 118-153 | 36 | Judgment | 22 | stays; dated owner quotes to ledger | Every line actionable now; which questions are the owner's |
| 172i | instruction-writing.md | 154-174 | 21 | Skill or path rule | 5 | docket housekeeping mode | Block is a handover; branch-sweep steps move, v0.3.8 story to ledger |
| 172j | instruction-writing.md | 175-181 | 7 | Judgment | 5 | stays | Name the group when lines are one problem |
| 172k | instruction-writing.md | 182-190 | 9 | Judgment | 7 | stays | Only what this discussion raised |
| 172l | instruction-writing.md | 191-202 | 12 | Judgment | 4 | stays; history to ledger | Refresh with bin/docket branch before the block |
| 172m | instruction-writing.md | 203-212 | 10 | Judgment | 7 | stays | Re-verify carried-over items |
| 172n | instruction-writing.md | 213-237 | 25 | Skill or path rule | 3 | docket next and start modes | Check other sessions before recommending work; list_sessions steps and PL-66FP story move |
| 173 | instruction-writing.md | 239-245 | 7 | Judgment | 5 | stays | Rule 15, clock times in US Central |
| 174 | plain-writing.md | 3-7 | 5 | History | 0 | ledger | Why the file has no paths: |
| 175 | plain-writing.md | 9-17 | 9 | Judgment | 9 | stays | Plain English for the named readers |
| 176 | plain-writing.md | 19-27 | 9 | Judgment | 9 | stays | Choose what goes in before writing |
| 177 | plain-writing.md | 29-45 | 17 | Judgment | 17 | stays | The reader table |
| 178 | plain-writing.md | 47-52 | 6 | History | 0 | tools/new_prose.py docstring | Why the table keeps five columns |
| 179 | plain-writing.md | 54-61 | 8 | Skill or path rule | 1 | path rule on docs/MODEL.md, docs/INTERFACE.md | Where the rest goes: "For developers" notes |
| 180 | plain-writing.md | 63-70 | 8 | Skill or path rule | 0 | sources-and-docstrings path rule (src/**) | Take a chosen value's reason from a record |
| 181-191 | plain-writing.md | 72-109 | 37 | Judgment | 37 | stays | Points 1-11 |
| 192 | plain-writing.md | 111-113 | 3 | History | 0 | ledger | Why points 7-11 exist (PL-ZT47) |
| 193 | plain-writing.md | 114-120 | 7 | Judgment | 7 | stays | Point 12, check every sentence |
| 194 | plain-writing.md | 122-129 | 8 | Skill or path rule | 1 | pull-request skill | Pull request titles; pr_title_check holds the ids |
| 195 | plain-writing.md | 131-136 | 6 | Judgment | 6 | stays | Match the code, not its prose |
| 196 | plain-writing.md | 138-143 | 6 | Judgment | 3 | stays | What this rule decides against the safety standard |
| 197-202 | plain-writing.md | 147-169 | 22 | Skill or path rule | 0 | path rules on docs/MODEL.md and src/** | MODEL.md paragraph and docstring examples |
| 203-204 | plain-writing.md | 171-196 | 25 | Judgment | 25 | stays | The reply example |
| 205-206 | plain-writing.md | 198-203 | 5 | Skill or path rule | 0 | pull-request skill (already holds the body examples) | Pull request body and title examples |

**What follows the owner's approval.** File the moves as items. File a check in `make check` that fails when the lines loaded at launch pass a cap. `CLAUDE.md` § "The queue, and how the project owner works" records that a ceiling on its size was refused earlier, and this answer reopens that.

**Generator check.** One-off. It is a sort the owner asked for, and no fact was misread to cause it.

**Done when.** The owner has approved or changed the table, and the moves and the cap are filed as items.
