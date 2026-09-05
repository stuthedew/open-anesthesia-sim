---
id: PL-MZJS
title: doc_check candidates matches a changed file's stem as a bare word, so render.py returns thirty lines of ordinary English
status: dropped
added: 2026-09-04
closed: 2026-09-05
reason: Duplicate of PL-B2NS (doc_check candidates matches ordinary prose): a changed file's stem is one of the terms PL-B2NS's fix has to decide about. Its render.py measurement - 37 lines reported, none about the module - is folded into PL-B2NS.
---

**Problem.** `python3 tools/doc_check.py candidates --base <ref>` searches the
documentation for words drawn from the diff, and a changed file contributes its
stem as a bare word. For `subprojects/docket/src/docket/render.py` that word is
`render`, which appears throughout `ROADMAP.md`, `docs/MODEL.md` and
`docs/ARCHITECTURE.md` in its ordinary English sense - chart rendering, math
rendering, a tidier rendering. Measured on `PL-YHD3`'s two-file diff: 37 lines
reported for `render.py`, of which none concerned the module.

Identifiers introduced by the diff feed the same search, so `vcs.py` added
`mine`, `holder` and `yields` and drew in `.claude/rules/expert-review.md`,
`docs/MODEL.md` and a citation rule alongside them.

**Why it matters.** The command's job is to shorten the close-out sweep by
naming the lines worth reading. A list that is ninety percent noise for a
common stem does the opposite, and `CLAUDE.md` names what follows: a signal
that fires every run without changing a decision trains a session to skim the
output, which is where a real candidate gets skimmed with it.

**Where.** `tools/doc_check.py`, the term extraction behind `candidates`.

**Done when.** A term as common in prose as it is in the tree either does not
enter the search or is reported separately from the terms that identify the
code - and the decision is stated in the tool, where a reader can check it.
