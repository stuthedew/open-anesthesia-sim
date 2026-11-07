---
id: PL-F0Q2
title: The copy editor drops requirements, qualifiers and reasons that no number or code-span check sees: on docs/MODEL.md it weakened or lost about 120 statements in 42 of 78 edited sections, turning 'must' into descriptions and cutting 'only', 'no others' and stated reasons
status: untriaged
feature: repo-copy-edit
touches: .claude/agents/copy-editor.md, tools/copy_edit.py
added: 2026-11-07
---

**Problem.** The copy editor drops requirements, qualifiers and reasons that no number or code-span check sees: on docs/MODEL.md it weakened or lost about 120 statements in 42 of 78 edited sections, turning 'must' into descriptions and cutting 'only', 'no others' and stated reasons

**What happened.** `PL-95SW` line-edited `docs/MODEL.md` with the copy editor after its fix (`PL-HGZS`). The edit passed every check on numbers, equations, code names, citations, markers and dates. Two blind reviews then found 8 lost statements, and a full comparison of each edited section's old and new text by six review agents found about 120 more in 42 of 78 sections. The losses were of four kinds: a requirement turned into a description ("must lengthen" became "a test checks that ... lengthens"; "No scientific parameter may be added without" became "Every scientific parameter added comes with"); a limiting word cut ("only", "no others", "explicit", "tagged"); a stated reason cut (why a source is tier 2, why a tier-2 citation is legitimate); and a list item or scope clause dropped (the fourth exclusion from the reproducibility guarantee). Fourteen sections went back to their old wording and 34 statements were restored (`#2049`).

**Why it matters.** `docs/MODEL.md` is the safety-critical specification. A requirement restated as a description, or a limit that loses "only", reads as a weaker claim to a later session that cites it to decide what the code must do. The same tool edited `docs/machine-abstraction.md` and `docs/machine-survey.md` (`PL-B7V7`), and rule 16 runs it on replies.

**Open question for the fix.** Whether the copy editor's instructions (`.claude/agents/copy-editor.md`) should forbid these four kinds of change, or whether `tools/copy_edit.py` should add a comparison read like the one that found them. The project owner debugs the copy editor one section at a time and approves each (2026-11-04), so the change is the project owner's to direct.
