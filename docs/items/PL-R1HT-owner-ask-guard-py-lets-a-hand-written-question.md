---
id: PL-R1HT
title: owner_ask_guard.py lets a hand-written question, options and recommendation carry an ask past arm's 'send the owner nothing' state, because arm --owner-ask exits 3 for six different answers and the hook then falls back to the form check meant for the coordinator
priority: P1
effort: S
status: done
classes: defect
feature: owner-ask-by-state
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-11-03
closed: 2026-11-03
pr: 1984
payoff: a thread whose pull request waits on the owner's read with no recorded ask can be told apart from the coordinator, so the guard can stop it sending anything
verify: grep -q 'def test_arm_owner_ask_tells_a_hold_for_the_owner_s_read_from_a_checkout_it_cannot_answer_for' subprojects/docket/tests/test_cli.py
---

**Problem.** owner_ask_guard.py lets a hand-written question, options and recommendation carry an ask past arm's 'send the owner nothing' state, because arm --owner-ask exits 3 for six different answers and the hook then falls back to the form check meant for the coordinator

**Reproduced 2026-11-03.** `refusal()` was run with `owner_ask` stubbed to return exit 3 and arm's line "send the owner nothing: hold - its pull request waits on the owner read, and no Owner-ask record says what to ask". "Read #1950 and merge it." is refused. The same text is let through once this is added: `Which unit should the label show? Option "mcg": keeps the label short. Option "mg": matches the pump. I recommend "mcg": it is what the item specifies.` The cause is in `subprojects/docket/src/docket/cli.py`. With `--owner-ask`, every answer that is not sendable returns `arming.NO_ASK`, so the hook cannot tell a held thread from the coordinator. `.claude/hooks/owner_ask_guard.py`'s `refusal()` then accepts any message that `renders_owner_ask` matches. `docs/maintainer.md` tells the owner "A thread cannot send the ask anyway", which this reproduction shows is false. The test in `tests/unit/test_owner_ask_guard.py` gives the coordinator exit 3, and it passes whether or not this is fixed.

**Fixed 2026-11-03.** `bin/docket arm --owner-ask` now gives each state its own exit status. It exits 0 with the recorded ask, 3 only where the pull request waits on the owner's read and no `Owner-ask` record says what to ask, 2 where it cannot answer, and 1 otherwise. `subprojects/docket/tests/test_cli.py`'s `test_arm_owner_ask_tells_a_hold_for_the_owner_s_read_from_a_checkout_it_cannot_answer_for` checks that a held branch exits 3 and the default branch exits 2, and `test_arm_owner_ask_prints_only_what_may_be_sent_to_the_owner` now expects 1 for a branch that arms and for one a claim holds. The hook's side is `PL-3D2F`. Its test of the reproduction above, `test_a_waiting_threads_ask_is_refused_until_it_records_one`, was run against the hook at `27754a0b`, and the hook let the hand-written question through: "assert None is not None".

**Generator check.** This belongs with `PL-3D2F`, and adds no head of its own. The fact misread was whether a thread's pull request waits on the owner's read. The hook inferred that from an exit status that six answers shared. The status is now distinct, so the hook reads the fact instead of inferring it.
