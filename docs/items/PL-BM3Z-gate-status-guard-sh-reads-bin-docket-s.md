---
id: PL-BM3Z
title: gate-status-guard.sh reads bin/docket's subcommand as its first argument, so a gate after docket's own options - bin/docket --no-fetch check 2>&1 | tail - is read as no gate and loses its status unrefused
status: untriaged
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads bin/docket's subcommand as its first argument, so a gate after docket's own options - bin/docket --no-fetch check 2>&1 | tail - is read as no gate and loses its status unrefused

**Found 2026-09-26 working `PL-QMN0`**, as hook payloads on `6efd8c41`:
`bin/docket --no-fetch check 2>&1 | tail -3`, `bin/docket --no-fetch verify
PL-QMN0 | tail` and `bin/docket --items docs/items check | tail` all pass the
gate guard, while `bin/docket check --no-fetch | tail` is refused.
`bin/docket --no-fetch check` is a command docket runs (exit 0 the same day):
its usage line takes `--items`, `--today`, `--now`, `--no-git` and
`--no-fetch` ahead of the subcommand, and each subparser takes them again after
it. `gate()` in `.claude/hooks/gate-status-guard.sh` tests `arguments[0] in
DOCKET_GATES`, so any of those ahead of `check` or `verify` stands where the
subcommand is read. `subprojects/docket/README.md` offers `--no-fetch` to "a
caller that already refreshed", and the session-start digest names it on its
own refs line, so this is a spelling a session can reach for rather than a
constructed one.

It is `PL-QMN0`'s shape one program over: that item reads `uv run`'s program
past uv's own options on either side of `run`, and here the word read is a
subcommand past docket's. Docket's grammar is argparse's, in
`subprojects/docket/src/docket/cli.py`, which also takes an unambiguous
abbreviation of a long option (`allow_abbrev`).
