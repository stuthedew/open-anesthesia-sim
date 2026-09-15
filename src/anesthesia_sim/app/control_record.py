"""What a run's settings are addressed by, and the change a run records.

The record half of a run's controls: which settings exist (`ControlInput`),
the unit each is recorded in (`CONTROL_INPUT_UNITS`), and one change the
running model actually saw (`ControlChange`). Nothing here reads simulation
state, holds a setting, or formats a value.

`app/control_timeline.py` is the display half - it turns a recorded timeline
into the acts a reader sees, and names each control in the interface's own
words - and it reads these definitions from here rather than the other way
round, so what a run records does not depend on the words chosen to show it.

**Why it is a module of its own rather than part of either.**
`app/controller.py` writes the record and `app/control_timeline.py` reads it,
so the definitions cannot sit in either without pointing an import backwards:
in the controller they made every reader of a recorded change import the
UI-to-core boundary, which is what `PL-RD3B` separated, and in the timeline
they would make the controller import a module whose job is formatting
strings for display. A leaf both import is the only placement that leaves the
direction one-way.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

__all__ = ["CONTROL_INPUT_UNITS", "ControlChange", "ControlInput"]


class ControlInput(StrEnum):
    """A setting the user can change during a run, under a stable identifier.

    The *value* of each member is what a recorded run stores, so it is
    chosen from the domain rather than from whatever the accessor happens
    to be called this release. That separation has now been paid for:
    `PL-3TLK` and `PL-9SH6` renamed both of the forwarding setters these
    members stand for - `set_delivered_concentration` became
    `set_delivered_partial_pressure_fraction`, and the circuit fraction
    became `inspired_partial_pressure_fraction` - and a timeline that had
    stored accessor names would now carry two retired ones in the history
    of every run recorded before the rename. The member names followed the
    code; the strings did not move.

    `DELIVERED` is the vaporizer dial: the concentration delivered into the
    circuit, which is not the same quantity as the inspired concentration
    the circuit reaches. Naming it for the dial would have tied it to one
    machine's control rather than to the quantity the model applies.

    These are the four live controls and there is no fifth. A
    `CIRCUIT_VOLUME` member was recorded here until `PL-GYH2` established
    the circuit volume as a fixed model parameter rather than a control:
    it was written only by `SimulationController.set_circuit_volume`, an
    app-layer setter no interface control ever reached, and retiring the
    setter left an identifier for a change a run can no longer undergo.
    Removing the member costs no recorded history, because a timeline is
    held in memory and cleared with the run that recorded it; it is never
    persisted, so no stored run carries the string.
    """

    FRESH_GAS_FLOW = "fresh_gas_flow"
    DELIVERED = "delivered"
    ALVEOLAR_VENTILATION = "alveolar_ventilation"
    CARDIAC_OUTPUT = "cardiac_output"


# The unit each control's recorded values are in, declared once and carried
# onto every entry that records one. Two properties are wanted at the same
# time and neither alone is enough: a single table is auditable at a glance
# and cannot drift between the recorder and the reader (the reason
# `chart_frame.COMPARTMENT_TRACES` is one table rather than six call sites),
# while a unit carried *on* the entry makes each recorded change
# self-describing, so a displayed line reads its unit from the change that
# produced it rather than from a lookup a later edit could desynchronise.
# `CLAUDE.md`'s safety-critical standard asks for explicit units and for a
# displayed value traceable to them; this is both halves.
#
# The values are the model's own units, not the interface's. The delivered
# concentration is stored as the fraction the core is set with, so
# re-applying a recorded timeline is a sequence of setter calls with the
# numbers already in them - the reconstruction property this item exists
# for - and the percent a reader sees is that fraction converted once, at
# the display, by the same formatter every other concentration goes
# through.
CONTROL_INPUT_UNITS: Final[Mapping[ControlInput, str]] = {
    ControlInput.FRESH_GAS_FLOW: "L/min",
    ControlInput.DELIVERED: "fraction of 1 atm",
    ControlInput.ALVEOLAR_VENTILATION: "L/min",
    ControlInput.CARDIAC_OUTPUT: "L/min",
}


@dataclass(frozen=True, slots=True)
class ControlChange:
    """One setting change the running model actually saw.

    Recorded per change rather than per user gesture, because the model
    integrates whatever value is in place at each step: a dial swept from
    2% to 4% across eight steps is eight different settings the run was
    computed under, and a record that kept only the endpoint would not
    reproduce the run it claims to describe.

    `adjustment` is what makes that faithful record readable. It groups the
    changes a user made as one act - one drag of one slider - so a reader
    sees one adjustment where the model saw eight settings. It is assigned
    from the input boundary the interface reports rather than guessed from
    the timing of the entries, so two separate turns of the same dial are
    two adjustments however close together they fall.
    """

    elapsed_s: float
    """Simulated time the change took effect, in seconds."""
    adjustment: int
    """Which user adjustment this change belongs to. See the class docstring."""
    control: ControlInput
    previous_value: float
    new_value: float
    unit: str
    """The unit both values are in, from `CONTROL_INPUT_UNITS`."""
