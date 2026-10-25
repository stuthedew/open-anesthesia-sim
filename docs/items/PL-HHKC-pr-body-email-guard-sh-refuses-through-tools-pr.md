---
id: PL-HHKC
title: pr-body-email-guard.sh refuses through tools/pr_body_check.py --screen and so logs no line to the guards' refusal log, leaving it with no count when PL-SG93's verdicts are read
priority: P2
effort: S
status: done
classes: defect
feature: defect-review-2026-10
milestone: v0.6.7
touches: tools/pr_body_check.py, tests/unit/test_hook_blocks.py, docs/apparatus.md
added: 2026-10-25
closed: 2026-10-25
pr: 1802
payoff: every refusal of the pull request email guard is counted in the guards' refusal log, so PL-SG93's verdict on it is read from real counts
verify: uv run pytest -q tests/unit/test_hook_blocks.py -k 'email_guard or built_by_deny'
---

**Problem.** pr-body-email-guard.sh refuses through tools/pr_body_check.py --screen and so logs no line to the guards' refusal log, leaving it with no count when PL-SG93's verdicts are read

**Why it matters.** `PL-SG93` built the guards' refusal log so that each
guard's cost in defects can be weighed against what it blocks, and a guard with
no count looks as if it blocks nothing. That is the reading that retires it.
Every Python guard builds its refusal with `hook_input.deny`, which writes the
line. `tools/pr_body_check.py`'s `screen` built its own refusal JSON, so
`pr-body-email-guard.sh` refused with no line logged.

**Done when.** `screen` refuses through `hook_input.deny`, under the guard name
`pr-body-email-guard` and the rule `email-address`, and a test runs the hook
script with a session id and finds the line. A second test refuses any Python
file under `.claude/hooks/` or `tools/`, other than `hook_input.py`, that
builds a `permissionDecision` itself, so the next guard written that way fails
a test rather than going uncounted. The shell guards' fallbacks for a missing
`python3` cannot reach `deny` and are left as they are.

**Generator check.** A one-off. `PL-SG93` routed the Bash guards and
`owner_ask_guard` through `deny` and missed the one refusal built in `tools/`.
The new test is what makes the next copy fail.
