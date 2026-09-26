---
id: PL-HK4J
title: The printed tag line can tag the wrong commit in a shallow clone: the oldest fetched commit reads as adding every file, so a cut older than the clone's depth resolves to that commit (release.tag_commands; cli._cut_seen_here and doc_check already refuse to name a cut there)
priority: P2
effort: S
status: ready
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a tag line run in a shallow clone stops instead of tagging the clone's oldest fetched commit as the release
verify: grep -q 'def test_tag_line_refuses_a_shallow_clone' subprojects/docket/tests/test_release.py
---

**Problem.** The printed tag line can tag the wrong commit in a shallow clone: the oldest fetched commit reads as adding every file, so a cut older than the clone's depth resolves to that commit (release.tag_commands; cli._cut_seen_here and doc_check already refuse to name a cut there)

**Reproduced 2026-09-26.** In a clone fetched to depth 5 from `origin/main`
(`6efd8c41`), whose boundary is `2de8cb0b`, the lookup the tag line runs -
`git log --first-parent --diff-filter=A --format=%H origin/main --
docs/releases/v0.5.11.md` - answers `2de8cb0`, the boundary, where the full
clone answers `fe2046f7`, the cut; `v0.5.9` answers the boundary the same way.
`git tag -a` takes whatever the lookup prints, so the tag lands there with no
error. `v0.5.12`, one first-parent commit behind the tip, resolves correctly
at that depth.

**Why it matters.** A release tag on a commit the release was not cut on,
placed silently, and the tag is what every reader after `PL-QHCW` takes for
the cut. It needs a shallow clone whose depth does not reach the cut, which
`cli._cut_seen_here` and `doc_check` already refuse to read.

**Done when.** The printed tag line refuses to tag in a shallow clone, as
`cli._cut_seen_here` and `doc_check` refuse to name a cut there, pinned by a
test that builds one in `subprojects/docket/tests/test_release.py`.

**Generator check.** An instance of `PL-QHCW`'s fact - which commit a release
was cut on - filed after the head closed, in the commit that closed it
(`a55b6d17`): the lookup its fix prints reads a shallow clone's boundary as
the cut. The first such instance recorded; three would make `PL-QHCW` a
generator whose fix did not hold.
