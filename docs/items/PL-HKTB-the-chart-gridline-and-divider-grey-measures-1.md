---
id: PL-HKTB
title: The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture
priority: P2
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: tools/contrast_check.py, src/anesthesia_sim/app/theme.py
added: 2026-09-08
---

**Problem.** The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture

**Why it matters.** Every other colour pair in this interface carries a declared
contrast requirement that `tools/contrast_check.py` enforces, and this one
carries none - so the question of whether it is legible has never been asked,
rather than having been asked and answered "exempt". WCAG 2.2 does not require
a minimum for purely decorative furniture, and a chart gridline plausibly is
that; a divider separating two regions of content plausibly is not, since it
carries structure a reader uses. At 1.31:1 it is far below the 3:1 that would
make it a non-text contrast pass, so if it is ever load-bearing it is failing.

The value of settling it is that the answer gets written down either way. A
recorded exemption is as good an outcome as a darker grey, and better than a
colour nobody has a requirement for - which is how this one has survived.

**Decision needed.** Whether the gridline and divider grey is darkened to meet
3:1 as a non-text contrast requirement, or recorded in `tools/contrast_check.py`
as exempt furniture with the reason. Note the two may separate: a gridline is a
stronger candidate for exemption than a divider, and there is no need to give
them one answer.

**Sequencing.** `PL-L9RD` re-expresses `app/theme.py` for Qt and makes the
interface pass's visual decisions once. This is one of those decisions, so it
lands there unless it is answered sooner - deciding it twice is the thing that
item exists to prevent.

**Done when.** The grey either meets a declared requirement in
`tools/contrast_check.py` or is recorded there as exempt with the reasoning, and
`make check` reports it under whichever it is.
