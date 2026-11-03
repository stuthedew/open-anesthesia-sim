---
id: PL-86VL
title: Two interface-wording tests in test_simulation_view.py pass any wording they do not list: the end-tidal check misses ET, Et, EtSevo and FET, and the emergence-time check finds a hedge only in the 12 characters before its phrase
priority: P1
effort: M
status: untriaged
classes: safety, test, defect
touches: tests/integration/test_simulation_view.py
deferred-from: v0.7.0 - captured after the freeze; it strengthens two interface-wording tests, and no string the view shows today uses an end-tidal abbreviation, so the release displays nothing wrong
added: 2026-11-03
payoff: a readout labelled with an end-tidal abbreviation, or any new interface wording, cannot reach the screen without a person approving it
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

**Generator check.** One-off. The two checks are the only interface tests that
hold wording to a list of forbidden phrases, and no head records that shape.
