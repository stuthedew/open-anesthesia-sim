"""Which compartments the chart draws: the reader's selection, as a value the dashboard owns.

The selection used to live in the legend's checkboxes, and the dashboard read
it back from them (`PL-VN6M`). That held while there was exactly one legend
in a fixed layout. The area system makes two ordinary acts of what were
impossible ones: a reader closes the Area holding the legend, and the
selection went with its boxes; a reader opens a second chart Area, and
nothing said which legend it followed (`.claude/rules/ui-areas.md`, test 2).
So the selection is a value here, held by the dashboard and handed down, the
pattern `chart_frame.ChartFrame` already sets for everything else the chart
draws: `TraceLegend` shows the selection it is handed and asks for a change
to it, and `assemble_chart_frame` draws from the same value.

**Two rules travel with it, and one of them is only read here.** The cap -
two compartments while more than one run is drawn - is
`chart_frame.compared_compartments`', and every question this module asks of
it goes through that function rather than restating the number. The rule for
a reader's click over the cap is this module's, moved here from the legend:
the compartment just asked for is shown, and the longest-standing one makes
room for it.

**A selection over the cap cannot be built**, the pattern
`.claude/rules/core-domain.md` gives a checked type. Every selection that
exists is inside the cap for the runs it was built for, so
`compared_compartments` returns all of it, and the legend's boxes and the
chart's curves, both drawn from one selection, cannot disagree. Nothing here
imports a toolkit, and `tests/unit/test_compartment_selection.py` holds it
without a display.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.chart_frame import COMPARED_COMPARTMENT_CAP, compared_compartments
from anesthesia_sim.app.dashboard_frame import MAX_DISPLAYED_RUNS
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity

__all__ = ["INITIAL_COMPARTMENT_SELECTION", "CompartmentSelection"]


@dataclass(frozen=True, slots=True)
class CompartmentSelection:
    """The compartments the reader has left drawn, held inside the cap for the runs on the chart.

    Attributes:
        order: The compartments shown, in the order the reader asked for
            them, the longest-standing first. The order is what a click over
            the cap reads (`with_compartment`); what is drawn, and in what
            order, is `shown`'s.
        run_count: How many runs the selection is drawn across, which is
            what decides whether the cap applies.

    Raises:
        TypeError: If `order` is not a tuple, holds anything but a
            `RecordedQuantity`, or `run_count` is not an `int` - a `bool`
            included, which subclasses `int` and would make `True` one run.
        ValueError: If `order` names a quantity the chart draws no trace for
            or names one twice; if `run_count` is not between 1 and
            `MAX_DISPLAYED_RUNS`, the most the dashboard draws; or if the
            selection is over the cap for its run count, which would leave
            a shown compartment off the plot.
    """

    order: tuple[RecordedQuantity, ...]
    run_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.order, tuple):
            raise TypeError(
                f"a compartment selection's order is a tuple, not {type(self.order).__name__}"
            )

        for quantity in self.order:
            _require_compartment(quantity)

        repeated = sorted(
            {quantity.value for quantity in self.order if self.order.count(quantity) > 1}
        )

        if repeated:
            raise ValueError(
                f"a compartment selection names each compartment once, and names "
                f"{', '.join(repeated)} more than once"
            )

        if isinstance(self.run_count, bool) or not isinstance(self.run_count, int):
            raise TypeError(f"a run count is an int, not {type(self.run_count).__name__}")

        if not 1 <= self.run_count <= MAX_DISPLAYED_RUNS:
            raise ValueError(
                f"a compartment selection is drawn across 1 to {MAX_DISPLAYED_RUNS} runs, the "
                f"most the dashboard draws, not {self.run_count}"
            )

        _, undrawn = compared_compartments(self.order, self.run_count)

        if undrawn:
            raise ValueError(
                f"{len(self.order)} compartments shown across {self.run_count} runs would leave "
                f"{undrawn} off the plot; a selection is held to the cap of "
                f"{COMPARED_COMPARTMENT_CAP} that `chart_frame.compared_compartments` applies"
            )

    @property
    def shown(self) -> tuple[RecordedQuantity, ...]:
        """The compartments drawn, in table order: the whole selection, which is inside the cap."""

        drawn, _ = compared_compartments(self.order, self.run_count)

        return drawn

    def with_compartment(self, quantity: RecordedQuantity, shown: bool) -> CompartmentSelection:
        """This selection with one compartment shown or hidden, as a reader's click asks.

        A compartment shown over the cap is honoured, and the longest-standing
        selections make room for it: the oldest rather than the newest, so the
        compartment a reader just asked for is the one they get. A cap that
        refused the click instead would leave them pressing a box that does not
        respond, which is the worse of the two surprises.

        Args:
            quantity: Which compartment.
            shown: Whether to draw it.

        Returns:
            The new selection, or this one where the compartment is already in
            the state asked for. Showing a compartment already shown keeps its
            place in the order rather than renewing it.

        Raises:
            TypeError: If `quantity` is not a `RecordedQuantity`.
            ValueError: If the chart draws no trace for `quantity`.
        """

        _require_compartment(quantity)

        if shown == (quantity in self.order):
            return self

        if not shown:
            return CompartmentSelection(
                tuple(held for held in self.order if held is not quantity), self.run_count
            )

        order = (*self.order, quantity)

        while compared_compartments(order, self.run_count)[1]:
            order = order[1:]

        return CompartmentSelection(order, self.run_count)

    def with_run_count(self, run_count: int) -> CompartmentSelection:
        """This selection drawn across another number of runs, held inside its cap.

        What is kept is exactly what the chart would draw for that many runs -
        the top of the compartment table, which is `compared_compartments`'
        rule - rather than a pair chosen here, so the boxes left checked are
        the curves on the plot. A selection the cap reduced stays reduced when
        the runs fall back to one, as it did while the legend held it: nothing
        here remembers what the cap took off.

        Args:
            run_count: How many runs are now drawn.

        Returns:
            The selection for that many runs.

        Raises:
            TypeError: If `run_count` is not an `int`.
            ValueError: If `run_count` is not between 1 and `MAX_DISPLAYED_RUNS`.
        """

        if isinstance(run_count, bool) or not isinstance(run_count, int):
            raise TypeError(f"a run count is an int, not {type(run_count).__name__}")

        drawn, _ = compared_compartments(self.order, run_count)

        return CompartmentSelection(
            tuple(quantity for quantity in self.order if quantity in drawn), run_count
        )


def _require_compartment(quantity: object) -> RecordedQuantity:
    """`quantity`, where it is a compartment the chart draws a trace for.

    A `RecordedQuantity` is a `str`, so a bare string spelling one compares
    equal to it and would pass a membership test; it is refused by type
    first.

    Raises:
        TypeError: If `quantity` is not a `RecordedQuantity`.
        ValueError: If it is one the chart draws no trace for - the wash-in
            ratio, which is a quotient of two compartments rather than one.
    """

    if not isinstance(quantity, RecordedQuantity):
        raise TypeError(f"a compartment selection holds RecordedQuantity members, not {quantity!r}")

    if quantity not in COMPARTMENT_QUANTITIES:
        raise ValueError(
            f"{quantity.value} is not a compartment the chart draws a trace for; the "
            f"compartments are {', '.join(member.value for member in COMPARTMENT_QUANTITIES)}"
        )

    return quantity


#: What the dashboard shows before a reader has chosen anything: every
#: compartment, on one run, in table order - so a second run's arrival keeps
#: the top of the table, which is where the circuit and alveolar traces are.
INITIAL_COMPARTMENT_SELECTION: Final = CompartmentSelection(COMPARTMENT_QUANTITIES, 1)
