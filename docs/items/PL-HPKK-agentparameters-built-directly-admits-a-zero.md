---
id: PL-HPKK
title: AgentParameters built directly admits a zero max_delivered_concentration_percent and a mac_percent above it: the loader's PositivePercent and _mac_percent_must_not_exceed_vaporizer_max hold for a file and for nothing past it, the shape PL-0FJ8 closed for the MAC's sign alone
priority: P2
effort: S
status: done
classes: defect
feature: parse-dont-validate
milestone: v0.6.0
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-11
closed: 2026-10-19
pr: 1676
payoff: an agent record built outside the loader is held to the same vaporizer maximum and MAC relation a file is, so no second route admits a MAC the dial cannot reach
verify: grep -q 'def test_an_agent_record_is_held_to_its_vaporizer_maximum_however_it_is_built' tests/unit/test_parameters.py
---

**Problem.** AgentParameters built directly admits a zero max_delivered_concentration_percent and a mac_percent above it: the loader's PositivePercent and _mac_percent_must_not_exceed_vaporizer_max hold for a file and for nothing past it, the shape PL-0FJ8 closed for the MAC's sign alone

**Found 2026-10-11, closing `PL-0FJ8`,** which made `AgentParameters.__post_init__`
refuse a zero `mac_percent` through `require_positive_finite`. The same record
still takes `max_delivered_concentration_percent` as any `Percent`, zero
included, and holds no relation between the two fields: the loader's
`_AgentPayload` refuses a zero maximum through `PositivePercent` and a MAC above
the maximum through `_mac_percent_must_not_exceed_vaporizer_max`, and a record
built by `dataclasses.replace` meets neither. Measured that day on `main`:
`replace(load_sevoflurane_parameters(), max_delivered_concentration_percent=Percent(0.0))`
builds, and so does `replace(..., mac_percent=Percent(9.0))` against the 8.0
maximum.

**Why it matters, and why it is a finding rather than a defect.** Nothing but the loader builds an
`AgentParameters` on an application path, so no displayed value is wrong, and a
zero maximum stops the dial rather than printing a plausible number. It is the
shape `.claude/rules/core-domain.md` § "Where it stops" names: a frozen record
whose constructor refuses its own fields is the parsed type for them, and a
relation between fields belongs to the record holding them. `PL-0FJ8` closed the
one field whose failure reaches a screen; this is the rest of the record.

**Done when.** Building `AgentParameters` with a zero `max_delivered_concentration_percent`,
or with `mac_percent` above it, raises, shown by unit tests, and the loader's
checks are unchanged.

**Checked 2026-10-19, and fixed on `claude/core-guard-defects-u39w8s`.** Still
real on `main` at `6fd84bd5`: `dataclasses.replace` built both records.
`AgentParameters.__post_init__` now refuses a zero maximum through
`require_positive_finite` and a MAC above the maximum with a message naming
both. The loader's checks are unchanged, so a file is still refused by the
payload first. One test covers both refusals and the admitted edge, a MAC
equal to the maximum, so the `verify:` greps that one name.

**Run against the code before the fix, 2026-10-19:** `git checkout origin/main -- src/anesthesia_sim/core` and then `uv run pytest -q -p no:randomly tests/unit/test_tissue.py tests/unit/test_blood.py tests/unit/test_parameters.py -k "overflows or however_it_is_built"` failed all three selected tests with `Failed: DID NOT RAISE SimulationConfigurationError`.
