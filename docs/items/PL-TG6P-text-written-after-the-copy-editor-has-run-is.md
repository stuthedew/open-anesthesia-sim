---
id: PL-TG6P
title: Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised
priority: P1
effort: M
status: needs-decision
classes: defect
feature: copy-editor
touches: .claude/skills/docket/modes/close-out.md, .claude/skills/pull-request/SKILL.md, tools/new_prose.py, tests/unit/test_new_prose.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: the copy editor arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
payoff: the text the owner reads is the text the copy editor last saw, so a reason written to answer the copy editor's query cannot reach main unreviewed
verify: grep -qE '^[*][*]Re-diagnosed, 20' docs/items/PL-TG6P-*.md
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

**Decision needed.** Is this item kept, changed or dropped? The session re-diagnosing `PL-J1ZM` decides, at the project owner's word of 2026-11-11.

**Stopped, 2026-11-11** (project owner). A fresh session is re-diagnosing `PL-J1ZM` from the start and will say whether this item is kept, changed or dropped. The item is open again, the claim is released, and nothing below has merged. A complete build of this item and of `PL-HNNH` is on branch `claude/peaceful-noether-5bvpno`, in draft pull request #2115, at commit `98050deaf`. It is unarmed. `bin/docket verify --self PL-HNNH PL-TG6P` accepted that commit and `make check` passed there. Close-out step 8's copy edit of the six test docstrings that the build adds was started and stopped unfinished, and the branch is 2 commits behind `origin/main`. If the item is dropped, close #2115 unmerged. If it is kept as built, finish the close-out there. The paragraphs below describe that build as it stands on the branch. The session that decides records the decision here in a paragraph that opens "**Re-diagnosed, ", which is what `verify:` now tests, and then rewrites `verify:` for the work that is left. The build's own test is named in the paragraph below.

**Built on the branch, 2026-11-11.** The copy edit of a pull request's title and body is now a recorded fact. `python3 tools/new_prose.py --body-record FILE` prints a `Body-review:` trailer that holds a digest of the body's words, and the session puts it in a commit. `bin/docket arm` holds a pull request that changes a simulator path while the published body's digest is not the one in the newest trailer. A body changed after the copy edit therefore holds the branch until it goes through the copy editor again. The digest leaves out what the harness adds to a published body: the opening comment, the "Requested by" line and the closing attribution. Close-out step 8 and the pull-request skill now say that text written after the copy editor's run goes back to it, and that a question from the copy editor which the reader does not need answered is answered to the writer alone. Its test is `test_arm_holds_while_the_published_body_is_not_the_recorded_one` in `subprojects/docket/tests/test_arming.py`.

**What was already built for changed files.** `PL-W04Z` holds a simulator branch where `tools/new_prose.py --count` finds prose that is newer than the newest `Prose-review:` trailer. On 2026-11-04 that count left out every passage of fewer than 30 words. `PL-HGZS` removed the limit on 2026-11-05, so a sentence added to `docs/MODEL.md` after the copy editor's run now holds the branch. Checked 2026-11-11: `tests/unit/test_new_prose.py` has `test_count_counts_a_new_model_paragraph_and_leaves_out_a_reviewed_one`. Whether the 30-word limit or a second trailer let `PL-J37P`'s sentence through was not established, because the branch's commits were squashed.

**What no check enforces.**

1. A reply. No hook runs in a Projects thread, and the copy editor does not edit replies (project owner, 2026-11-10).
2. A pull request that changes no simulator path. Its body is published unedited until `PL-BF6K` measures the copy editor's cost (project owner, 2026-11-11, `PL-WBT6`), so no `Body-review:` trailer is asked of it. `PL-P7B3` records the reviewed documents this leaves unchecked.
3. Whether the copy editor ran. The trailer records that the session says it did, as the `Prose-review:` trailer does. A session that skips the step now meets a hold that names it.

**Findings for the re-diagnosis, 2026-11-11.**

1. The gap for changed files may already be closed. See "What was already built for changed files" above: the 30-word limit that the count had on 2026-11-04 was removed the next day.
2. A hold on the body has a running cost. Each change to a body after its copy edit sends the whole title and body through the copy editor again. On `#2088` one such edit of 381 words took 12 model runs, 15 minutes and $2.75 (`PL-WBT6`). A session that adds one line to a body, such as a note on a fix, pays that again.
3. The hold cannot tell whether the copy editor ran. It tells only that the published body is the text the session recorded.
4. Both of the owner's objections on 2026-11-04 were to an answer to the copy editor's query. Telling the session to answer such a query to itself, where the reader does not need the answer, removes the text and needs no check. The build adds that sentence to close-out step 8 and to the hold's message.
