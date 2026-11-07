---
id: PL-F0Q2
title: The copy editor drops requirements, qualifiers and reasons that no number or code-span check sees: on docs/MODEL.md it weakened or lost about 120 statements in 42 of 78 edited sections, turning 'must' into descriptions and cutting 'only', 'no others' and stated reasons
priority: P1
effort: M
status: untriaged
classes: defect
feature: repo-copy-edit
touches: .claude/agents/copy-editor.md, tools/copy_edit.py
deferred-from: v0.7.0 - captured after the freeze; workflow tooling, worked now at P1 because the owner paused the remaining copy edits until it lands, and nothing the schematic release ships waits on it
added: 2026-11-07
---

**Problem.** The copy editor drops requirements, qualifiers and reasons that no number or code-span check sees: on docs/MODEL.md it weakened or lost about 120 statements in 42 of 78 edited sections, turning 'must' into descriptions and cutting 'only', 'no others' and stated reasons

**What happened.** `PL-95SW` line-edited `docs/MODEL.md` with the copy editor after its fix (`PL-HGZS`). The edit passed every check on numbers, equations, code names, citations, markers and dates. Two blind reviews then found 8 lost statements, and a full comparison of each edited section's old and new text by six review agents found about 120 more in 42 of 78 sections. The losses were of four kinds: a requirement turned into a description ("must lengthen" became "a test checks that ... lengthens"; "No scientific parameter may be added without" became "Every scientific parameter added comes with"); a limiting word cut ("only", "no others", "explicit", "tagged"); a stated reason cut (why a source is tier 2, why a tier-2 citation is legitimate); and a list item or scope clause dropped (the fourth exclusion from the reproducibility guarantee). Fourteen sections went back to their old wording and 34 statements were restored (`#2049`).

**Why it matters.** `docs/MODEL.md` is the safety-critical specification. A requirement restated as a description, or a limit that loses "only", reads as a weaker claim to a later session that cites it to decide what the code must do. The same tool edited `docs/machine-abstraction.md` and `docs/machine-survey.md` (`PL-B7V7`), and rule 16 runs it on replies.

**Open question for the fix.** Whether the copy editor's instructions (`.claude/agents/copy-editor.md`) should forbid these four kinds of change, or whether `tools/copy_edit.py` should add a comparison read like the one that found them. The project owner debugs the copy editor one section at a time and approves each (2026-11-04), so the change is the project owner's to direct.

**Approach** (chosen by this session on 2026-11-07 and told to the project owner in the thread, not yet ratified). Both halves of the open question. The instructions are fixed where they invite the losses: step 4 lists "a reason the reader cannot act on" among what a reader can do without, step 3 rewrites a paragraph from a list of facts that carries no requirement's force, and the list of what must never be cut names no "must", no limiting word such as "only", no list count, no scope clause and no stated reason. `tools/copy_edit.py` also gains a comparison read after the edit: a separate run whose one job is to compare each original sentence with the edit for those five things, with each statement it finds lost sent back to be restored. The instructions already asked for that comparison twice (step 7, and step 3 of the second read), and up to four reads still lost about 120 statements, while an audit given that one job found them. Models broaden claims even when told to be accurate: "Even when explicitly prompted for accuracy, most LLMs produced broader generalizations" (Peters and Chin-Yee, arXiv:2504.00025, 2025). A model that reviews its own output without outside feedback rarely improves it (Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024, arXiv:2310.01798).

**Test set.** Six parts of `docs/MODEL.md` as it stood before `#2049` (commit d26e8c70), as `tools/new_prose.py` splits it for a line edit, with the losses the audit found in each: 42 "v0.2.0: isoflurane and desflurane" (5), 43 "Delivery-limit and MAC parameters" (6), 37 "Supported simulation step" (5), 75 "Supported run length" (10), 71 "The canonical evaluation rule" (13), and 118, the second run of "Known limitations" (7). The audit findings are in the project's shared folder, `v0.7.0/repo-copy-edit/audit-findings/`.

**Done when.** On each part of the test set, the fixed copy editor keeps every statement that the audit found lost there, and a fresh audit of its edit, by the brief that found them, reports no requirement, limiting word, list item, scope clause or stated reason lost. The project owner has then approved the parts one at a time, each before the next, with any change to the instructions starting again from the first (project owner, 2026-11-04).

**Generator check.** The fact misread is that a passage the copy editor rewrote still says everything the original said, with the same force and scope. `PL-B7V7`, the audit of the two machine documents, is the only other item it caused, and a generator needs two. `PL-HGZS`'s misread is a different fact: that a passage the copy editor passed is plain enough for its reader. So this is a defect the owner asked to have fixed, and no generator.

**Decision.** The remaining copy edits of the repository wait until this is fixed (project owner, 2026-11-07, ratified, over continuing with a six-reviewer audit of each document before it merges). The references and maintainer-guide edits run on the owner's Mac (branch `claude/repo-copy-edit-api`) stay unmerged until then, and are re-run or audited on the fixed copy editor.
