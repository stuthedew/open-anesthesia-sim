---
id: PL-5H48
title: Release facts are read twice - whether a version row shipped (roadmap's Completed, doc_check casefolded), whether a tag names a version (release.is_untagged, doc_check._is_tagged), a version's tag name (tag_release names vv0.5.0 for a declared v0.5.0) and a milestone's Required scope heading (roadmap, doc_check)
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.28
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, tools/doc_check.py, tools/tag_release.py, tests/unit/test_tag_release.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1546
payoff: a release's shipped state and tag read the same to docket, doc_check and the tagger
verify: grep -q 'def test_a_declared_leading_v_names_one_tag' tests/unit/test_tag_release.py
---

**Problem.** Release facts are read twice - whether a version row shipped (roadmap's Completed, doc_check casefolded), whether a tag names a version (release.is_untagged, doc_check._is_tagged), a version's tag name (tag_release names vv0.5.0 for a declared v0.5.0) and a milestone's Required scope heading (roadmap, doc_check)

- Whether a version row shipped: `roadmap.COMPLETED` (case-sensitive), `released_versions` and an inline test in `milestone_states`, beside `doc_check.COMPLETED_MARK` (casefolded). On a status cell `completed` doc_check demands a tag and docket reads the version unreleased. Found by two sweepers.
- Whether a tag names a version: `release.is_untagged` strips a leading `v`; `doc_check._is_tagged` does not. On version `v0.4.8` with tag `0.4.8` release reads it tagged and doc_check untagged; latent, since doc_check passes bare versions.
- A version's tag name: `release.tag_confirmation` and three sites in cli name `v0.5.0` for a declared `v0.5.0`; `tag_release` writes `f"v{version}"` and names `vv0.5.0`.
- A milestone's Required scope heading: `roadmap.parse_milestones` (not exported) reads ids under the last of two such headings; `doc_check._subsection_line` cites the first.
- A version's comparable triple: `roadmap.version_tuple` and `release.version_key` agree on every version and differ on a non-version by contract (`PL-M6GY` left the pair).

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** doc_check and tag_release read these through `docket.roadmap` and `docket.release`, and a test pins `completed`, the `v`-less tag and the declared `v`.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
