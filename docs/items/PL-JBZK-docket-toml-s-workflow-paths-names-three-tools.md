---
id: PL-JBZK
title: docket.toml's workflow_paths names three tools tests by path, so the other seven and every new one fall on the product side of the lane boundary
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
added: 2026-09-05
verify: uv run pytest subprojects/docket/tests/test_model.py subprojects/docket/tests/test_config.py && grep -rq 'def test_a_tools_script_and_its_own_test_land_in_the_same_lane' subprojects/docket/tests tests
---

**Problem.** `docket.toml`'s `workflow_paths` names three test files
individually - `tests/unit/test_doc_check.py`, `tests/unit/test_contrast_check.py`,
`tests/unit/test_import_boundary_check.py` - with a comment saying they test
`tools/` scripts and only live in the simulator's tree because that is where
pytest is configured to look. Seven more test files are in exactly that
position and are not listed: `test_branch_id_check.py`,
`test_docket_branch_guard.py`, `test_docket_digest_hook.py`,
`test_ignore_check.py`, `test_pr_title_check.py`, `test_stop_hook_patch.py`,
`test_tools_portability.py`. So does every test file a *future* `tools/` check
will bring with it.

**Why it matters.** An item whose `touches` mixes workflow and product paths is
claimed by neither lane: `docket next workflow` and `docket next product` both
set it aside for a session that can hold the whole change. An item that is
plainly one `tools/` script and its own test therefore goes to neither session,
which is the outcome the three hand-listed entries exist to prevent - the
comment beside them says so in as many words, and names eight items it would
otherwise have misplaced. The list simply stopped at the files that existed
when it was written.

Observed at triage on 2026-09-05, filling in `PL-8XPQ` (a `make check` guard on
the glyphs an interface string uses). Its honest `touches` is
`tools/glyph_check.py`, `tests/unit/test_glyph_check.py`, `Makefile` - two
workflow paths and one product path for a change that touches no product code
at all - so a `P2` item was set aside from both lanes by a filename.

**Where.** `docket.toml`'s `workflow_paths`. The reading is a path-prefix match
against each item's `touches`, so the shapes available are another hand-listed
entry per file, a prefix that catches the family, or a matcher that
understands a `tests/unit/test_<x>_check.py` naming convention. The first is
what has already drifted once.

**Done when.** A `tools/` script and its own test sit on the same side of the
lane boundary without anybody having to remember to add the file, or the list
records why hand-listing is the right cost.
