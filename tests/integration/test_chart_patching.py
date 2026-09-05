"""Prove a live Flet client is told when a reused chart point changes.

`SimulationView` mutates the `LineChartDataPoint` objects the chart already
holds instead of rebuilding them every frame (PL-010). That is only safe if
Flet's diff notices the mutation. A mutation it missed would leave the client
drawing the previous frame's trace beneath the current frame's readouts - the
correct number under a stale picture, which `CLAUDE.md` counts as a safety
failure rather than a cosmetic one. PL-001 declined this optimization for
exactly that reason and left confirming it as PL-010's first step.

Nothing here stubs the diff. `_RecordingConnection` is a real
`flet.messaging.connection.Connection`; it serializes each outbound message
the same way the WebSocket transport does and then keeps it. The
serialization is not incidental - it is what writes the structural snapshots
the *next* diff compares against, so a stand-in that skipped it would answer
a question the running app never asks. The patch asserted on below is
therefore the patch a browser would receive.

Confirmed end to end on 2026-09-02 against Chromium driving the real
`flet_web` server: with the trace advanced by in-place mutation alone, the
rendered line moved between frames. This file is what keeps that true - a
Flet upgrade that stopped reporting in-place mutation would fail here rather
than silently freeze the chart.
"""

from statistics import median
from typing import Any

import flet as ft
import msgpack
import pytest
from flet.controls.base_control import BaseControl
from flet.controls.object_patch import Operation
from flet.messaging.connection import Connection
from flet.messaging.protocol import (
    ClientAction,
    ClientMessage,
    PatchControlBody,
    configure_encode_object_for_msgpack,
)
from flet.messaging.session import Session
from flet.pubsub.pubsub_hub import PubSubHub

from anesthesia_sim.app.chart_downsampling import first_index_at_or_after
from anesthesia_sim.app.chart_series import CHART_COLUMN_BUDGET_PER_SERIES, PARKED_CONTROL_MARK_X
from anesthesia_sim.app.controller import (
    ControlChange,
    ControlInput,
    HistoryWindow,
    RecordedQuantity,
    RunHistory,
    SimulationHistorySample,
    SimulationSnapshot,
)
from anesthesia_sim.app.simulation_view import (
    MAX_CHART_CONTROL_MARKS,
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SimulationView,
)
from anesthesia_sim.core.parameters import load_agent_parameters

#: The agent whose run this suite replays, and so the substance its recorded
#: samples are keyed by. The snapshot and the run must name the same one: the
#: view reads the run under the agent its snapshot names.
AGENT_ID = "sevoflurane"

# One render tick covers this many recorded simulation samples.
SAMPLES_PER_RENDER_TICK = round(RENDER_INTERVAL_S / SIMULATION_STEP_S)
# Long enough that the visible window is saturated, so decimation is active
# and the drawn point count holds steady from one tick to the next.
SATURATED_SAMPLE_COUNT = 4_000


def _encode(payload: Any) -> None:
    """Serialize exactly as the WebSocket transport does, and discard it.

    Called for the side effect: encoding records the list, dict and nested
    dataclass snapshots on each control that the following diff reads back.
    """

    msgpack.packb(payload, default=configure_encode_object_for_msgpack(BaseControl))


class _RecordingConnection(Connection):
    """A real Flet connection that serializes messages and keeps them."""

    def __init__(self) -> None:
        super().__init__()
        self.pubsubhub = PubSubHub()
        self.messages: list[ClientMessage] = []

    def send_message(self, message: ClientMessage) -> None:
        _encode([message.action, message.body])
        self.messages.append(message)


