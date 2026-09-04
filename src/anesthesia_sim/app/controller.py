"""SimulationController: the boundary between the UI and the scientific
core. Owns run/pause/reset state, applies user-facing settings to the
core, and exposes read-only `SimulationSnapshot`s for the view to render.
Contains no physiological calculations of its own, and holds no default
values of its own: every unspecified setting comes from the core, which
builds it from the versioned data files.
"""

from array import array
from bisect import bisect_right
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Final, Self

from anesthesia_sim.app.chart_downsampling import M4AggregateCache, first_index_at_or_after
from anesthesia_sim.app.wash_in import is_wash_in, wash_in_ratio
from anesthesia_sim.core.exceptions import SimulationExecutionError
from anesthesia_sim.core.parameters import MacAwakeReference, load_agent_parameters
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


class ControlInput(StrEnum):
    """A setting the user can change during a run, under a stable identifier.

    The *value* of each member is what a recorded run stores, so it is
    chosen from the domain rather than from whatever the accessor happens
    to be called this release. `PL-9SH6` and `PL-3TLK` rename two of the
    forwarding setters in v0.4.1 - `set_delivered_concentration` becomes a
    `_partial_pressure_fraction` form, and the circuit fraction becomes
    `inspired_` - and a timeline that had stored accessor names would carry
    retired ones in the history of every run recorded before the rename.
    The member names may follow the code; the strings may not.

    `DELIVERED` is the vaporizer dial: the concentration delivered into the
    circuit, which is not the same quantity as the inspired concentration
    the circuit reaches. Naming it for the dial would have tied it to one
    machine's control rather than to the quantity the model applies.
    """

    FRESH_GAS_FLOW = "fresh_gas_flow"
    DELIVERED = "delivered"
    ALVEOLAR_VENTILATION = "alveolar_ventilation"
    CARDIAC_OUTPUT = "cardiac_output"
    CIRCUIT_VOLUME = "circuit_volume"


# The unit each control's recorded values are in, declared once and carried
# onto every entry that records one. Two properties are wanted at the same
# time and neither alone is enough: a single table is auditable at a glance
# and cannot drift between the recorder and the reader (the reason
# `chart_series.PlottedSeries` is one table rather than six call sites),
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
    ControlInput.CIRCUIT_VOLUME: "L",
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
    sample_index: int
    """Index into the run's recorded history the change took effect at.

    The change applies to every step computed *after* this sample, so this
    is the last sample recorded under the previous value. It is stored
    rather than derived from `elapsed_s` because the two must not be able
    to disagree: a mark placed on the chart from a recomputed index would
    drift from the sample the model actually changed at.
    """
    adjustment: int
    """Which user adjustment this change belongs to. See the class docstring."""
    control: ControlInput
    previous_value: float
    new_value: float
    unit: str
    """The unit both values are in, from `CONTROL_INPUT_UNITS`."""


@dataclass(frozen=True, slots=True)
class SimulationHistorySample:
    """Read-only concentrations recorded at one simulation time."""

    elapsed_s: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float


class RecordedQuantity(StrEnum):
    """One quantity a run records for every sample, under a stable identifier.

    A run keeps its samples *by quantity* rather than by instant, and this
    is the key into that. Members are named for the compartment or the
    quantity rather than for whichever field or accessor currently spells
    it, for the reason `ControlInput`'s are: `PL-9SH6` and `PL-3TLK` rename
    two of the fields these read from, and a key that had followed the code
    would have to be renamed with them while meaning the same thing
    throughout.

    `WASH_IN_RATIO` is the one derived member. It is not a compartment
    state but the quotient `app/wash_in.py` specifies, recorded alongside
    the states it is formed from so that the plot drawing it is summarized
    the same way every other trace is, and so that the stretches where it
    is undefined are recorded as undefined once rather than reconstructed
    on every frame.
    """

    CIRCUIT = "circuit"
    ALVEOLAR = "alveolar"
    MIXED_VENOUS = "mixed_venous"
    VESSEL_RICH = "vessel_rich"
    MUSCLE = "muscle"
    FAT = "fat"
    WASH_IN_RATIO = "wash_in_ratio"


