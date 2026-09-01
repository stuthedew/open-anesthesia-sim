---
id: PL-5QKT
title: A verify command whose -k selects no test exits 5, so it reads as discriminating forever
priority: P2
effort: S
status: ready
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py
added: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'selects no test' subprojects/docket/src/docket/checks.py
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

**Triaged 2026-09-01.** Grouped with `delegation`, the feature that built the
`verify:` mechanism: `PL-G049` established that an unrun command is not a
specification, and this is the same claim one step further along - a command
that runs, exits non-zero, and still specifies nothing.

**Its own `verify:` deliberately avoids `-k`.** Writing `-k selects_no_test`
here would be the defect committing itself: confirmed against the source
while triaging, that flag deselects all 54 tests in the file and exits 5, so
`docket check` would read it as a command that correctly fails and this item
would sit in the queue proving nothing about itself. The command pairs the
whole file's suite with a `grep` for text the work adds, which is the shape
`.claude/skills/docket/SKILL.md` recommends for exactly this reason. Run
before being written down: it exits 1 today.

**Adjacent to `PL-20CQ`** (a `verify:` invoking `docket check` recurses without
bound), which is a different defect in the same two files. Both change how
`checks.py` treats the commands it runs, so they contend and should be worked
together or in sequence rather than in parallel.