class _ReplayController:
    """Serve one recorded run to the view, one render tick per frame.

    Answers `snapshot` and `history_window` the way the real controller
    does: the snapshot is the instant, the window is the part of the run
    the caller asks for. The cursor advances on the snapshot alone, so both
    halves of one frame describe the same instant however many times the
    window is read.
    """

    def __init__(
        self,
        samples: tuple[SimulationHistorySample, ...],
        start: int,
        control_timeline: tuple[ControlChange, ...] = (),
    ) -> None:
        self._samples = samples
        # The whole run is recorded up front and the cursor bounds what the
        # view may see, which is what the real controller's append-only
        # history gives a reader for free: a window is a range, and a range
        # that stops short of the newest sample reads exactly as it did when
        # that sample was the newest.
        self._run = RunHistory.of(samples)
        self._cursor = start
        self._control_timeline = control_timeline
        self.is_running = True

    def history_window(self, start_s: float) -> HistoryWindow:
        # The cursor runs past the recorded run on the last frames of a
        # replay, exactly as `snapshot` lets it; a window is still a range
        # within what was recorded.
        stop_index = min(self._cursor, len(self._run))
        start_index = min(first_index_at_or_after(self._run.times_s(), start_s), stop_index)

        return HistoryWindow(run=self._run, index_offset=start_index, stop_index=stop_index)

    def snapshot(self) -> SimulationSnapshot:
        history = self._samples[: self._cursor]
        self._cursor += SAMPLES_PER_RENDER_TICK
        latest = history[-1]
        recorded = latest.substances[AGENT_ID]

        return SimulationSnapshot(
            is_running=True,
            elapsed_s=latest.elapsed_s,
            agent_id=AGENT_ID,
            agent_display_name="Sevoflurane",
            max_delivered_concentration_percent=8.0,
            agent_mac_percent=2.0,
            agent_mac_awake=load_agent_parameters(AGENT_ID).mac_awake,
            circuit_volume_l=6.0,
            fresh_gas_flow_l_min=4.0,
            delivered_concentration_fraction=0.08,
            alveolar_ventilation_l_min=4.0,
            cardiac_output_l_min=5.0,
            circuit_concentration_fraction=recorded[RecordedQuantity.CIRCUIT],
            alveolar_concentration_fraction=recorded[RecordedQuantity.ALVEOLAR],
            mixed_venous_concentration_fraction=recorded[RecordedQuantity.MIXED_VENOUS],
            vessel_rich_partial_pressure_fraction=recorded[RecordedQuantity.VESSEL_RICH],
            muscle_partial_pressure_fraction=recorded[RecordedQuantity.MUSCLE],
            fat_partial_pressure_fraction=recorded[RecordedQuantity.FAT],
            delivered_agent_l=0.012345,
            exhausted_agent_l=0.002345,
            stored_agent_l=0.01,
            unaccounted_agent_l=1.5e-13,
            agent_accounting_absolute_error_l=1.5e-13,
            agent_accounting_passes_validation=True,
            control_timeline=self._control_timeline,
            failure_reason=None,
        )


def _recorded_run(sample_count: int) -> tuple[SimulationHistorySample, ...]:
    """A monotone wash-in whose six traces never coincide.

    The alveolar trace *lags* the circuit one - a slower rise to a lower
    asymptote - which is not decoration. The chart draws F_A/F_I from this
    pair, and that ratio is only inside the domain `app/wash_in.py` states
    while alveolar stays under circuit; a fixture where the alveolar trace
    led would describe a run in which the lung filled the circuit, and would
    leave the wash-in trace here drawing nothing or growing where every
    other trace is steady. The two decay constants are 0.999 and 0.9993, so
    the ratio rises from 0.61 to its 0.875 asymptote across the run and is
    saturated at the window sizes these tests use.
    """

    return tuple(
        SimulationHistorySample(
            elapsed_s=index * SIMULATION_STEP_S,
            substances={
                AGENT_ID: {
                    RecordedQuantity.CIRCUIT: 0.080 * (1.0 - 0.999**index),
                    RecordedQuantity.ALVEOLAR: 0.070 * (1.0 - 0.9993**index),
                    RecordedQuantity.MIXED_VENOUS: 0.050 * (1.0 - 0.997**index),
                    RecordedQuantity.VESSEL_RICH: 0.060 * (1.0 - 0.996**index),
                    RecordedQuantity.MUSCLE: 0.030 * (1.0 - 0.995**index),
                    RecordedQuantity.FAT: 0.010 * (1.0 - 0.994**index),
                }
            },
        )
        for index in range(sample_count)
    )


def _control_timeline(
    count: int, first_elapsed_s: float, spacing_s: float
) -> tuple[ControlChange, ...]:
    """`count` adjustments, cycling the controls, `spacing_s` apart.

    The caller places them inside the visible window: a mark outside it is
    not drawn, so a spacing that overruns the window would leave a test
    measuring an empty pool while looking as though it measured a full one.
    """

    controls = list(ControlInput)

    return tuple(
        ControlChange(
            elapsed_s=first_elapsed_s + index * spacing_s,
            sample_index=round((first_elapsed_s + index * spacing_s) / SIMULATION_STEP_S),
            adjustment=index + 1,
            control=controls[index % len(controls)],
            previous_value=1.0,
            new_value=2.0,
            unit="L/min",
        )
        for index in range(count)
    )


