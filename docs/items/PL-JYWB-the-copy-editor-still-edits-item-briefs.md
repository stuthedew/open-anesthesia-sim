---
id: PL-JYWB
title: The copy editor still edits item briefs, workflow files, pull request bodies and replies, which the project owner limited it away from on 2026-11-10
status: untriaged
added: 2026-11-10
---

**Problem.** The project owner decided on 2026-11-10 that the copy editor
runs only on the documents and code that a clinician, a learner or a
contributor reads. It no longer runs on replies, item briefs, commit messages,
pull request bodies or the workflow's files. The owner's words: "Only do copy
editor on core human docs. Not on responses etc" (project owner, 2026-11-10).
This replaces the two-read limit for those texts that `PL-NDWC` built on
2026-11-09.

Three places still sent those texts to the copy editor:

1. `tools/new_prose.py` printed passages from item briefs and the workflow's
   files at close-out, and `tools/copy_edit.py` limited them to two reads.
2. Reply rule 16 in `.claude/rules/instruction-writing.md` copy edited a long
   reply or a decision request before it was sent.
3. The pull-request skill copy edited every pull request title and body.

**Done when.** `tools/new_prose.py` prints no passage whose only readers are a
later session or the project owner, `tools/copy_edit.py` has no two-read limit
left to apply, rule 16 and the pull-request skill's copy-edit step are gone,
and the documents that describe the review say what it now covers.
