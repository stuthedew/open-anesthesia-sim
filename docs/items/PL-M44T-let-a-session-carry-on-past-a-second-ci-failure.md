---
id: PL-M44T
title: Let a session carry on past a second CI failure whose new cause it reproduced, and stop at four failed runs of one check
priority: P2
effort: S
status: ready
classes: docs
feature: projects-trial
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-10-19
payoff: a session stops on a repeated CI failure only when the owner has something to weigh, and never retries one check more than four times
verify: grep -q 'Four failed runs of one check on one pull request' CLAUDE.md
---

**Problem.** Let a session carry on past a second CI failure whose new cause it reproduced, and stop at four failed runs of one check

`CLAUDE.md`'s commit-and-push bullet stops a session whenever the same check
fails twice, and has it tell the owner before any retry. The stop exists to
keep a session from retrying blindly. On #1650 (`PL-L59K`) it fired when the
second failure had a different cause, which the thread had already reproduced
and fixed with a test-only change. The owner's only call at that stop was
whether to retry on Opus, and the thread was already on Opus, so asking him
settled nothing.

**Why it matters.** A stop that asks the owner a question with no trade-off
spends his attention and leaves the code place idle until he answers. Removing
the stop outright would let a session loop on a check forever, which the owner
asked never to happen (project owner, 2026-10-19: "as long as it doesn't get
stuck in an infinite loop").

**Done when.** The bullet says three things. A session carries on past a
second failure of a check on one pull request only when it reproduced the new
failure and its cause differs from every earlier failure of that check there. A
repeated cause, a failure it cannot explain, or a need for a stronger model
stops it, and its reply states what failed, why and what it wants, without
dressing that as a decision. Four failed runs of one check on one pull request
stop it whatever the causes, and that reply says the check failed four times,
names each cause, and asks a real question with options and a recommendation,
never only whether to try again (project owner, 2026-10-19: "make it clear
that it has failed 4 times and ask me a real question rather than just saying
can i try again"). `docs/resident-instructions.md` records the change and what
paid for it.

**Generator check.** Not a head. It explains no other open item: the stop has
fired without a decision behind it on #1650 alone that anyone recorded.
