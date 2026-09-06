---
id: PL-WB5K
title: Delete README.md until a deliberate rewrite replaces it
priority: P2
effort: S
status: done
classes: docs, infra
feature: project-introduction
milestone: v0.4.3
touches: README.md, pyproject.toml, .claude/rules/readme-hold.md, tools/readme_hold_check.py, tests/unit/test_readme_hold_check.py, Makefile, .github/workflows/quality.yml, docs/ARCHITECTURE.md, docs/MODEL.md, docs/WORKING_NOTES.md
added: 2026-09-05
closed: 2026-09-05
pr: 366
verify: python3 tools/readme_hold_check.py && python3 tools/doc_check.py check
---

**Problem.** The root `README.md` was doing net harm. Two failures, and they
compound: sessions were reading it as instruction — its "Development" section
restated the Makefile, `make check`'s composition and the CI job layout, so a
second, unenforced copy of that material sat where a session would find it
first and trust it — and for a human reader it had become a 241-line
accumulation of paragraph-scale improvements with no shape, which is the exact
failure `.claude/rules/readme-hold.md` was written to stop and did not.

**Why it matters.** The freeze held the file still but left it in place, so it
kept being read. Removing it is what actually stops both harms, and it costs
little that is not recoverable: the content is in git history, and no reader is
losing it — the repository is private, `PL-XYRN` (decide when the repository
goes public and run the human-facing pass immediately before it) still gates
publication, and `CITATION.cff` already carries the project abstract and the
educational-only limit at the root.

**Where.** Delete `README.md` and `.claude/rules/readme-hold.md` (a rule
guarding a file that no longer exists, and one whose own closing line says to
delete it in the same commit as the first README change). Drop
`readme = "README.md"` from `pyproject.toml`, which the `uv_build` backend
would otherwise fail on. Then repair every remaining citation of the path, all
of which `tools/doc_check.py` holds to the tree: `CLAUDE.md`'s two-standards
paragraph, `.claude/rules/expert-review.md`, `.claude/rules/apparatus-standard.md`,
`docs/MODEL.md`'s caveat note, `docket.toml`'s `workflow_paths` commentary, and
`docs/WORKING_NOTES.md`.

**The hold has to be enforced, not written down.** `PL-QTN6` already tried
prose: a `.claude/rules/` freeze on editing the file. A path-scoped rule loads
when a session **reads** a matching file, and a first write is preceded by no
read, so delivery was best-effort by construction — `PL-BTSW` records it being
missed one day after it was written, and `PL-3V4N` diagnosed why. The condition
here needs no judgment at all (does `README.md` exist at the root?), which is
exactly what `CLAUDE.md` says to put in code, so `tools/readme_hold_check.py`
runs in `make check` and in the bare-interpreter section of CI's `checks` job,
where `PL-D551` folded the former `floor` job, and fails while the file exists — a
stub included, since a stub reproduces both harms at smaller scale. It is
silent on every clean run, and it retires itself: `PL-N092` deletes the script
and its invocations in the commit that writes the deliberate README.

**Done when.** `README.md` is gone, `make check` is green, no surviving
document cites the path as a live file, and recreating it fails the build with
a message naming what to do instead. The rewrite itself stays where it already
is: `PL-N092` (rewrite README as a human-readable introduction), sequenced
behind `PL-XYRN`.
