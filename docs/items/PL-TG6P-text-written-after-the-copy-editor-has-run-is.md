---
id: PL-TG6P
title: Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised
priority: P1
effort: M
status: ready
classes: defect
feature: copy-editor
touches: .claude/skills/docket/modes/close-out.md, tools/new_prose.py, subprojects/docket/src/docket/arming.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: the copy editor arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
payoff: the text the owner reads is the text the copy editor last saw, so a reason written to answer the copy editor's query cannot reach main unreviewed
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
