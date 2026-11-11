---
id: PL-TG6P
title: Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised
priority: P1
effort: M
status: done
classes: defect
feature: copy-editor
touches: .claude/skills/docket/modes/close-out.md, .claude/skills/pull-request/SKILL.md, tools/new_prose.py, tests/unit/test_new_prose.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: the copy editor arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
closed: 2026-11-11
pr: 2115
payoff: the text the owner reads is the text the copy editor last saw, so a reason written to answer the copy editor's query cannot reach main unreviewed
verify: grep -q 'def test_arm_holds_while_the_published_body_is_not_the_recorded_one' subprojects/docket/tests/test_arming.py
not-delegable: which moment a check can reach (close-out step 8, the pull request body, or bin/docket arm) is chosen while the item is worked, so no command can name its test beforehand
---

**Problem.** Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04", from the session transcripts). In `PL-9331` the copy editor flagged that a reader could not see what was wrong with the old arterial-blood wording. The session then wrote a reason, which wrongly implied that "flow-limited" and "perfusion limited" differ, into the reply and the pull request body, and neither went back to the copy editor. The owner asked what the difference was. In `PL-J37P` the copy editor asked whether "cannot be misled" still held. The session added a warning about two compartments that are crossing, and the owner had it taken out. In `PL-BSYT`, two item passages written after the copy editor's run were never reviewed.

**What a fix needs.** The copy editor's last run must see the text that is published. A query it raises is answered in the text and then sent back to it, or answered to the writer alone. `tools/new_prose.py --count` already counts long prose added after the newest `Prose-review:` trailer, but `bin/docket arm` holds on it only where the branch waits on the owner's review. Nothing compares a pull request body or a reply with the copy editor's last run.

**Checked 2026-11-09:** `subprojects/docket/src/docket/arming.py` still holds a branch only on long docstrings and comments added since the newest `Prose-review:` trailer, and only where the branch waits on the owner's review. Nothing reads the pull request body or a reply against the copy editor's last run (`grep -n "Prose-review" subprojects/docket/src/docket/*.py tools/*.py`).

**Why it matters.** Both of the owner's objections in `PL-J1ZM`'s measurement landed on text written after the copy editor ran. One of them, a reason that wrongly implied flow-limited and perfusion-limited differ, reached `main` in squash commit 2d61ba9f7. Text written to answer the copy editor's own query is the text most likely to need review, and it is the text that gets none.

**Done when.** Text that a session writes or changes after the copy editor's last run, in a changed file or in the pull request body, goes back through the copy editor before the pull request is marked ready, or the query it answers is answered to the writer alone. Close-out step 8 says so, and where a check can reach the moment (the changed files and the pull request body at `bin/docket arm`), the check holds the branch until it has happened.

**Generator check.** Part of the fix for the live head `PL-J1ZM`, which is blocked on it; the 2026-11-04 measurement traced both of the owner's objections to this gap. Not a member of its `root-cause-of`. The pause on new workflow mechanisms does not hold it, because it fixes that generator.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. The copy editor did not exist at 817a4d88. It arrived in efc1dc3f (`PL-22T5`, 2026-11-04), so this is a new problem. It is deferred with `PL-J1ZM`, which waits on it.

**Built, 2026-11-11.** The copy edit of a pull request's title and body is now a recorded fact. `python3 tools/new_prose.py --body-record FILE` prints a `Body-review:` trailer that holds a digest of the body's words, and the session puts it in a commit. `bin/docket arm` holds a pull request that changes a simulator path while the published body's digest is not the one in the newest trailer. A body changed after the copy edit therefore holds the branch until it goes through the copy editor again. The digest leaves out what the harness adds to a published body: the opening comment, the "Requested by" line and the closing attribution. Close-out step 8 and the pull-request skill now say that text written after the copy editor's run goes back to it, and that a question from the copy editor which the reader does not need answered is answered to the writer alone.

**What was already built for changed files.** `PL-W04Z` holds a simulator branch where `tools/new_prose.py --count` finds prose that is newer than the newest `Prose-review:` trailer. On 2026-11-04 that count left out every passage of fewer than 30 words. `PL-HGZS` removed the limit on 2026-11-05, so a sentence added to `docs/MODEL.md` after the copy editor's run now holds the branch. Checked 2026-11-11: `tests/unit/test_new_prose.py` has `test_count_counts_a_new_model_paragraph_and_leaves_out_a_reviewed_one`. Whether the 30-word limit or a second trailer let `PL-J37P`'s sentence through was not established, because the branch's commits were squashed.

**What no check enforces.**

1. A reply. No hook runs in a Projects thread, and the copy editor does not edit replies (project owner, 2026-11-10).
2. A pull request that changes no simulator path. Its body is published unedited until `PL-BF6K` measures the copy editor's cost (project owner, 2026-11-11, `PL-WBT6`), so no `Body-review:` trailer is asked of it. `PL-P7B3` records the reviewed documents this leaves unchecked.
3. Whether the copy editor ran. The trailer records that the session says it did, as the `Prose-review:` trailer does. A session that skips the step now meets a hold that names it.
