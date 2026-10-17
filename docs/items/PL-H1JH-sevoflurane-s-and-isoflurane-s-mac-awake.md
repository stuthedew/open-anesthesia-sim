---
id: PL-H1JH
title: Sevoflurane's and isoflurane's MAC-awake fraction_of_mac and all three agents' standard_deviation_fraction_of_mac have no behavioural oracle or literal pin from the adopted primary source, so a 10% transcription error passes every data-dependent simulator test, and desflurane's one published check passes only by float rounding
status: untriaged
feature: tests-detect-wrong-values
added: 2026-10-17
---

**Problem.** Sevoflurane's and isoflurane's MAC-awake fraction_of_mac and all three agents' standard_deviation_fraction_of_mac have no behavioural oracle or literal pin from the adopted primary source, so a 10% transcription error passes every data-dependent simulator test, and desflurane's one published check passes only by float rounding

**Severity: safety.** The MAC-awake band is the emergence threshold a learner
reads the brain trace against. Audit finding DP-1. The verifier rated it
"partly" true and corrected it; the corrected claim is what this item states.

**Evidence.** The stored values sit under `mac_awake` in
`src/anesthesia_sim/data/agents/*.json`. Sevoflurane is 0.34 ± 0.05 x MAC and
isoflurane 0.31 ± 0.05, both from Katoh et al. 1993 (Anesth Analg
77(5):1012-1017; tier primary, adopted). Desflurane is 0.36 ± 0.063, from
Chortkoff et al. 1995 (tier primary, adopted).

Perturbation runs:

- Sevoflurane `fraction_of_mac` 0.34 to 0.374 (+10%), over every
  data-dependent unit and integration test: 1654 passed, 0 failed. The only
  failure anywhere was `tests/unit/test_doc_check.py::test_this_repository_is_clean`,
  which checks the provenance table in `docs/MODEL.md` against the data file.
  The same change over `test_formatting`, `test_dashboard_frame`,
  `test_chart_frame`, `test_parameters` and the Qt chart and simulation-view
  integration tests: 714 passed.
- Desflurane `standard_deviation_fraction_of_mac` 0.063 to 0.0693 over the same
  set: 714 passed. The band centre does not depend on the SD, so the one
  desflurane check cannot see it.
- Desflurane `fraction_of_mac` 0.36 to 0.396: 2 failed. They were
  `test_the_mac_awake_band_uses_the_fraction_rather_than_a_published_percent`
  and the doc_check test.

`grep -rn Katoh tests/` finds nothing, and Chortkoff appears only in a
comment. The band tests in `tests/unit/test_formatting.py` build their
expected band from the loaded value. The 0.34 / 0.05 literals elsewhere in
that file are synthetic arguments, not reads of the shipped file, and the 0.34
fixtures in `tests/unit/test_parameters.py` are synthetic payloads.

So desflurane's fraction is pinned end to end, and the other five values are
not. Even desflurane's pin is fragile. That test asserts the band centre is
`approx(2.16)`, and then asserts
`abs(centre - 2.17) < CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` against Song et
al.'s published 2.17%. The resolution is 10**-2, and `abs(0.36 * 6.0 - 2.17)`
evaluates to 0.009999999999999787. The check passes only because of float
rounding: in exact arithmetic the distance equals the bound, and `<` fails.
Its tolerance is also a display resolution rather than Song et al.'s reported
spread.

**Why it matters.** A 10% transcription error in a MAC-awake fraction or SD
moves the awake band by 10%. Sevoflurane's 0.58-0.78% would become
0.65-0.85%. `docs/MODEL.md` tells the reader to read that band against the
vessel-rich (brain) trace to teach emergence, so a misleading emergence
threshold would ship with a green suite. doc_check catches a later accidental
edit. It cannot catch a value that was wrong when it was entered, because its
table row is written from that value.

**Where.** `src/anesthesia_sim/data/agents/sevoflurane.json`, `isoflurane.json`
and `desflurane.json` (`mac_awake`); `src/anesthesia_sim/app/formatting.py`
(`mac_awake_band_percent`); `tests/unit/test_formatting.py`;
`tests/unit/test_parameters.py`.

**Recommended test.** Write one source test per agent. It asserts
`mac_awake.fraction_of_mac` and `standard_deviation_fraction_of_mac` equal
values typed from the adopted primary source, not read from the JSON. Each
expected value carries its page or table locator in the test: Katoh 1993 for
sevoflurane (0.34 ± 0.05) and isoflurane (0.31 ± 0.05), slow washout, and
Chortkoff 1995 for desflurane. Add one end-to-end display test whose band
edges are (mean ± SD) x displayed MAC, written as literals. Rewrite the Song
comparison so it does not depend on float rounding: compare against Song et
al.'s reported spread, or use `<=` and say why. Record the route and depth of
each reading, as `.claude/rules/citing-sources.md` requires.

**Done when.** Each agent's stored fraction and SD is asserted against a
literal that names its source and locator, and a ±10% change to any of the
six values fails a test other than the doc_check test.

**Related.** `PL-FY35` (the same gap for MAC itself). `PL-Z3V5` (ready) defines
extraction notes with locators, which are the natural record of the typed
values.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
