---
id: PL-XYJF
title: docket's checks._passage starts a passage at a soft-wrapped line opening with 17. or a pipe, which CommonMark keeps in the paragraph above, so _standing, _left_statuses and _ended_waits read a superseded passage as standing and advise on it; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's checks._passage starts a passage at a soft-wrapped line opening with 17. or a pipe, which CommonMark keeps in the paragraph above, so _standing, _left_statuses and _ended_waits read a superseded passage as standing and advise on it; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. On a `ready` item, `[superseded 2026-09-30] ... count at\n17. It is left at "needs-decision" ...` makes the passage start at "17.", so `_standing` returns True and `_left_statuses` emits the brief-status advisory; the same text on one line gives []. An ordered list interrupts a paragraph only when it starts at 1 (CommonMark 0.31.2 § 5.2). Latent: no such split in the 293 open briefs.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
