"""The vocabulary a run's drawn values are addressed by, and the window one
frame reads them from.

What a chart trace *is* - one substance's values for one quantity - as
against how any toolkit draws it. `app/chart_frame.py` settles what a frame
claims and `app/qt_chart.py` paints it; `app/dashboard_frame.py` addresses
its readouts in the same terms. Nothing here reads simulation state, holds a
widget, or formats a value.

**Why it is a module of its own.** `app/controller.py` is the boundary
between the UI and the scientific core, and none of this is that: a
`RecordedSeries` names a trace whether or not a run exists, and a
`DrawnWindow` is the answer to one `SimulationController.drawn_window` call
rather than any part of the controller's own state. The seam was a fact about
the imports before it was a module - the frames read these names and nothing
else of the controller's - and `PL-RD3B` is where it became one. The
controller imports `DrawnWindow` from here to declare what it returns, and
nothing here imports the controller, which is what keeps that direction
one-way.

**The identifiers are stable, and deliberately not the accessors' names.**
`RecordedQuantity` and `control_record.ControlInput` are the two vocabularies
a run is addressed by, and both are named for the domain rather than for
whichever field currently spells them, so that a rename in `core/` cannot
silently re-point a trace. Each enum's own docstring carries what that has
already been worth.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.wash_in import wash_in_ratio
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.run_definition import DisplayState

__all__ = [
    "COMPARTMENT_QUANTITIES",
    "COMPARTMENT_STATE_INDEX",
    "DrawnWindow",
    "RecordedQuantity",
    "RecordedSeries",
]


class RecordedQuantity(StrEnum):
    """One quantity the interface draws, under a stable identifier.

    What a chart trace is bound to, and the key a drawn window is read by.
    Members are named for the compartment or the quantity rather than for
    whichever field or accessor currently spells it, for the reason
    `control_record.ControlInput`'s are: `PL-3TLK` and `PL-9SH6` renamed two of the fields
    these read from, and a key that had followed the code would have had to
    be renamed with them while meaning the same thing throughout. `CIRCUIT`
    is the one to look at - the field behind it is now
    `inspired_partial_pressure_fraction`, and this key did not move.

    `WASH_IN_RATIO` is the one derived member. It is not a compartment state
    but the quotient `app/wash_in.py` specifies, named here so that the plot
    drawing it is addressed the same way every other trace is - and it is
    deliberately absent from `COMPARTMENT_STATE_INDEX`, which is what keeps
    it from being read as a state the equations carry.
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
#: Every `RecordedQuantity` except `WASH_IN_RATIO`, which is not a compartment
#: state: it is the quotient `app/wash_in.py` forms from two of these, so
#: including it here would present a derived value as one the equations carry.
#: Written out rather than filtered from the enum, so that adding a member
#: forces a decision here instead of silently joining the compartments.
COMPARTMENT_QUANTITIES: Final = (
    RecordedQuantity.CIRCUIT,
    RecordedQuantity.ALVEOLAR,
    RecordedQuantity.MIXED_VENOUS,
    RecordedQuantity.VESSEL_RICH,
    RecordedQuantity.MUSCLE,
    RecordedQuantity.FAT,
)

#: Which core state each drawn quantity reads, by position in the state vector.
#:
#: **The whole of the run's pairing is here**, one entry per compartment, and
#: it is the one place a trace could come to carry another compartment's
#: values. It replaces the same pairing `_build_history_sample` held while the
#: chart was drawn from recorded samples (`PL-2FM6`): the chart now evaluates
#: the run definition instead, so what a trace needs is a position in
#: `governing_equations`' state order rather than a compartment accessor.
#:
#: The three tissue groups are consecutive from `FIRST_TISSUE_FRACTION` in
#: `PatientCompartmentsState.tissues`' own order, which
#: `AgentUptakeSystem.state_vector` writes them in. That order is an
#: assumption this table makes about another module, so
#: `tests/integration/test_controller.py`'s
#: `test_each_recorded_quantity_carries_the_compartment_it_names` holds it
#: against the core's own attributes rather than restating it.
#:
#: `WASH_IN_RATIO` is absent deliberately: it is not a state but the quotient
#: `app/wash_in.py` forms from two of these, so giving it a position here
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


@dataclass(frozen=True, slots=True)
class RecordedSeries:
    """One recorded trace: one substance's values for one quantity.

    The address of one trace in a drawn window, and what a chart trace is
    bound to. One value rather than two loose arguments, because the binding
    is a presentation-correctness property rather than a lookup convenience:
    a trace drawn from another substance's values misstates the run exactly
    as one drawn from another compartment's does, and a pair that travels
    together cannot be half-rebound. `app/chart_frame.py`'s `_run_frame`
    builds one per drawn trace for that reason.
    """

    substance_id: str
    """Which substance's values, under the identifier the run records it by.

    A run records one substance today - the agent `SimulationController` is
    running - because `set_agent` starts a new run rather than adding to
    this one. Nitrous oxide is what makes a run's mapping wider than one
    entry; until then the shape is what carries the generality, not the data.
    """

    quantity: RecordedQuantity
    """Which of that substance's quantities. See `RecordedQuantity`."""


