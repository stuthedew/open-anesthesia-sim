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

from anesthesia_sim.app.chart_series import MAX_CHART_POINTS_PER_SERIES
from anesthesia_sim.app.controller import SimulationHistorySample, SimulationSnapshot
from anesthesia_sim.app.simulation_view import RENDER_INTERVAL_S, SIMULATION_STEP_S, SimulationView
from anesthesia_sim.core.parameters import load_agent_parameters

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
    """Serve snapshots from a recorded run, one render tick per call."""

    def __init__(self, samples: tuple[SimulationHistorySample, ...], start: int) -> None:
        self._samples = samples
        self._cursor = start
        self.is_running = True

    def snapshot(self) -> SimulationSnapshot:
        history = self._samples[: self._cursor]
        self._cursor += SAMPLES_PER_RENDER_TICK
        latest = history[-1]

        return SimulationSnapshot(
            is_running=True,
            elapsed_s=latest.elapsed_s,
            agent_id="sevoflurane",
            agent_display_name="Sevoflurane",
            max_delivered_concentration_percent=8.0,
            agent_mac_percent=2.0,
            agent_mac_awake=load_agent_parameters("sevoflurane").mac_awake,
            circuit_volume_l=6.0,
            fresh_gas_flow_l_min=4.0,
            delivered_concentration_fraction=0.08,
            alveolar_ventilation_l_min=4.0,
            cardiac_output_l_min=5.0,
            circuit_concentration_fraction=latest.circuit_concentration_fraction,
            alveolar_concentration_fraction=latest.alveolar_concentration_fraction,
            mixed_venous_concentration_fraction=latest.mixed_venous_concentration_fraction,
            vessel_rich_partial_pressure_fraction=latest.vessel_rich_partial_pressure_fraction,
            muscle_partial_pressure_fraction=latest.muscle_partial_pressure_fraction,
            fat_partial_pressure_fraction=latest.fat_partial_pressure_fraction,
            delivered_agent_l=0.012345,
            exhausted_agent_l=0.002345,
            stored_agent_l=0.01,
            unaccounted_agent_l=1.5e-13,
            agent_accounting_absolute_error_l=1.5e-13,
            agent_accounting_passes_validation=True,
            concentration_history=history,
            failure_reason=None,
        )


def _recorded_run(sample_count: int) -> tuple[SimulationHistorySample, ...]:
    """A monotone wash-in whose six traces never coincide."""

    return tuple(
        SimulationHistorySample(
            elapsed_s=index * SIMULATION_STEP_S,
            circuit_concentration_fraction=0.080 * (1.0 - 0.999**index),
            alveolar_concentration_fraction=0.070 * (1.0 - 0.998**index),
            mixed_venous_concentration_fraction=0.050 * (1.0 - 0.997**index),
            vessel_rich_partial_pressure_fraction=0.060 * (1.0 - 0.996**index),
            muscle_partial_pressure_fraction=0.030 * (1.0 - 0.995**index),
            fat_partial_pressure_fraction=0.010 * (1.0 - 0.994**index),
        )
        for index in range(sample_count)
    )


def _mounted_view(
    start: int = SATURATED_SAMPLE_COUNT // 2,
) -> tuple[SimulationView, Session, _RecordingConnection]:
    """Mount the dashboard on a real session with a client already registered.

    Args:
        start: How many recorded samples the run has produced when the
            dashboard is built. The default saturates the visible window, so
            decimation is active and the drawn count holds steady.
    """

    connection = _RecordingConnection()
    session = Session(connection)
    controller = _ReplayController(_recorded_run(SATURATED_SAMPLE_COUNT), start=start)
    view = SimulationView(page=session.page, controller=controller)
    view.mount()

    # What the client is sent when it first registers. Encoding it is what
    # puts the session into the state an incremental patch is computed from.
    _encode(session.get_page_patch())
    connection.messages.clear()

    return view, session, connection


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
    # Saturated, but not at an exact count: the width ladder that keeps the
    # selection stable (PL-Q197) spends somewhere between half the budget and
    # all of it, so pinning the number would assert the ladder's rung rather
    # than the buffer behavior under test.
    drawn_when_saturated = len(view._circuit_series.points)
    assert MAX_CHART_POINTS_PER_SERIES // 2 <= drawn_when_saturated <= MAX_CHART_POINTS_PER_SERIES

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
    assert drawn_at_mount < MAX_CHART_POINTS_PER_SERIES

    view._controller = _ReplayController(  # type: ignore[assignment]
        _recorded_run(SATURATED_SAMPLE_COUNT), start=SATURATED_SAMPLE_COUNT // 2
    )
    view._refresh_view()
    session.page.update()

    drawn_now = len(view._circuit_series.points)
    assert MAX_CHART_POINTS_PER_SERIES // 2 <= drawn_now <= MAX_CHART_POINTS_PER_SERIES

    additions = [
        operation for operation in _patch_operations(connection) if operation[0] is Operation.Add
    ]
    # One addition per trace per point gained, across all six traces.
    assert len(additions) == 6 * (drawn_now - drawn_at_mount)


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
