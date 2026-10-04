---
id: PL-B1D0
title: docket's instructions.parse dates a soft-wrapped record by the newest date on each physical line, so a record whose re-verified date wraps onto the next line is read as two assertions, the first already old: CLAUDE.md lines 229-230 and 569-570 today, reported stale from 2026-12-16
priority: P2
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/checks.py, subprojects/docket/README.md, docket.toml, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: a dated record is read as the sentence it is, so the stale-instruction advisory dates it by its newest date wherever its line breaks fall, and never reports one re-verified on its next line
verify: grep -qF '"instruction audit, ' tests/unit/test_doc_check.py
---

**Problem.** docket's instructions.parse dates a soft-wrapped record by the newest date on each physical line, so a record whose re-verified date wraps onto the next line is read as two assertions, the first already old: CLAUDE.md lines 229-230 and 569-570 today, reported stale from 2026-12-16

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `(measured 2026-06-01, re-verified\n2026-10-04).` is read as two assertions: line 1 dated 2026-06-01, over `instruction_stale_days` (90), and the fragment `2026-10-04).` dated today; on one line it is one assertion dated 2026-10-04. Live input: `CLAUDE.md` lines 229-230 (2026-09-16, re-anchored 2026-09-21 on the next line) and 569-570 (2026-09-25 / 2026-10-03); line 229 is reported from 2026-12-16 where the record's newest date gives 86 days. Its docstring takes the line as its unit on purpose, comparing it only with counting each date, never with a statement that wraps.

**Reproduced 2026-10-04, at triage.** `instructions.parse` reads `(measured 2026-06-01, re-verified\n2026-10-04).` as two assertions, line 1 dated 2026-06-01 and line 2 dated 2026-10-04, and the same record on one line as one, dated 2026-10-04. `CLAUDE.md`'s record at line 229 is dated 2026-09-16 where its newest date is 2026-09-21, so it reads stale from 2026-12-16, at 86 days.

**Why it matters.** The stale-instruction advisory asks a session to re-verify a record, so one re-verified on its next line is reported stale while it is current: a session re-checks what was just checked, or learns to skim the advisory.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** A dated record is one assertion, dated by its newest date wherever the paragraph's line breaks fall, pinned by an `instruction audit, ...` case in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** `parse` reads each file a paragraph at a time through `roadmap.statement_lines`, a CommonMark walker checked against markdown-it-py 4.2.0 on every tracked Markdown file, and splits each paragraph into sentences at `roadmap.SENTENCE_BREAK`. An assertion is a sentence, dated by its newest date and placed on the line holding it - not the paragraph, which would date a paragraph's oldest claim by its newest. Over the instruction set seven date occurrences moved, each onto a newer date, and no line's dates fell in two sentences; on 2026-12-16, 29 assertions read stale where 31 did. The advisory now asks for today's date in the sentence, and `subprojects/docket/README.md` says a sentence where it said a line. `docket.toml` counted `docs/maintainer.md`'s dated assertions at 12, which was stale under either reading - 38 lines, 33 sentences - and now says 33. One guard case, failing on main's reader.
