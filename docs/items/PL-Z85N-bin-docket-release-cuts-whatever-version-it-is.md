---
id: PL-Z85N
title: bin/docket release cuts whatever version it is handed, so the reserved-version answer exists only in the advisory digest and nothing objects on the cut path
priority: P2
effort: S
status: done
classes: defect
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md
added: 2026-09-14
closed: 2026-09-30
pr: 1228
verify: grep -q 'def test_a_version_the_roadmap_reserves_is_refused_on_the_cut_path' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket release cuts whatever version it is handed, so the reserved-version answer exists only in the advisory digest and nothing objects on the cut path

**Verified 2026-09-14, re-confirmed 2026-09-30.** `RESERVED` is produced by
`release_offer` in `subprojects/docket/src/docket/release.py` and consumed only
in `render.py`, by `format_status` and `_release_advice` - the survey's and the
digest's own rendering. It appears nowhere in `cli.py`, so `cmd_release` never
asks the question: it reads the plan only after every refusal, for the
hand-off. The answer therefore exists only as text in an advisory.

Reproduced 2026-09-30 on 0.5.17, with `ROADMAP.md` reserving 0.6.0, 0.7.0 and
0.8.0: `bin/docket release 0.6.0 --dry-run` exits 0 and prints v0.6.0's notes,
and the only objection it raises - no claim on the release train - prints the
`bin/docket new --resource release-train "Cut v0.6.0 ..."` line that files a
release item under the reserved number.

**Found while working it, 2026-09-30.** Asking on the cut path exposed a false
reservation in the reading itself: `_reserved_versions` in
`subprojects/docket/src/docket/roadmap.py` counted a `## Current baseline: vX`
heading as a milestone section, so a roadmap written ahead for the cut of vX
reserved vX for a milestone with no name. The digest already printed `the
roadmap gives 0.2.6 to ""` in that state; the new refusal failed
`test_a_release_whose_roadmap_is_already_written_says_nothing_is_owed`.
Baseline sections are now left out by kind: they record a release rather than
plan one.

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
an unfinished milestone, naming the milestone, on the cut path as it refuses an
untagged previous release - and the refusal is overridable only by the roadmap
changing, not by a flag. A dry run is refused too, as a version below the
current one is: a reserved number is a wrong number rather than a state a dry
run exists to review, and the train refusal a dry run would otherwise print
hands over a command filing a release item under it. A roadmap that exists but
cannot be read refuses the cut rather than skipping the question, as an
unreadable tag list does. `subprojects/docket/tests/` covers the refusal - the
brief first named `tests/unit/`, where the release command has no tests.
