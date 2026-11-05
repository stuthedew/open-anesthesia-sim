---
id: PL-HNNH
title: Sessions skip naming, in the pull request body, the facts a grown passage adds: PL-W6JM's two docstrings grew by 44 and 46 words and PL-J37P's subsections grew, and neither body says what the added words carry, though tools/new_prose.py --compare printed the growth
status: untriaged
feature: copy-editor
added: 2026-11-04
---

**Problem.** Sessions skip naming, in the pull request body, the facts a grown passage adds: PL-W6JM's two docstrings grew by 44 and 46 words and PL-J37P's subsections grew, and neither body says what the added words carry, though tools/new_prose.py --compare printed the growth.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04"). `PL-W6JM`'s `prepare_clone` docstring went from 40 words to 86, and its test docstring from 12 to 56. #2021's body gives the copy editor's counts and no facts for the growth. #2022's thread read the rule and its comparison showed growth, but its body has no such list and does not say that nothing grew. `PL-BSYT`, `PL-9331` and `PL-SMM2` named them.

**What a fix needs.** Which passages grew is decidable: `tools/new_prose.py --compare` prints it. Whether the body names them can be checked against a syntax the writer puts there on purpose, such as a list keyed by file and heading, at `bin/docket arm`. Whether the named facts are real stays the reader's judgment. `PL-TTBF` must land first, because on a restructured section the growth figures are wrong.
