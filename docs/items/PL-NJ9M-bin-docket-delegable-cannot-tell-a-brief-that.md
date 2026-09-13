---
id: PL-NJ9M
title: bin/docket delegable cannot tell a brief that determines the fix from one that leaves the choice open, so a hand-off meant to need no reading still does
status: untriaged
added: 2026-09-08
---

**Problem.** bin/docket delegable cannot tell a brief that determines the fix from one that leaves the choice open, so a hand-off meant to need no reading still does

**What was observed.** Reviewing the 86 items `bin/docket delegable` currently
offers, for a hand-off to an external (non-Claude) worker on 2026-09-08:
`PL-YNCW` (`docket new --touches` before the title swallows it) is offered, and
its brief ends "Options worth weighing at triage: `nargs="+"` with repeated
use, a comma-separated single value, or leaving the parser alone and fixing
only the error message", with a `**Done when.**` permissive enough to accept
any of the three. Nothing in the front matter distinguishes that from
`PL-38PN` (stale source line citations), whose brief names the wrong line
numbers *and* the right ones, leaving nothing to choose.

**Why it matters.** `delegable` exists so a session can hand work off without
reading the queue - the command says so, and `docs/worker.md` tells the worker
to stop and write `**Blocked.**` when a brief is unclear. Both behave
correctly here and the round trip still happens: the item is dispatched, read,
blocked and returned, which is the cost the command was built to remove. The
failure is not silent, so this is friction rather than a wrong answer, and it
falls hardest on a worker that cannot ask - a session in another vendor's
harness, which is the case that motivated the review.

**Not decided: which end to fix.** Either triage resolves the options before an
item may read as delegable (a `**Decision needed.**` heading already exists for
questions the owner owns, and this is a smaller kind), or `delegable` prints
the caution beside the item rather than withholding it. The second is cheaper
and admits that "the brief still has a choice in it" is a judgment no check can
make from front matter alone - unless the shape of a resolved brief is made
decidable, which is the third option and the largest. Related: `PL-S2L4` (the
delegable list offers items `docs/worker.md` forbids a worker to touch) is the
other half of "the list cannot be handed over as printed".
