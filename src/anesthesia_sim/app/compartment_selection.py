"""Which compartments the chart draws: the reader's selection, as a value the dashboard owns.

The selection used to live in the legend's checkboxes, and the dashboard read
it back from them (`PL-VN6M`). That worked while there was exactly one legend
in a fixed layout. The area system turns two acts that were impossible into
ordinary ones. A reader can close the Area that holds the legend, and the
selection would disappear with its boxes. A reader can open a second chart
Area, and nothing would say which legend it followed (`.claude/rules/ui-areas.md`,
test 2). So the selection is now a value here, which the dashboard holds and
passes down. This follows the pattern that `chart_frame.ChartFrame` already
sets for everything else the chart draws. `TraceLegend` shows the selection
it is given and asks for changes to it, and `assemble_chart_frame` draws from
the same value.

**Two rules come with the selection. This module owns one of them and only
reads the other.** The cap, which is two compartments while more than one run is drawn,
belongs to `chart_frame.compared_compartments`. Every question this module
asks about the cap goes through that function rather than restating the
number. The rule for a reader's click over the cap belongs to this module,
and was moved here from the legend. The compartment just asked for is shown,
and the longest-standing one makes room for it.

**A selection over the cap cannot be built.** This is the checked-type
pattern that `.claude/rules/core-domain.md` describes. Every selection that
exists is inside the cap for the runs it was built for, so
`compared_compartments` returns all of it. The legend's boxes and the chart's
curves are both drawn from one selection, so they cannot disagree. Nothing
here imports a toolkit, and `tests/unit/test_compartment_selection.py` tests
it without a display.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.chart_frame import COMPARED_COMPARTMENT_CAP, RunCount, compared_compartments
from anesthesia_sim.app.dashboard_frame import displayed_run_count
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity

__all__ = ["INITIAL_COMPARTMENT_SELECTION", "CompartmentSelection"]


@dataclass(frozen=True, slots=True)
class CompartmentSelection:
    """The compartments the reader has left drawn, held inside the cap for the runs on the chart.

    Attributes:
        order: The compartments shown, in the order the reader asked for
            them, the longest-standing first. A click over the cap uses this
            order (`with_compartment`). What is drawn, and in what order, is
            decided by `shown`.
        run_count: How many runs the selection is drawn across, which
            decides whether the cap applies. It is passed as an `int` and
            built here as a `RunCount`, which checks it, so the selection
            always holds a checked count.

    Raises:
        TypeError: If `order` is not a tuple, holds anything but a
            `RecordedQuantity`, or `run_count` is not an `int`. A `bool` is
            rejected too, because it subclasses `int` and would make `True`
            count as one run.
        ValueError: If `order` names a quantity the chart draws no trace for
            or names one twice; if `run_count` is not between 1 and
            `MAX_DISPLAYED_RUNS`, the most the dashboard draws; or if the
            selection is over the cap for its run count, which would leave
            a shown compartment off the plot.
    """

    order: tuple[RecordedQuantity, ...]
    run_count: RunCount

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

        # A frozen record can write its own field here, once. So the record
        # holds the checked count rather than the `int` it was given.
        object.__setattr__(self, "run_count", displayed_run_count(self.run_count))
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
        """Return this selection with one compartment shown or hidden, as a reader's click asks.

        A compartment shown over the cap is honoured, and the longest-standing
        selections make room for it. The oldest are removed rather than the
        newest, so the compartment a reader just asked for is the one they get.
        A cap that refused the click instead would leave them pressing a box
        that does not respond, which is the worse of the two surprises.

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
        """Return this selection drawn across another number of runs, held inside its cap.

        What is kept is exactly what the chart would draw for that many runs,
        rather than a pair chosen here. That is the top of the compartment
        table, by the rule in `compared_compartments`. So the boxes left
        checked are the curves on the plot. A selection that the cap reduced
        stays reduced when the runs fall back to one, as it did while the
        legend held the selection. Nothing here remembers what the cap removed.

        Args:
            run_count: How many runs are now drawn.

        Returns:
            The selection for that many runs.

        Raises:
            TypeError: If `run_count` is not an `int`.
            ValueError: If `run_count` is not between 1 and `MAX_DISPLAYED_RUNS`.
        """

        count = displayed_run_count(run_count)
        drawn, _ = compared_compartments(self.order, count)

        return CompartmentSelection(
            tuple(quantity for quantity in self.order if quantity in drawn), count
        )


def _require_compartment(quantity: object) -> RecordedQuantity:
    """Return `quantity` if it is a compartment the chart draws a trace for.

    A `RecordedQuantity` is a `str`, so a bare string spelling one compares
    equal to it and would pass a membership test. So the type is checked
    first, and a bare string is refused.

    Raises:
        TypeError: If `quantity` is not a `RecordedQuantity`.
        ValueError: If it is one the chart draws no trace for. That is the
            wash-in ratio, which is a quotient of two compartments rather
            than one compartment.
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
#: compartment, on one run, in table order. So when a second run arrives,
#: the selection keeps the top of the table, where the circuit and alveolar
#: traces are.
INITIAL_COMPARTMENT_SELECTION: Final = CompartmentSelection(COMPARTMENT_QUANTITIES, RunCount(1))
