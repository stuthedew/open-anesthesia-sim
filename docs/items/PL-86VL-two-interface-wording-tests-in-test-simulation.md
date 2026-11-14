---
id: PL-86VL
title: Two interface-wording tests in test_simulation_view.py pass any wording they do not list: the end-tidal check misses ET, Et, EtSevo and FET, and the emergence-time check finds a hedge only in the 12 characters before its phrase
priority: P1
effort: M
status: done
classes: safety, test, defect
feature: presentation-safety
touches: tests/integration/test_simulation_view.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json, docs/ARCHITECTURE.md, tools/regex_baseline.py
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): no string the view shows uses an end-tidal abbreviation, and the alveolar readout reads "end-tidal-equivalent"; none of the eight phrases the emergence-time check guards appears in a string the view shows, only in the docstring at app/controller.py:426; so no learner can see a wrong value now
added: 2026-11-03
closed: 2026-11-11
pr: 2140
payoff: a readout labelled with an end-tidal abbreviation, or any new interface wording, cannot reach the screen without a person approving it
verify: grep -q 'def test_every_string_the_view_shows_is_on_the_approved_list' tests/integration/test_interface_wording.py && grep -q 'ET sevo' tests/integration/test_simulation_view.py
---

**Problem.** Two interface-wording tests in test_simulation_view.py pass any wording they do not list: the end-tidal check misses ET, Et, EtSevo and FET, and the emergence-time check finds a hedge only in the 12 characters before its phrase

Found on 2026-11-03 by a read-only review of the repository's regular
expressions, and filed at the owner's request.

**What the two checks do.** `tests/integration/test_simulation_view.py` reads
every string the simulation view shows and checks it two ways.

- `_UNHEDGED_END_TIDAL` refuses "end-tidal", "end tidal" or "endtidal" unless
  "-equivalent" follows. The aim is that the modeled alveolar value never
  reads as a measured end-tidal gas.
- The emergence-time test refuses phrases such as "time to wake" and
  "predicted wake" unless "not " appears in the 12 characters before the
  phrase.

**Reproduced 2026-11-03** on Python 3.13, with the test's own pattern and
window:

- `_UNHEDGED_END_TIDAL` finds nothing in "ET sevo 2.1 %", "Et 1.8", "EtSevo"
  or "FET". These are the abbreviations clinicians and anesthesia monitors use
  most often for end-tidal. No string on screen uses one today: a search of
  `src/anesthesia_sim/` found them only in data provenance notes. So nothing
  shown is wrong now, but a future label using one would pass the test.
- The 12-character window fails "this is never a time to wake", which hedges,
  and passes "not shown; predicted wake time", which does not.

**Why it matters.** `CLAUDE.md`'s safety-critical standard requires that a
predicted value not be shown in a way that could be mistaken for a
measurement. These two checks are what hold the interface to that for the
alveolar reading and for emergence. A list of forbidden phrases catches only
the wording someone thought of, and this one misses the commonest clinical
abbreviation.

**Approach (recommended).** Hold the view's text to an allowed list. Record
every string the view shows at a few fixed simulated times in a file kept
beside the test, and fail on any difference until a person approves the new
text. The simulation is deterministic, so the strings at a fixed time are too.
This is snapshot or approval testing: syrupy does it as a pytest plugin (MIT,
https://github.com/syrupy-project/syrupy), and a JSON file with a plain
comparison does the same with no new dependency. Which to use is the
implementing session's call. Keep the two forbidden-phrase checks as a second
line: widen `_UNHEDGED_END_TIDAL` to "ET", "Et", "Et" followed by an agent
name, and "FET" as whole words, and read the hedge from the clause that holds
the phrase. NegEx, the clinical-text method this window resembles, ends a
negation's scope at the end of the sentence (Harkema H, Dowling JN, Thornblade
T, Chapman WW, J Biomed Inform 2009;42(5):839-851,
doi:10.1016/j.jbi.2009.05.002).

**Done when.** A change to any text the simulation view shows fails a test
until the stored list is updated, and a readout labelled "ET sevo" fails it.
The approved-list test is named
`test_every_string_the_view_shows_is_on_the_approved_list`, and the
end-tidal check's test names "ET sevo" among the labels it refuses.

**Generator check.** One-off. The two checks are the only interface tests that
hold wording to a list of forbidden phrases, and no head records that shape.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). Both wording checks were byte-identical at `817a4d88` (`ae8fc7bc`, 2026-09-15).

**Built 2026-11-11.** `tests/integration/test_interface_wording.py` builds a dashboard with one Area for each registered View, and records every string it holds, hidden ones included, for a sevoflurane run before Start, at 2 min and at 10 min. `test_every_string_the_view_shows_is_on_the_approved_list` compares them with `tests/integration/approved_interface_strings.json`. A failure lists each string that is new or gone at each point, and says to rerun with `APPROVE_INTERFACE_WORDING=1` and commit the file, so the reviewer sees the wording change in the diff. A plain JSON file was used rather than syrupy, so there is no new dependency. The build version is replaced by `{version}` before the comparison, because it changes with every commit. Widths of 1000, 1400 and 1900 px gave the same strings, so the strings do not depend on the font or the layout.

In `tests/integration/test_simulation_view.py`, `_UNHEDGED_END_TIDAL` now also refuses "ET" and "FET" as whole words, and "Et" alone or joined to an agent's name, matched with their capitals so that "Reset" and "Settings" pass. The wake-up check reads the negation from the clause that holds the phrase, with "not", "never", "no" or "cannot" counting, instead of the 12 characters before it. `test_the_end_tidal_check_refuses_each_spelling_and_abbreviation` names "ET sevo 2.1 %" among the labels it refuses. Against the code before the fix, the old pattern finds none of "ET sevo 2.1 %", "Et 1.8", "EtSevo" and "FET", so those four cases fail; the old 12-character window passes "not shown; predicted wake time" and refuses "this is never a time to wake", so `test_the_wake_up_check_reads_the_hedge_from_the_phrase_s_own_clause` fails on both (checked by running the old expressions on the same inputs).

**Every branch that changes interface text now updates the approved list.** Two open branches change text on screen: the agent-amount captions (`PL-HQPF`, #2136) and the start-over work (`PL-MVCF`, #2138, whose withheld-value strings show only on a halt and so are not recorded here). Whichever merges second reruns the approval and commits the file.

**Blind review, pass 1 (2026-11-11).** Four should-fix findings, all fixed.
(1) The wake-up check took a negation anywhere earlier in the clause, and only
sentence marks ended a clause, so "Modelled, not measured, predicted wake"
passed. A comma or a dash now ends a clause too, and the negation must stand
among the four words before the phrase. (2) The abbreviation pattern needed a
word boundary after the abbreviation, so "ET2.1%", "Et1.8 %", "EtSevo2.1",
"ETsevo", "EtSEV", "EtAA" and "etSev" passed. The pattern now says which letter
may not follow each form, and the refused list names all seven. (3) Only the
default sevoflurane run was recorded. Desflurane and isoflurane are now
recorded at 2 min, and the test module and `docs/ARCHITECTURE.md` say that a
string shown only after a setting change, or in a halt or failure notice, is
not on the list. `PL-4G79` holds the rest. (4) The list held every model value,
so a correct model change would fail with dozens of numbers and bury a wording
change. Each digit is now masked as `#`, which keeps the count of digits and
the decimal point, so a change of displayed precision still fails.
