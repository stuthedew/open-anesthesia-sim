---
id: PL-JYWB
title: The copy editor still edits item briefs, workflow files, pull request bodies and replies, which the project owner limited it away from on 2026-11-10
status: done
deferred-from: v0.7.0 - an owner-requested change to the workflow, worked at once rather than placed on the release's gate
added: 2026-11-10
closed: 2026-11-10
pr: 2079
verify: uv run pytest tests/unit/test_new_prose.py -k 'unedited or leaves_out or no_row_to_draft' && ! grep -q 'COPY-EDIT A DECISION REQUEST' .claude/rules/instruction-writing.md && ! grep -q LIMITED_READS tools/copy_edit.py
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

**Why it matters.** Each copy-editor run on a reply or a pull request body
took minutes and delayed the message, and its meaning checks spent the same
again, on text that no clinician or learner reads. The owner judged the edits
not worth that cost for these readers.

**Done when.** `tools/new_prose.py` prints no passage whose only readers are a
later session or the project owner, `tools/copy_edit.py` has no two-read limit
left to apply, rule 16 and the pull-request skill's copy-edit step are gone,
and the documents that describe the review say what it now covers.

## Done 2026-11-10

`tools/new_prose.py` now leaves out every reader row whose reader is in its
new `UNEDITED_READERS`: "A later session, or the owner reading the history"
and "The project owner, an anesthesiologist and intensive-care physician".
Every mode of the tool, including `--count`, which `bin/docket arm` reads,
then prints and counts nothing from an item brief or a workflow file, and
`--draft --kind replies` refuses. A file that a row names only for those
readers is passed over without the "Not reviewed" note that a file with no row
gets. `tools/copy_edit.py` and its tests go back to their state before
`PL-NDWC`, because no passage reaches it for those readers now and the two-read
limit had nothing left to apply to.

Rule 16 is gone from `.claude/rules/instruction-writing.md`, and
`docs/resident-instructions.md` marks it retired. That takes about 620
characters out of the resident set, and the sentence added to
`.claude/rules/plain-writing.md` puts back about 230. The pull-request skill
says the title and body are not copy edited. Close-out step 8 and
`docs/prose-review/README.md` say what the review covers.

The narrower reading was chosen: the texts that `PL-NDWC` limited to two reads
now get none, and the docstrings, comments and interface strings in `src/` and
`tests/` stay in the review, because their readers are a developer and a
learner.
