---
id: PL-HNNH
title: Sessions skip naming, in the pull request body, the facts a grown passage adds: PL-W6JM's two docstrings grew by 44 and 46 words and PL-J37P's subsections grew, and neither body says what the added words carry, though tools/new_prose.py --compare printed the growth
priority: P1
effort: M
status: ready
classes: defect
feature: copy-editor
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_arming.py, subprojects/docket/README.md, docket.toml, tools/new_prose.py, tools/open_pull_requests.py, tests/unit/test_new_prose.py, .claude/skills/docket/modes/close-out.md
blocked-by: PL-TTBF
deferred-from: v0.7.0 - a new problem, not present at the freeze: the request to name a grown passage's facts arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
payoff: every grown passage on a branch has its added facts named before merge, so growth with no new fact, the mark of over-explaining, is caught on the branch that adds it
verify: grep -qE '^[*][*]Re-diagnosed, 20' docs/items/PL-HNNH-*.md
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

**Decision needed.** Is this item kept, changed or dropped? The session re-diagnosing `PL-J1ZM` decides, at the project owner's word of 2026-11-11.

**Stopped, 2026-11-11** (project owner). A fresh session is re-diagnosing `PL-J1ZM` from the start and will say whether this item is kept, changed or dropped. The item is open again, the claim is released, and nothing below has merged. A complete build of this item and of `PL-TG6P` is on branch `claude/peaceful-noether-5bvpno`, in draft pull request #2115, at commit `98050deaf`. It is unarmed. `bin/docket verify --self PL-HNNH PL-TG6P` accepted that commit and `make check` passed there. Close-out step 8's copy edit of the six test docstrings that the build adds was started and stopped unfinished, and the branch is 2 commits behind `origin/main`. If the item is dropped, close #2115 unmerged. If it is kept as built, finish the close-out there. The paragraphs below describe that build as it stands on the branch. The session that decides records the decision here in a paragraph that opens "**Re-diagnosed, ", which is what `verify:` now tests, and then rewrites `verify:` for the work that is left. The build's own test is named in the paragraph below.

**Built on the branch, 2026-11-11.** `bin/docket arm` now holds a pull request that changes a simulator path until its body has one list item for each passage that grew. The item opens ``- Added words in `FILE` § "HEADING": `` and the facts follow its colon, on the same line. `tools/new_prose.py --compare` prints the items to complete, and the hold prints the ones that are missing, each with its rows and word counts. `arm` reads the body through `docket.toml`'s new `body_prose_command`, which runs `tools/new_prose.py --body-check NUMBER`. That mode reads the committed branch and fetches the body from GitHub through `tools/open_pull_requests.py`. Its test is `test_arm_holds_until_the_body_names_each_grown_passage` in `subprojects/docket/tests/test_arming.py`.

**What the earlier fixes built, and why sessions still skipped the step.** `PL-JP8X` built `--compare`, which prints each changed passage's words before and after. `PL-22T5` wrote the request for the facts into close-out step 8, as the last sentence of one of its ten paragraphs. `PL-TTBF` made the growth figures true for a section rewritten under new subheadings. None of them read the pull request body. In the same step, `PL-W04Z` had put the `Prose-review:` trailer behind a hold in `arm`, and every measured branch recorded that trailer and gave its three counts in the body. The part of the step that a check asked for was done on every branch, and the part that only prose asked for was skipped on two branches of five.

**Decisions taken in the build.**

1. A body owes nothing where no passage grew, and need not say that nothing grew. The check itself reports that, and a sentence required on every pull request would be written without being read.
2. A passage grew when it held prose at the fork and holds more words now. A passage that is new on the branch owes no item. It has no earlier text, and the copy editor reads it whole.
3. An item is keyed by file and section heading, and by file alone in a Python file. Rows move with every edit, so one item covers every grown passage under the same file and section.
4. The item may say why a passage grew with no new fact, such as a compressed sentence split in two. The check tests that an item is there and has text. Whether the text names real facts stays the reader's judgment, as this brief said.
5. The hold applies where the branch changes a simulator path, the same condition as the `Prose-review:` hold. `PL-P7B3` records the reviewed documents outside those paths that this leaves unchecked, with the count.

**Findings for the re-diagnosis, 2026-11-11.**

1. Growth alone does not mark over-explaining. Both before-and-after pairs under "Three examples from this repository" in `.claude/rules/plain-writing.md` are longer after the rewrite than before, because the rule also asks for whole sentences. So a check on growth has to accept an item that says a passage grew with no new fact, and then it tests only that the session wrote something.
2. The measurement's five branches split by whether a check asked for the step. All five recorded the `Prose-review:` trailer, which `bin/docket arm` holds on. Two skipped the list of facts, which only close-out step 8's prose asked for.
3. A hold on the body needs the body. `arm` already asks GitHub whether the pull request merged, so reading the body adds one request and one `uv run` to each answer on a simulator branch.
