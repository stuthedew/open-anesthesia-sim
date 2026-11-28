"""The names of the values a run draws, and the window from which one frame reads them.

This module says what a chart trace *is*: one substance's values for one
quantity. It does not say how any toolkit draws the trace.
`app/chart_frame.py` decides what a frame claims, and `app/qt_chart.py`
paints it. `app/dashboard_frame.py` names its readouts in the same terms.
Nothing here reads simulation state, holds a widget, or formats a value.

**Why it is a module of its own.** `app/controller.py` is the boundary
between the UI and the scientific core, and nothing here belongs to that
boundary. A `RecordedSeries` names a trace whether or not a run exists. A
`DrawnWindow` is the result of one `SimulationController.drawn_window` call,
not part of the controller's own state. The imports showed this split before
it was a module: the frames used these names and nothing else from the
controller. `PL-RD3B` made the split a module. The controller imports
`DrawnWindow` from here to declare what it returns. Nothing here imports the
controller, and that keeps the dependency pointing one way.

**The identifiers are stable, and deliberately differ from the accessors' names.**
`RecordedQuantity` and `control_record.ControlInput` are the two sets of
names by which a run's values are addressed. Both are named for the domain,
not for whichever field currently spells them, so that a rename in `core/`
cannot silently point a trace at a different value. Each enum's own
docstring records the renames that this naming has already protected against.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.wash_in import is_ventilated, wash_in_quotient
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.supported_ranges import AlveolarVentilation

__all__ = [
    "COMPARTMENT_FRACTION_NAMES",
    "COMPARTMENT_GLOSSES",
    "COMPARTMENT_NAMES",
    "COMPARTMENT_QUANTITIES",
    "COMPARTMENT_STATE_INDEX",
    "DrawnWindow",
    "RecordedQuantity",
    "RecordedSeries",
]


class RecordedQuantity(StrEnum):
    """One quantity the interface draws, under a stable identifier.

    A chart trace is bound to a member, and a drawn window is read with a
    member as the key. Members are named for the compartment or the quantity,
    not for whichever field or accessor currently spells it. The reason is the
    same as for the members of `control_record.ControlInput`. `PL-3TLK` and
    `PL-9SH6` renamed two of the fields these members read from. A key that
    had followed the code would have had to be renamed with them, although its
    meaning never changed. `CIRCUIT` is the example: the field behind it is
    now `inspired_partial_pressure_fraction`, and this key did not change.

    `WASH_IN_RATIO` is the one derived member. It is not a compartment state
    but the quotient that `app/wash_in.py` specifies. It is named here so that
    the plot drawing it is addressed in the same way as every other trace. It
    is deliberately absent from `COMPARTMENT_STATE_INDEX`, and that absence
    keeps it from being treated as a state the equations carry.
    """

    CIRCUIT = "circuit"
    ALVEOLAR = "alveolar"
    MIXED_VENOUS = "mixed_venous"
    VESSEL_RICH = "vessel_rich"
    MUSCLE = "muscle"
    FAT = "fat"
    WASH_IN_RATIO = "wash_in_ratio"


#: The compartment quantities the interface draws for each substance, in the
#: order it lists them.
#:
#: It contains every `RecordedQuantity` except `WASH_IN_RATIO`. That member is not
#: a compartment state but the quotient that `app/wash_in.py` forms from two of
#: these. Including it here would present a derived value as one the equations
#: carry. The tuple is written out rather than filtered from the enum, so that
#: adding a member forces a decision here instead of the member silently joining
#: the compartments.
COMPARTMENT_QUANTITIES: Final = (
    RecordedQuantity.CIRCUIT,
    RecordedQuantity.ALVEOLAR,
    RecordedQuantity.MIXED_VENOUS,
    RecordedQuantity.VESSEL_RICH,
    RecordedQuantity.MUSCLE,
    RecordedQuantity.FAT,
)

#: The name the interface shows for each compartment: in its readout, in the
#: chart's legend and hover readout, over its schematic container, in the mark
#: editor's list of compartments, and in a refused mark's notice.
#: `chart_frame.TraceStyle` and `dashboard_frame.ReadoutPanel` read each name
#: from here and hold no copy, so every place names a compartment the same way
#: (`PL-5867`, `PL-GRC6`). NUREG-0700 Rev. 3 guideline 1.3.3-4 asks for that:
#: "the same item is given the same label whenever it appears".
#:
#: The names are the field's own. The Gas Man Workbook names "the vessel-rich
#: group (VRG) ... muscle (MUS), and finally fat (FAT)" (p. 21), and
#: OpenAnesthesia's page on uptake and distribution lists "Vessel-rich group",
#: "Muscle" and "Fat".
COMPARTMENT_NAMES: Final[Mapping[RecordedQuantity, str]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: "Circuit",
        RecordedQuantity.ALVEOLAR: "Alveolar",
        RecordedQuantity.MIXED_VENOUS: "Mixed venous",
        RecordedQuantity.VESSEL_RICH: "Vessel-rich group",
        RecordedQuantity.MUSCLE: "Muscle",
        RecordedQuantity.FAT: "Fat",
    }
)

#: The hedge shown with each compartment's name: what a clinician would compare
#: the modelled value with, or None where nothing measured corresponds to it.
#: The readout row shows it under the name, and the chart's hover readout beside
#: it, because a floating box has no readout row beside it to supply the hedge.
#: `chart_frame.TraceStyle` and `dashboard_frame.ReadoutPanel` read it from here.
#:
#: The alveolar gloss is "end-tidal-equivalent", never "end-tidal".
#: `docs/INTERFACE.md` § "Minimum displayed outputs" requires the hedge, because
#: dead space, airway sampling delay, shunt and V/Q mismatch are all listed in
#: `docs/MODEL.md` § "Known limitations", so this value is not end-tidal in any
#: patient. End-tidal is the name of a measurement, and it is the one a
#: clinician would most readily compare this value with. Do not shorten either
#: gloss to fit a layout. `test_the_alveolar_readout_is_labelled_end_tidal_equivalent`
#: checks the pair.
COMPARTMENT_GLOSSES: Final[Mapping[RecordedQuantity, str | None]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: "inspired",
        RecordedQuantity.ALVEOLAR: "end-tidal-equivalent",
        RecordedQuantity.MIXED_VENOUS: None,
        RecordedQuantity.VESSEL_RICH: None,
        RecordedQuantity.MUSCLE: None,
        RecordedQuantity.FAT: None,
    }
)

#: Which core state each drawn quantity reads, by position in the state vector.
#:
#: **This table is the whole of the run's pairing of quantities to states**,
#: with one entry per compartment. It is the one place where a trace could come
#: to carry another compartment's values. It replaces the same pairing that
#: `_build_history_sample` made while the chart was drawn from recorded samples
#: (`PL-2FM6`). The chart now reads the states that the run stored
#: (`core/stored_states.py`), so a trace needs a position in
#: `governing_equations`' state order, not a compartment accessor.
#:
#: The three tissue groups are consecutive, starting at `FIRST_TISSUE_FRACTION`.
#: They follow the order of `PatientCompartmentsState.tissues`, which is the
#: order that `AgentUptakeSystem.state_vector` writes them in. This table
#: assumes that order from another module. So
#: `tests/integration/controller/test_controller_running.py`'s
#: `test_each_drawn_quantity_reads_the_state_of_the_compartment_it_names` checks the
#: order against the core's own attributes rather than restating it.
#:
#: `WASH_IN_RATIO` is deliberately absent. It is not a state but the quotient
#: that `app/wash_in.py` forms from two of these. Giving it a position here
#: would present a derived value as one the equations carry.
COMPARTMENT_STATE_INDEX: Final[Mapping[RecordedQuantity, int]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: INSPIRED_FRACTION,
        RecordedQuantity.ALVEOLAR: ALVEOLAR_FRACTION,
        RecordedQuantity.MIXED_VENOUS: VENOUS_FRACTION,
        RecordedQuantity.VESSEL_RICH: FIRST_TISSUE_FRACTION,
        RecordedQuantity.MUSCLE: FIRST_TISSUE_FRACTION + 1,
        RecordedQuantity.FAT: FIRST_TISSUE_FRACTION + 2,
    }
)

#: The name that an error message gives each compartment's fraction, where the
#: interface builds the fraction itself (`PL-7DJK`).
#:
#: These are the names that `AgentUptakeSystem._write_state_vector` gives the
#: same six quantities when a step writes them (`PL-SPN6`). The interface builds
#: a checked `Fraction` for the snapshot's fractions, the MAC multiples and a
#: drawn column. A value rejected there is named as the step that computed it
#: would have named it. So a reader of the halted-run notice learns which
#: compartment failed, whichever of the two rejected it. `WASH_IN_RATIO` is
#: absent for the reason given above: it is a quotient of two of these, and the
#: interface builds no `Fraction` of it.
COMPARTMENT_FRACTION_NAMES: Final[Mapping[RecordedQuantity, str]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: "inspired_partial_pressure_fraction",
        RecordedQuantity.ALVEOLAR: "alveolar partial_pressure_fraction",
        RecordedQuantity.MIXED_VENOUS: "venous partial_pressure_fraction",
        RecordedQuantity.VESSEL_RICH: "vessel_rich partial_pressure_fraction",
        RecordedQuantity.MUSCLE: "muscle partial_pressure_fraction",
        RecordedQuantity.FAT: "fat partial_pressure_fraction",
    }
)


@dataclass(frozen=True, slots=True)
class RecordedSeries:
    """One recorded trace: one substance's values for one quantity.

    It is the address of one trace in a drawn window, and what a chart trace
    is bound to. It is one value rather than two loose arguments, because the
    binding is a matter of presentation correctness, not a lookup convenience.
    A trace drawn from another substance's values misstates the run exactly as
    one drawn from another compartment's values does. A pair that travels
    together cannot have one half rebound without the other.
    `app/chart_frame.py`'s `_run_frame` builds one per drawn trace for that
    reason.
    """

    substance_id: str
    """Which substance's values, under the identifier the run records it by.

    A run records one substance today, the agent that `SimulationController`
    is running, because `set_agent` starts a new run rather than adding to
    this one. Nitrous oxide is what will make a run's mapping wider than one
    entry. Until then, the shape of the type carries the generality, not the
    data.
    """

    quantity: RecordedQuantity
    """Which of that substance's quantities. See `RecordedQuantity`."""


