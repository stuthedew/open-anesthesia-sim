---
id: PL-VJNQ
title: docs/machine-survey.md admits a machine on a study published 2006-2025, and no record gives the reason for the 2006 start year or says what moving it would change
priority: P3
effort: S
status: ready
classes: docs
feature: machine-docs-structure
touches: docs/machine-survey.md
added: 2026-11-11
payoff: A contributor can tell whether a machine studied before 2006 belongs in the survey, and what admitting it would change.
---

**Problem.** `docs/machine-survey.md` § "The machines surveyed, and why those" admits a machine if it is the subject or comparator of a peer-reviewed study published between 2006 and 2025. The window's end is the survey's own year. No record gives a reason for the start year. The survey that set it (`PL-4DCG`, 2026-09-19) has no "2006" in its brief, and `git log -S 2006 -- docs/machine-survey.md` finds only that survey and the 2026-11-08 restructure (`PL-3MTS`). The oldest study inside the window is Fukuda et al. 2006, but nothing records that it set the start. A reader who wants to add a machine studied only before 2006, such as the Dräger Sulla 808V in Biro 1997, cannot tell whether the window was meant to keep it out.

**Fix.** Decide what the start year is for: a proxy for machines still in service, or a bound on the search. Write that reason beside the rule, with what moving it would change. If no reason holds up, choose a start year that one does support.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "records no reason for its start year" docs/machine-survey.md` still finds the sentence "The survey that set the window (`PL-4DCG`) records no reason for its start year", and the rule still reads "published between 2006 and 2025".

**Why it matters.** The window decides which machines the survey admits, and so which machines a future machine profile can be compared with. A contributor who finds a useful study published before 2006 cannot tell whether the window was meant to exclude it, so they either leave out a machine on a rule nobody chose or widen the rule without knowing what it protected.

**Done when.** The rule in `docs/machine-survey.md` gives the start year's reason, and the sentence "The survey that set the window (`PL-4DCG`) records no reason for its start year" is gone.

**Found by** `PL-8ZD7` (2026-11-11), answering the structure read's query on the window.

**Generator check.** A one-off. The misread fact is why one inclusion rule chose its start year, which nobody recorded when `PL-4DCG` set it. No head's `misread:` states a missing reason for a chosen value.
