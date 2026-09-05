---
id: PL-BFV8
title: "The simulator cannot be cited: no CITATION.cff, no DOI, and nothing in the repository says how to reference it"
status: dropped
feature: documentation-standard
touches: CITATION.cff
added: 2026-09-05
closed: 2026-09-05
reason: duplicate of PL-8DDG, which landed CITATION.cff on main from a concurrent session working the same paper and is better stated - it reasons the DOI, `version` and `date-released` questions through and defers them to the release path rather than leaving them open
---

**Problem as filed.** Lee 2018 rule 10 asks that software say how to cite it,
and this repository had no `CITATION.cff`, no DOI and no citation section.
True when `PL-MPZ0`'s audit ran against `af1804b`; false by the time that work
was pushed.

**What actually happened.** `PL-8DDG` (add CITATION.cff so the simulator is
citable) merged as #338 while this branch was open, from a session reading the
same paper. `CITATION.cff` is at the root at CFF 1.2.0 with the four required
keys plus `abstract`, `type`, `repository-code`, `license` and `keywords`.

**Why nothing is left here.** The two questions this item would otherwise have
carried are already answered on `PL-8DDG`, and answered better: `version` and
`date-released` are deliberately absent, because both go stale at every release
and nothing in `make check` reads the file; and a DOI, if one is ever minted,
brings those fields with it and must be written by `docket release` rather than
by hand. That is the right sequencing and it is recorded there. The DOI
decision itself remains the project owner's and is not lost — it is stated as a
condition on `PL-8DDG` rather than as an open item.
