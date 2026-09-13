---
id: PL-4YY1
title: Record provenance for the circuit volume and default fresh gas flow
priority: P1
effort: S
status: done
classes: defect, science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/data, docs/MODEL.md, docs/ARCHITECTURE.md, tools/doc_check.py, tests/unit/test_circuit.py, tests/unit/test_parameters.py, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
closed: 2026-09-13
verify: grep -rq 'circuit_volume_l' src/anesthesia_sim/data/ && python3 tools/doc_check.py check
---

**Problem.** `core/circuit.py:46` hardcodes `circuit_volume_l: float = 6.0` and
`:47` `fresh_gas_flow_l_min: float = 4.0`. Neither is in a data file, neither
has a row in `docs/MODEL.md`'s provenance table, and 6.0 is restated a third
time as `CIRCUIT_VOLUME_L` at `tests/reference/test_coupled_dynamics.py:53`.

**The value is settled: keep 6.0.** The project owner has ruled that which
value is used is not critical. This item is provenance work only and must not
change any modelled number.

**Why it matters.** Circuit volume sets the fresh-gas wash-in time constant
(tau = V/FGF, 90 s at the defaults), so it sits between the vaporizer dial and
every displayed value. A learner watching the early lag attributes it to
uptake, when at these settings a large part of it belongs to the machine — that
is the anesthesia circuit's most-taught teaching point, and the constant
governing it currently has no recorded source at all. It is exactly the kind of
"clinically meaningful transformation" `CLAUDE.md` requires provenance for.

The tooling cannot see it, and that is the second half of the finding.
`tools/doc_check.py`'s `check_provenance` walks *data files* in both
directions, so a scientific constant that never entered one is structurally
invisible to the only tool built to catch this class of omission. And
`docs/ARCHITECTURE.md:26-27` claims "`core/` never contains hardcoded
scientific constants for the agent or patient it loads by default" — literally
true, and the machine-parameter carve-out is what these two escape through.

**Where.** `core/circuit.py:46-47`; `tests/reference/test_coupled_dynamics.py:53`;
`docs/MODEL.md`'s provenance table; `docs/ARCHITECTURE.md:26-27`;
`tools/doc_check.py` (`check_provenance`).

**Approach.** Move both constants into a versioned, cited data file beside
`data/patients/` — machine parameters are their own kind, not patient or agent
parameters — and add their provenance rows. Record there that the published Gas
Man convention is 8 L (De Wolf AM, Van Zundert TC, De Cooman S, Hendrickx JF.
*Theoretical effect of hyperventilation on speed of recovery and risk of
rehypnotization following recovery - a Gas Man simulation.* BMC Anesthesiol
2012;12:22) and that 6.0 L is retained
deliberately, so a later reader finds a decision rather than an accident.
Reconcile `docs/ARCHITECTURE.md:26-27` with whatever carve-out remains.

Consider extending `tools/doc_check.py` to flag float literals in `core/`
dataclass field defaults against an allowlist. That is the check that would
have caught this, and it stays on the decidable side of the line the tool is
built around: it can see that a literal exists and is unlisted, and makes no
attempt to judge whether the value is right.


**Appended 2026-09-01 — an open class question for the owner's triage; not
re-classed here.** This item is currently `classes: defect, docs` at `P2`. An
external review argues it reads as `science`, and the argument is worth
recording because the class is currently deciding something other than
labelling.

`circuit_volume_l = 6.0` is not an internal implementation constant. It
appears in `docs/MODEL.md`'s Symbols table as $`V_C`$ (`:148`) and inside the
breathing-circuit governing equation, and $`\tau_C = V_C / \dot V_F`$ sets the
machine lag that a learner will attribute to uptake — 90 s at this project's
defaults against 120 s at Gas Man's published 8 L. `docs/MODEL.md:662-664`
states that no scientific parameter may be added without a full source
citation. This one has none, which is the whole of the **Problem.** above.

If that makes it a scientific parameter, `science` is the class, and the
consequence is not cosmetic: `ROADMAP.md`'s debt-gate rules admit `P0`,
`safety` and `science` findings into the *current* gate regardless of the
presence presumption, while `defect` follows the ordinary rule. So the class
on this item is deciding its gate membership as a side effect of a labelling
choice nobody made deliberately. `docket check` would also pin a `science`
item to `P1` or `P0`, so the priority moves with it.

**This is flagged, not decided.** Re-classing it would move an item between
gates on a session's judgment, which is the project owner's call. Nothing here
is changed.

**Done when.** Circuit volume and default fresh gas flow are loaded from a
versioned, cited data file with provenance rows in `docs/MODEL.md`, the Gas Man
8 L convention and the deliberate retention of 6.0 are recorded,
`docs/ARCHITECTURE.md`'s claim matches what `core/` now holds, the third
restatement in the reference test reads from the same source, and no modelled
value has changed.