def _mounted_view(
    start: int = SATURATED_SAMPLE_COUNT // 2, control_timeline: tuple[ControlChange, ...] = ()
) -> tuple[SimulationView, Session, _RecordingConnection]:
    """Mount the dashboard on a real session with a client already registered.

    Args:
        start: How many recorded samples the run has produced when the
            dashboard is built. The default saturates the visible window, so
            decimation is active and the drawn count holds steady.
        control_timeline: Recorded control changes the run carries, which
            the chart draws marks for. Empty by default, since most of
            these tests are about the traces.
    """

    connection = _RecordingConnection()
    session = Session(connection)
    controller = _ReplayController(
        _recorded_run(SATURATED_SAMPLE_COUNT), start=start, control_timeline=control_timeline
    )
    view = SimulationView(page=session.page, controller=controller)
    view.mount()

    # What the client is sent when it first registers. Encoding it is what
    # puts the session into the state an incremental patch is computed from.
    _encode(session.get_page_patch())
    connection.messages.clear()

    return view, session, connection


def _wash_in_drawn(view: SimulationView) -> int:
    """How many points the wash-in ratio is drawing, across every segment.

    The trace is a pool of segments rather than one series, because it
    breaks wherever the ratio leaves its domain, so "how long is it" is a
    sum over the pool. The runs these tests replay stay inside the domain
    throughout, so in practice one segment holds all of it.
    """

    return sum(len(series.points) for series in view._wash_in_segment_series)


def _patch_operations(connection: _RecordingConnection) -> list[list[Any]]:
    """Every operation in every control patch the client was sent."""

    operations: list[list[Any]] = []

    for message in connection.messages:
        if message.action is not ClientAction.PATCH_CONTROL:
            continue
        assert isinstance(message.body, PatchControlBody)
        # patch[0] is the tree index the operations address; the rest are the
        # operations themselves.
        operations.extend(message.body.patch[1:])

    return operations


def test_a_frame_of_moved_points_reaches_the_client() -> None:
    """The whole point of PL-010: mutation is patched, not silently dropped."""

    view, session, connection = _mounted_view()

    before = [(point.x, point.y) for point in view._circuit_series.points]
    assert len(before) > 4, "expected a decimated trace, not a handful of samples"

    view._refresh_view()
    session.page.update()

    after = [(point.x, point.y) for point in view._circuit_series.points]
    moved = {y for (_, y), (_, previous_y) in zip(after, before, strict=True) if y != previous_y}
    assert moved, "the replayed run did not move the trace; the test proves nothing"

    replaced_y = {
        operation[3]
        for operation in _patch_operations(connection)
        if operation[0] is Operation.Replace and operation[2] == "y"
    }

    assert moved <= replaced_y


def test_a_steady_trace_length_is_patched_without_replacing_any_point() -> None:
    """Reuse, stated as the wire behavior rather than as object identity.

    Rebuilding the points would send the client a new control for each drawn
    sample every frame. This is the assertion that PL-010's saving is real
    for the client too, not only for the Python process.
    """

    view, session, connection = _mounted_view()
    drawn = len(view._circuit_series.points)

    view._refresh_view()
    session.page.update()

    assert len(view._circuit_series.points) == drawn

    operations = _patch_operations(connection)
    assert operations, "the frame sent nothing at all"
    assert all(operation[0] is Operation.Replace for operation in operations)


