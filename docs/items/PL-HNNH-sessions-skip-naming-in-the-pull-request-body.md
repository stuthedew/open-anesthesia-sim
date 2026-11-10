---
id: PL-HNNH
title: Sessions skip naming, in the pull request body, the facts a grown passage adds: PL-W6JM's two docstrings grew by 44 and 46 words and PL-J37P's subsections grew, and neither body says what the added words carry, though tools/new_prose.py --compare printed the growth
priority: P1
effort: M
status: ready
classes: defect
feature: copy-editor
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, tools/new_prose.py, .claude/skills/docket/modes/close-out.md
blocked-by: PL-TTBF
deferred-from: v0.7.0 - a new problem, not present at the freeze: the request to name a grown passage's facts arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
payoff: every grown passage on a branch has its added facts named before merge, so growth with no new fact, the mark of over-explaining, is caught on the branch that adds it
verify: grep -q 'def test_a_grown_passage_the_body_does_not_name_holds_the_arm' subprojects/docket/tests/test_arming.py
---

**Problem.** Sessions skip naming, in the pull request body, the facts a grown passage adds: PL-W6JM's two docstrings grew by 44 and 46 words and PL-J37P's subsections grew, and neither body says what the added words carry, though tools/new_prose.py --compare printed the growth.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04"). `PL-W6JM`'s `prepare_clone` docstring went from 40 words to 86, and its test docstring from 12 to 56. #2021's body gives the copy editor's counts and no facts for the growth. #2022's thread read the rule and its comparison showed growth, but its body has no such list and does not say that nothing grew. `PL-BSYT`, `PL-9331` and `PL-SMM2` named them.

**What a fix needs.** Which passages grew is decidable: `tools/new_prose.py --compare` prints it. Whether the body names them can be checked against a syntax the writer puts there on purpose, such as a list keyed by file and heading, at `bin/docket arm`. Whether the named facts are real stays the reader's judgment. `PL-TTBF` must land first, because on a restructured section the growth figures are wrong.

**Checked 2026-11-09:** `grep -n -i "grew\|growth\|grown"` finds the request only in close-out step 8's prose in `.claude/skills/docket/modes/close-out.md`, and nothing in `subprojects/docket/src/docket/arming.py`. No check holds a pull request whose grown passages go unnamed.

**Why it matters.** Growth that adds no fact is the mark of the over-explaining that `PL-J1ZM` is about. That head stays live until sessions name the facts, and a step that two of the five measured branches skipped will be skipped again.

**Done when.** A pull request that changes a passage which `tools/new_prose.py --compare` shows growing cannot be armed until its body names, for each such passage, the facts its added words carry, or says that nothing grew. A test covers both cases.

[superseded 2026-11-10] **Was blocked on `PL-TTBF`.** A check keyed on the growth figures would have asked for facts on growth that did not happen on a restructured section. Since `PL-TTBF`, `--compare` counts such a section against the heading that both sides share, so the figures this check would read are true. Checked 2026-11-10: close-out step 8 in `.claude/skills/docket/modes/close-out.md` still asks for the facts each grown passage adds, and `subprojects/docket/src/docket/arming.py` still has no check for them, so nothing else holds this item.

**Generator check.** Part of the fix for the live head `PL-J1ZM`, which is blocked on it; one of the three failures its 2026-11-04 measurement found, and not a member of its `root-cause-of`. The pause on new workflow mechanisms does not hold it, because it fixes that generator.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, close-out step 8 did not ask for the facts a grown passage adds. That request arrived in efc1dc3f (`PL-22T5`, 2026-11-04), so this is a new problem. It is deferred with `PL-J1ZM`, which waits on it.
