---
id: PL-HPKK
title: AgentParameters built directly admits a zero max_delivered_concentration_percent and a mac_percent above it: the loader's PositivePercent and _mac_percent_must_not_exceed_vaporizer_max hold for a file and for nothing past it, the shape PL-0FJ8 closed for the MAC's sign alone
status: untriaged
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
added: 2026-10-11
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

**Why a finding rather than a defect.** Nothing but the loader builds an
`AgentParameters` on an application path, so no displayed value is wrong, and a
zero maximum stops the dial rather than printing a plausible number. It is the
shape `.claude/rules/core-domain.md` § "Where it stops" names: a frozen record
whose constructor refuses its own fields is the parsed type for them, and a
relation between fields belongs to the record holding them. `PL-0FJ8` closed the
one field whose failure reaches a screen; this is the rest of the record.

**Done when.** Building `AgentParameters` with a zero `max_delivered_concentration_percent`,
or with `mac_percent` above it, raises, shown by unit tests, and the loader's
checks are unchanged.
