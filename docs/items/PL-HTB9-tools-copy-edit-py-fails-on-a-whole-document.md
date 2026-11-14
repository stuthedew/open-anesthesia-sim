---
id: PL-HTB9
title: tools/copy_edit.py fails on a whole-document request: on 2026-11-09 the first read of a 40-passage, 137 KB request from tools/new_prose.py (PL-T8RL's restructure of docs/interface-provenance.md) returned only the reply's last 16 KB, passage 40 and the end of 39, so the run stopped with 'no verdict' for passages 1-39 after 38 minutes; close-out step 8 gives no way to split a request, and the session split it by hand into eight batches of whole sections
priority: P2
effort: M
status: dropped
classes: defect
feature: repo-copy-edit
touches: tools/copy_edit.py, tools/new_prose.py, tests/unit/test_copy_edit.py, tests/unit/test_new_prose.py, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - a new problem, not present at the freeze: tools/copy_edit.py and its reply handling arrived in 7fca61f8 (PL-TQ4J)
added: 2026-11-09
closed: 2026-11-14
reason: The project owner chose on 2026-11-14 to remove the copy editor completely, and PL-GL45 removed it with its agents, the blind judge and their tests, so this work on the copy editor has nothing left to act on.
payoff: a restructured document's close-out copy edit runs in one command and returns a verdict for every passage, instead of losing the run and needing a hand split
verify: grep -q -r --include=test_*.py 'def test_a_close_out_request_over_the_limit_is_read_in_batches' tests/unit
---

**Problem.** tools/copy_edit.py fails on a whole-document request: on 2026-11-09 the first read of a 40-passage, 137 KB request from tools/new_prose.py (PL-T8RL's restructure of docs/interface-provenance.md) returned only the reply's last 16 KB, passage 40 and the end of 39, so the run stopped with 'no verdict' for passages 1-39 after 38 minutes; close-out step 8 gives no way to split a request, and the session split it by hand into eight batches of whole sections

**Checked 2026-11-09:** `reply_of` in `tools/copy_edit.py` still keeps only the last assistant message (`PL-DM95`). The close-out report in `tools/new_prose.py` still puts every changed passage into one request; only the structure read and the section line edit split a long document by `REQUEST_LIMIT_WORDS` (6,000 words). Close-out step 8 in `.claude/skills/docket/modes/close-out.md` still gives no way to split a request.

**Why it matters.** A restructure changes every passage of a document, so its close-out request is the whole document. That run lost 38 minutes and returned no verdict for 39 of its 40 passages, and the session had to split the request by hand into eight batches.

**Done when.** A close-out request longer than `REQUEST_LIMIT_WORDS` is cut into batches of whole sections, each batch is read on its own, and the verdicts are joined into one report. A test covers a request over the limit. Fix `PL-DM95` first or with it, because a reply cut to its last message would still lose verdicts inside one batch.

**Generator check.** One-off. Its first fault misreads the same fact as `PL-DM95`: what the `result` field of `claude -p`'s JSON output holds. Its second is a size limit that two of the tool's three request kinds apply and the close-out kind does not. No head states either fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. `tools/copy_edit.py` did not exist at 817a4d88. The reply handling that fails arrived in 7fca61f8 (`PL-TQ4J`, #2026, 2026-11-04), so this is a new problem and is deferred.

**Checked 2026-11-10:** `PL-DM95` is fixed, so the first fault is gone.
`reply_of` now joins every assistant message. PL-BLN0's close-out sent a
43-passage, 142 KB request in one run. Its first read returned a whole 77 KB
reply in about 15 minutes, and each later read took about 17. The batching
this item asks for is still not built. It is now needed only where one read
would exceed `COPY_EDIT_TIMEOUT_S` (40 minutes) or the model's context, which
this run did not show.
