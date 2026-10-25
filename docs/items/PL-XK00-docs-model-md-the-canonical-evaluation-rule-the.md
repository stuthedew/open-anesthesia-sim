---
id: PL-XK00
title: docs/MODEL.md § "The canonical evaluation rule": the paragraph on the two evaluation paths calls 1.8e-14 and 3.7e-15 eleven orders of magnitude below 1e-4, the readout's resolution; they are about ten (log10 of the ratio is 9.7 and 10.4). Same error PL-KJ9H fixed in tests/unit/test_run_definition.py (found in the PL-KJ9H docs sweep, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: docs/MODEL.md
added: 2026-10-25
closed: 2026-10-25
pr: 1841
payoff: a reader of the model specification weighing the two evaluation paths against the displayed precision is given the true margin
verify: ! grep -qF 'Both are eleven orders of magnitude' docs/MODEL.md && grep -qF 'Both are about ten orders of magnitude below 1e-4' docs/MODEL.md
---

**Problem.** docs/MODEL.md § "The canonical evaluation rule": the paragraph on the two evaluation paths calls 1.8e-14 and 3.7e-15 eleven orders of magnitude below 1e-4, the readout's resolution; they are about ten (log10 of the ratio is 9.7 and 10.4). Same error PL-KJ9H fixed in tests/unit/test_run_definition.py (found in the PL-KJ9H docs sweep, 2026-10-25)

**Reproduced 2026-10-25.** On `main` at `662ed2f3`, `docs/MODEL.md` line 5893 reads "Both are eleven orders of magnitude below 1e-4". The paragraph sits under § "The run is that record, and every state is derived from it", just before § "The canonical evaluation rule" that it points to; the title names the later section. log10(1e-4 / 1.8e-14) is 9.74 and log10(1e-4 / 3.7e-15) is 10.43, so both are about ten orders below.

The sweep of the file's other order-of-magnitude claims found them right: 7.70e-16 against 1e-4 is 11.1 and 8.17e-14 L against 1e-6 is 7.1 (line 6362), 2.29e-4 against 5.89e-14 is 9.6 (line 4057), and 5.89e-14 against 1e-4 is 9.2 (line 9876).

**Why it matters.** The sentence is the model specification's statement of how far the two evaluation paths sit from a displayed digit. A reader weighing that margin, or checking it against the test that pins it, is given a figure ten times too generous.

**Done when.** The sentence gives the margin as about ten orders of magnitude, matching `tests/unit/test_run_definition.py` after PL-KJ9H, and no other statement in the paragraph changes.
