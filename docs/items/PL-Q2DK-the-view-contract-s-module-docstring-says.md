---
id: PL-Q2DK
title: The View contract's module docstring says pinning a View to one run is left to PL-7Z84, which is done, and cites a ROADMAP heading that has since gained the word Completed
priority: P3
effort: S
status: done
classes: defect, docs
feature: repo-copy-edit
touches: src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/area_layout.py
deferred-from: v0.7.0 - a new problem: the cited heading was renamed after the freeze, by #2058 (7081a909, PL-W0TS), work done while clearing this gate
added: 2026-11-11
closed: 2026-11-22
pr: 2211
payoff: A reader following the View contract or the Area layout to the roadmap finds the section by the heading the citation names.
verify: ! grep -qF '§ "v0.6.0 - the layout is the reader' src/anesthesia_sim/app/view_contract.py
---

**Problem.** The View contract's module docstring says pinning a View to one run is left to PL-7Z84, which is done, and cites a ROADMAP heading that has since gained the word Completed

The copy editor found both while reading `PL-9YPR`'s changed prose
(2026-11-11). Neither sentence was written by that item, so neither was
changed there.

1. `src/anesthesia_sim/app/view_contract.py`, the last paragraph of the module
   docstring: "Where a Workspace pins a View to one run, that binding is left
   to `PL-7Z84`. Until then, every View draws every displayed run." `PL-7Z84`
   is done, and `app/simulation_view.py`'s module docstring says "A Workspace
   pinned to a run draws that run alone". The sentence should say how a pinned
   Workspace reaches a View today.
2. The same docstring cites `ROADMAP.md` § "v0.6.0 - the layout is the
   reader's" twice. The heading is now "Completed: v0.6.0 - the layout is the
   reader's".

**Checked 2026-11-22**, at `d4e8200c`. The first part is fixed: #2200
(`b74bd381`) rewrote the paragraph, which now says "A Workspace that pins a run
draws that run alone, in every one of its Views (`PL-7Z84`)" (line 127). The
second part is still there. `grep -rn '§ "v0.6.0 - the layout is the reader' src`
printed two citations, `app/view_contract.py:4` and `app/area_layout.py:105`,
while `ROADMAP.md` line 6012 reads `## Completed: v0.6.0 - the layout is the
reader's`. The heading gained the word on 2026-11-07, in #2058 (`7081a909`,
`PL-W0TS`), after the Gate 3 freeze. The document check still passes, because
it tests a docstring's citation by whether the document holds the words, and
the words are inside the longer heading.

**Why it matters.** A section mark tells a reader which heading to search for.
A heading that no longer matches sends them to search by hand, and it hides
the citation from any later check that compares citations with headings.

**Done when.** Each citation in `src/` of the v0.6.0 roadmap section names the
heading as `ROADMAP.md` now gives it.

**Generator check.** The fact is which heading a `§` citation names. See
`PL-GC7Z` (a citation of a `docs/MODEL.md` note in a form no check reads):
both are citations that the document check cannot test against the cited
document's headings, and `PL-97S1` was a third. No head's `misread:` states
that fact.

**Done 2026-11-22**, in `PL-LPCB`'s change. The first point was already fixed
on main: the module docstring's last paragraph says that a Workspace that pins
a run draws that run alone, in every one of its Views. Both citations of the
milestone heading now name it as `ROADMAP.md` writes it, with "Completed: ".
The document check now refuses a section mark whose heading the document does
not hold as written, so the next heading that gains a word is caught.