**Re-classed 2026-09-12** from `defect, docs` at P2 to `defect, science, docs`
at P1, on the project owner's decision. The class was the defect underneath the
defect: `subprojects/docket/src/docket/checks.py` pins `safety`- and
`science`-classed items to P1, so while this item read as `docs` the band that
exists for "a clinician could be misled" was never consulted about it. Both
constants are scientific parameters by `CLAUDE.md`'s own list - it requires
provenance for "constants, parameter sets" - and tau = V/FGF puts them between
the vaporizer dial and every displayed concentration. Found by the `PL-6ZQY`
consolidation sweep and recorded in `PL-NGLV`.


**Closed 2026-09-13.** Both constants now load from
`src/anesthesia_sim/data/machines/reference_circle_system.json` - a third kind
of parameter file beside the agent and the patient, because the breathing
system belongs to neither - through `BreathingCircuitParameters`,
`_BreathingCircuitPayload`, `parse_breathing_circuit_parameters()` and
`load_reference_circle_system_parameters()` in `core/parameters.py`, and
`AgentUptakeSystem.for_agent()` passes both explicitly the way it already
passed the alveolar pair. Neither modelled value changed, and the whole suite
(2571 tests, 100% coverage) is green.

**Provenance recorded, and it is a gap rather than a citation.** Both `sources`
entries are cited and *not adopted*, which is stronger than the reference
patient's gap and is the honest state. Circuit volume 6.0 L departs
deliberately from the Workbook's published 8.0 L (page 168, read at the source
2026-09-06) and from De Wolf et al. 2012's Methods, which print the same 8 L
(read at full text from PubMed Central 2026-09-13) - the owner's 2026-09-01
ruling that the value is not critical is recorded with what the departure
costs, which is a 90 s apparatus lag against 120 s, a 25 percent shorter
machine time constant on the part of the early rise a learner is likeliest to
attribute to uptake. Default fresh gas flow 4.0 L/min has *no* published
counterpart anywhere reached: the Workbook's circuit row carries a volume and
no flow, and the two Gas Man studies read here chose their own flows. It is
labelled a project convention with its design rationale, not a measurement.

**The third restatement was pinned rather than removed, and that is a departure
from the Done-when worth stating.** The Done-when asked that
`tests/reference/test_coupled_dynamics.py`'s `CIRCUIT_VOLUME_L` "read from the
same source". It must not: that module restates the operating point
deliberately, for the reason its own comment gives - the pinned reference
states below it are that operating point's solution, so binding the constant to
the data file would let a changed file silently re-point the gate at a
trajectory it never measured. The end state the Done-when wants - no unsourced
third copy, no silent drift - is reached instead by
`test_the_historical_operating_point_is_still_the_shipped_machine_s`, written
in the idiom that file already uses for the supported ranges
(`test_envelope_limits_match_the_supported_input_ranges`), which fails loudly
and says the pinned states must be recomputed. `PL-4YY1`'s
`load_reference_circle_system_parameters` was added to that module's
`ALLOWED_PACKAGE_IMPORTS`; it is a parameter loader, which the independence
rule permits, and it solves nothing.

`core/circuit.py` keeps its field defaults, for the same reason: making them
required would push package-data loading into every bare unit test of circuit
physics. They are now a *checked* restatement -
`test_the_bare_circuit_defaults_match_the_shipped_machine_file` - and the
docstring says where the authority is.

**`docs/ARCHITECTURE.md`'s claim is reconciled** rather than deleted: the
layering bullet now says every scientific constant a shipped run uses comes
from a data file because `for_agent()` passes each explicitly, that the
defaults remain in `core/` for bare construction, and that each is pinned by a
test. The package map, the data-flow diagram, the `parameters.py` line, the
"Data files" section and "Where new code belongs" all name the third kind.

**The `doc_check.py` extension was considered and deferred, with the count**
(`PL-65HT`). `core/` holds 15 numeric dataclass field defaults; 11 are 0 or 1,
and the four that are scientific are the two closed here and the two
`PL-DJYF` names. Identifier-matching against the provenance table needs a
hand-maintained mapping (`default_fresh_gas_flow_l_min` against
`fresh_gas_flow_l_min`); value-matching against all of `data/` would pass the
circuit volume by matching the vessel-rich tissue volume, which is the
authoritative-and-wrong failure. The decidable rule that remains, and the
interpreter-floor problem with its home, are in that item.

**Also found and filed:** `PL-DJYF` (`AlveolarCompartment` restates the
reference patient's 2.5 and 4.0 the same way, unpinned).
