---
id: PL-Z85N
title: bin/docket release cuts whatever version it is handed, so the reserved-version answer exists only in the advisory digest and nothing objects on the cut path
priority: P2
effort: S
status: ready
classes: defect
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, tests/unit
added: 2026-09-14
verify: uv run pytest tests/unit/test_docket_digest_hook.py && grep -q RESERVED subprojects/docket/src/docket/cli.py
---


**Problem.** bin/docket release cuts whatever version it is handed, so the reserved-version answer exists only in the advisory digest and nothing objects on the cut path

**Verified 2026-09-14.** `RESERVED` is produced in
`subprojects/docket/src/docket/release.py:556` and consumed in exactly one
module: `render.py:1328` and `:1467`, which are the digest's own rendering. It
appears nowhere in `cli.py`, so `cmd_release` never asks the question. The
answer therefore exists only as text in an advisory.

**Why it matters.** The guard is on the reading path and not on the writing one.
A session that reads the digest is told the version is reserved; a session that
runs `make release VERSION=0.5.0` because it was asked to, or because it read
the reserved version as the next one to cut, is not stopped. The consequence is
the one `PL-6T4L` already priced: a release cut under a milestone's name with
most of the milestone missing, `milestone:` stamped onto items that are not that
milestone's, and notes that are permanently wrong about what shipped.
`bin/docket release` already refuses two other things on the cut path - an
untagged previous release, and a cut another session is carrying - so this is a
missing member of a set that exists rather than a new kind of guard.

**Done when.** `bin/docket release` refuses a version the roadmap reserves for
an unfinished milestone, naming the milestone, the same way it refuses an
untagged previous release - and the refusal is overridable only by the roadmap
changing, not by a flag. `tests/unit/` covers the refusal.
