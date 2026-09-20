---
id: PL-KZ99
title: Store each agent's molar mass and liquid density with the density's measurement temperature, so a vapour-to-liquid conversion is derived from a primary measurement rather than from a published composite constant
priority: P2
effort: M
status: blocked
classes: science, anticipated
feature: liquid-agent-consumption
touches: src/anesthesia_sim/data, src/anesthesia_sim/core/parameters.py, docs/MODEL.md, tests/reference
blocked-by: PL-S6WW, PL-B396
added: 2026-09-16
---

**Problem.** Store each agent's molar mass and liquid density with the density's measurement temperature, so a vapour-to-liquid conversion is derived from a primary measurement rather than from a published composite constant

**Why derive rather than store the published constant.** The consumption
literature publishes a single composite number per agent — the vapour volume
from 1 mL of liquid — and it is tempting to store that. Biro P, "Calculation
of volatile anaesthetics consumption from agent concentration and fresh gas
flow", *Acta Anaesthesiol Scand* 2014;58(8):968-72, doi:10.1111/aas.12374,
gives halothane 229 mL, isoflurane 195 mL, sevoflurane 184 mL, desflurane
210 mL. Storing those would put a temperature-dependent quantity in the data
files with its temperature invisible, which is the failure `PL-S6WW` is about.

**The primary measurement exists and carries its own temperature.** Laster MJ,
Fang Z, Eger EI II, "Specific gravities of desflurane, enflurane, halothane,
isoflurane, and sevoflurane", *Anesth Analg* 1994;78(6):1152-3, PMID 8198275,
doi:10.1213/00000539-199406000-00022, measured at 20 °C in four 50-mL
volumetric flasks: desflurane 1.4651 ± 0.0004 g/mL, isoflurane 1.5019 ±
0.0006, sevoflurane 1.5203 ± 0.0008 (mean ± SD), and reports a temperature
coefficient of −0.00250 ± 0.00014 g/mL per °C over 0-25 °C. That is tier 1
under `docs/MODEL.md` § "Source hierarchy", it states its reference
conditions, and it reports a dispersion — the form the agent files already
require. Molar masses are exact from formula: sevoflurane (C4H3F7O) 200.053,
isoflurane (C3H2ClF5O) 184.492, desflurane (C3H2F6O) 168.038 g/mol.

**The derivation reproduces the published composite, which makes Biro a test
rather than a source.** With the ideal-gas molar volume at 20 °C and 760 mmHg
(24.055 L/mol), density/molar-mass × molar volume gives sevoflurane 182.8,
isoflurane 195.8, desflurane 209.7 mL of vapour per mL of liquid, against
Biro's 184, 195 and 210 — within 1 % on all three. That belongs in
`tests/reference/` as an independent cross-check of the conversion, in the
same spirit as the existing published-reference tests.

**Shape of the work.** Two new fields per entry under
`src/anesthesia_sim/data/agents/`, each with its `sources` entry and its
measurement temperature; `schema_version` 2 → 3 and the migration that implies
in `core/parameters.py`; the conversion itself in `core/`, pure and unit-
explicit, never in a UI callback. Blocked by `PL-S6WW`: the conversion cannot
be written until the gas volumes' reference temperature is on record, because
that temperature is one of its two inputs.

**Re-pointed 2026-09-16.** This was filed to serve a liquid-millilitre figure
on the accounting panel; the project owner has since ruled that panel
developer-facing (`PL-B396`). The consumer is now `ROADMAP.md` § "Planned
milestones" item 28, agent cost, which needs the same two constants for the
same conversion. Nothing about the work changes — the same two fields, the
same primary source, the same `schema_version` bump, the same block on
`PL-S6WW`. Only the thing that consumes it does.

**Why it matters.** The alternative is storing the published composite constant
- one number per agent for the vapour volume from 1 mL of liquid - which puts a
temperature-dependent quantity in the data files with its temperature invisible.
That is the same defect as `PL-S6WW`, reproduced one layer down and harder to
see, and it would sit under a displayed millilitre figure a reader would take as
the bottle. Storing the two primary quantities instead keeps the conversion
auditable to a measurement that states its own conditions and its own dispersion,
which is what `docs/MODEL.md` § "Source hierarchy" asks of a stored value, and it
turns Biro 2014 from a source into an independent cross-check in
`tests/reference/`.

**Blocked on `PL-S6WW`** (the model's undocumented reference temperature), which
is now declared in `blocked-by` rather than only in prose: the conversion has two
inputs and that temperature is one of them, so it cannot be written first.
`docket check` was advising on exactly that gap.

**Classed `anticipated` at triage, 2026-09-17.** No vapour-to-liquid conversion
exists in this application, so the hazard these two constants would remove -
a liquid-equivalent figure derived from a composite constant whose temperature
is invisible - is one planned-milestone item 28 will create rather than one that
is live. With `status: blocked` that is the carve-out `ROADMAP.md` § "The gate is
a snapshot" records (project owner, 2026-09-16, ratified): an `anticipated`
`safety` or `science` finding is not debt until its hazard exists, and its
disposition is a placement in the milestone that creates it rather than a
deferral. Item 28 is named by no release, which is why the disposition is
recorded in the gate's declined subsection alongside `PL-0S0V` and `PL-VJZK`,
on the same ground and with the same expiry: the day item 28 is placed, this
belongs in that milestone's `Required scope`.

## Groomed 2026-09-20 under `PL-JFQ3`: `PL-S6WW` closed, and the second edge this item always had is now declared

**`PL-S6WW` has closed** (`done`, `2026-09-17`, `pr: 669`), so the reference
temperature this conversion needs as one of its two inputs is on record and
that half of the block is genuinely resolved. `bin/docket check` was correctly
reporting "every blocker has closed; it is ready to promote".

**Promoting it would have been wrong, and the roadmap already says why.**
`ROADMAP.md` § the gate's declined subsection names this item as "the same case
as `PL-0S0V` and `PL-VJZK` above, against the same planned-milestone item 28,
and takes the same disposition for the same reason: item 28 is named by no
release, so there is no `Required scope` to place it in. It expires the day item
28 is placed." Both of those siblings carry `blocked-by: PL-B396` — `PL-0S0V`
as `PL-S6WW, PL-B396`, `PL-VJZK` as `PL-B396` alone — and this item was the one
of the three that never had the second edge written in. That is the whole of
why it appeared in the advisory and neither of them did.

**So the real blocker is `PL-B396`** (agent amounts are displayed in litres of
vapour, which is not the unit a reader buys, fills or wastes agent in — report a
liquid-equivalent millilitre figure), `needs-decision`, which the roadmap calls
"whether item 28 is scoped at all, which is a milestone decision rather than
gate work". It is written into `blocked-by` beside `PL-S6WW`, whose closure is
kept as the record of what this waited on first.

**Why not a milestone blocker instead.** `blocked-by` takes an item id or a
`vX.Y.Z` the roadmap places, and `checks.py` `_check_references` errors on a
version the roadmap places nowhere — which is exactly the state item 28 is in.
There is no version to name until `PL-B396` produces one, which is the same
fact the edge now records.

**The `anticipated` carve-out is therefore intact and honest.** The hazard —
a liquid-equivalent figure derived from a composite constant whose temperature
is invisible — still does not exist, because no vapour-to-liquid conversion
exists. `anticipated` and `status: blocked` hold together, which is what
`check_gate_reentries` requires since `PL-ZF2G`.
