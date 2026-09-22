---
id: PL-3DN1
title: bin/docket release accepts a VERSION below the current one, so a typo silently downgrades pyproject.toml's version field
priority: P2
effort: S
status: ready
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-13
verify: grep -rq 'def test_a_version_below_the_current_one_is_refused' subprojects/docket/tests/ && uv run pytest subprojects/docket/tests/test_release.py subprojects/docket/tests/test_cli.py -q
---

**Problem.** bin/docket release accepts a VERSION below the current one, so a typo silently downgrades pyproject.toml's version field

**Why it matters.** `cmd_release` takes the version from `args.version or
resuming or ready.suggested_version` and hands it to the bump, which rewrites
`pyproject.toml` through `VERSION_RE.sub`. Nothing compares it against the
version already there, although `version_key()` sits in the same module and
orders versions numerically, so the comparison is available and simply not
made.

`docket.toml` sets `version_policy = "manual"`, which is what makes this
reachable rather than theoretical: the number is typed by a person at the
moment they are doing something else, and `make release VERSION=0.4.8`
against a tree at 0.4.18 is one keystroke away. The bump then succeeds, the
notes are written under the lower number, and every item in the cut is stamped
with it. Recovery is not a re-run - the stamps are already in the item files
and `bin/docket release` would next see a newer notes file above a lower
current version - so this is a typo that has to be unpicked by hand.

The guards that exist watch other things. `is_untagged()` checks the previous
release's tag, and `cuts_in_flight` watches other branches; neither reads the
requested number against the one in `version_file`.

**Done when.** `bin/docket release` refuses a `VERSION` below the version
`version_file` declares, naming both, before anything is written or stamped -
with the interrupted-cut resume still able to re-cut the version it is
resuming, and with the equal-to-current case decided explicitly rather than
falling out of the comparison. A test for each.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and it was never
partly overtaken - but one sentence of it was wrong on the day it was
filed.** The defect reproduces exactly as described where the number has no
notes file: `bin/docket release 0.2.0 --dry-run --no-fetch` prints
`0.4.28 -> 0.2.0` and `## v0.2.0 - 2026-09-19` and exits 0, with no refusal.
Nothing compares the requested number to `version_file`: `version_key` never
appears in `cli.py`, and none of the five refusal helpers there reads the two
against each other. No test exists, so the `verify:` still fails.

Two corrections. The brief's own example - `make release VERSION=0.4.8`
against a tree at 0.4.18 - does **not** get through: `already_released` catches
it, because v0.4.8 has shipped notes on the base, and the command exits 1. That
guard landed in `91b60d8` (`PL-66FP`, #323) on 2026-09-04, nine days before this
item was added, so the illustration was false at filing rather than overtaken.
And the brief's claim that no existing guard "reads the requested number
against the one in `version_file`" is not exhaustive: `already_released`
(`release.py:264-301`) does, for **equality** only. Ordering is the gap, and it
is a real one - so re-illustrate with a low number that never shipped, such as
`0.2.0`.
