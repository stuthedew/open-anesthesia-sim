---
id: PL-XR8B
title: owner_ask_guard.py refused a message that asked for nothing: over to you' and 'your call' beside a pull request
priority: P2
effort: S
status: done
classes: defect
feature: review-hold
milestone: v0.6.0
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
added: 2026-10-20
closed: 2026-10-20
pr: 1688
verify: grep -q 'quote mark is a mention' .claude/hooks/owner_ask_guard.py && grep -q 'PL-XR8B' tests/unit/test_owner_ask_guard.py
reenters: PL-TLPH
---

**Problem.** owner_ask_guard.py refused a message that asked for nothing: over to you' and 'your call' beside a pull request

**What happened.** On 2026-10-19 this thread edited one of its own replies on
#1688 to strike through an out-of-date ask. The reply described the hook's new
hand-off rule and listed the words it counts, such as "over to you" and "your
call", in quote marks in a sentence that also said "pull request". The hook
read that sentence as an ask and refused the edit. Nothing in the reply asked
the owner to read or merge anything.

**Fix.** A hand-off just after a quote mark is a mention, not an ask, so
`_HANDOFF` in `.claude/hooks/owner_ask_guard.py` no longer matches there. Two
rows in `tests/unit/test_owner_ask_guard.py` pin it, with straight and curly
quote marks. Both failed against the hook before the fix
(`pytest tests/unit/test_owner_ask_guard.py -k progress`: 2 failed, 13
passed). The recorded Owner-ask line on #1688 quoted the same two words, so it
matched the rule it describes for the same reason.

**Generator check.** Not a generator. It is one defect in the hand-off pattern
that PL-TLPH added the same day, and it has no other members.
