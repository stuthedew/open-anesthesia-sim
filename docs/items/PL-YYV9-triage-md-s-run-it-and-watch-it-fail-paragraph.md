---
id: PL-YYV9
title: triage.md's 'Run it and watch it fail' paragraph says docket check --verify raises an advisory that CI catches only after the push, but the replay has been an error since PL-71P4, make check runs it scoped to the branch, and since PL-FTDB bin/docket set --verify refuses a passing command as it is written
status: untriaged
touches: .claude/skills/docket/modes/triage.md
added: 2026-09-26
---

**Problem.** triage.md's 'Run it and watch it fail' paragraph says docket check --verify raises an advisory that CI catches only after the push, but the replay has been an error since PL-71P4, make check runs it scoped to the branch, and since PL-FTDB bin/docket set --verify refuses a passing command as it is written

**Found 2026-09-26 closing `PL-FTDB`**, in its docs sweep; `PL-FTDB`'s
`touches` stop at `cli.py` and `test_cli.py`, so the paragraph was not its to
edit. `.claude/skills/docket/modes/triage.md` § "Run it and watch it fail, not
merely run it" says `docket check --verify` "raises an advisory for the ones
that pass" and that "CI is what passes that flag, so it is caught after the
item is written *and* after it is pushed". Three things have moved under it:
`checks.py` reports an open item whose command already passes as an error
(`PL-71P4`); the `Makefile`'s `check` target runs `bin/docket check --verify
--verify-base origin/main`, so a local `make check` replays every item the
branch changed; and `bin/docket set --verify` now runs the command it writes
and refuses one that already passes (`PL-FTDB`). The advice itself, to see the
command fail before recording it, still stands; only the account of when the
tools catch a skipped step is stale.
