---
id: PL-WTXB
title: Remove the unreferenced docket milestone command
priority: P3
effort: S
status: ready
classes: refactor
feature: docket-store
touches: subprojects/docket
added: 2026-09-13
verify: ! bin/docket --help | grep -q milestone && uv run pytest subprojects/docket/tests/test_cli.py
---

**Problem.** Remove the unreferenced docket milestone command
**Why it matters.** Verified 2026-09-13: `milestone` is a registered subcommand
("release membership and progress") and nothing outside the CLI invokes it - not
`subprojects/docket/README.md`, not `.claude/skills/docket/SKILL.md`, not the
`Makefile`, not the hooks. The question it answers is answered elsewhere by
`bin/docket wave`, `status` and `release`. An unused command is not free: it is
listed in `--help`, so every session reading the command list weighs it and has
to work out that it is not the one they want, and it is code that must keep
passing the suite and keep agreeing with a store format nothing exercises it
against. `.claude/rules/apparatus-standard.md` is the bar this is judged at.

**Done when.** The `milestone` subcommand and its tests are removed,
`bin/docket --help` no longer lists it, and any line documenting it in
`subprojects/docket/README.md` goes with it. A worker who finds a caller this
search missed should stop and say so rather than remove a live command.
