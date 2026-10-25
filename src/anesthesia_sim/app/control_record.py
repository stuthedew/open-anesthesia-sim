"""This module defines the names and units of a run's settings, and one recorded change.

It is the record half of a run's controls. It defines which settings exist
(`ControlInput`) and the unit each one is in (`CONTROL_INPUT_DISPLAY_UNITS`, with
its recorded spelling in `CONTROL_INPUT_UNITS`). It also defines `ControlChange`,
one change that the running model actually saw. Nothing here reads simulation
state, holds a setting, or formats a value.

`app/control_timeline.py` is the display half. It turns a recorded timeline into
the acts a reader sees, and it names each control in the interface's own words.
That module imports these definitions from this one, and never the other way
round. So what a run records does not depend on the words chosen to show it.

**Why it is a module of its own rather than part of either.**
`app/controller.py` writes the record and `app/control_timeline.py` reads it. If
the definitions sat in either module, one import would point the wrong way. When
they were in the controller, every reader of a recorded change had to import the
UI-to-core boundary, which `PL-RD3B` separated. In the timeline, they would make
the controller import a module whose job is to format strings for display. A
leaf module that both of them import is the only place that keeps every import
pointing one way.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant

__all__ = ["CONTROL_INPUT_DISPLAY_UNITS", "CONTROL_INPUT_UNITS", "ControlChange", "ControlInput"]


class ControlInput(StrEnum):
    """A setting the user can change during a run, under a stable identifier.

    The *value* of each member is what a recorded run stores, so it is
    chosen from the domain rather than from whatever the accessor happens
    to be called this release. That separation has now been paid for:
    `PL-3TLK` and `PL-9SH6` renamed both of the forwarding setters these
    members stand for - `set_delivered_concentration` became
    `set_delivered_partial_pressure_fraction`, and the circuit fraction
    became `inspired_partial_pressure_fraction` - and `PL-NJPB` renamed the
    first again, to `set_delivered_concentration_percent`, so a timeline
    that had stored accessor names would now carry three retired ones in the
    history of every run recorded before the renames. The member names
    followed the code; the strings did not move.

    `DELIVERED` is the vaporizer dial: the concentration delivered into the
    circuit, which is not the same quantity as the inspired concentration
    the circuit reaches. Naming it for the dial would have tied it to one
    machine's control rather than to the quantity the model applies. Its
    recorded value is the percent the dial was set to, which is what the
    circuit holds (`PL-NJPB`), so every control's value is in the unit it
    was set in.

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


# The unit of each control's recorded values. It is declared once, here, and carried
# onto every entry that records a value. Two properties are wanted at the same time,
# and neither is enough alone. A single table can be audited at a glance, and it
# cannot drift between the recorder and the reader. That is why
# `chart_frame.COMPARTMENT_TRACES` is one table rather than six call sites. A unit
# carried *on* each entry makes each recorded change describe itself. A displayed
# line then reads its unit from the change that produced it, not from a lookup that
# a later edit could put out of step. `CLAUDE.md`'s safety-critical standard asks for
# explicit units and for each displayed value to be traceable to its unit. The table
# and the unit on each entry together meet both requirements.
#
# The values are the model's own units, not the interface's. The delivered
# concentration is stored as the percent the core is set with, which is the percent
# that was dialled (`PL-NJPB`). So re-applying a recorded timeline is a sequence of
# setter calls with the numbers already in them. That reconstruction property is what
# the record exists for. The percent a reader sees is rendered by the same formatter
# that every other concentration goes through.
#
# Each control's unit is one `DisplayUnit` member, and the panel's slider label reads
# that member too (`dashboard_frame.ParameterControl.unit`). So the label beside a
# slider and the unit on its recorded changes are two spellings of one member. They
# cannot name different units (`PL-Q3G9`).
CONTROL_INPUT_DISPLAY_UNITS: Final[Mapping[ControlInput, DisplayUnit]] = {
    ControlInput.FRESH_GAS_FLOW: DisplayUnit.FLOW,
    ControlInput.DELIVERED: DisplayUnit.CONCENTRATION,
    ControlInput.ALVEOLAR_VENTILATION: DisplayUnit.FLOW,
    ControlInput.CARDIAC_OUTPUT: DisplayUnit.FLOW,
}
CONTROL_INPUT_UNITS: Final[Mapping[ControlInput, str]] = {
    control: unit.recorded for control, unit in CONTROL_INPUT_DISPLAY_UNITS.items()
}


@dataclass(frozen=True, slots=True)
class ControlChange:
    """One setting change the running model actually saw.

    A change is recorded per change rather than per user gesture, because the
    model integrates whatever value is in place at each step. A dial swept
    from 2% to 4% across eight steps gives eight different settings that the
    run was computed under. A record that kept only the endpoint would not
    reproduce the run it claims to describe.

    `adjustment` makes that faithful record readable. It groups the changes
    that a user made as one act, such as one drag of one slider, so a reader
    sees one adjustment where the model saw eight settings. It is assigned
    from the input boundary that the interface reports, not guessed from the
    timing of the entries. So two separate turns of the same dial are two
    adjustments, however close together they fall.

    Raises:
        TypeError: If `elapsed_s` was not built as a `CaseInstant`, because
            then nothing has checked it against the supported run length
            (`core/supported_ranges.py`, `PL-RCYZ`).
    """

    elapsed_s: CaseInstant
    """Simulated time the change took effect, in seconds. The instant the
    running state was at, so a `CaseInstant` like every other holder of one."""
    adjustment: int
    """Which user adjustment this change belongs to. See the class docstring."""
    control: ControlInput
    previous_value: float
    new_value: float
    unit: str
    """The unit both values are in, from `CONTROL_INPUT_UNITS`."""

    def __post_init__(self) -> None:
        require_case_instant("elapsed_s", self.elapsed_s)
