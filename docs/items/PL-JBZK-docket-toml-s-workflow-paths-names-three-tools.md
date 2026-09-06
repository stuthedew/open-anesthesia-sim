---
id: PL-JBZK
title: docket.toml's workflow_paths names three tools tests by path, so the other seven and every new one fall on the product side of the lane boundary
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py, Makefile, .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-06
pr: 405
verify: uv run pytest tests/unit/test_workflow_paths_check.py && grep -q 'def test_a_tools_script_and_its_own_test_land_in_the_same_lane' tests/unit/test_workflow_paths_check.py
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

**Done 2026-09-06, by the third shape rather than the first.** Hand-listing was
rejected on this item's own evidence: the list was three entries when written,
nine short by the time it was picked up, and two of the nine had arrived within
the previous day. Completing it by hand restarts exactly that. So the
membership rule moved into `tools/workflow_paths_check.py` and the list became
a derived artifact `make check` holds to it.

**The rule is decidable, which is what earns it a hard failure.** A test file
under `tests/` is apparatus when it does not import `anesthesia_sim`, and the
simulator's when it does. Measured across the tree before writing it: 26 of the
38 files under `tests/unit/` import the package and are product tests, the 12
that do not are precisely the twelve apparatus tests, and every file under
`tests/integration/` and `tests/reference/` imports it. No file needs a
judgment, so nothing here is the "worse than no tool" case `CLAUDE.md` names -
the check asks only what a file imports, never whether it should exist. The
rule also keeps working on files nobody has written yet: the next `tools/`
check's test will import `tools/`, not the simulator, without anyone deciding
to make it so.

`ast` rather than a grep for the package name, because several of the apparatus
tests write `src/anesthesia_sim/...` as fixture data - they check tools that
read the tree - and read as text that looks like a dependency.

**Measured effect on the queue.** One open item changed lane:
`PL-G8TR` (no-prune-guard is evaded by the form it recommends) moved from
`crossing`, where both lanes set it aside and no session was offered it, to
`workflow`. That is a smaller number than the problem statement implies, and it
is the right size: the cost of this defect is not a backlog, it is a slow leak
at the rate `tools/` grows, and `PL-8XPQ` (nothing checks that an interface
string uses glyphs the Flutter client can draw) would have joined `PL-G8TR`
the moment `tests/unit/test_glyph_check.py` existed.

**Two things the work turned up and settled in passing.** The comment above
`workflow_paths` said "Four entries are here for reasons the directory names do
not carry" and then named two test files; the list already held three, so the
count was stale. And the check demands its own test file be listed, which is
the first thing it did on being run - a satisfying confirmation that the rule
closes over itself.

**`verify:` was repaired rather than run as written.** The command this item
carried pointed at `subprojects/docket/tests/`, where no part of this work
landed: the lane logic in `Item.lane` was already correct, and what was wrong
was the data it reads. The replacement names the suite the work adds. It exits
4 before the work, because the file it names is the file the work creates - not
the usual paired shape, and recorded here so a reader does not mistake it for a
typo'd path. The test it greps for,
`test_a_tools_script_and_its_own_test_land_in_the_same_lane`, is the item's
title stated as an assertion and runs end to end through `Item.lane` against
this repository's real `workflow_paths`, so it fails if the check passes while
the thing the check is for is still broken.