@dataclass(frozen=True, slots=True)
class DrawnWindow:
    """The states one frame draws, each read from the states the run stored.

    `SimulationController.drawn_window` returns this window, and the chart is
    drawn from nothing else. Each state is the one that the run stored for
    its second (`core/stored_states.py`), so a point on a trace is the value
    that the readout showed at that second (`PL-MH9J`).

    `SimulationController.preview_window` returns one too. Its states are
    predicted, for a setting that the reader is trying, and no run stored
    them. They are drawn as a preview and used for nothing else.

    Attributes:
        substance_id: Which substance every state here describes. It is
            carried so that a trace cannot be drawn from another substance's
            values. The frame that asks for the window names the agent from
            which its readouts were formatted. `compartment_fractions`
            rejects any other agent.
        times_s: The instants drawn, ascending, in simulated seconds.
        states: One state per instant.
        alveolar_ventilations_l_min: For each instant, the alveolar
            ventilation of the step that reached its state, in L/min. The
            F_A/F_I plot draws nothing at a state that a step at zero
            ventilation reached (rule 3 of `app/wash_in.py`), so the window
            carries the ventilation beside each state rather than leaving the
            chart to look it up.

    Raises:
        SimulationConfigurationError: If the three sequences differ in length.
            A trace would then be drawn against another trace's time axis.
            Also raised if an instant is NaN or infinite. Every instant here
            is a time the run reached, so a non-finite one is a defect. The
            chart hands its points to pyqtgraph without pyqtgraph's own
            finiteness check, so this check is what keeps such an instant off
            the plot (`app/chart_frame.py`, `PL-TCNT`).
    """

    substance_id: str
    times_s: tuple[float, ...]
    states: tuple[tuple[float, ...], ...]
    alveolar_ventilations_l_min: tuple[AlveolarVentilation, ...]

    def __post_init__(self) -> None:
        if len(self.times_s) != len(self.states):
            raise SimulationConfigurationError(
                f"a drawn window has {len(self.times_s)} instants and {len(self.states)} "
                "states; each state belongs to one instant"
            )

        if len(self.alveolar_ventilations_l_min) != len(self.times_s):
            raise SimulationConfigurationError(
                f"a drawn window has {len(self.times_s)} instants and "
                f"{len(self.alveolar_ventilations_l_min)} alveolar ventilations; each "
                "instant needs the ventilation of the step that reached it"
            )

        for time_s in self.times_s:
            if not isfinite(time_s):
                raise SimulationConfigurationError(
                    f"a drawn window holds the instant {time_s} s, which is not finite; "
                    "every drawn instant is a time the run reached"
                )

    def compartment_fractions(self, series: RecordedSeries) -> list[float]:
        """This trace's value at every drawn instant, as a fraction of 1 atm.

        Args:
            series: Which substance's quantity to read.
                `COMPARTMENT_STATE_INDEX` pairs each quantity with its state.
                It has no entry for `RecordedQuantity.WASH_IN_RATIO`, which is
                a quotient rather than a state. Use `wash_in_quotients` for
                that one.

        Returns:
            One fraction per entry of `times_s`, in the same order.

        Raises:
            SimulationConfigurationError: If `series` names a substance this
                window does not describe, or names the derived wash-in ratio.
        """

        self._require_substance(series.substance_id)

        if series.quantity not in COMPARTMENT_STATE_INDEX:
            raise SimulationConfigurationError(
                f"{series.quantity} is not a compartment state; it is derived from two of "
                "them, and `wash_in_quotients` is what forms it"
            )

        index = COMPARTMENT_STATE_INDEX[series.quantity]

        return [state[index] for state in self.states]

    def wash_in_quotients(self, substance_id: str) -> list[float | None]:
        """F_A/F_I at every drawn instant, or `None` where there is no quotient.

        While the run kept a history, `app/wash_in.py`'s rules ran once per
        *recorded sample*, and the stretches they produced were updated
        incrementally. The stretches are now a property of the drawn columns
        instead. The quotient is plain arithmetic
        on the two fractions this window already carries, so it is formed for
        what is being plotted rather than for samples behind it.

        This change is an improvement, not just a move. A stretch boundary can
        now fall only on a drawn instant, so the point where the curve stops
        is a point the chart actually plots. Before, it was a recorded sample
        that the decimation might not have selected.

        The method returns the quotient rather than a `WashInReading`, because
        the chart needs the number *outside* the domain too. A stretch is
        drawn one column past equilibrium, so that it meets the reference line
        rather than stopping short of it. Choosing that column means comparing
        its ratio against the axis ceiling. `None` is what
        `wash_in.wash_in_ratio` itself returns when the denominator is less
        than the smallest concentration the display resolves. It is also the
        entry for a state that a step at zero alveolar ventilation reached
        (`wash_in.is_ventilated`), where the ratio is not a wash-in fraction
        on either side of one. In both cases there is nothing to draw at all,
        and no crossing column either, so a stretch ends at the last
        ventilated state.

        Args:
            substance_id: The substance whose ratio to form. The quotient is
                formed from that substance's own two fractions.

        Returns:
            One entry per entry of `times_s`, in the same order.

        Raises:
            SimulationConfigurationError: If `substance_id` is not the one
                this window describes.
        """

        self._require_substance(substance_id)
        alveolar = COMPARTMENT_STATE_INDEX[RecordedQuantity.ALVEOLAR]
        circuit = COMPARTMENT_STATE_INDEX[RecordedQuantity.CIRCUIT]

        return [
            wash_in_quotient(state[alveolar], state[circuit], ventilated=is_ventilated(ventilation))
            for state, ventilation in zip(
                self.states, self.alveolar_ventilations_l_min, strict=True
            )
        ]

    def _require_substance(self, substance_id: str) -> None:
        """Reject a read for a substance this window does not describe.

        The run's own store made the same check before the store was deleted,
        and the check is kept for the same reason. A trace drawn from another
        substance's values misstates the run exactly as one drawn from another
        compartment's values does. Every value in such a trace would still be
        one the model really produced.
        """

        if substance_id != self.substance_id:
            raise SimulationConfigurationError(
                f"this window describes {self.substance_id!r}, so it cannot draw "
                f"{substance_id!r}; a run is of one agent"
            )
