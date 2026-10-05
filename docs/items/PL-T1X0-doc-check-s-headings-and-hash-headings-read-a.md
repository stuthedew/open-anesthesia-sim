---
id: PL-T1X0
title: doc_check's _headings and _hash_headings read a # line inside a fence as a heading, and link anchors are checked against bold runs GitHub gives no anchor, so a shell comment in a fence answers a section citation and README.md#cite-this-repository passes; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1371
payoff: a section citation or link anchor whose heading is gone is reported, instead of passing on a shell comment in a code sample or on a bold lead-in GitHub gives no anchor
verify: grep -q 'def test_a_hash_line_inside_a_fence_is_not_a_citable_heading' tests/unit/test_doc_check.py && grep -q 'def test_a_link_anchor_naming_a_bold_marker_is_an_error' tests/unit/test_doc_check.py
recurrences: 2026-10-05 PL-0Y7J withdrawn 2026-10-05 PL-0Y7J
---

**Problem.** doc_check's _headings and _hash_headings read a # line inside a fence as a heading, and link anchors are checked against bold runs GitHub gives no anchor, so a shell comment in a fence answers a section citation and README.md#cite-this-repository passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_headings` and `_hash_headings` read lines inside a fenced block as titles, so `# make sure the venv exists` in a bash fence answers a `§ "make sure the venv exists"` citation. The link-anchor check in `check_citations` tests anchors against `_headings`, which includes `**Bold.**` runs that GitHub renders without an anchor, so `[citing](../README.md#cite-this-repository)` passes. Not members of `PL-R417`. Latent: no citation or anchor rests on either today.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, `check_citations` over a scratch repository - a guide whose bash fence opens on the comment `# make sure the venv exists`, and a README whose one heading is `## Citation`, over a line opening `**Cite this repository**` - passed the guide's `§ "make sure the venv exists"` and its `[citing](../README.md#cite-this-repository)`, and reported both controls beside them, `§ "no such section"` and an anchor `#no-such-anchor`. `_hash_headings` returned the fence's comment as the title `make sure the venv exists`. Latent, as the line above says: over the 38 documents `read_docs` returns, re-reading with fenced lines left out adds no error, and none of them links to a relative path with an anchor.

**Why it matters.** `check_citations` is what fails a `§` citation or a link anchor whose section was renamed or removed, and each half lets a dead one pass: a `#` comment in any fenced shell sample stands in for a section heading, and an anchor named for a `**Bold.**` lead-in reads as resolving while GitHub, which anchors headings only, opens the link at the top of the page. Either way the check reports a broken reference as sound, the silent wrong answer the apparatus floor refuses.

**Generator check.** Its fence half is an instance of `PL-R417`'s fact, where one statement ends: a `#` line inside a fenced block is part of that block, the half `PL-HKHP`, a member, has in docket's heading scans, so it belongs to the head. Not added to `PL-R417`'s `root-cause-of:` here, since that file is on the head's own branch; put to its thread. Its anchor half, bold runs GitHub gives no anchor, is a one-off reading of GitHub's anchor rules. Recorded in `PL-R417`'s `root-cause-of:` by that head's link 8 (`#1358`, 2026-10-05).

**Done when.** `_hash_headings`, and so `_headings`, reads no line inside a fenced block as a heading, so a fenced `# make sure the venv exists` answers no `§` citation; a link's anchor is held to the linked document's `#` headings alone, so an anchor named for a `**Bold.**` marker is reported, while a `§` citation of one still resolves (`test_a_bold_marker_is_a_citable_section_title` keeps passing); and `tests/unit/test_doc_check.py` gains `test_a_hash_line_inside_a_fence_is_not_a_citable_heading` and `test_a_link_anchor_naming_a_bold_marker_is_an_error`, pinning each.