class RunHistory:
    """Every sample a run has recorded, kept by quantity and summarized as it grows.

    The chart's read side. A run's history grows for as long as the
    simulation advances, while a chart draws a bounded window of it at a
    few hundred columns, so what this class exists to make cheap is
    answering *which samples does this window draw* without touching the
    samples it does not.

    **Stored by quantity, not by instant.** Every recorded sample used to
    be one `SimulationHistorySample`, which is the right shape for the one
    row a readout formats and the wrong one for a trace: drawing six traces
    meant walking the whole visible window six times to pull one field out
    of each row. Here each quantity is its own
    `chart_downsampling.M4AggregateCache`, which holds the values *and* the
    dyadic ladder of M4 aggregates over them, so a window is read as a few
    hundred cached aggregates whatever its width. `sample()` rebuilds a row
    where one is wanted.

    **Append-only, and that is load-bearing.** A completed aggregate is
    final, and every read is bounded by an explicit stop index, so a window
    handed out here cannot change underneath the caller as the run
    advances. That is what removes the copy the window used to make: the
    hazard it guarded against - one trace drawn half from one instant and
    half from the next - is closed by the structure instead
    (`chart_downsampling.M4AggregateCache`).

    The wash-in stretches are maintained here for the same reason the
    aggregates are. Which samples lie inside `app/wash_in.py`'s domain is a
    property of the run rather than of the frame, so it is decided once as
    each sample arrives; recomputing it per frame was a second pass over
    the whole visible window.
    """

    __slots__ = ("_elapsed_s", "_quantities", "_wash_in_starts", "_wash_in_stops")

    def __init__(self) -> None:
        self._elapsed_s = array("d")
        self._quantities = {quantity: M4AggregateCache() for quantity in RecordedQuantity}
        # Maximal stretches of consecutive samples inside the wash-in
        # domain, as parallel start and stop lists so the newest stretch
        # can be extended in place. Both are ascending, which is what lets
        # `wash_in_stretches` find a window's own by binary search.
        self._wash_in_starts: list[int] = []
        self._wash_in_stops: list[int] = []

    @classmethod
    def of(cls, samples: Iterable[SimulationHistorySample]) -> Self:
        """Build a history holding a run that has already been recorded.

        For a test or a caller replaying a stored run. A live run is built
        by `record` as it advances, which is the path that has to stay
        cheap.
        """

        history = cls()

        for sample in samples:
            history.record(sample)

        return history

    def __len__(self) -> int:
        """How many samples the run has recorded."""

        return len(self._elapsed_s)

    def record(self, sample: SimulationHistorySample) -> None:
        """Add one recorded sample, and everything derived from it.

        The single place a sample enters the run, listing every quantity
        explicitly rather than reflecting over the sample's fields: a trace
        drawn from another compartment's values would misstate the run as
        surely as a wrong number would, so the mapping is written where a
        reader can audit it at a glance.
        `tests/integration/test_controller.py` holds it against the samples
        `sample()` reads back.

        Args:
            sample: The concentrations recorded at one simulation time.
                Its time must not precede the previous sample's.
        """

        index = len(self._elapsed_s)
        self._elapsed_s.append(sample.elapsed_s)
        quantities = self._quantities
        quantities[RecordedQuantity.CIRCUIT].record(sample.circuit_concentration_fraction)
        quantities[RecordedQuantity.ALVEOLAR].record(sample.alveolar_concentration_fraction)
        quantities[RecordedQuantity.MIXED_VENOUS].record(sample.mixed_venous_concentration_fraction)
        quantities[RecordedQuantity.VESSEL_RICH].record(
            sample.vessel_rich_partial_pressure_fraction
        )
        quantities[RecordedQuantity.MUSCLE].record(sample.muscle_partial_pressure_fraction)
        quantities[RecordedQuantity.FAT].record(sample.fat_partial_pressure_fraction)

        ratio = wash_in_ratio(
            sample.alveolar_concentration_fraction, sample.circuit_concentration_fraction
        )
        wash_in = quantities[RecordedQuantity.WASH_IN_RATIO]

        if ratio is None:
            # Rule 1 of `app/wash_in.py`: no agent in the circuit yet, so
            # the quotient has no value the interface may show. Recorded as
            # undefined rather than as a substituted zero, which is what
            # keeps the trace broken there instead of drawing a line the
            # run never produced.
            wash_in.record_undefined()
        else:
            wash_in.record(ratio)

        self._extend_wash_in_stretches(index, ratio)

    def elapsed_s(self, index: int) -> float:
        """Simulated time of one recorded sample, in seconds."""

        return self._elapsed_s[index]

    def times_s(self) -> Sequence[float]:
        """Every recorded sample time, ascending. Read-only to callers."""

        return self._elapsed_s

    def aggregates(self, quantity: RecordedQuantity) -> M4AggregateCache:
        """The values and M4 aggregates of one quantity over the whole run."""

        return self._quantities[quantity]

    def sample(self, index: int) -> SimulationHistorySample:
        """Rebuild one recorded sample as a row.

        The inverse of `record`, and deliberately not the shape anything on
        the render path uses: a trace wants one quantity over many samples,
        which `aggregates` answers without building a row at all.
        """

        return SimulationHistorySample(
            elapsed_s=self._elapsed_s[index],
            circuit_concentration_fraction=self.value(RecordedQuantity.CIRCUIT, index),
            alveolar_concentration_fraction=self.value(RecordedQuantity.ALVEOLAR, index),
            mixed_venous_concentration_fraction=self.value(RecordedQuantity.MIXED_VENOUS, index),
            vessel_rich_partial_pressure_fraction=self.value(RecordedQuantity.VESSEL_RICH, index),
            muscle_partial_pressure_fraction=self.value(RecordedQuantity.MUSCLE, index),
            fat_partial_pressure_fraction=self.value(RecordedQuantity.FAT, index),
        )

    def value(self, quantity: RecordedQuantity, index: int) -> float:
        """One quantity's recorded value at one sample."""

        return self._quantities[quantity].value(index)

    def wash_in_stretches(self, start: int, stop: int) -> list[tuple[int, int]]:
        """The wash-in domain's maximal stretches, clipped to `[start, stop)`.

        A stretch is a run of consecutive samples whose F_A/F_I quotient is
        inside the domain `app/wash_in.py` states. The chart draws one line
        per stretch rather than one line through every in-domain sample,
        because a single polyline would join across the samples it skipped
        and draw values the run never produced.

        Found by binary search over the stretches recorded so far, so the
        cost is a property of how many stretches the window contains rather
        than of how many samples it spans.

        Args:
            start: First position of the window, absolute within the run.
            stop: One past the window's last position.

        Returns:
            One `(start, stop)` pair per stretch the window overlaps,
            oldest first, each already clipped to the window.
        """

        stretches: list[tuple[int, int]] = []

        for position in range(bisect_right(self._wash_in_stops, start), len(self._wash_in_starts)):
            stretch_start = self._wash_in_starts[position]

            if stretch_start >= stop:
                break

            stretches.append((max(stretch_start, start), min(self._wash_in_stops[position], stop)))

        return stretches

    def window_from(self, start_s: float) -> HistoryWindow:
        """The window of this run at or after `start_s`.

        Located by binary search, so finding the window costs the same on a
        week-long run as on a minute-long one.
        """

        return HistoryWindow(
            run=self,
            index_offset=first_index_at_or_after(self._elapsed_s, start_s),
            stop_index=len(self._elapsed_s),
        )

    def _extend_wash_in_stretches(self, index: int, ratio: float | None) -> None:
        """Place one sample in the wash-in domain's stretches, or in none.

        Both of `app/wash_in.py`'s rules are applied here and nowhere else
        on the chart's path: a sample with no quotient fails rule 1, and one
        above equilibrium fails rule 2. Either ends the stretch in progress.
        """

        if ratio is None or not is_wash_in(ratio):
            return

        if self._wash_in_stops and self._wash_in_stops[-1] == index:
            self._wash_in_stops[-1] = index + 1

            return

        self._wash_in_starts.append(index)
        self._wash_in_stops.append(index + 1)


