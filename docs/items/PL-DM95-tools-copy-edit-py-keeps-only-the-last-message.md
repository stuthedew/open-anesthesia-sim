---
id: PL-DM95
title: tools/copy_edit.py keeps only the last message of a read whose reply spans several messages, so the read is called unreadable and dropped: #2056's fourth read (8 turns) came back starting mid-passage, and its 16 verdicts were lost (2026-11-09)
priority: P2
effort: S
status: ready
classes: defect
feature: repo-copy-edit
touches: tools/copy_edit.py, tests/unit/test_copy_edit.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: tools/copy_edit.py and its reply_of arrived in 7fca61f8 (PL-TQ4J)
added: 2026-11-09
payoff: a copy-edit read whose reply runs over several messages keeps all its verdicts, so a long review is not lost and rerun
verify: grep -q 'def test_a_reply_spread_over_several_messages_is_read_whole' tests/unit/test_copy_edit.py
---

**Problem.** tools/copy_edit.py keeps only the last message of a read whose reply spans several messages, so the read is called unreadable and dropped: #2056's fourth read (8 turns) came back starting mid-passage, and its 16 verdicts were lost (2026-11-09)

**Checked 2026-11-09:** `reply_of` in `tools/copy_edit.py` still returns only `data["result"]` from `claude -p --output-format json`. That field holds the final assistant message, so a read whose reply spans several messages keeps only the last.

**Why it matters.** The copy editor is close-out step 8 on every branch that changes prose, and the fix for the live head `PL-J1ZM` rests on it. A lost read throws away its verdicts (16 on #2056) and the time and credit the read cost, and the passages it covered get no review. `PL-HTB9` is very likely the same fault on a larger request.

**Done when.** A read whose reply spans several assistant messages is assembled whole, or is reported as cut with what was lost, and a test built from a multi-message reply asserts it.

**Generator check.** One-off. The fact misread is what the `result` field of `claude -p`'s JSON output holds: the last assistant message, not the whole reply. `PL-HTB9` misreads the same fact, and no head states it.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. `tools/copy_edit.py` did not exist at 817a4d88. `reply_of` arrived with it in 7fca61f8 (`PL-TQ4J`, #2026, 2026-11-04), so this is a new problem and is deferred.
