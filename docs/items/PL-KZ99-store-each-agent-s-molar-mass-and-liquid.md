---
id: PL-KZ99
title: Store each agent's molar mass and liquid density with the density's measurement temperature, so a vapour-to-liquid conversion is derived from a primary measurement rather than from a published composite constant
priority: P1
effort: M
status: done
classes: science, anticipated
feature: liquid-agent-consumption
touches: src/anesthesia_sim/data, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/liquid_agent.py, src/anesthesia_sim/core/units.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/reference, tests/unit, docs/items/PL-1P15-show-what-the-delivered-agent-cost-in-money-at.md, docs/items/PL-0S0V-agent-volume-display-decimals-and-the-other.md
deferred-from: v0.6.0 - deferred to Gate 3 on beat 3's terms (PL-DB64, project owner, 2026-09-27, ratified, over keeping it on the list): work planned-milestone item 28 would create, waiting on PL-B396; science, but not live at 19af95d - nothing in src/ stores or displays a liquid volume, a density or a molar mass
added: 2026-09-16
closed: 2026-10-26
pr: 1866
payoff: a vapour-to-liquid conversion is derived from each agent's stored molar mass and liquid density, each with its source and measurement temperature
verify: grep -q 'def test_the_conversion_reproduces_gas_mans_published_delivered_costs' tests/reference/test_published_vapour_to_liquid.py && grep -q 'def test_the_derived_ratio_is_within_one_percent_of_biros_published_constant' tests/reference/test_published_vapour_to_liquid.py && grep -q 'def test_liquid_density_matches_its_adopted_primary_source' tests/unit/test_parameters.py
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
measurement temperature; `schema_version` 3 → 4 in the three files and in
`AGENT_SCHEMA_VERSIONS` in `core/parameters.py`; the conversion itself in `core/`, pure and unit-
explicit, never in a UI callback. It waited on `PL-S6WW` (done 2026-09-17): the
conversion cannot be written until the gas volumes' reference temperature is on
record, because that temperature is one of its two inputs.

**Re-pointed 2026-09-16.** This was filed to serve a liquid-millilitre figure
on the accounting panel; the project owner has since ruled that panel
developer-facing (`PL-B396`). The consumer is now `ROADMAP.md` § "Planned
milestones" item 28, agent cost, which needs the same two constants for the
same conversion. Nothing about the work changes — the same two fields, the
same primary source, the same `schema_version` bump. Only the thing that
consumes it does. (`PL-S6WW`, which held it then, closed on 2026-09-17.)

**Why it matters.** The alternative is storing the published composite constant -
one number per agent for the vapour volume from 1 mL of liquid - which puts a
temperature-dependent quantity in the data files with its temperature invisible.
That is the same defect as `PL-S6WW`, reproduced one layer down and harder to
see, and it would sit under a displayed millilitre figure a reader would take as
the bottle. Storing the two primary quantities instead keeps the conversion
auditable to a measurement that states its own conditions and its own dispersion,
which is what `docs/MODEL.md` § "Source hierarchy" asks of a stored value, and it
turns Biro 2014 from a source into an independent cross-check in
`tests/reference/`.

[superseded 2026-10-25: `PL-S6WW` closed on 2026-09-17]
[superseded 2026-09-17: `PL-S6WW` closed; groomed below]
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

[superseded 2026-10-25: v0.7.0 schedules item 28, and `PL-B396` now waits on this item]
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

**The question moved, 2026-09-27 (`PL-18BD`); this item's edge did not.**
`PL-B396` is now `blocked` on `PL-YRLM`, which holds whether a release
schedules item 28, so the passage above calling `PL-B396` `needs-decision`, and
saying no version exists until `PL-B396` produces one, is dated: the version
will come from `PL-YRLM`'s answer. `blocked-by: PL-S6WW, PL-B396` stands, and
`bin/docket wave` reaches `PL-YRLM` through it.

**Scheduled in v0.7.0, 2026-10-25.** `PL-LF0P` scoped v0.7.0 with planned-milestone item 28, agent cost, inside it (project owner, 2026-10-25, ratified, over leaving item 28 unscheduled and deferring this item to Gate 4). `PL-YRLM` closed with that answer. This item is in `ROADMAP.md` § "v0.7.0 - the schematic" → "Required scope", so v0.7.0 clears it itself.

