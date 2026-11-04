---
id: PL-8RGF
title: PL-SG93's refusal log counts a false refusal and each retry as a block, and its brief says Projects threads run no guard though thread files hold 45 of 118 logged lines, so the keep-or-retire verdicts due 2026-11-23 would read friction as value
priority: P2
effort: M
status: done
classes: defect
feature: defect-review-2026-10
milestone: v0.6.15
touches: docs/items/PL-SG93-the-bash-guard-hooks-account-for-74-defects.md, tools/hook_blocks.py, tests/unit/test_hook_blocks.py, .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py, docs/hook-blocks/README.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-03
closed: 2026-11-03
pr: 1993
payoff: the guard verdicts due 2026-11-23 rest on refusals judged true or false, not on a count inflated by false refusals and retries
verify: ! grep -qF 'runs no guard at all' docs/items/PL-SG93-*.md && ! grep -qF 'Projects threads add nothing to the count' docs/items/PL-SG93-*.md && grep -q 'def test_count_reports_a_burst_once' tests/unit/test_hook_blocks.py
---

**Problem.** PL-SG93's refusal log counts a false refusal and each retry as a block, and its brief says Projects threads run no guard though thread files hold 45 of 118 logged lines, so the keep-or-retire verdicts due 2026-11-23 would read friction as value

**Evidence, 2026-11-03.** A guard review in one session had three of its own commands refused as `gate-status-guard status-swallowed`, and none of them was a gate. They were `python3 -X importtime tools/pr_body_check.py --screen ... | tail`, `python3 tools/branch_id_check.py --hint ... | cut`, and a timing of `tools/doc_check.py` with its output sent to `/dev/null`. All three went into the real log. Of the 118 tracked lines, 23 repeat the same guard and rule in the same session within 2 minutes, and one session holds 13. The owner-ask guard logged 2 refusals, while 4 of its false refusals were filed on 2026-11-02 and 2026-11-03. The log records no matched pattern and nothing about what the session did next. So a count cannot separate a refusal that prevented an error from one that blocked correct work.

**What to fix before 2026-11-23.** Correct `PL-SG93`'s sentence about Projects threads, since `PL-X6VN` gave them the hooks. Have the verdict session judge a sample of refusals as true or false, rather than read the count as value. Logging which pattern refused would make that sample possible.

**Reproduced 2026-11-03.** `docs/hook-blocks/` now holds 125 distinct refusal lines, and 47 of them sit in the 13 files named `claude-project-thread-*`, so Projects threads do run the guards. `PL-SG93`'s brief still says twice that they run none: "Projects threads add nothing to the count" and "A Projects thread runs no guard at all". Counting a line as a repeat when the same session, guard and rule refused within 2 minutes before gives 26 repeats, and the busiest session holds 16 lines. `python3 tools/hook_blocks.py count` reports 91 `status-swallowed` refusals across 27 sessions and gives no sign of the repeats. Each logged line holds only the time, session, guard and rule, so nothing says which command or gate was refused.

**Why it matters.** `PL-SG93` will give each guard a keep, simplify or retire verdict from these counts on 2026-11-23. A false refusal and every retry it causes add to a guard's count, so the guard that blocks the most correct work looks the most valuable. Of the gate-status guard's refusals, at least five false ones were met on 2026-11-03 alone. Three are the guard review's above. The other two were met by the triage session that wrote this, each a command that fed a test payload to `tools/pr_body_check.py --screen` and read its output, which runs no gate (`PL-9PPJ`). If the method is not corrected before that date, the verdicts will be drawn from friction rather than from prevented errors.

**Done when.** `PL-SG93`'s brief no longer says that Projects threads run no guard. `python3 tools/hook_blocks.py count` reports a burst of refusals from one session, guard and rule within 2 minutes as one, or shows bursts apart, with a test in `tests/unit/test_hook_blocks.py`. The gate-status guard's logged rule names the gate it read, never the command text. `PL-SG93`'s "What is left" tells the verdict session to judge a sample of each guard's refusals as true or false before reading a count as value. All of it lands before 2026-11-23.

**Generator check.** One-off measurement-quality defect in `PL-SG93`'s method.

**Built, 2026-11-03.** `PL-SG93`'s brief no longer says that Projects threads run no guard, and its new section "Judge a sample before reading a count as value" tells the verdict session to judge up to ten bursts per guard as true or false. `python3 tools/hook_blocks.py count` now prints bursts beside refusals: a refusal less than 120 seconds after the one before it, from the same guard and rule in the same session, joins its burst. On the 125 tracked lines that gives 99 bursts. The gate-status guard logs its rule as `status-swallowed:<gate>`, with the gate's name as the guard read it and never the command. Lines logged before the change keep `status-swallowed`, so `count` lists them on a line of their own.
