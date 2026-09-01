---
id: PL-JWXF
title: Scope the selects-no-test advisory to what next is about to offer, as the unspecified-command advisory already is
priority: P2
effort: S
status: done
classes: infra
feature: delegation
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-01
closed: 2026-09-01
commit: 44ede6c
pr: 148
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'whose command selects nothing' subprojects/docket/src/docket/checks.py
---

**Problem.** `PL-5QKT` gave `docket check` an advisory for open items whose
`verify:` command selects no test. Run against this store it names eighteen of
thirty-one, because `-k <the name the work will add>` is the shape
`.claude/skills/docket/SKILL.md` recommends and every unstarted item using it
selects nothing until its work lands. So the advisory is correct, fires on
every run, and can be discharged by nothing short of a campaign across the
whole backlog.

**Why it matters.** `_groom` has already been here, and its own comment says
what it cost: "Naming all of it fired on every run and could be discharged by
nothing short of a campaign, so it was an advisory that could not reach zero -
and the cost of one of those is not the items it names but the next advisory,
which gets read the same way." `docket check`'s advisories are the only
channel grooming has, and there are now two of them competing with an
eighteen-id line for the same attention.

The narrowing is not a softening. The moment an item is offered is the first
moment its selector can be checked against work someone is about to do, which
is the same argument `_groom` makes for asking about a missing command then
rather than earlier. Before that there is no one to act on it.

**Where.** `checks._check_selects_nothing`
(`subprojects/docket/src/docket/checks.py`) is the whole change: intersect
`landed.vacuous` with `offered`, which `analyze` already receives and already
hands to `_groom`, and carry the store-wide total in the sentence the way
`_groom` carries `len(unspecified)`. `verify.already_passing` keeps computing
the full set - the count is the half of `PL-5QKT` worth keeping, and it costs
nothing extra to produce.

A caller that supplied no `offered` names nothing, which is the same rule
`_groom` follows: an advisory that depends on ranking the queue is not owed by
a caller who did not ask for a ranking.

**Done when.** The advisory names only items `next` is about to offer, and
still prints how many of the store's open items select no test. A run where
nothing offered has the problem says nothing.

**Its `verify:` pairs the file's suite with a `grep`**, not a `-k`, for the
reason `PL-5QKT` documents. Run before being written down: it exits 1 today,
on the `grep`, having collected and passed the suite.

**Worked 2026-09-01.** `_check_selects_nothing` gained `offered` and
intersects `landed.vacuous` with it; `analyze` already had the set and already
hands it to `_groom`, so nothing new is computed and `verify.already_passing`
still returns the whole population. The total travels in the sentence -
"1 of 18 open item(s) whose command selects nothing, 31 checked" - so
narrowing costs no visibility of the scale.

**The `verify:` command caught its own defect first.** Written and run before
the work, it exited 1 on the `grep`, as intended. After the work it still
exited 1: the message had been built as an f-string broken across two literals
at exactly `whose command selects / nothing`, so the phrase never appeared
contiguously in the source and the `grep` could never match. That is a command
that would have passed only by accident - the same class of finding `PL-5QKT`
is about, arriving on `PL-5QKT`'s own successor. The source was reflowed so the
phrase is contiguous, and the command now exits 0 having exited 1 before.
