---
id: PL-C0C0
title: docket check's unmerged-cut advisory measures from the branch's merge-base with the base, so merging the base in - the absorb route's own first step, and what update-armed.yml does to an armed release pull request whenever main moves - silences it while the work that landed is still named in no notes
status: untriaged
feature: release-process
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests
added: 2026-09-27
---

**Problem.** docket check's unmerged-cut advisory measures from the branch's merge-base with the base, so merging the base in - the absorb route's own first step, and what update-armed.yml does to an armed release pull request whenever main moves - silences it while the work that landed is still named in no notes

**Why it matters.** `cut_window` in `subprojects/docket/src/docket/vcs.py`
reads `landed` as the ids leading `fork..base`, where `fork` is `git
merge-base HEAD base`. Once the base is merged into the cut's branch the
merge-base is the base's tip, so nothing has landed, and `_check_cut_window`
in `subprojects/docket/src/docket/checks.py` says nothing, while the work that
merged is still inside the tag's span and named in no notes. Two things merge
the base in. One is the absorb route itself, whose first step is "merge the
base in": a session that merges and then does not re-run the cut, or whose
re-run is refused (by the train guard, once the release item is closed), has
lost the report. The other is `.github/workflows/update-armed.yml`, which
brings `main` into every armed pull request on each push to `main`. An armed
release pull request therefore has `main` merged in before any check runs
against it, and the advisory cannot fire for work landing after it was armed.
What is lost is the choice, not the record. Once the tag is pushed,
`check_tag_span_covers_its_notes` in `tools/doc_check.py` fails `make check`
until the notes carry an `### also inside this tag's span` pointer for each
such closure, so the work reaches the next release's notes by default. The
absorb route, the only way to have this release's own notes name it, is what
goes unoffered, and `PL-028F` gave that choice to the session. It is not rare:
20 closing pull requests landed inside 16 of 65 tagged spans (`PL-P669`,
2026-09-22).

Observed 2026-09-27 while fixing `PL-2TDX`, in the `_TrainRepo` harness in
`subprojects/docket/tests/test_release.py`: v0.2.6 cut and committed on the
release branch, `PL-N3W1` closed on `main`. `docket check` on the branch named
`PL-N3W1` and the absorb route. After `git merge main` the same check printed
no cut-window advisory, and `docs/releases/v0.2.6.md` still named only
`PL-D1D1`.

**Done when.** A checkout whose unmerged cut's notes do not name work the base
took after the cut was written is reported whether or not the base has been
merged in since, and a test drives the merge. One candidate: measure `landed`
from the commit that added the notes file on this branch rather than from the
merge-base, since that commit is not moved by a base merge. Its cost is the
"let it go to the next release" disposition, which then reports on every run
until the cut merges; whether that noise is acceptable for the one session in
a release is the design question.

**Recommendation:** take it before the next release cut. It meets the
silent-wrong-answer test, since the advisory passes while the state it exists
to report still holds, and `update-armed.yml` makes that the normal case for
an armed release pull request. The damage is bounded by the tag-span check
above, which is why this is a recommendation on order rather than a priority
band.
