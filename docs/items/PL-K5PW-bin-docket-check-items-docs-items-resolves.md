---
id: PL-K5PW
title: bin/docket check --items docs/items resolves config from docs/ rather than the repo root, so it reports a clean store as 112 errors
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-07
verify: uv run pytest -q subprojects/docket/tests/test_cli.py && grep -q 'def test_check_names_the_config_file_it_loaded' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket check --items docs/items resolves config from docs/ rather than the repo root, so it reports a clean store as 112 errors

**Why it matters.** `_load` resolves settings from `args.items.parent`, so
`--items docs/items` reads `docs/docket.toml`, finds none, and applies library
defaults to this project's store. That is deliberate and documented - pointing
`--items` at another project's queue must not silently apply this project's
policy to it - but the failure it produces here is loud and wrong in the
alarming direction: 112 errors on a store that `bin/docket check` calls clean a
second later. Observed 2026-09-07 while working `PL-D188` (the capture template
stranded above a brief).

A session that meets this mid-task reads it as the store having been corrupted
by its own edits, which is the most expensive possible misreading. The command
is one a session naturally types, because `--items` is the documented way to
point at a store and `docs/items` is where this one lives.

**Where.** `subprojects/docket/src/docket/cli.py`, `_load`. The cheap fix is a
line on the output naming which config file was loaded, or that none was found
and defaults are in force - `docket check` already prints a cost line, so there
is a place for it. Refusing the run is wrong: the behaviour is correct and
another project's store is a real use.

**Neighbour.** `PL-P757` (`bin/docket --items` pointed at a nested store makes
every annotating commit read as work) is a different defect on the same surface
and declares the same two files. The two are startable independently; land the
smaller first and expect to resolve against the other.

**Done when.** A run that found no `docket.toml` beside its store says so on
its own output, so a reader can tell a broken store from a store being read
under the wrong policy.
