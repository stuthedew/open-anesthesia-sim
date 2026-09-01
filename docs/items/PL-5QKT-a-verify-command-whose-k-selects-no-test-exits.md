---
id: PL-5QKT
title: A verify command whose -k selects no test exits 5, so it reads as discriminating forever
status: untriaged
added: 2026-09-01
---

**Problem.** `PL-D2GW` carried `verify: uv run pytest
subprojects/docket/tests/test_release.py -k gate`. No test in that file has
`gate` in its name, so pytest deselected all 27, printed `27 deselected` and
exited 5 - before the work and after it alike, until the item's own session
renamed the tests it was about to write.

`docket check` runs every open item's command and raises an advisory for the
ones that already pass, which is the "proves nothing" case it was built for.
Exit 5 is not exit 0, so a command that selects nothing reads to that check
as a command that correctly fails, and it stays invisible for as long as the
item is open.

**Why it matters.** The whole point of running the command before writing it
down is that an unrun command fails after a worker has done the work. This is
the failure mode one step further along: the command runs, the exit code is
non-zero, everything looks right, and it will report success the moment
somebody adds a test whose name happens to match - or never, which is worse,
because `docket verify` then accepts a delegated branch that did none of the
work and nothing distinguishes a finished item from an unstarted one.

It is also silent by construction. `-k` matching nothing is the same shell
exit as a real failure, so the only reader who can tell them apart is one
looking at the count line, and no check reads that.

**Where.** `verify.LandedReport`
(`subprojects/docket/src/docket/verify.py:417`) is the already-passes answer
and `checks.py:284` writes the sentence, so the counterpart belongs beside
both. Pytest's exit codes are the
discriminator: 5 is "no
tests collected", 1 is "tests failed", 0 is "passed", so the three are
already distinguishable without parsing output. A command that is not pytest
has no such code, and the check should say so rather than guess.

**Done when.** An open item whose `verify:` command selects no test is
reported, distinctly from one that fails. How many items this catches across
the current queue is worth printing at the same time - `PL-D2GW`'s was found
by hand, and nothing says it was the only one.