@dataclass(frozen=True, slots=True)
class HistoryWindow:
    """The part of a run one frame draws, as a bounded range over its history.

    What `SimulationController.history_window` answers with, and the whole
    of what the chart is drawn from. A run's history grows for as long as
    the simulation advances; a window is the bounded part of it a display
    can actually show, so handing over a window rather than the run keeps
    the cost of a frame a property of the visible axis rather than of how
    long the simulation has been running.

    It is a *range*, not a copy. Nothing inside `[index_offset, stop_index)`
    can change once those two numbers are fixed - `RunHistory` is
    append-only and its aggregates are final once complete - so the
    stale-state hazard the copy used to guard against, one trace drawn half
    from one instant and half from the next, is closed by the structure
    rather than by copying the samples out.
    """

    run: RunHistory
    """The run this window is a range over."""

    index_offset: int
    """Absolute index, within the whole recorded run, of the window's first sample.

    Carried because decimation anchors its buckets to the run rather than
    to the window: a selection re-derived from the window's own length
    rebuckets on every frame and rewrites every drawn point, which is what
    `chart_downsampling.py`'s docstring records the cost of.
    """

    stop_index: int
    """One past the absolute index of the window's last sample."""

    @property
    def sample_count(self) -> int:
        """How many recorded samples fall inside the window."""

        return self.stop_index - self.index_offset

    @property
    def samples(self) -> tuple[SimulationHistorySample, ...]:
        """The window's samples as rows, oldest first.

        Builds every row, so it costs the window's width. Nothing on the
        render path uses it - a trace reads one quantity through
        `RunHistory.aggregates` instead - and it is here for the callers
        that genuinely want a recorded instant.
        """

        return tuple(self.run.sample(index) for index in range(self.index_offset, self.stop_index))


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    elapsed_s: float
    agent_id: str
    agent_display_name: str
    max_delivered_concentration_percent: float
    agent_mac_percent: float
    """The running agent's 1 MAC, as a percent of one atmosphere.

    Exposed because the interface displays every compartment in multiples
    of it as well as in percent, so it is the divisor of a clinically
    meaningful displayed value rather than only the starting position of
    the vaporizer dial. It travels in the snapshot, beside the
    concentrations it scales and the agent it belongs to, so a readout
    cannot be produced from one agent's concentration and another agent's
    MAC — which would be the correct number under the wrong label that
    `CLAUDE.md` treats as a safety failure.

    `docs/MODEL.md` § "MAC multiples as a display unit" states what the
    quotient asserts, and § "Delivery-limit and MAC parameters" holds the
    value's provenance.
    """
    agent_mac_awake: MacAwakeReference
    """The running agent's population MAC-awake, as a fraction of its MAC.

    Travels whole rather than as two loose floats, and beside
    `agent_mac_percent` for the same reason that field gives: the chart's
    reference band is `fraction_of_mac` times that divisor, so pairing one
    agent's MAC-awake with another agent's MAC would draw a correct number
    at the wrong height on a labelled axis.

    The interface reads it, `core/` does not: no governing equation consumes
    MAC-awake, exactly as none consumes `mac_percent`. `docs/MODEL.md`
    § "MAC-awake as a chart reference" states what the band asserts, which
    trace it is read against, and why it is not a time to wake-up.
    """
    circuit_volume_l: float
    fresh_gas_flow_l_min: float
    delivered_concentration_fraction: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float
    delivered_agent_l: float
    exhausted_agent_l: float
    stored_agent_l: float
    unaccounted_agent_l: float
    agent_accounting_absolute_error_l: float
    agent_accounting_passes_validation: bool
    control_timeline: tuple[ControlChange, ...]
    """Every setting change this run has seen, oldest first.

    Empty for a run nobody has touched, and cleared with the rest of the
    run by `reset()` and by a change of agent. A setting the core refused
    is absent: it never took effect, so it is not part of the run.
    """
    failure_reason: str | None
    """Why the run stopped abnormally, or `None` if it did not.

    A non-`None` value means a step or a setting raised and the session is
    halted: `is_running` is `False`, but this is not the same state as a
    user pause, and the interface must not present it as one.

    Every other field in this snapshot is nonetheless a completed step's.
    `AgentUptakeSystem.advance()` rolls a failed step back, and elapsed
    time advances only after it returns, so a halted session reports the
    last step that finished — at the simulation time it finished at —
    rather than one abandoned partway through.
    """