def test_a_shorter_trace_removes_the_points_it_no_longer_draws() -> None:
    """A buffer that only ever grew would redraw samples the run has left.

    Points beyond the drawn count are not merely wasted payload: they are
    the *previous* frame's samples, still carrying their own time and value,
    and the chart would draw them as part of the current trace.
    """

    view, session, connection = _mounted_view()
    # Saturated, but not at an exact count, and bounded in points rather
    # than columns: the width ladder that keeps the selection stable
    # (PL-Q197) spends somewhere between half the budget and all of it, and
    # each column it does spend contributes between two and four of M4's
    # tuples. Pinning the number would assert the ladder's rung and the
    # trace's shape rather than the buffer behavior under test.
    drawn_when_saturated = len(view._circuit_series.points)
    assert (
        CHART_COLUMN_BUDGET_PER_SERIES <= drawn_when_saturated <= 4 * CHART_COLUMN_BUDGET_PER_SERIES
    )

    # A run that has only just started draws every recorded sample, so the
    # trace is far shorter than the saturated one already on screen.
    view._controller = _ReplayController(_recorded_run(12), start=12)  # type: ignore[assignment]
    view._refresh_view()
    session.page.update()

    assert len(view._circuit_series.points) == 12
    assert view._circuit_series.points[-1].x == pytest.approx(11 * SIMULATION_STEP_S)

    removals = [
        operation for operation in _patch_operations(connection) if operation[0] is Operation.Remove
    ]
    assert removals, "the client was left holding the points the view stopped drawing"


def test_a_longer_trace_adds_the_points_it_has_gained() -> None:
    """The mirror of the shrink case: a growing run must reach the client."""

    view, session, connection = _mounted_view(start=12)
    drawn_at_mount = len(view._circuit_series.points)
    wash_in_at_mount = _wash_in_drawn(view)
    assert drawn_at_mount < CHART_COLUMN_BUDGET_PER_SERIES

    view._controller = _ReplayController(  # type: ignore[assignment]
        _recorded_run(SATURATED_SAMPLE_COUNT), start=SATURATED_SAMPLE_COUNT // 2
    )
    view._refresh_view()
    session.page.update()

    drawn_now = len(view._circuit_series.points)
    assert CHART_COLUMN_BUDGET_PER_SERIES <= drawn_now <= 4 * CHART_COLUMN_BUDGET_PER_SERIES

    additions = [
        operation for operation in _patch_operations(connection) if operation[0] is Operation.Add
    ]
    # One addition per trace per point gained: six compartment traces, plus
    # the wash-in ratio, which is drawn from the same recorded run and grows
    # with it but is decimated on its own and so gains its own count.
    assert len(additions) == 6 * (drawn_now - drawn_at_mount) + (
        _wash_in_drawn(view) - wash_in_at_mount
    )


def _ops_per_frame(
    view: SimulationView, session: Session, connection: _RecordingConnection, frames: int
) -> list[int]:
    """Patch operations the client is sent, one entry per render frame."""

    counts: list[int] = []

    for _ in range(frames):
        connection.messages.clear()
        view._refresh_view()
        session.page.update()
        counts.append(len(_patch_operations(connection)))

    return counts


def test_a_growing_run_does_not_grow_the_traffic_it_sends() -> None:
    """PL-Q197's regression guard, in the units that actually saturated.

    What pegged the Flutter client was not the amount of data - about 50 kB
    a frame, which is nothing - but the number of discrete control mutations
    it had to decode, route and repaint: roughly 2 700 per frame once
    decimation engaged, 13 500 a second at `RENDER_INTERVAL_S`. Python was
    under half a core throughout, which is why the process that looked busy
    was the wrong one.

    A steady frame past that threshold now moves the newest bucket and the
    final sample and nothing else. The bound below is generous against the
    ~20 observed, and still an order of magnitude under the broken
    behavior, so it fails on a regression rather than on noise.
    """

    view, session, connection = _mounted_view(start=600)

    counts = _ops_per_frame(view, session, connection, frames=40)

    assert max(counts) <= 80, f"a frame sent {max(counts)} operations"


def test_a_scrolling_window_rebuilds_only_at_a_bucket_boundary() -> None:
    """Past `MAX_CHART_WINDOW_S` the window slides, and that costs differently.

    A window of fixed length sliding along a fixed bucket grid spans
    alternately `k` and `k + 1` buckets, so the number of chosen samples has
    to change, and any change shifts every later point one position along a
    positional list. That rebuild is a floor rather than a defect; what
    matters is that it is confined to one frame per bucket width instead of
    happening on all of them.

    The median is therefore the statistic under test: it reads the ordinary
    frame, which the rebuild must not become. Before the selection was
    anchored, every frame here was a rebuild and the median was the same
    ~3 500 operations as the peak.
    """

    view, session, connection = _mounted_view(start=3100)

    counts = _ops_per_frame(view, session, connection, frames=40)

    assert median(counts) <= 60, f"the typical frame sent {median(counts)} operations"
    assert sum(counts) / len(counts) <= 400, "the amortized cost of rebuilding grew"


