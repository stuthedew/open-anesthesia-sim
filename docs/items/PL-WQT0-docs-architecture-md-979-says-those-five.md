---
id: PL-WQT0
title: docs/ARCHITECTURE.md:979 says 'those five commands' where the list nine lines above names four and quality.yml runs four, and doc_check passes over the contradiction
priority: P3
effort: S
status: dropped
classes: docs
touches: docs/apparatus.md
added: 2026-09-19
closed: 2026-10-11
reason: dead on PL-YVV4's count (2026-10-11): the passage moved to docs/apparatus.md (#1400) and says 'those six commands' over a six-item list since 5bb363a2 (#882); what is left of the list's staleness is PL-5N7T's
payoff: stops the architecture doc telling a session CI runs five floor commands where it runs four
verify: grep -qF 'four commands' docs/apparatus.md
---

**Problem.** docs/ARCHITECTURE.md:979 says 'those five commands' where the list nine lines above names four and quality.yml runs four, and doc_check passes over the contradiction

**Why it matters.** The sentence is a claim about what CI runs, in the document
a session reads to find out. The list nine lines above it names four commands -
`python3 tools/doc_check.py check`, `python3 tools/branch_id_check.py`,
`python3 tools/rules_paths_check.py` and `bin/docket check` - and the floor
section of `.github/workflows/quality.yml` runs those four. The count was right
until `PL-L17Q` removed `contrast_check.py` from that job and left the closing
sentence at five, so the paragraph now contradicts its own list.

`tools/doc_check.py` cannot catch it: the count is a statement about prose
rather than a path, a section or a line citation, and none of its checks reads
an English numeral against the length of a list above it. Verified against the
tree 2026-09-20.

**Done when.** `docs/apparatus.md`'s sentence names the same number of
commands the list above it does.

**Re-pointed 2026-10-11 (`PL-KRGY`).** The paragraph moved with the rest of
the `tools/` section to `docs/apparatus.md` § "Developer tooling (`tools/`)",
so `touches`, `verify:` and the Done-when name that file; the title's line
number describes `docs/ARCHITECTURE.md` before the move. Read that day, the
contradiction the title names is gone: the list names six commands and the
sentence after it says "those six commands". The list itself is stale instead,
since the bare-interpreter section of `.github/workflows/quality.yml` runs
seven, adding `python3 tools/pr_body_check.py --anchors`, which is `PL-5N7T`'s
drift. A session starting this re-confirms it first.
