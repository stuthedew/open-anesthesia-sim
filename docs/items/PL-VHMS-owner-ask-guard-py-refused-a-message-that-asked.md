---
id: PL-VHMS
title: owner_ask_guard.py refused a message that asked for nothing: wait for your read
priority: P3
effort: S
status: done
classes: defect
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
added: 2026-11-02
closed: 2026-11-02
pr: 1948
payoff: a session can tell the owner that later pull requests will hold for the read without the guard refusing the reply
verify: grep -q '_foretold' .claude/hooks/owner_ask_guard.py && grep -q 'each will wait for your read' tests/unit/test_owner_ask_guard.py
reenters: PL-TLPH
---

**Problem.** On 2026-11-02 `.claude/hooks/owner_ask_guard.py` refused a thread
reply that said "Because each one changes MODEL.md, each will wait for your
read". The sentence stated a fact about what would happen and asked the owner
for nothing in that reply. The guard read "wait for your read" as an ask for a
generic read, which `owner-ask-not-generic-read` forbids. The reply was reworded
to pass.

**Why it matters.** A false refusal costs a reword each time, and teaches a
session to avoid stating that a pull request will hold for the owner's read,
which the owner needs to know.

**How.** Read the guard's pattern for a read ask and narrow it to a request
form, such as an imperative or a question addressed to the owner, so a
statement in the future tense passes. Add the refused sentence as a test case
that must pass.

**Done when.** The guard passes the sentence above and still refuses the asks
its tests already list.

**Generator check.** An instance of `PL-TLPH`'s fact, "whether the owner may be
sent a read or merge ask about a pull request", like `PL-YGR6` and `PL-XR8B`
before it. The guard leans toward refusing on purpose, and its refusal asks for
an item each time it is wrong, so each false refusal is a narrowing with a test
row rather than a sign of a live generator. Recorded as `reenters: PL-TLPH`.

**Fixed 2026-11-02.** `asked()` in `.claude/hooks/owner_ask_guard.py` now lets
one form of the hold pattern (`HOLD_FOR_YOUR_READ`, "waits on your read",
"ready for your review") through. A modal such as "will", "would", "'ll" or "is
going to" must come just before the verb, with at most one word between them,
as "be" does. The hold still counts as an ask when its subject is "it", "this" or "that", or
when its sentence names a pull request in any form. So "each will wait for your
read" passes, while "#1945 will wait for your read", "The pull request will
wait for your read" and "It will wait for your read" are still refused, because
each may be about a pull request that exists. The hole this leaves is a future
hold about an existing pull request whose sentence neither names it nor points
at it, such as "They will need your review" written about open ones. `tests/unit/test_owner_ask_guard.py` adds the
refused sentence and two other future holds to the replies let through, and
five future holds to the asks refused.
