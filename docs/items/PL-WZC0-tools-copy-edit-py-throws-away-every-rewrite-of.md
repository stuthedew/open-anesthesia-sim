---
id: PL-WZC0
title: tools/copy_edit.py throws away every rewrite of a request when one meaning-check reply has two verdicts for a passage, even where the checker retracted the first itself; #2056's whole 16-passage edit came back as keep after 90 minutes because reader 2 corrected its [7] verdict in the same reply. Retry that reader once instead (2026-11-09)
priority: P2
effort: S
status: ready
classes: defect
feature: repo-copy-edit
touches: tools/copy_edit.py, tests/unit/test_copy_edit.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: meaning_findings arrived in 37c88630 (PL-F0Q2)
added: 2026-11-09
payoff: one checker correcting its own verdict no longer discards a whole copy edit after an hour or more of reading
verify: grep -q 'def test_a_meaning_check_reply_with_two_verdicts_is_read_again_once' tests/unit/test_copy_edit.py
---

**Problem.** tools/copy_edit.py throws away every rewrite of a request when one meaning-check reply has two verdicts for a passage, even where the checker retracted the first itself; #2056's whole 16-passage edit came back as keep after 90 minutes because reader 2 corrected its [7] verdict in the same reply. Retry that reader once instead (2026-11-09)

**Checked 2026-11-09:** `meaning_findings` in `tools/copy_edit.py` still raises `ValueError` where a passage has two verdicts, and `meaning_check` then marks every edited passage lost, so none of the request's edits is kept.

**Why it matters.** One checker correcting itself in its own reply costs the whole request: on #2056 that was 16 passages and about 90 minutes. The review then reports every passage as kept although none was judged, and the session has to run it again.

**Done when.** A meaning-check reply with two verdicts for one passage is read again once, by a fresh run of the same reader, before any edit is discarded. Where the second reply is also unreadable, the edits are discarded as now. A test covers both cases, and `test_a_meaning_check_reply_without_one_verdict_per_passage_is_refused` is changed to match.

**Generator check.** One-off. The fact misread is how a meaning checker's reply may state a verdict, including one it corrects in the same reply. No head states it.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. `tools/copy_edit.py` did not exist at 817a4d88, and `meaning_findings` arrived in 37c88630 (`PL-F0Q2`, #2052, 2026-11-08), so this is a new problem and is deferred.