**It no longer waits on `PL-B396`.** The edge ran this way only while
`PL-B396` stood in for item 28. Now `PL-B396` builds the readout, and the
readout needs these constants first, so the edge is reversed.

**Done when.** Each shipped agent's parameter file stores its molar mass and
its liquid density with the density's measurement temperature and source. The
vapour-to-liquid factor is derived from them in one place, and a reference test
checks it against Biro's and Gas Man's published constants within their
stated rounding.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still needed, and smaller than the brief says.** No agent file stores a molar mass or a liquid density, and nothing under `src/` converts vapour to liquid. Two things changed. The agent files are already at `schema_version` 3, and `AGENT_SCHEMA_VERSIONS` reads minimum 3, current 3, so the bump is 3 to 4, corrected above. `SupportedSchemaVersions` upcasts nothing, so there is no migration to write. And `docs/MODEL.md` § "Agent amount" already carries the densities, molar masses and derived factors (`PL-S6WW`). What is left is the stored fields with their sources, the conversion in `core/` and the reference test, after which that section's table restates the stored values beside their citation. The sevoflurane molar mass differs between this brief (200.053 g/mol) and that table (200.055). The difference is in the third decimal and depends on the atomic weights used, so take the figure from the source the data file cites.

## Outcome, 2026-10-26

**Built as the brief describes, with three departures, each recorded here.**
Each agent file now stores `molar_mass_g_mol` and a `liquid_density` group
holding the density, its standard deviation and the temperature it was
measured at. Agent files are at `schema_version` 4. `core/liquid_agent.py`
derives the vapour-to-liquid ratio in one place, as density / molar mass x
the molar volume at 20 °C and one standard atmosphere. It works out that
molar volume from CODATA 2022's exact constants instead of storing 24.055.
`AgentParameters.vapour_volume_per_liquid_volume` reads it. A density
measured at a temperature other than 20 °C is refused when the file loads,
because no correction for temperature is stored.

1. **The molar masses are ChEMBL's, tier 2, not "exact from formula".** A
   formula mass needs the standard atomic weights, and the IUPAC
   Commission's tables, PubChem, BIPM and NIST were all refused at the
   proxy on 2026-10-26. ChEMBL release 34 gives each formula and its mass to
   two decimals: 200.05, 184.49 and 168.04 g/mol. The brief's 200.053 and
   `docs/MODEL.md`'s 200.055 differ from that in the fourth significant
   figure, which moves the ratio by less than 0.003 %. The table in
   `docs/MODEL.md` § "Agent amount" now restates the stored values.
2. **The comparison with the published ratios uses a tolerance, not "their
   stated rounding".** Two of the six published ratios fall outside their own
   rounding. Biro gives sevoflurane 184, against 182.8 derived (0.65 %).
   Gas Man gives desflurane 209, against 209.7 derived (0.35 %). So the
   reference test holds the derived ratios within 1 % of Biro's and 0.5 % of
   Gas Man's, and its docstrings say what each tolerance can and cannot
   detect. A reference temperature of 37 °C, the error `PL-S6WW` guarded
   against, is 5.8 % and fails both.
3. **A worked cost example was added, at the project owner's request.** On
   2026-10-26 the owner asked for "a sanity check for calculated agent
   price". The conversion is the half of the price that this item builds. So
   `tests/reference/test_published_vapour_to_liquid.py` prices the
   isoflurane delivered in the Gas Man Workbook's Exercises 14-1 and 14-2
   (printed pp. 133-136). The results must match the four delivered costs
   the book prints ($2.17, $8.06, $0.68 and $2.00), allowing for the cent
   and for Gas Man's whole-millilitre ratio. `PL-1P15`, which builds the
   price on screen, now carries the owner's requirement and an end-to-end
   version of the same check.

**The commissioned `verify:` command was rewritten.** It was `grep -q
'liquid_density' src/anesthesia_sim/data/agents/sevoflurane.json`, which any
mention of the key satisfies, including a file that stores no density. The
new command names the reference tests and the test of each stored density
against Laster, Fang and Eger's abstract.
