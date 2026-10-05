---
id: PL-9XP0
title: check_citations reads a link anchor with a slug that is not GitHub's - it drops _ and non-ASCII letters, slugs a heading's raw Markdown rather than its rendered text, and ignores the -1 a repeated heading takes - so a correct anchor is reported and a wrong one can pass; latent, no link in the 38 documents carries an anchor
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a link to a heading is checked against the anchor GitHub actually gives it, so a correct link is not refused and one GitHub opens at the page's top does not pass
verify: grep -q 'def test_a_link_anchor_is_read_as_github_slugs_its_heading' tests/unit/test_doc_check.py
---

**Problem.** check_citations reads a link anchor with a slug that is not GitHub's - it drops _ and non-ASCII letters, slugs a heading's raw Markdown rather than its rendered text, and ignores the -1 a repeated heading takes - so a correct anchor is reported and a wrong one can pass; latent, no link in the 38 documents carries an anchor

**Found 2026-10-05 by `PL-R417`'s link 11 (`#1371`)**, which held a link's anchor to the linked document's headings alone for `PL-T1X0`. `check_citations` turns each heading into an anchor by lowercasing it, writing a hyphen for each space and dropping every character outside `[a-z0-9-]`. GitHub's rule differs in four ways. Checked against github-slugger (https://github.com/Flet/github-slugger, `index.js`, `regex.js` and its README, read 2026-10-05), whose README says it generates a slug "just like GitHub does for markdown headings":

- it keeps `_` and every letter or digit outside ASCII, where this drops them, so a heading naming `make_targets` is anchored `#make_targets` and this reads `#maketargets`;
- it slugs a heading's plain text, so a code span's backticks, a link's destination and emphasis markers are gone first, where this slugs the raw Markdown and keeps a link's destination as letters;
- a repeated heading's anchor takes `-1`, `-2` in order, which this never reads;
- GitHub anchors a heading inside a blockquote or a list item, which `_hash_headings` reads as none, since `markdown.headings` reads the top-level ones.

So a correct anchor is reported as naming no heading, which is loud, and an anchor GitHub does not have can pass, which is silent.

**Latent.** No link in the 38 documents `read_docs` returns carries an anchor (counted 2026-10-05), so nothing rests on the slug today.

**Reproduced 2026-10-05** at triage, on `main` at `b67dace8` under python3 3.11.15, and the count re-run there, still 0 anchored links in 38 documents. `check_citations` over a document linking `OTHER.md#make_targets`, `OTHER.md#notes-1`, `OTHER.md#make-check` and `OTHER.md#maketargets`, where `OTHER.md` holds `## make_targets`, `## Notes` twice and ``## `make check` ``, reported the first two as naming no heading - the anchors GitHub gives the first heading and the second `Notes` - and passed `#maketargets`, which GitHub gives no heading.

**Why it matters.** The first anchored link written to a heading carrying `_`, a link, a non-ASCII letter or a repeated title is refused though GitHub opens it, and the remedy the message invites is to respell the link the way this reader slugs, which GitHub then opens at the page's top while `make check` passes. The silent half is the costly one: a link to the wrong place, certified.

**Generator check.** Not a member of `PL-R417`, whose fact is where a statement ends. Like `PL-T1X0`'s anchor half, a one-off reading of GitHub's anchor rules.

**Done when.** The anchor check derives each heading's anchor as github-slugger does, from the heading's plain text, a repeated one suffixed in order, and reads a nested heading or declines it by name; each form pinned by a test in `tests/unit/test_doc_check.py`.
