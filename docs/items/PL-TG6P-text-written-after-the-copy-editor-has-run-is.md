---
id: PL-TG6P
title: Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised
status: untriaged
feature: reader-first-prose
added: 2026-11-04
---

**Problem.** Text written after the copy editor has run is published without review, and both of the owner's objections in PL-J1ZM's measurement landed on such text: PL-9331's wrong reason for a rewording, in its reply and pull request body, and PL-J37P's warning sentence in docs/MODEL.md, each written to answer a question the copy editor raised.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04", from the session transcripts). In `PL-9331` the copy editor flagged that a reader could not see what was wrong with the old arterial-blood wording. The session then wrote a reason, which wrongly implied that "flow-limited" and "perfusion limited" differ, into the reply and the pull request body, and neither went back to the copy editor. The owner asked what the difference was. In `PL-J37P` the copy editor asked whether "cannot be misled" still held. The session added a warning about two compartments that are crossing, and the owner had it taken out. In `PL-BSYT`, two item passages written after the copy editor's run were never reviewed.

**What a fix needs.** The copy editor's last run must see the text that is published. A query it raises is answered in the text and then sent back to it, or answered to the writer alone. `tools/new_prose.py --count` already counts long prose added after the newest `Prose-review:` trailer, but `bin/docket arm` holds on it only where the branch waits on the owner's review. Nothing compares a pull request body or a reply with the copy editor's last run.
