---
id: PL-P3B6
title: The verify replay costs every make check 31s to answer a question about the queue rather than the commit
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, Makefile, .github/workflows/quality.yml, subprojects/docket/README.md
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_check_does_not_replay_verify_commands_unless_asked' subprojects/docket/tests/test_cli.py
added: 2026-09-04
---

**Problem.** `verify.already_passing` runs every open item's `verify:` command
on every `bin/docket check`, and `bin/docket check` is in `make check`.
Measured 2026-09-04 on a four-core box: `bin/docket check` is 31.5 s, of which
`DOCKET_SKIP_LANDED=1 bin/docket check` shows 0.28 s is the store validation.
The other 31.2 s is 83 subprocesses. `make check` in full is about 67 s, so the
replay is a little under half the local gate.

**Why it matters.** It is the wrong question at that moment. The finding is
"work merged without its item's `status` being set" - the docstring names four
known instances, and all four are about work that had already *merged*. A
pre-commit gate on a feature branch is asking, once per commit, about the
default branch's merged state, which the commit being gated cannot have
changed.

The cost also grows in the wrong direction. `check`'s own advisory reports 149 s
of work across 8 workers for the 80 non-outlier commands, so narrowing the three
slow ones cannot take the run below about 19 s: the floor is set by the size of
the queue, and every item triaged to `ready` adds its command's runtime to every
future `make check`. The healthier the store gets, the more the gate costs.

**Where.** `subprojects/docket/src/docket/cli.py:170` passes
`landed=already_passing(root, items)` unconditionally. `checks.py:485` already
has the `landed is None` path - "a caller that did not ask; every command but
`check`" - so the mechanism for not asking exists and is used by `list`,
`digest` and `next`.

**Approach.** Add `--verify` to the `check` subparser and gate the
`already_passing` call on it. `make check` and `make docket` keep the bare
invocation and get the store validation alone; `.github/workflows/quality.yml`'s
`checks` job passes `--verify`, so CI coverage is exactly what it is today - the
same replay, on the same two events, in the same job. Nothing moves except which
caller pays.

Deliberately *not* a new report bucket saying "the replay did not run". The
`landed is None` path is silent for `list` and `digest` because they were never
the right caller, and after this neither is a pre-commit gate; a line printed on
every `make check` to say so would be the advisory-nobody-reads that
`CLAUDE.md` asks to retire rather than add. The `floor` job keeps its bare
`bin/docket check`: it has no `uv`, so the replay declines there anyway, and
that job is about portability under the 3.11 floor.

`DOCKET_SKIP_LANDED` is untouched. It guards re-entrancy - a `verify:` command
that itself runs `docket check` - which is a different question and still live
under `--verify`.

**Done when.** `bin/docket check` validates the store without running any
`verify:` command; `bin/docket check --verify` does both; CI runs the second
form; and `subprojects/docket/tests/test_cli.py` holds both paths.
