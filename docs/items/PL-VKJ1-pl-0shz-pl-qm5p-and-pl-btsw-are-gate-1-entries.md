---
id: PL-VKJ1
title: PL-0SHZ, PL-QM5P and PL-BTSW are Gate 1 entries citing line numbers in a README.md deleted the same day they were filed
status: untriaged
feature: project-introduction
added: 2026-09-06
---

**Problem.** PL-0SHZ, PL-QM5P and PL-BTSW are Gate 1 entries citing line numbers in a README.md deleted the same day they were filed

**Why it matters.**

**Where.**

**Done when.**

**Problem.** Three entries on the Gate 1 list state their defect as a line
number in the root `README.md`: `PL-0SHZ` cites `README.md:185-192` (the
bare-interpreter paragraph naming two `ruff.toml` pins), `PL-QM5P` cites
`README.md:179` (the `doc_check.py` `candidates` gloss), and `PL-BTSW` cites an
unwrapped line left by `#336`. All three were filed 2026-09-05. The root
`README.md` was deleted later the same day, by `#366` (`PL-WB5K`), and
`tools/readme_hold_check.py` now makes its absence a hard error. All three
still carry `touches: README.md` and `status: blocked`, `blocked-by: PL-N092`.

**Why it matters.** The stated problem cannot be reproduced, so a session that
picks one up spends its first minutes discovering the file is gone. The
sequencing behind `PL-N092` is right — each is really a constraint on the
README that gets written, not a defect in one that exists — but nothing in the
three says so, and the titles assert the present tense. Gate 1 is also the
project's measure of readiness for v0.5.0: three of its 117 open entries
currently describe a file the tree does not hold, which overstates the gate by
whatever share of it turns out to be moot.

**The distinction to draw, per item.** `PL-QM5P` and `PL-0SHZ` describe
statements a *new* README would only carry if it chose to restate tooling
detail, which `PL-RM83`'s boundary rule argues against — so both may be
`dropped` with a reason once `PL-N092` lands, rather than worked. `PL-BTSW` is
narrower still: the unwrapped line it records went with the deleted file, and
what survives is the freeze-procedure finding already recorded in its own body.
`PL-4MHK` is not in this set — its subject is `pyproject.toml`, which exists.

**Do this as part of `PL-N092`, not before it.** Deciding now what each item
becomes means deciding against a README nobody has written. The cheap, correct
moment is the close-out of `PL-N092`, when the new file is in front of the
session: each of the three is then either satisfied, restated against a real
line, or dropped with a reason.

**Done when.** None of `PL-0SHZ`, `PL-QM5P` or `PL-BTSW` states its problem as
a location in a file the tree does not hold, and each is closed, dropped with a
reason, or restated as a requirement on the README that now exists.
