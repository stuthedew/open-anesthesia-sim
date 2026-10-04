---
id: PL-B1D0
title: docket's instructions.parse dates a soft-wrapped record by the newest date on each physical line, so a record whose re-verified date wraps onto the next line is read as two assertions, the first already old: CLAUDE.md lines 229-230 and 569-570 today, reported stale from 2026-12-16
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's instructions.parse dates a soft-wrapped record by the newest date on each physical line, so a record whose re-verified date wraps onto the next line is read as two assertions, the first already old: CLAUDE.md lines 229-230 and 569-570 today, reported stale from 2026-12-16

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `(measured 2026-06-01, re-verified\n2026-10-04).` is read as two assertions: line 1 dated 2026-06-01, over `instruction_stale_days` (90), and the fragment `2026-10-04).` dated today; on one line it is one assertion dated 2026-10-04. Live input: `CLAUDE.md` lines 229-230 (2026-09-16, re-anchored 2026-09-21 on the next line) and 569-570 (2026-09-25 / 2026-10-03); line 229 is reported from 2026-12-16 where the record's newest date gives 86 days. Its docstring takes the line as its unit on purpose, comparing it only with counting each date, never with a statement that wraps.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