class SimulationController:
    """Own run controls and read-only history for one app session."""

    def __init__(
        self,
        agent_id: str = "sevoflurane",
        circuit_volume_l: float | None = None,
        fresh_gas_flow_l_min: float | None = None,
        delivered_concentration_fraction: float | None = None,
        alveolar_ventilation_l_min: float | None = None,
        cardiac_output_l_min: float | None = None,
    ) -> None:
        """Build a session, taking every unspecified setting from the core.

        Each argument is an explicit override. `None` means "use the value
        the core built from the versioned data files" — the reference
        patient's cited alveolar ventilation and cardiac output, the
        circuit's own volume and fresh gas flow, and the agent's own 1 MAC.
        The controller holds no copy of those defaults, so correcting a
        cited value in a data file changes what the app actually runs.
        """

        self._is_running = False
        self._failure_reason: str | None = None
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=circuit_volume_l,
            fresh_gas_flow_l_min=fresh_gas_flow_l_min,
            delivered_concentration_fraction=delivered_concentration_fraction,
            alveolar_ventilation_l_min=alveolar_ventilation_l_min,
            cardiac_output_l_min=cardiac_output_l_min,
        )

    def _build_state(
        self,
        agent_id: str,
        circuit_volume_l: float | None,
        fresh_gas_flow_l_min: float | None,
        delivered_concentration_fraction: float | None,
        alveolar_ventilation_l_min: float | None,
        cardiac_output_l_min: float | None,
    ) -> None:
        """(Re)build dynamic state from scratch for a chosen agent.

        Every argument is an override applied on top of the state
        `AgentUptakeSystem.for_agent()` already built from the data files;
        a `None` leaves that data-file value in place, including the
        agent's own 1 MAC delivered concentration. A requested delivered
        concentration above the agent's real vaporizer maximum is rejected
        by the core rather than clamped here.
        """

        agent_parameters = load_agent_parameters(agent_id)
        uptake_system = AgentUptakeSystem.for_agent(agent_id)

        if circuit_volume_l is not None:
            uptake_system.circuit.set_circuit_volume(circuit_volume_l)

        if fresh_gas_flow_l_min is not None:
            uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)

        if delivered_concentration_fraction is not None:
            uptake_system.set_delivered_concentration(delivered_concentration_fraction)

        if alveolar_ventilation_l_min is not None:
            uptake_system.set_alveolar_ventilation(alveolar_ventilation_l_min)

        if cardiac_output_l_min is not None:
            uptake_system.set_cardiac_output(cardiac_output_l_min)

        self._agent_id = agent_id
        self._agent_display_name = agent_parameters.display_name
        self._max_delivered_concentration_percent = (
            agent_parameters.max_delivered_concentration_percent
        )
        self._agent_mac_percent = agent_parameters.mac_percent
        self._agent_mac_awake = agent_parameters.mac_awake
        self._state = SimulationState(uptake_system=uptake_system)
        self._history = RunHistory()
        self._history.record(self._build_history_sample())
        self._clear_control_timeline()

        # Every compartment above is newly constructed, so no state survives
        # from a run that failed: a stale failure reason would halt a
        # session that has nothing wrong with it.
        self._failure_reason = None

    def _clear_control_timeline(self) -> None:
        """Drop the recorded timeline, for a run that is starting over."""

        self._control_timeline: tuple[ControlChange, ...] = ()
        self._adjustment_count = 0
        self._open_adjustment_control: ControlInput | None = None
        self._open_adjustment = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def has_failed(self) -> bool:
        """Whether the session is halted by a failure rather than paused."""

        return self._failure_reason is not None

    def fail(self, reason: str) -> None:
        """Halt the session because something raised, recording why.

        Distinct from `pause()`, which is a user decision the run resumes
        from. A failure means a step or a setting raised, and while the
        core rolls a failed step back — so the state left behind is the
        last completed step rather than a partial one — resuming is still
        not offered. The run reached a state the model could not step
        from, so a resumed run would fail again on its first tick, and
        offering Start would present that as a working control. Only a
        fresh run clears it, via `reset()` or `set_agent()`.
        """

        self._is_running = False

        # The first failure is the one that explains the rest, so a later
        # raise (e.g. from the render loop reacting to the same broken
        # state) must not overwrite it.
        if self._failure_reason is None:
            self._failure_reason = reason

    def set_agent(self, agent_id: str) -> None:
        """Start fresh with a different agent at that agent's own 1 MAC.

        The delivered-concentration fraction is reset to the new agent's
        mac_percent rather than carrying over the old agent's raw percentage,
        since the same percent number corresponds to a different clinical
        depth for each agent (e.g. 2% is 1 MAC of sevoflurane but only about
        a third of a MAC of desflurane). Circuit, flow, ventilation, and
        cardiac output settings are preserved.

        Mid-run agent switching with residual washout accounting is a
        distinct, harder feature (see ROADMAP.md's anesthesia-machine
        milestone); this always begins a new run rather than attempting it.
        Because it begins a new run it also clears a failed session, the
        same way `reset()` does.
        """

        self.pause()
        current = self.snapshot()

        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=current.circuit_volume_l,
            fresh_gas_flow_l_min=current.fresh_gas_flow_l_min,
            delivered_concentration_fraction=None,
            alveolar_ventilation_l_min=current.alveolar_ventilation_l_min,
            cardiac_output_l_min=current.cardiac_output_l_min,
        )

    def snapshot(self) -> SimulationSnapshot:
        """Build a fresh, read-only view of current simulation state."""

        system = self._state.uptake_system
        circuit = system.circuit
        alveoli = system.alveoli
        patient = system.patient
        accounting = system.agent_simulation_validation

        return SimulationSnapshot(
            is_running=self._is_running,
            elapsed_s=self._state.elapsed_s,
            agent_id=self._agent_id,
            agent_display_name=self._agent_display_name,
            max_delivered_concentration_percent=(self._max_delivered_concentration_percent),
            agent_mac_percent=self._agent_mac_percent,
            agent_mac_awake=self._agent_mac_awake,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            delivered_concentration_fraction=(circuit.delivered_concentration_fraction),
            alveolar_ventilation_l_min=(alveoli.alveolar_ventilation_l_min),
            cardiac_output_l_min=patient.cardiac_output_l_min,
            circuit_concentration_fraction=(circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(patient.vessel_rich.partial_pressure_fraction),
            muscle_partial_pressure_fraction=(patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(patient.fat.partial_pressure_fraction),
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=(accounting.absolute_error_l),
            agent_accounting_passes_validation=(accounting.passes_validation),
            control_timeline=self._control_timeline,
            failure_reason=self._failure_reason,
        )

    def history_window(self, start_s: float) -> HistoryWindow:
        """The recorded samples at or after `start_s`, with their run offset.

        The read the render path makes, and deliberately not a field of
        `snapshot()`. A snapshot is the run's state at one instant, which is
        a fixed number of values however long the run; the history is the
        run itself. Carrying the history in the snapshot meant copying every
        sample ever recorded on every frame - work proportional to the run
        length, five times a second, with all but the visible few hundred
        samples discarded by the chart immediately (`PL-0VM7`). Asking for
        the window instead makes what crosses this boundary a property of
        the visible axis: at the chart's 300 s window and 0.1 s step, at
        most 3 001 samples, whether the run is a minute or a week old.

        `start_s` is the caller's own left edge rather than a span chosen
        here, so the samples handed over are exactly the ones that window
        can show. A cut this method made itself could fall inside the drawn
        window and truncate the trace, which would understate the run rather
        than merely slow it down - a plot beginning later than the run did,
        with nothing on it to say so.

        Located by binary search, so finding the window costs the same on a
        week-long run as on a minute-long one. A linear scan here would put
        the unbounded per-frame cost straight back, in the one place the
        change above was made to remove it.

        Args:
            start_s: Earliest simulated time to include, in seconds.
                Samples before it lie outside the caller's window and are
                not returned. A value at or below zero returns the whole
                recorded run.

        Returns:
            The samples at or after `start_s`, oldest first, paired with the
            absolute index within the run of the first of them.
        """

        return self._history.window_from(start_s)

    def start(self) -> None:
        """Start or resume the run, refusing to resume a failed session.

        Raising rather than quietly declining is deliberate: silently
        ignoring a start would leave the interface showing a stopped run
        with no indication that starting it did nothing, which is the
        hidden mode `CLAUDE.md` forbids.
        """

        if self._failure_reason is not None:
            raise SimulationExecutionError(
                f"cannot resume a failed simulation ({self._failure_reason}); reset it first"
            )

        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run, clear any failure, and clear dynamic state.

        Settings are preserved. This is the only way out of a failed
        session: every compartment goes back to its initial state, so
        nothing carries over from the run that could not continue.
        """

        self.pause()
        self._failure_reason = None
        self._state.reset()
        self._history = RunHistory()
        self._history.record(self._build_history_sample())
        self._clear_control_timeline()

    def set_circuit_volume(self, circuit_volume_l: float) -> None:
        """Change volume without creating or losing stored agent.

        The conservation and the capacity guard are the circuit's own
        (PL-006). This forwards because circuit volume is not one of the four
        live inputs `AgentUptakeSystem` exposes; it reaches the compartment
        that owns it, as the system's docstring says such a setting should.
        """

        circuit = self._state.uptake_system.circuit
        previous_value = circuit.circuit_volume_l
        circuit.set_circuit_volume(circuit_volume_l)
        self._record_control_change(
            ControlInput.CIRCUIT_VOLUME, previous_value, circuit.circuit_volume_l
        )

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.fresh_gas_flow_l_min
        self._state.uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)
        self._record_control_change(
            ControlInput.FRESH_GAS_FLOW, previous_value, circuit.fresh_gas_flow_l_min
        )

    def set_delivered_concentration(self, delivered_concentration_fraction: float) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.delivered_concentration_fraction
        self._state.uptake_system.set_delivered_concentration(delivered_concentration_fraction)
        self._record_control_change(
            ControlInput.DELIVERED, previous_value, circuit.delivered_concentration_fraction
        )

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: float) -> None:
        alveoli = self._state.uptake_system.alveoli
        previous_value = alveoli.alveolar_ventilation_l_min
        self._state.uptake_system.set_alveolar_ventilation(alveolar_ventilation_l_min)
        self._record_control_change(
            ControlInput.ALVEOLAR_VENTILATION, previous_value, alveoli.alveolar_ventilation_l_min
        )

    def set_cardiac_output(self, cardiac_output_l_min: float) -> None:
        patient = self._state.uptake_system.patient
        previous_value = patient.cardiac_output_l_min
        self._state.uptake_system.set_cardiac_output(cardiac_output_l_min)
        self._record_control_change(
            ControlInput.CARDIAC_OUTPUT, previous_value, patient.cardiac_output_l_min
        )

    def begin_control_adjustment(self) -> None:
        """Declare that the changes that follow are a new user adjustment.

        The interface calls this when a drag begins. Without it a slider
        dragged twice would be indistinguishable from one dragged once:
        both arrive as a run of changes to the same control, and only the
        input device knows where one act ended and the next began. Guessing
        it back from the timing of the entries would need a threshold, and
        no threshold survives the playback multiplier v0.4.0 adds - the same
        drag spans more simulated time the faster the run is played.

        It records nothing on its own and changes no simulation state: it
        only closes whichever adjustment is open, so the next change starts
        a new one. A change that arrives with no adjustment open - a
        keyboard press on a slider, a programmatic call, a test - therefore
        becomes an adjustment of its own, which is the honest reading of a
        single discrete input and the reason the grouping degrades safely
        rather than wrongly when this is never called.
        """

        self._open_adjustment_control = None

    def _record_control_change(
        self, control: ControlInput, previous_value: float, new_value: float
    ) -> None:
        """Record one setting change, after the core has accepted it.

        Called *after* the forwarding setter returns, which is what makes a
        refused setting record nothing: the core raises before this line is
        reached, the exception reaches the interface, and the run - which
        the core left untouched - keeps a timeline that says so.

        Both values are read off the compartment that holds them rather
        than taken from the caller's argument. The core rejects an
        out-of-range setting rather than clamping it, so the two are equal
        today - but a record of what was *asked for* would silently become
        a record of something the run never used the day that stopped being
        true, and this timeline's whole claim is that re-applying it
        reproduces the run.

        Two changes are deliberately not recorded, and both are cases where
        the model saw nothing:

        - a value equal to the one already in place, which a slider emits
          freely as a drag re-enters a position; and
        - a change superseded within the same simulation step. Only the
          value standing when `advance()` runs is integrated, so a dial
          moved from 2% to 3% to 4% between two steps is one change from 2%
          to 4% as far as the run is concerned. Collapsing them is what
          makes the timeline a record of the run rather than of the mouse -
          and if the collapse lands back on the value the step began with,
          the entry goes entirely, because nothing about the run differs.
        """

        if new_value == previous_value:
            return

        if control is not self._open_adjustment_control:
            self._adjustment_count += 1
            self._open_adjustment_control = control
            self._open_adjustment = self._adjustment_count

        sample_index = len(self._history) - 1

        if self._control_timeline:
            latest = self._control_timeline[-1]

            if latest.control is control and latest.sample_index == sample_index:
                if latest.previous_value == new_value:
                    self._control_timeline = self._control_timeline[:-1]
                    return

                self._control_timeline = (
                    *self._control_timeline[:-1],
                    replace(latest, new_value=new_value),
                )
                return

        self._control_timeline = (
            *self._control_timeline,
            ControlChange(
                elapsed_s=self._state.elapsed_s,
                sample_index=sample_index,
                adjustment=self._open_adjustment,
                control=control,
                previous_value=previous_value,
                new_value=new_value,
                unit=CONTROL_INPUT_UNITS[control],
            ),
        )

    def advance(self, simulation_step_s: float) -> None:
        """No-op while paused; otherwise advance state and record history."""

        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        self._history.record(self._build_history_sample())

    def _build_history_sample(self) -> SimulationHistorySample:
        system = self._state.uptake_system

        return SimulationHistorySample(
            elapsed_s=self._state.elapsed_s,
            circuit_concentration_fraction=(system.circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(system.alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(system.patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(
                system.patient.vessel_rich.partial_pressure_fraction
            ),
            muscle_partial_pressure_fraction=(system.patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(system.patient.fat.partial_pressure_fraction),
        )
