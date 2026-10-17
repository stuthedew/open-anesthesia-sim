---
id: PL-FY35
title: The MAC and maximum-delivered literal pins in tests/unit/test_parameters.py carry no source locator, and nothing cross-checks a stored MAC against a second source such as Mapleson 1996's age-40 values, which the agent files' own notes already record
priority: P2
effort: M
status: done
classes: test
feature: tests-detect-wrong-values
touches: tests/unit/test_parameters.py
added: 2026-10-17
closed: 2026-10-17
pr: 1506
payoff: each stored MAC and vaporizer maximum is pinned by a test that names its source, and a MAC that drifts from Mapleson 1996 by more than its recorded deviation fails
verify: grep -q 'def test_mac_matches_its_cited_source_and_its_recorded_mapleson_deviation' tests/unit/test_parameters.py
---

**Problem.** The MAC and maximum-delivered literal pins in tests/unit/test_parameters.py carry no source locator, and nothing cross-checks a stored MAC against a second source such as Mapleson 1996's age-40 values, which the agent files' own notes already record

**Severity: medium.** The audit first rated this safety. The verifier rated it
"partly" true and lowered it, because today's values match their cited
source. What remains is traceability and a plausibility cross-check. Audit
finding DP-2; the corrected claim is what this item states.

**Evidence.** `test_loads_built_in_sevoflurane_parameters`,
`test_loads_built_in_isoflurane_parameters` and
`test_loads_built_in_desflurane_parameters` in
`tests/unit/test_parameters.py` assert MAC 2.0, 1.2 and 6.0% and vaporizer
maxima 8, 5 and 18%, with no source locator. Those literals equal the adopted
authority's own sentence. That is De Wolf et al. 2012, quoted in the agent
files' notes as "desflurane 6%, sevoflurane 2%, isoflurane 1.2%", and the
vaporizer-specification entries. So a wrong value does not pass today.
Raising sevoflurane's MAC from 2.0 to 2.2 failed 23 of 1654 data-dependent
tests. Some of those are end-to-end clinical facts, such as "6% is 3 MAC of
sevoflurane and 1 MAC of desflurane" in `tests/unit/test_dashboard_frame.py`
and the divisor strings in `tests/integration/test_simulation_view.py`.
Raising the sevoflurane maximum from 8.0 to 8.8 failed 4 tests that restate
it.

Two things are missing. First, a locator: nothing tells a reader whether a pin
was typed from the paper or from the JSON. Second, any check against a second
source. `grep -rn Mapleson tests/` finds only an unrelated venous-pool
comment. The agent files' notes already record Mapleson 1996's age-40 MAC as
sevoflurane 1.8, isoflurane 1.17 and desflurane 6.6, with 95% limits of ±7%,
±7% and ±10%. The stored sevoflurane 2.0 is 11.1% above 1.8.

The authority itself is disputed. Meybohm et al. 2021 (tier 3) prints
sevoflurane 2.1 and isoflurane 1.1 for the same Gas Man parameter set, as
`sevoflurane.json` records under `PL-0SG0`. A test that transcribes De Wolf
must say which source it transcribes; it cannot settle which figure is right.
A Mapleson band alone is not enough either, because it depends on direction:
desflurane x1.1 is 6.6%, exactly Mapleson's value.

**Why it matters.** The stored MAC divides every displayed xMAC readout. It
also sets the MAC axis, the 1 MAC line, the MAC-awake band and the dial a run
opens at. A pin with no locator cannot show that it was checked against
anything but the file it pins.

**Where.** `src/anesthesia_sim/data/agents/*.json` (`mac_percent`,
`max_delivered_concentration_percent`); `tests/unit/test_parameters.py`.

**Recommended test.** For each agent, assert `mac_percent` equals De Wolf
2012's sentence, typed in the test with its locator, and record Meybohm 2021's
disagreement beside it. Separately, assert each stored MAC's recorded
deviation from Mapleson 1996's age-40 value (sevoflurane +11.1%, the others
from the notes) to within 0.5 percentage points, with Mapleson's figures typed
from the paper. Do the same for `max_delivered_concentration_percent` against
the vaporizer-specification entries. The 23 tests that restate the MAC then
depend on one checked number instead of each being its own copy.

**Done when.** Each stored MAC and vaporizer maximum is pinned by a test that
names its source and locator, and each MAC's deviation from Mapleson 1996 is
asserted.

**Related.** `PL-H1JH` (the same gap for the MAC-awake values). `PL-HPKK`
(ready) is about `AgentParameters` built directly, not about where the values
come from.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Fail-before, 2026-10-17.**
`test_mac_matches_its_cited_source_and_its_recorded_mapleson_deviation` in
`tests/unit/test_parameters.py` types De Wolf et al. 2012's MACs (Methods,
first paragraph, read as full text from PubMed Central), Mapleson 1996's
age-40 MACs (Abstract, read through PubMed) and the deviations the agent
files record. `test_vaporizer_maximum_matches_its_cited_specification` types
the three dial maxima beside their sources. Both pass on the shipped files.

Each MAC and each maximum was then changed by +10% and by -10%, one at a
time, as `PL-H1JH`'s record describes. All 12 runs exited 1. Sevoflurane's
MAC at 2.2 failed with `assert 2.2 == 2.0`, and also failed `PL-H1JH`'s
literal band test, since the band is a fraction of the MAC. Sevoflurane's
maximum at 8.8 failed with `assert 8.8 == 8.0`. The deviation assertion
catches a change that retypes the first literal too. With sevoflurane's MAC
and its literal both set to Meybohm et al.'s 2.1, it failed with
`assert 16.666666666666675 == 11.1 ± 0.5`.

Two maxima could not be read at their source. The gateway refused the
Dräger page and www.draeger.com at CONNECT on 2026-10-17, and Kelly and
Kong 2011's abstract does not state the scale, its full text being outside
PubMed Central. Their pins name the source and say what was read instead.
`PL-L46W` holds the reading.