@dataclass(frozen=True, slots=True)
class DrawnWindow:
    """The states one frame draws, evaluated from the run's definition.

    What `SimulationController.drawn_window` answers with, and the whole of
    what the chart is drawn from. It replaces `HistoryWindow`, and the
    difference is what `PL-2FM6` is: a window over *recorded samples* asked
    which of them to draw and cost what the window spanned, where this one
    is the answer itself - the states at the instants the chart plots, and
    nothing else exists behind them.

    **A drawn value is not a recorded one, and the type says so.** Every
    state here is a `DisplayState`, which `core/run_definition.py` makes
    structurally not a state vector precisely so that a drawn value cannot
    become a keyframe, an export or a fork's opening state by having the
    right shape. `docs/MODEL.md` § "The canonical evaluation rule" is the
    guarantee; this class is one of the places it has to hold.

    Attributes:
        substance_id: Which substance every state here describes. Carried so
            a trace cannot be drawn from another substance's values: the
            frame that asks for the window names the agent its readouts were
            formatted from, and `compartment_fractions` refuses any other.
        times_s: The instants drawn, ascending, in simulated seconds.
        states: One state per instant.

    Raises:
        SimulationConfigurationError: If the two sequences differ in length,
            which would draw one trace against another's time axis.
    """

    substance_id: str
    times_s: tuple[float, ...]
    states: tuple[DisplayState, ...]

    def __post_init__(self) -> None:
        if len(self.times_s) != len(self.states):
            raise SimulationConfigurationError(
                f"a drawn window has {len(self.times_s)} instants and {len(self.states)} "
                "states; each state belongs to one instant"
            )

    def compartment_fractions(self, series: RecordedSeries) -> list[float]:
        """This trace's value at every drawn instant, as a fraction of 1 atm.

        Args:
            series: Which substance's quantity to read.
                `COMPARTMENT_STATE_INDEX` is the pairing, and it holds no
                entry for `RecordedQuantity.WASH_IN_RATIO`, which is a
                quotient rather than a state - use `wash_in_readings`.

        Returns:
            One fraction per entry of `times_s`, in the same order.

        Raises:
            SimulationConfigurationError: If `series` names a substance this
                window does not describe, or the derived wash-in ratio.
        """

        self._require_substance(series.substance_id)

        if series.quantity not in COMPARTMENT_STATE_INDEX:
            raise SimulationConfigurationError(
                f"{series.quantity} is not a compartment state; it is derived from two of "
                "them, and `wash_in_readings` is what forms it"
            )

        index = COMPARTMENT_STATE_INDEX[series.quantity]

        return [state.values[index] for state in self.states]

    def wash_in_quotients(self, substance_id: str) -> list[float | None]:
        """F_A/F_I at every drawn instant, or `None` where there is no quotient.

        `app/wash_in.py`'s rules ran once per *recorded sample* while the run
        kept a history, and the stretches they produced were maintained
        incrementally. With no history to maintain they become a property of
        the drawn column instead: the quotient is pure arithmetic over the two
        fractions this window already carries, so it is formed for what is
        being plotted rather than for samples behind it.

        That is a strengthening rather than a like-for-like move. A stretch
        boundary can now fall only on a drawn instant, so the point where the
        curve stops is a point the chart actually plots - where before it was
        a recorded sample the decimation might not have selected.

        The quotient rather than a `WashInReading` because the chart needs the
        number *outside* the domain too: a stretch is drawn one column past
        equilibrium so that it meets the reference line rather than stopping
        short of it, and choosing that column means comparing its ratio
        against the axis ceiling. `None` is `wash_in.wash_in_ratio`'s own
        answer for a denominator below the display floor, and it is the case
        with nothing to draw at all.

        Args:
            substance_id: Whose ratio. The quotient is formed from one
                substance's own two fractions.

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
            wash_in_ratio(state.values[alveolar], state.values[circuit]) for state in self.states
        ]

    def _require_substance(self, substance_id: str) -> None:
        """Refuse a read for a substance this window does not describe.

        The same guard the run's own store made before it was deleted, kept for the
        same reason: a trace drawn from another substance's values misstates
        the run exactly as one drawn from another compartment's does, and
        every value in it would be one the model really produced.
        """

        if substance_id != self.substance_id:
            raise SimulationConfigurationError(
                f"this window describes {self.substance_id!r}, so it cannot draw "
                f"{substance_id!r}; a run is of one agent"
            )