def _hide_traces(view: SimulationView, *quantities: RecordedQuantity) -> None:
    """Uncheck these compartments through their own controls, as a reader would."""

    for quantity in quantities:
        trace = view._trace(quantity)
        trace.checkbox.value = False
        handler = trace.checkbox.on_change
        assert handler is not None
        handler(ft.Event(name="change", control=trace.checkbox))


def test_hiding_a_trace_takes_its_points_off_the_client() -> None:
    """`PL-CG7J`'s "removes rather than blanks", asserted on the wire.

    A unit test can see the series leave `data_series`; only this can see
    the *client* told to drop it. The distinction is the whole mechanism: a
    trace left in place with an empty point list would still be a control
    the client holds, diffs and repaints, and - worse - one no longer being
    redrawn, sitting on the chart with whatever frame it was last drawn in.
    """

    view, session, connection = _mounted_view(start=600)
    view._refresh_view()
    session.page.update()
    connection.messages.clear()

    _hide_traces(view, RecordedQuantity.MUSCLE, RecordedQuantity.FAT)

    removals = [
        operation for operation in _patch_operations(connection) if operation[0] is Operation.Remove
    ]
    assert len(removals) == 2, "the client was left holding the hidden traces"


def test_hiding_traces_cuts_what_a_frame_sends() -> None:
    """The render-cost half of `PL-CG7J`, measured rather than argued.

    What reaches the client each frame is about two patch operations per
    drawn point whose chosen sample moved (`PL-Q197`), so a frame's cost is
    linear in the traces drawn and hiding four of six should take a visible
    bite out of it. Unlike every other lever on this number - fewer points, a
    coarser bucket - it costs no resolution: a trace nobody is looking at is
    not a fidelity loss.

    Asserted as a reduction against the same view rather than as an absolute.
    The absolute is what the two tests above are for, and a second copy of it
    here would fail on their subject rather than on this one. The bound is
    one operation per hidden trace against the nine observed, so it fails on
    a frame that went back to redrawing hidden traces and not on noise: the
    wash-in plot and both references are unaffected by any of this and are
    most of what is left.
    """

    view, session, connection = _mounted_view(start=600)
    with_all_six = median(_ops_per_frame(view, session, connection, frames=20))

    hidden = (
        RecordedQuantity.CIRCUIT,
        RecordedQuantity.MIXED_VENOUS,
        RecordedQuantity.VESSEL_RICH,
        RecordedQuantity.FAT,
    )
    _hide_traces(view, *hidden)

    with_two = median(_ops_per_frame(view, session, connection, frames=20))

    assert with_two <= with_all_six - len(hidden), (
        f"a frame sent {with_two} operations with two traces drawn against {with_all_six} with six"
    )


def test_a_run_full_of_control_marks_costs_a_frame_nothing_extra() -> None:
    """The mark pool is fixed, so a marked run must cost what an unmarked one does.

    The two tests above run with no recorded changes, which measures the
    marks only in their parked state - and parking was where the first
    regression was: relative to the moving window, it rewrote both points of
    all 24 marks on every frame of a scrolling run. Drawn marks are the
    other half, and they are the half a real teaching run has. A mark sits
    at a fixed simulated time and spans a range that moves only with the
    agent, so a steady frame must send nothing for it; this fails if one
    ever comes to be recomputed per frame.
    """

    marked = _mounted_view(
        start=3100,
        control_timeline=_control_timeline(MAX_CHART_CONTROL_MARKS, 30.0, spacing_s=11.0),
    )
    unmarked = _mounted_view(start=3100)

    drawn = [
        series
        for series in marked[0]._control_mark_series
        if series.points[0].x != PARKED_CONTROL_MARK_X
    ]
    assert len(drawn) == MAX_CHART_CONTROL_MARKS, (
        f"only {len(drawn)} of {MAX_CHART_CONTROL_MARKS} marks landed inside the window, "
        "so this measures a pool that is mostly parked"
    )

    marked_counts = _ops_per_frame(*marked, frames=40)
    unmarked_counts = _ops_per_frame(*unmarked, frames=40)

    assert median(marked_counts) <= median(unmarked_counts), (
        f"a full mark pool cost the typical frame "
        f"{median(marked_counts) - median(unmarked_counts)} extra operations"
    )
