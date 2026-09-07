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
from types import MappingProxyType
from typing import Final, Self

from anesthesia_sim.app.chart_downsampling import M4AggregateCache, first_index_at_or_after
from anesthesia_sim.app.wash_in import is_wash_in, wash_in_ratio
from anesthesia_sim.core.exceptions import SimulationDomainLimitError, SimulationExecutionError
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


#: The quantities every recorded sample carries for each substance, in the
#: order the interface lists its compartments.
#:
#: Every `RecordedQuantity` except `WASH_IN_RATIO`, which is not a compartment
#: state: it is the quotient `RunHistory` forms from two of these as the sample
#: arrives, so a sample supplying one would present a derived value as a
#: recorded one. Written out rather than filtered from the enum, so that adding
#: a member forces a decision here instead of silently joining what a caller
#: must supply.
COMPARTMENT_QUANTITIES: Final = (
    RecordedQuantity.CIRCUIT,
    RecordedQuantity.ALVEOLAR,
    RecordedQuantity.MIXED_VENOUS,
    RecordedQuantity.VESSEL_RICH,
    RecordedQuantity.MUSCLE,
    RecordedQuantity.FAT,
)


@dataclass(frozen=True, slots=True)
class RecordedSeries:
    """One recorded trace: one substance's values for one quantity.

    The address of a series inside `RunHistory`, and what a chart trace is
    bound to. One value rather than two loose arguments, because the binding
    is a presentation-correctness property rather than a lookup convenience:
    a trace drawn from another substance's values misstates the run exactly
    as one drawn from another compartment's does, and a pair that travels
    together cannot be half-rebound. `app/chart_series.py`'s `PlottedSeries`
    carries it for that reason.
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
class SimulationHistorySample:
    """Read-only concentrations recorded at one simulation time, by substance.

    **Keyed by substance rather than by six flat named floats** (`PL-W3DD`).
    Every compartment state a run records belongs to some substance, and a
    record naming six of them flatly can hold exactly one: adding nitrous
    oxide to that shape would mean six more fields, six more places for a
    value to be paired with the wrong compartment, and a rewrite of whatever
    had been written against the flat form. Here a second substance is one
    more entry and no new name at all. The reshaping is done now, before the
    forking work of a later milestone writes its element-wise reproducibility
    proof against this record, so that the proof is written once against the
    shape it keeps.

    Its compartment keys are `RecordedQuantity`'s stable identifiers rather
    than field names, which is what keeps the record's shape independent of
    the naming pass v0.4.1 runs over the code that fills it.

    This record is the *row* form of a run. `RunHistory` stores by series
    instead, and rebuilds a row through `RunHistory.sample` where one is
    wanted; nothing on the render path builds one.

    Attributes:
        elapsed_s: Simulated time this sample was recorded at, in seconds.
            Flat because it belongs to the instant rather than to any one
            substance: two substances recorded together share it, and a
            per-substance time would let them disagree.
        substances: One entry per substance the run records, each holding
            exactly `COMPARTMENT_QUANTITIES` as fractions of one atmosphere.
            Both levels are wrapped read-only at construction, so a caller
            holding a sample cannot have its values changed underneath it.

    Raises:
        ValueError: If no substance is given, or a substance's entry does
            not carry exactly `COMPARTMENT_QUANTITIES`. Checked here rather
            than left to the reader: a missing compartment would otherwise
            surface as a `KeyError` with the run already half-recorded, and
            an unrecognised key would be dropped without a word.
    """

    elapsed_s: float
    substances: Mapping[str, Mapping[RecordedQuantity, float]]

    def __post_init__(self) -> None:
        if not self.substances:
            raise ValueError("a recorded sample must carry at least one substance")

        expected = frozenset(COMPARTMENT_QUANTITIES)
        recorded: dict[str, Mapping[RecordedQuantity, float]] = {}

        for substance_id, values in self.substances.items():
            if frozenset(values) != expected:
                raise ValueError(
                    f"substance {substance_id!r} must record exactly "
                    f"{sorted(expected)}, not {sorted(values)}"
                )

            recorded[substance_id] = MappingProxyType(dict(values))

        object.__setattr__(self, "substances", MappingProxyType(recorded))


class RunHistory:
    """Every sample a run has recorded, kept by series and summarized as it grows.

    The chart's read side. A run's history grows for as long as the
    simulation advances, while a chart draws a bounded window of it at a
    few hundred columns, so what this class exists to make cheap is
    answering *which samples does this window draw* without touching the
    samples it does not.

    **Stored by series, not by instant.** Every recorded sample used to
    be one `SimulationHistorySample`, which is the right shape for the one
    row a readout formats and the wrong one for a trace: drawing six traces
    meant walking the whole visible window six times to pull one field out
    of each row. Here each `RecordedSeries` - one substance's values for one
    quantity - is its own `chart_downsampling.M4AggregateCache`, which holds
    the values *and* the dyadic ladder of M4 aggregates over them, so a
    window is read as a few hundred cached aggregates whatever its width.
    `sample()` rebuilds a row where one is wanted.

    **Its substances are fixed when it is built** (`PL-W3DD`). A series
    that began part-way through a run would be shorter than the ones beside
    it while sharing their time axis, so every one of its values would be
    drawn at another sample's instant - a whole trace displaced, from data
    that is individually correct. `record` refuses a sample carrying any
    other set for that reason. One substance is recorded today, the agent
    the controller is running; a second is an entry rather than a change of
    shape.

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

    __slots__ = ("_elapsed_s", "_series", "_substances", "_wash_in_starts", "_wash_in_stops")

    def __init__(self, substances: Sequence[str]) -> None:
        """Build an empty history for the substances a run will record.

        Args:
            substances: Every substance this run records, in the order the
                run declares them. Fixed for the life of the history; see
                the class docstring for why.

        Raises:
            ValueError: If no substance is given, or one is named twice.
                A duplicate would collapse two series into one and record
                each sample's value over the other's.
        """

        if not substances:
            raise ValueError("a run must record at least one substance")

        if len(set(substances)) != len(substances):
            raise ValueError(f"a substance may be recorded once only, got {list(substances)}")

        self._substances = tuple(substances)
        self._elapsed_s = array("d")
        self._series = {
            substance_id: {quantity: M4AggregateCache() for quantity in RecordedQuantity}
            for substance_id in self._substances
        }
        # Maximal stretches of consecutive samples inside the wash-in
        # domain, per substance, as parallel start and stop lists so the
        # newest stretch can be extended in place. Both are ascending, which
        # is what lets `wash_in_stretches` find a window's own by binary
        # search. Per substance because the quotient is: F_A/F_I is formed
        # from one substance's own two fractions, so where it is defined is
        # a property of that substance's trace and not of the run.
        self._wash_in_starts: dict[str, list[int]] = {
            substance_id: [] for substance_id in self._substances
        }
        self._wash_in_stops: dict[str, list[int]] = {
            substance_id: [] for substance_id in self._substances
        }

    @classmethod
    def of(cls, samples: Iterable[SimulationHistorySample]) -> Self:
        """Build a history holding a run that has already been recorded.

        For a test or a caller replaying a stored run. A live run is built
        by `record` as it advances, which is the path that has to stay
        cheap.

        The run's substances are the first sample's, and `record` holds
        every later sample to them.

        Raises:
            ValueError: If `samples` is empty. A history's substances
                cannot be read from a run with no samples in it, and
                inventing an empty set would build a history that refuses
                the first sample recorded into it. Build one directly with
                `RunHistory(substances)` instead.
        """

        recorded = iter(samples)
        first = next(recorded, None)

        if first is None:
            raise ValueError("cannot read a run's substances from no samples")

        history = cls(tuple(first.substances))
        history.record(first)

        for sample in recorded:
            history.record(sample)

        return history

    @property
    def substances(self) -> tuple[str, ...]:
        """Every substance this run records, in the order it declares them."""

        return self._substances

    def __len__(self) -> int:
        """How many samples the run has recorded."""

        return len(self._elapsed_s)

    def record(self, sample: SimulationHistorySample) -> None:
        """Add one recorded sample, and everything derived from it.

        The single place a sample enters the run. Which value lands in which
        series is not decided here and cannot be got wrong here: the sample
        names every value by the substance and the compartment it belongs
        to, so the two pairings a misdrawn trace could come from - one
        compartment's values on another's line, one substance's on
        another's - are both made where the sample is built, in
        `SimulationController._build_history_sample`, one line per
        compartment. `tests/integration/test_controller.py`'s
        `test_each_recorded_quantity_carries_the_compartment_it_names`
        audits that pairing against the core's own state, and
        `tests/unit/test_run_history.py` holds this rearrangement lossless.

        Args:
            sample: The concentrations recorded at one simulation time.
                Its time must not precede the previous sample's.

        Raises:
            ValueError: If the sample does not carry exactly this run's
                substances. Recording it would leave the series it did
                carry longer than the ones it did not, so every later value
                of the short ones would be read at another sample's instant.
        """

        if frozenset(sample.substances) != frozenset(self._series):
            raise ValueError(
                f"this run records {sorted(self._series)}, "
                f"but the sample carries {sorted(sample.substances)}"
            )

        index = len(self._elapsed_s)
        self._elapsed_s.append(sample.elapsed_s)

        for substance_id, series in self._series.items():
            values = sample.substances[substance_id]

            for quantity in COMPARTMENT_QUANTITIES:
                series[quantity].record(values[quantity])

            ratio = wash_in_ratio(
                values[RecordedQuantity.ALVEOLAR], values[RecordedQuantity.CIRCUIT]
            )
            wash_in = series[RecordedQuantity.WASH_IN_RATIO]

            if ratio is None:
                # Rule 1 of `app/wash_in.py`: no agent in the circuit yet, so
                # the quotient has no value the interface may show. Recorded as
                # undefined rather than as a substituted zero, which is what
                # keeps the trace broken there instead of drawing a line the
                # run never produced.
                wash_in.record_undefined()
            else:
                wash_in.record(ratio)

            self._extend_wash_in_stretches(substance_id, index, ratio)

    def elapsed_s(self, index: int) -> float:
        """Simulated time of one recorded sample, in seconds."""

        return self._elapsed_s[index]

    def times_s(self) -> Sequence[float]:
        """Every recorded sample time, ascending. Read-only to callers."""

        return self._elapsed_s

    def aggregates(self, series: RecordedSeries) -> M4AggregateCache:
        """The values and M4 aggregates of one series over the whole run.

        Raises:
            KeyError: If this run records no such series, which means the
                caller is drawing a substance the run does not hold rather
                than that it asked wrongly. Failing is the point: the
                alternative is a trace silently drawn from whichever
                substance the run happened to have.
        """

        return self._series[series.substance_id][series.quantity]

    def sample(self, index: int) -> SimulationHistorySample:
        """Rebuild one recorded sample as a row.

        The inverse of `record`, and deliberately not the shape anything on
        the render path uses: a trace wants one series over many samples,
        which `aggregates` answers without building a row at all.
        """

        return SimulationHistorySample(
            elapsed_s=self._elapsed_s[index],
            substances={
                substance_id: {
                    quantity: series[quantity].value(index) for quantity in COMPARTMENT_QUANTITIES
                }
                for substance_id, series in self._series.items()
            },
        )

    def value(self, series: RecordedSeries, index: int) -> float:
        """One series' recorded value at one sample."""

        return self.aggregates(series).value(index)

    def wash_in_stretches(self, substance_id: str, start: int, stop: int) -> list[tuple[int, int]]:
        """One substance's wash-in stretches, clipped to `[start, stop)`.

        A stretch is a run of consecutive samples whose F_A/F_I quotient is
        inside the domain `app/wash_in.py` states. The chart draws one line
        per stretch rather than one line through every in-domain sample,
        because a single polyline would join across the samples it skipped
        and draw values the run never produced.

        Found by binary search over the stretches recorded so far, so the
        cost is a property of how many stretches the window contains rather
        than of how many samples it spans.

        Args:
            substance_id: Whose quotient. The domain is a property of one
                substance's own two fractions, so two substances recorded
                together enter and leave it at different samples.
            start: First position of the window, absolute within the run.
            stop: One past the window's last position.

        Returns:
            One `(start, stop)` pair per stretch the window overlaps,
            oldest first, each already clipped to the window.

        Raises:
            KeyError: If this run does not record that substance.
        """

        starts = self._wash_in_starts[substance_id]
        stops = self._wash_in_stops[substance_id]
        stretches: list[tuple[int, int]] = []

        for position in range(bisect_right(stops, start), len(starts)):
            stretch_start = starts[position]

            if stretch_start >= stop:
                break

            stretches.append((max(stretch_start, start), min(stops[position], stop)))

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

    def _extend_wash_in_stretches(self, substance_id: str, index: int, ratio: float | None) -> None:
        """Place one substance's sample in its wash-in stretches, or in none.

        Both of `app/wash_in.py`'s rules are applied here and nowhere else
        on the chart's path: a sample with no quotient fails rule 1, and one
        above equilibrium fails rule 2. Either ends the stretch in progress.
        """

        if ratio is None or not is_wash_in(ratio):
            return

        starts = self._wash_in_starts[substance_id]
        stops = self._wash_in_stops[substance_id]

        if stops and stops[-1] == index:
            stops[-1] = index + 1

            return

        starts.append(index)
        stops.append(index + 1)


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
    supported_limit_reason: str | None
    """Why the run stopped at a declared limit of the model's domain, or
    `None` if it did not.

    A non-`None` value means the run reached the supported run length and
    the core refused the next step. `is_running` is `False`, and this is
    neither a pause nor a failure: nothing was miscalculated, no step was
    rolled back, and every value in this snapshot is a completed step's at
    a simulated time inside the supported span. What ended is the claim
    that a further step would stand for a patient.

    It is separate from `failure_reason` because the interface must not
    present the two alike. Telling a reader the simulator broke, when it
    stopped exactly where `docs/MODEL.md` says it should, misrepresents a
    correct model as a defective one - and the reverse would be worse.
    Both are `None` for a run that is merely paused.
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

    @property
    def has_recorded_run(self) -> bool:
        """Whether this run holds anything that starting over would destroy.

        True once the run has advanced past its first sample or has recorded
        a setting change; false for a run that has been built and not yet
        touched, which is the state both a fresh session and `reset()` leave.

        It exists so the interface can tell a destructive act from a harmless
        one. `set_agent` always begins a new run, which is unrecoverable where
        there is a run to lose and is nothing at all where there is not, and a
        confirmation that fires in both cases states something untrue in the
        second and has been answered without reading by the time it matters in
        the first.

        Elapsed time and the timeline are read together because either alone
        misses a case: a run paused at its first sample with the vaporizer
        already turned has a recorded input and no elapsed time, and a run
        advanced with nothing touched has the reverse.
        """

        return self.elapsed_s > 0.0 or bool(self.control_timeline)


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
        self._supported_limit_reason: str | None = None
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
        # One substance: the agent this run is of. `set_agent` comes back
        # through here and builds a new history under the new agent's id,
        # so a run's recorded substance is always the one its samples were
        # produced by.
        self._history = RunHistory((agent_id,))
        self._history.record(self._build_history_sample())
        self._clear_control_timeline()

        # Every compartment above is newly constructed, so no state survives
        # from a run that failed: a stale failure reason would halt a
        # session that has nothing wrong with it. A stale limit reason would
        # do the same to a run that has taken no steps at all.
        self._failure_reason = None
        self._supported_limit_reason = None

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

    @property
    def has_reached_supported_limit(self) -> bool:
        """Whether the run stopped at a declared limit of the model's domain."""

        return self._supported_limit_reason is not None

    def halt_at_supported_limit(self, reason: str) -> None:
        """Stop the run because it reached the end of the supported domain.

        Distinct from `fail()`, which records that something went wrong,
        and from `pause()`, which the run resumes from. Here nothing went
        wrong and there is nothing to resume *to*: the core refused the
        next step before taking it, so the run stands on a completed step
        at a simulated time the model is claimed to represent a patient at,
        and the step after it would be refused identically.

        Resuming is therefore not offered, for the reason `fail()` gives -
        a Start that does nothing is a control presenting itself as
        working - and `reset()` or `set_agent()` is the way to a new run.
        What differs is only what the interface says about it, and that
        difference is required rather than cosmetic: see
        `SimulationSnapshot.supported_limit_reason`.

        The first reason is kept, like `fail()`'s, so a later tick reaching
        the same boundary cannot overwrite the one that explains it.
        """

        self._is_running = False

        if self._supported_limit_reason is None:
            self._supported_limit_reason = reason

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

        And because it begins a new run it *destroys* one, irrecoverably:
        the recorded history, the control-input timeline and the simulated
        time the run reached all go, and nothing here or anywhere else keeps
        a copy. Calling this is therefore not something a caller may do on a
        gesture that reads as choosing a view. `docs/MODEL.md`
        § "Agent-change behavior" states what the interface owes a user
        first, and `SimulationSnapshot.has_recorded_run` is what tells it
        whether this call would cost anything.
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
            supported_limit_reason=self._supported_limit_reason,
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
        """Start or resume the run, refusing a session that cannot continue.

        Raising rather than quietly declining is deliberate: silently
        ignoring a start would leave the interface showing a stopped run
        with no indication that starting it did nothing, which is the
        hidden mode `CLAUDE.md` forbids.

        Two states refuse, for the same reason and with different meanings.
        A failed session would raise again on its first tick; a session
        standing at the supported run length would have its first step
        refused by the core. Neither can be resumed, and each says which it
        is, so a caller reporting the refusal does not have to guess.
        """

        if self._failure_reason is not None:
            raise SimulationExecutionError(
                f"cannot resume a failed simulation ({self._failure_reason}); reset it first"
            )

        if self._supported_limit_reason is not None:
            raise SimulationDomainLimitError(
                f"this run has reached the supported run length "
                f"({self._supported_limit_reason}); reset it to start a new run"
            )

        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run, clear any failure or limit, and clear dynamic state.

        Settings are preserved. This is the only way out of a failed
        session, and out of one standing at the supported run length: every
        compartment goes back to its initial state and the step count goes
        back to zero, so nothing carries over from the run that could not
        continue.
        """

        self.pause()
        self._failure_reason = None
        self._supported_limit_reason = None
        self._state.reset()
        self._history = RunHistory((self._agent_id,))
        self._history.record(self._build_history_sample())
        self._clear_control_timeline()

    # No `set_circuit_volume` here, deliberately (`PL-GYH2`). The circuit
    # volume is a fixed model parameter rather than a control: it is set
    # once, when this controller builds the system, and no interface control
    # reaches it thereafter. The setter that used to sit here was public and
    # unbounded, so it offered every caller of the app layer a route to a
    # circuit volume outside anything `docs/MODEL.md` verifies, for a knob no
    # teaching case has asked for. `BreathingCircuit.set_circuit_volume`
    # stays, because `_build_state()` is how the parameter reaches the circuit at
    # all; what is removed is the app-level passthrough, not the core
    # primitive. `docs/MODEL.md` § "What is not bounded this way" carries the
    # argument.

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
        """Read the core's compartments into one recorded row.

        **The whole of the run's pairing is here**, one line per
        compartment: which core state each `RecordedQuantity` carries, and
        which substance the row belongs to. `RunHistory.record` decides
        neither - it stores each value under the key the sample already
        gives it - so this is the one place a compartment could come to
        carry another's values, and the one place it is audited.
        `tests/integration/test_controller.py`'s
        `test_each_recorded_quantity_carries_the_compartment_it_names`
        holds it against the core's own attributes.
        """

        system = self._state.uptake_system

        return SimulationHistorySample(
            elapsed_s=self._state.elapsed_s,
            substances={
                self._agent_id: {
                    RecordedQuantity.CIRCUIT: (system.circuit.circuit_concentration_fraction),
                    RecordedQuantity.ALVEOLAR: (system.alveoli.concentration_fraction),
                    RecordedQuantity.MIXED_VENOUS: (system.patient.mixed_venous_fraction),
                    RecordedQuantity.VESSEL_RICH: (
                        system.patient.vessel_rich.partial_pressure_fraction
                    ),
                    RecordedQuantity.MUSCLE: (system.patient.muscle.partial_pressure_fraction),
                    RecordedQuantity.FAT: (system.patient.fat.partial_pressure_fraction),
                }
            },
        )
