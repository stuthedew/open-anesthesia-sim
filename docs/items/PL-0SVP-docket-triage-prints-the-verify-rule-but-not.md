---
id: PL-0SVP
title: docket triage prints the verify: rule but not the payoff: rule, so a triage pass writes --status ready and meets a refusal the rule list never named
priority: P2
effort: S
status: done
classes: defect
feature: recommendation-rationale
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-19
payoff: a triage pass learns the payoff rule from the rule list instead of from a refusal it could not have predicted
verify: grep -q 'def test_triage_states_the_payoff_rule_before_a_pass_writes_ready' subprojects/docket/tests/test_cli.py
---

**Problem.** docket triage prints the verify: rule but not the payoff: rule, so a triage pass writes --status ready and meets a refusal the rule list never named

**Why it matters.** `render._triage_rules` is the one surface whose job is to
state the rules a triage pass's answers have to satisfy, read from `docket.toml`
and the checker so the pass is held to what `docket check` will hold it to
rather than to what anybody remembers. It names the `verify:` gate whenever
`verify_required_from` is set. `PL-WYKF` added a second gate at the same status
and did not add it here, so from 2026-09-20 a pass would write `--status ready`,
be refused for a field the rule list never mentioned, and have to go and find
out why. The cost is one wasted round per triaged item, and it lands on the
command this project built specifically so triage would not have to remember
anything.

**Where.** `subprojects/docket/src/docket/render.py`, `_triage_rules`.

**Done when.** `bin/docket triage` states the `payoff:` requirement whenever
`payoff_required_from` is set, and says nothing about it where the rule is off.
Stated in `_triage_rules` rather than in `_unset`, which is where `verify:` is
not stated either: both gates fire at `ready` rather than at capture, so
listing either beside `priority` would mark as missing a field the item does
not yet owe.
