---
id: PL-K5PW
title: bin/docket check --items docs/items resolves config from docs/ rather than the repo root, so it reports a clean store as 112 errors
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.5.0
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-09-07
closed: 2026-09-21
pr: 846
verify: uv run pytest -q subprojects/docket/tests/test_cli.py && grep -q 'def test_check_names_the_config_file_it_loaded' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-20 PL-T441
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-K5PW (S) bin/docket check --items docs/items resolves config from docs/ rather than the repo root, so it reports a clean store as 112 errors
