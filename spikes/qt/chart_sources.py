"""What the spike's six traces draw, and the one read that produces them.

Qt-free and simulation-only: everything here reads a `SimulationController`
and answers with plain lists of floats. The Qt shell does not know how a trace
was produced, which keeps the question this module answers - *which numbers is
the chart drawing* - readable on its own.

**One read path, because there is now only one.** `PL-2FM6` landed while this
spike was being written: `RunHistory`, `history_window` and the M4 decimation
`PL-55DH` was scoped against are gone, and `SimulationController.drawn_window`
is the whole of what a chart is drawn from. That is a simplification for the
spike rather than a complication - one evaluation serves all six traces,
because a state carries every compartment at once - and it removes the reason
the spike would otherwise have needed a source selector: the shipped path is
now the faithful one, so measuring it and drawing it are the same act.

**What stays a control is the column budget.** `PL-QXSB` argued that Qt's
array transport would make the drawn point count stop mattering; with M4 gone
that question is no longer "can decimation be dropped" but "can the column
budget be raised", which is the same question in the architecture that
replaced it. `CHART_COLUMN_BUDGET_PER_SERIES` is 150 because Flet charges
~24.5 us per point control per frame whether or not the point moved; nothing
in the model or in the reader's eye chose it. So the spike offers it as a
control, defaulting to the shipped value, and reports the point count each
setting produces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.chart_series import CHART_COLUMN_BUDGET_PER_SERIES
from anesthesia_sim.app.controller import (
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
    SimulationController,
    SimulationSnapshot,
)

#: Column counts the spike offers, the shipped budget first.
#:
#: Multiples of `CHART_COLUMN_BUDGET_PER_SERIES` rather than round numbers, so
#: that a frame cost read off the instrument panel is a multiple of the shipped
#: frame's and the comparison needs no arithmetic. The top of the ladder is
#: sixteen times the shipped budget, which at the 12-hour time base is a column
#: every 18 seconds - finer than the model's own 0.1 s step could ever be
#: distinguished at that width, so it is a ceiling on the question rather than
#: a setting anyone would run.
COLUMN_BUDGETS: Final[tuple[int, ...]] = tuple(
    CHART_COLUMN_BUDGET_PER_SERIES * multiple for multiple in (1, 2, 4, 8, 16)
)

#: The caption under the plot: what produced these points, and what they may
#: not be read as. Required rather than decorative - `CLAUDE.md` asks a
#: displayed value to be traceable to the model, inputs and transformations
#: that produced it, and asks a modelled value not to be presentable as a
#: measured one. The spike draws the same numbers the application draws, so it
#: owes the same statement.
POINT_PROVENANCE = (
    "Points are the run's score evaluated at {columns} grid columns across the axis, plus "
    "one column per control change in the window and the two ends of the drawn range: "
    "{points} points over {traces} traces. Every plotted point is a modelled state at the "
    "instant it is drawn at, not a measurement; the straight segment between two points is "
    "the plot's rendering and not a state the model computed."
)


@dataclass(frozen=True, slots=True)
class SpikeTrace:
    """One compartment trace: what it draws, and how it is drawn.

    The spike's counterpart of `simulation_view._CompartmentTrace`, reduced to
    what a plot and a readout need. It holds the compartment, the two label
    lines and the two visual channels in one record for the reason the shipped
    table does: a trace drawn from one compartment under another's name
    misstates the run exactly as a wrong number does, and three lists that had
    to be kept in step would eventually not be.

    Attributes:
        quantity: The compartment this trace draws.
            `DrawnWindow.compartment_fractions` resolves it to a state index,
            so the spike keeps no second copy of that pairing.
        label: The compartment's name, as the shipped readout row says it.
        qualifier: The smaller line beneath, where the shipped row draws one.
            Not decoration: "end-tidal-equivalent" and "inspired" are required
            hedges (`PL-NV9W`, `PL-8M05`), because what the model computes is
            a compartment and what a clinician would set beside it on a
            monitor is a different, measured thing. A spike that dropped them
            would present a modelled compartment as that measurement.
        color: The trace's line colour, copied from `app/theme.py`.
        dash: The dash pattern, in units of line width. Copied from the
            shipped chart and carried because colour alone does not separate
            these six: `theme.py` records that the four models of simulated
            colour-vision deficiency put pairs of them as close as 1.08, far
            under the 3:1 that would make colour sufficient, so the pattern is
            the separating channel. A spike without it would look better than
            the design it is testing.
        width: Line width in pixels, as the shipped chart draws it.
    """

    quantity: RecordedQuantity
    label: str
    qualifier: str | None
    color: str
    dash: tuple[float, ...] | None
    width: float


#: The six compartment traces, in the order the shipped interface lists them.
#:
#: Colours and dash patterns are *copies* of `app/theme.py` and
#: `app/simulation_view.py`, not imports. `theme.py` holds no Flet and could be
#: imported, but the dash patterns are written inline in `simulation_view.py`,
#: which does, and a spike that imported it would load the toolkit it exists to
#: be compared against. Copying is admissible only because this tree is
#: disposable and says that it copied; `PL-2CS8` consolidated every display
#: token into `theme.py` precisely so that nothing shipped keeps a second copy.
TRACES: Final[tuple[SpikeTrace, ...]] = (
    SpikeTrace(RecordedQuantity.CIRCUIT, "Circuit", "inspired", "#176B87", None, 3.0),
    SpikeTrace(
        RecordedQuantity.ALVEOLAR, "Alveolar", "end-tidal-equivalent", "#159789", (10.0, 4.0), 3.0
    ),
    SpikeTrace(RecordedQuantity.MIXED_VENOUS, "Mixed venous", None, "#7C3AED", (4.0, 3.0), 2.0),
    SpikeTrace(RecordedQuantity.VESSEL_RICH, "Vessel-rich group", None, "#DC2626", (6.0, 6.0), 2.0),
    SpikeTrace(RecordedQuantity.MUSCLE, "Muscle", None, "#D17206", (2.0, 3.0), 2.0),
    SpikeTrace(RecordedQuantity.FAT, "Fat", None, "#64748B", (12.0, 4.0, 2.0, 4.0), 2.0),
)


@dataclass(frozen=True, slots=True)
class TracePoints:
    """One frame's points for every trace, in percent of one atmosphere.

    Times are shared rather than carried per trace because the read is shared:
    `drawn_window` evaluates one set of instants and every compartment is a
    component of the state at each. Holding one time axis is what makes it
    structurally impossible for two traces on this plot to come from different
    instants - the failure `DrawnWindow`'s own length check guards on the
    other side of the boundary.

    Percent rather than fraction because percent is what the axis is labelled
    in and what the readouts show. The conversion happens once, here, so a
    factor of a hundred can be wrong in one place rather than in seven.

    Attributes:
        times_s: The drawn instants, ascending, in simulated seconds.
        percents: One list per entry of `TRACES`, in that order, each the same
            length as `times_s`.
    """

    times_s: list[float]
    percents: list[list[float]]

    @property
    def point_count(self) -> int:
        """How many points this frame puts on the plot, across every trace."""

        return len(self.times_s) * len(self.percents)


def read_traces(
    controller: SimulationController,
    snapshot: SimulationSnapshot,
    start_s: float,
    stop_s: float,
    columns: int,
) -> TracePoints:
    """Evaluate every trace across the axis the caller is about to draw.

    The same call `chart_series.redraw_visible_window` makes, with the same
    bounds and the same budget, so a frame timed here is the frame the
    application draws.

    The agent comes from the snapshot the same frame formats its readouts
    from, so a trace and the number beside it cannot describe different
    agents: `DrawnWindow.compartment_fractions` refuses a substance the
    window does not describe rather than drawing whichever one it holds.

    Args:
        controller: The running session.
        snapshot: The frame's snapshot, for the agent the run is of.
        start_s: Left edge of the axis, in simulated seconds.
        stop_s: Right edge of the axis, in simulated seconds.
        columns: Grid columns the axis is divided into.

    Returns:
        The drawn instants and one percent series per trace. Empty where the
        axis lies entirely ahead of the run, which is an ordinary state at the
        very start of one.
    """

    window = controller.drawn_window(start_s, stop_s, columns)

    return TracePoints(
        times_s=list(window.times_s),
        percents=[_percents(window, snapshot.agent_id, trace) for trace in TRACES],
    )


def _percents(window: DrawnWindow, agent_id: str, trace: SpikeTrace) -> list[float]:
    """One trace's drawn values, as a percent of one atmosphere."""

    fractions = window.compartment_fractions(RecordedSeries(agent_id, trace.quantity))

    return [fraction * 100.0 for fraction in fractions]


