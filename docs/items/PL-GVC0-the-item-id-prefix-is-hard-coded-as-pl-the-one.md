---
id: PL-GVC0
title: The item id prefix is hard-coded as `PL-`, the one thing in docket that is not configurable
priority: P3
effort: S
status: dropped
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/vcs.py, docket.toml
added: 2026-08-30
closed: 2026-09-26
reason: no second project uses docket and none is planned, which the brief sets as the condition for starting; a configurable prefix would mean threading Config to about twenty import-time regexes, tested only against a made-up prefix. The one independent spelling moves to store.ID_PATTERN under PL-PB8V. Reopen when a second consumer appears
verify: uv run pytest subprojects/docket/tests -k custom_prefix
---

**Problem.** `store.ID_PREFIX = "PL-"` and the branch-name regex in
`vcs.BRANCH_ID_RE` both spell this repository's id prefix into the package.
Every other project-specific value — protected paths, debt classes, the check
command, the roadmap and version filenames, the band limits — already reads
from `docket.toml`, and `config.py` says in its own docstring that it exists
"so the package is usable outside the repository it grew in".

**Why it matters.** It is the only thing standing between the package and a
second project, and it fails quietly rather than loudly: a project using a
different prefix gets ids that generate, files that write, and a `flight`
command that silently recognizes no branch as carrying work, because the
regex matches nothing. Nothing errors.

Small enough to be worth doing at the moment a second consumer appears, and
not before: with one consumer the setting has no second value to be tested
against, and an untested configuration seam is a claim rather than a feature.

**Where.** `store.py` (`ID_PREFIX`, used by `new_id` and the filename shape),
`vcs.py` (`BRANCH_ID_RE`, which also encodes the id *shape* — three digits or
four consonant-safe characters), `config.py` and `docket.toml`.

**Done when.** A project can set its own prefix in `docket.toml` and have id
generation, filenames and branch detection all follow it, with a test
covering a prefix that is not `PL-`.

**Dropped 2026-09-26** (project owner, 2026-09-26, ratified, over building the
configurable prefix now). Re-confirmed against 718b42ee: the brief's facts still
hold, and its own condition for starting has not arrived. No second project uses
docket, and nothing in `ROADMAP.md`, `docs/WORKING_NOTES.md` or the queue plans
one.

What the work would be, so that a session reopening it starts from the count
rather than from this brief. The prefix now lives in one constant,
`store.ID_PREFIX`, and `store.ID_PATTERN` derives from it. About twenty regular
expressions compile from `ID_PATTERN` when their module is imported: in
`checks`, `claiming`, `claims`, `notes`, `release`, `roadmap` and `vcs`, and in
`tools/dead_ends.py`, `tools/doc_check.py` and `tools/generator_check.py`.
`config.load` needs a project root, and those patterns are compiled before one
is known. So a configurable prefix means either threading `Config` to each of
them, or a global set on load, which two roots in one process (the test suite)
would collide over. A partial version recreates this brief's failure (ids that
generate and one reader that silently ignores them), inside the tool where it is
harder to see. With one consumer, the only test would be a made-up prefix.
`tools/generator_check.py`'s two `glob("PL-*.md")` and
`.claude/hooks/item_read_log.py`'s `"PL-" in pattern` are repository tooling
rather than package code, and would follow the setting or not by choice.

The one independent spelling, `vcs.BRANCH_ID_RE`, is a real defect in its own
right, and `PL-PB8V` (BRANCH_ID_RE's unguarded second spelling of the grammar)
moves it onto `ID_PATTERN`. After that, reopening this is threading one
constant, not finding a second one first.

**Reopen when** a second project adopts docket, or one is planned.
