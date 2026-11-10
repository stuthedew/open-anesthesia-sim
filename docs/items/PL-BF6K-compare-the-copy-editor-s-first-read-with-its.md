---
id: PL-BF6K
title: Compare the copy editor's first read with its last read on saved runs, using the blind judge, before deciding whether to cut the audit reads
priority: P2
effort: M
status: ready
classes: session-cost
feature: copy-editor
touches: tools/copy_edit.py, docs/prose-review/README.md
added: 2026-11-10
payoff: the owner decides on a measurement whether three of the copy editor's four reads earn their time and cost
verify: grep -qE '^[*][*]Measured 20' docs/items/PL-BF6K-*.md
---

**Problem.** Compare the copy editor's first read with its last read on saved runs, using the blind judge, before deciding whether to cut the audit reads

**Why it matters.** The copy editor reads each request up to four times
before the meaning check starts (`MAX_READS` in `tools/copy_edit.py`), and a
request can take 18 model runs in all: four reads, ten meaning checks and
four restore reads. Every run on record used all four reads. Four reads of a
1,174-word section took about 37 minutes and $4.94, and four reads of 5,348
words took about 65 minutes and $9.44 (`PL-HGZS`, runs 20 to 24, before the
meaning check existed). The owner said on 2026-11-10 that the copy editor
helps but takes a long time and uses many tokens.

Published work on model self-revision finds that later rounds add little.
Madaan et al. report "diminishing returns in the improvement as the number
of iterations increases" (Self-Refine, https://arxiv.org/abs/2303.17651).
Tao et al. find the gain from a model reflecting on its own output near zero
or negative, and recommend an independent sample or an outside check
(https://arxiv.org/abs/2607.28908). The meaning check is such an outside
check. The three audit reads are the copy editor revising its own edit.

The owner ratified audits until clean with a limit of four on 2026-11-05,
over exactly two reads (`PL-HGZS`). A ratified decision reopens on ordinary
evidence, and this measurement would be that evidence.

**How to do it.** `tools/copy_edit.py --reads DIR` keeps each read's request
and reply. On sections the copy editor's instructions were not tuned on, run
the copy editor with `--reads`, then give the blind judge
(`tools/prose_judge.py`) the first read's text against the last read's text
for each passage. Count how often the judge prefers the last read, and count
the statements the meaning check finds lost in each version.

**Done when.** This item records the result in a paragraph that opens
"**Measured 20**" with the date, and either puts a change of `MAX_READS` to
the owner with that result or says why the limit of four stays.

**Generator check.** A one-off. It measures part of the fix built for
`PL-J1ZM` (sessions over-explain in every kind of text), so the pause on new
workflow mechanisms does not hold it.
