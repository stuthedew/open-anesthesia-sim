---
id: PL-N2VQ
title: Put pull request titles and bodies back in the copy editor's review, at the owner's request of 2026-11-10
priority: P1
effort: S
status: ready
classes: defect
feature: copy-editor
touches: tools/new_prose.py, tests/unit/test_new_prose.py, .claude/rules/plain-writing.md, .claude/skills/pull-request/SKILL.md, .claude/skills/docket/modes/close-out.md, docs/prose-review/README.md
deferred-from: v0.7.0 - the owner's request of 2026-11-10, after the gate froze
added: 2026-11-10
payoff: pull request titles and bodies, which become the history on main, are copy edited again as the owner asked
verify: grep -q 'def test_a_pull_request_body_has_a_row_to_draft_for' tests/unit/test_new_prose.py
---

**Problem.** On 2026-11-10 at 01:02 UTC the project owner took every text written only for a later session or for the owner out of the copy editor's review (`PL-JYWB`, #2079). At 02:14 UTC the owner wrote "Add PR text and titles to copy editor". Pull request titles and bodies go back into the review. Replies, item briefs, commit messages and the workflow's files stay out.

**Why it matters.** The squash merge makes a pull request's title and body the commit message on `main`, which is the record a later reader of the history sees.

**How.** `tools/new_prose.py` leaves out the reader rows named in `UNEDITED_READERS`, and pull request titles and bodies share the row for "A later session, or the owner reading the history" with item briefs and commit messages. They get a row of their own in `.claude/rules/plain-writing.md`, whose reader is not in `UNEDITED_READERS`, so `--draft --kind "pull request"` prints a draft again. The pull-request skill gets back its step that copy edits the title and body before the pull request is marked ready. Close-out step 8, the plain-writing sentence after the table and `docs/prose-review/README.md` say what the review now covers.

**Done when.** `python3 tools/new_prose.py --draft FILE --kind "pull request"` prints a draft for review, a reply still has no row, and the pull-request skill asks for the copy edit. A test asserts both.

**Generator check.** A one-off: the owner's own change to a scope set an hour earlier. No head states the fact, and the pause on new workflow mechanisms does not hold it, because the owner asked for it.
