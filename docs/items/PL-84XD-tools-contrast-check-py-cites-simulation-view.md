---
id: PL-84XD
title: tools/contrast_check.py cites simulation_view.py line numbers that no longer point at what they claim
status: dropped
added: 2026-09-05
closed: 2026-09-05
reason: Duplicate of PL-GJDW (contrast_check's requirement descriptions cite simulation_view line numbers, and all eight are wrong): same REQUIREMENTS tuple, same rot, same fix. Its 2026-09-05 line-by-line recheck, the three entries already citing by symbol, and its proposal that contrast_check refuse a simulation_view.py:NNN criterion are folded into PL-GJDW.
---

**Problem.** tools/contrast_check.py cites simulation_view.py line numbers that no longer point at what they claim

**Why it matters.**

**Where.**

**Done when.**

**Problem.** Nine of the entries in `tools/contrast_check.py`'s `REQUIREMENTS`
name where their colour pair appears as `simulation_view.py:NNN` line numbers -
`:208`, `:242-244`, `:320`, `:336`, `:346`, `:356`, `:406`, `:417`, `:619`,
`:622`, `:653`, `:678`, `:682`, `:731`. Checked line by line on 2026-09-05: not
one of them lands on what its entry claims. `:682` is cited as "the run-status
word while running" and is the control-mark series list; `:406` is cited as the
educational-use disclaimer and is a comment about agent render styles; `:731` is
cited as an accounting status word and is a chart gridline colour.

**Why it matters.** The criterion string is the *judgment half* of this tool -
the part `tools/contrast_check.py`'s own header says a person writes and the
tool only evaluates, because deciding which background a colour is actually
drawn on is not decidable from the palette. `.claude/rules/ui-color.md`'s
judgment 1 asks a session adding a colour to "read the source and confirm which
background it is drawn on"; the citation is what makes that re-checkable. A
citation that silently points somewhere else sends the next session to the
wrong line, and a session that follows one and finds an unrelated comment
learns to stop following them - which is the whole entry going unread, not one
number.

It rots by construction: nothing verifies these, and any edit above a cited
line moves it. `tools/doc_check.py`'s dangling-citation check reads `docs/`
and does not look at `tools/`.

**Where.** `tools/contrast_check.py`, the `REQUIREMENTS` tuple.

**Done when.** No `REQUIREMENTS` criterion locates a usage by line number.
Three entries already cite by symbol instead - `_build_agent_accounting_panel`,
`_off_scale_text`, `_build_new_case_dialog` - and that form does not rot,
because a renamed symbol is a rename a session performs deliberately. Convert
the rest, and decide whether `contrast_check.py` should refuse a criterion
matching `simulation_view.py:\d` so the form cannot come back. Prefer the
check if it is a few lines: this is exactly the decidable half the project's
tooling rule asks to be moved out of a session's head.
