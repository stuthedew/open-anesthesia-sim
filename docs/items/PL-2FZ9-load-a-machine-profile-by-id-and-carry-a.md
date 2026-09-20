---
id: PL-2FZ9
title: Load a machine profile by id and carry a machine id through AgentUptakeSystem.for_agent, so a second profile in data/machines is reachable at all
priority: P2
effort: S
status: ready
classes: feature
feature: machine-profile-framework
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, tests/unit/test_parameters.py
added: 2026-09-20
payoff: a second machine profile dropped into data/machines is actually used by a run, instead of being ignored by the program and failing make check
verify: grep -q 'def test_rejects_unknown_machine_id' tests/unit/test_parameters.py
---

**Problem.** Load a machine profile by id and carry a machine id through AgentUptakeSystem.for_agent, so a second profile in data/machines is reachable at all

**Why it matters.** This is the keystone of the `machine-profile-framework`
group: planned-milestone item 40 (`ROADMAP.md:6947`) states the deliverable as
"a second profile dropped into `src/anesthesia_sim/data/machines/` should be
loadable, selectable in code, and refused where it is not admissible". Today
none of the three holds, and the failure is silent in the one direction that
matters and noisy in the one that does not.

**Measured, not inferred (2026-09-20, reproduced in this session).** A
throwaway `throwaway_probe_machine.json` was dropped into
`src/anesthesia_sim/data/machines/` - schema-valid, `schema_version: 2`,
`circuit_volume_l: 2.1`, `default_fresh_gas_flow_l_min: 1.0`, one source
entry, a `provenance_gap` - and then deleted. Three observations:

1. **The runtime ignored it completely.** `AgentUptakeSystem.for_agent(
   "sevoflurane")` still built a circuit at 6.0 L, and
   `load_reference_circle_system_parameters()` still returned the profile with
   `id='reference_circle_system'`, `circuit_volume_l=6.0`,
   `default_fresh_gas_flow_l_min=4.0`. There is no code path by which the
   second file could have been read.
2. **The unit suite did not notice.** `uv run pytest tests/unit -q` reported
   `1 failed, 1613 passed`, and the single failure was
   `tests/unit/test_doc_check.py::test_this_repository_is_clean` - which is
   `doc_check` expressed as a test, not the simulation noticing anything.
3. **`make check` failed, on provenance alone.** `uv run python -m
   tools.doc_check check` exited 1 with, verbatim:

   > `docs/MODEL.md: no provenance row for data/machines/throwaway_probe_machine.json circuit_volume_l = 2.1; every constant a clinician could read belongs in the table`

   and the matching line for `default_fresh_gas_flow_l_min = 1`. Two errors
   rather than the audit's four, because this probe declared
   `deliverable_fresh_gas_flow_range: null`; a profile declaring a range
   carries two more leaf numbers and so owes two more rows.
   `tools/doc_check.py:925-933` walks `_leaf_numbers` over every
   `data/**/*.json`, which is why the count tracks numbers rather than files.

So a second profile is invisible to the program and fatal to `make check` -
the exact inversion of what the framework is for.

**Where.** `src/anesthesia_sim/core/parameters.py:869`,
`load_reference_circle_system_parameters()`, hardcodes the one filename and
takes no argument. `src/anesthesia_sim/core/uptake_system.py:249` calls it
directly from `for_agent()`, whose signature
(`uptake_system.py:221`) is `for_agent(cls, agent_id: str)` - no machine
anywhere in it. The profile's own `id` and `display_name` are parsed into
`BreathingCircuitParameters` and read by nothing in `src/`.

**The pattern to mirror, verified.** Agents already do all of this, twenty
lines above the machine loader in the same file: `AGENT_DATA_FILENAMES` at
`core/parameters.py:828` maps id to filename; `load_agent_parameters(agent_id)`
at `:835` looks the filename up and refuses an unknown id at `:841-843` with
`unknown agent_id: ...; expected one of ...`; and `:848-851` cross-checks the
loaded `parameters.id` against the id it was asked for, raising
`{filename} declares id {...!r}, expected {...!r}`. That cross-check is the
half worth copying deliberately: the machine profile's `id` is parsed and never
compared to anything, so a profile whose `id` disagrees with its filename loads
silently today. With one shipped profile that cannot yet mislead anyone, which
is why this is framework work and not a defect - but it is a safety-critical
data path, and the identity of the machine a displayed circuit time constant
came from is exactly what `PL-WZVZ` (make an inter-machine difference
attributable to a named parameter) will need to be true.

**Why now rather than later.** The signature change is cheap while `for_agent`
has few callers and none passes a machine. Deferred, it reaches
`src/anesthesia_sim/app/controller.py:292` (`AgentUptakeSystem.for_agent(
agent_id)`), the `SimulationController(...)` construction at
`src/anesthesia_sim/app/main.py:32`, the branch-rebuild at
`controller.py:694`, and every consumer written between now and then. A default
argument - `for_agent(agent_id, machine_id="reference_circle_system")` - means
no call site changes on the day it lands.

**Done when.**

- `core/parameters.py` holds a `MACHINE_DATA_FILENAMES` mapping and
  `load_machine_parameters(machine_id)` beside `AGENT_DATA_FILENAMES` and
  `load_agent_parameters`, refusing an unknown id in the same words and with a
  `SimulationConfigurationError`.
- That loader cross-checks the loaded profile's `id` against the id it was
  asked for, mirroring `core/parameters.py:848-851`.
- `AgentUptakeSystem.for_agent` takes `machine_id` with
  `"reference_circle_system"` as its default, so no existing call site is
  edited, and passes it through instead of calling the fixed-filename loader.
- `load_reference_circle_system_parameters()` either delegates to the new
  loader or is retired in favour of it - one code path reads
  `data/machines/`, not two.
- `tests/unit/test_parameters.py` holds `test_rejects_unknown_machine_id` and a
  mismatched-id test mirroring `test_rejects_agent_file_with_mismatched_id`
  (`tests/unit/test_parameters.py:196`).

**Explicitly not in scope.** No second shipped profile - item 40 ships one, and
which machines exist is item 1's with no timeframe. No machine chooser or any
display surface (`PL-WZVZ`, held behind item 34's View contract). No extraction
of the delivery and removal rates from `core/governing_equations.py:355-360`
and `core/circuit.py:433-448`: that refactor costs the same with one profile or
ten, which is exactly why it waits. No displayed number changes.

**What would falsify this.** If a run turns out to name its machine through a
run-definition object rather than through `for_agent` - the shape
`docs/machine-abstraction.md` uses for a run's opening conditions - then the
keyword argument is the wrong seam and the registry should hang off that object
instead. The registry and the id cross-check survive either way; only the
`for_agent` signature is at risk. It would also be falsified if machines were
selected by filename rather than by id, but that contradicts the profile
already carrying an `id` field and the agent precedent beside it.