def snapshot_percents(snapshot: SimulationSnapshot) -> tuple[float, ...]:
    """The snapshot's own compartment readings, in `TRACES` order, as percent.

    The readout row's numbers, read straight off the snapshot rather than off
    the chart. Kept beside the chart's read so that `verify_trace_binding` can
    compare the two, and written out in `TRACES` order rather than looked up
    so that a reordering of the table cannot silently rebind a readout onto
    another compartment's value.
    """

    return (
        snapshot.circuit_concentration_fraction * 100.0,
        snapshot.alveolar_concentration_fraction * 100.0,
        snapshot.mixed_venous_concentration_fraction * 100.0,
        snapshot.vessel_rich_partial_pressure_fraction * 100.0,
        snapshot.muscle_partial_pressure_fraction * 100.0,
        snapshot.fat_partial_pressure_fraction * 100.0,
    )


def verify_trace_binding(
    controller: SimulationController, snapshot: SimulationSnapshot, tolerance_percent: float
) -> list[str]:
    """Check that each trace's newest point matches the readout beside it.

    The end-to-end presentation check `CLAUDE.md` asks for - patient inputs,
    model, units, formatting, displayed value - reduced to the one thing this
    spike could get wrong on its own. `TRACES` binds a compartment to a label
    and to a position in the readout row, and nothing in the type system stops
    those naming different compartments; a swap shows up here as two traces
    whose newest drawn value does not match the number printed beneath them.

    The two are not expected to agree exactly. The chart's value is the score
    evaluated at the run's reach and the readout's is the compartment's own
    canonical state, and `core/run_score.py` states the two are equal "to
    floating-point composition, not exactly". So this compares against a
    tolerance - one far tighter than a swapped compartment could hide in, and
    stated by the caller rather than assumed here.

    Args:
        controller: A session that has advanced at least one step.
        snapshot: Its current snapshot.
        tolerance_percent: How far the two may differ, in percentage points.

    Returns:
        One message per disagreeing trace; empty when every trace agrees, and
        empty for a run that has not advanced, which has nothing to compare.
    """

    if not snapshot.has_recorded_run:
        return []

    points = read_traces(
        controller, snapshot, 0.0, snapshot.elapsed_s, CHART_COLUMN_BUDGET_PER_SERIES
    )
    failures: list[str] = []

    if not points.times_s:
        return [f"the chart drew no points for a run {snapshot.elapsed_s:.1f} s long"]

    for trace, drawn, shown in zip(
        TRACES, points.percents, snapshot_percents(snapshot), strict=True
    ):
        difference = abs(drawn[-1] - shown)

        if difference > tolerance_percent:
            failures.append(
                f"{trace.label}: the chart's newest point is {drawn[-1]:.4f}% and the "
                f"readout says {shown:.4f}%, a difference of {difference:.4f} "
                f"percentage points"
            )

    return failures
