"""PySide6 + pyqtgraph spike: the concentration chart and the readout row.

`PL-55DH`. A disposable experiment, not a port. It draws the shipped
concentration chart and readout row behind the *existing*
`SimulationController`, so that `PL-X9T3` has something to run on the project
owner's own machine and measure the one term no session in this container can:
**paint cost on real hardware, and whether it looks the way it is meant to.**

**What it is for.** `PL-QXSB` measured PySide6 with pyqtgraph at 0.51 ms for
the frame Flet does in 20.3 ms, flat in point count, and could not measure
paint at all - no GPU, a software rasteriser, an offscreen platform plugin.
That is the load-bearing half of the evidence, and a decision to rewrite the
interface on the other half alone would be exactly the "recommend first,
research afterwards" `CLAUDE.md` names. So this window instruments its own
frame in the split `PL-YSZN` used on Flet, and puts the numbers on screen.

**What it deliberately is not.** Not the agent selector, the wash-in plot, the
control marks, the new-case dialog, the notice banner, or any theming beyond
enough colour and dash to tell six traces apart. Missing pieces are missing on
purpose; the question is frame cost and feel, not completeness.

**It imports from the shipped package and nothing shipped imports it.**
Deleting the spike is `rm -rf spikes/`, and no module under
`src/anesthesia_sim/` will notice. Its dependencies are not in
`pyproject.toml`: `spikes/qt/README.md` carries the one command that runs it.

**Two copies it knowingly keeps**, both recorded here because a copy nobody
declared is how a spike quietly becomes a fork: the six trace colours and dash
patterns (`chart_sources.TRACES`, copied because the patterns live inside the
Flet view), and nothing else. The step size, the tick and render cadences, the
column budget, the time-base ladder, every unit conversion and every displayed
string come from the shipped modules themselves.

**The numbers on screen are the application's numbers.** Every displayed value
goes through `app/formatting.py` - the same percent, the same MAC multiple,
the same elapsed clock, the same hedged labels - because a spike showing a
correct value with a wrong unit or an unhedged label is the presentation
failure `CLAUDE.md` counts as a safety failure whether or not the window it is
in is disposable. `--self-check` asserts that what the chart drew and what the
readouts printed describe the same compartments.
"""

from __future__ import annotations

import argparse
import sys
from time import perf_counter

import pyqtgraph as pg
from chart_sources import (
    COLUMN_BUDGETS,
    POINT_PROVENANCE,
    TRACES,
    read_traces,
    verify_trace_binding,
)
from frame_timing import FrameCost, StageClock
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPaintEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.chart_series import CHART_COLUMN_BUDGET_PER_SERIES
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    ChartTimeBase,
    fit_to_run,
    fitted_window,
    following_window,
)
from anesthesia_sim.app.controller import SimulationController, SimulationSnapshot
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_chart_time_label,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_subtitle,
    format_time_base,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
)
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S

# The model's step, taken as the core's declared ceiling rather than copied as
# a digit. `simulation_view.SIMULATION_STEP_S` sits at that ceiling
# deliberately - its comment derives why, and
# `test_the_shipped_step_is_within_the_maximum_simulation_step` holds the
# relation - and taking the ceiling means the spike has no second literal to
# drift from the application's. If the shipped app ever moves off the ceiling
# this line has to be re-pointed, which is why it is stated rather than
# assumed.
SIMULATION_STEP_S = MAXIMUM_SIMULATION_STEP_S

# The two cadences, mirroring `simulation_view.py`. They are named apart there
# for reasons that survive here: the tick is a property of this host's event
# loop and the step is a property of the model's numerics, and the playback
# multiplier is the ratio between them. A spike that changed either would be
# measuring a frame the application does not draw.
SIMULATION_TICK_INTERVAL_S = SIMULATION_STEP_S
RENDER_INTERVAL_S = 0.2

# Colours, taken from `app/theme.py`'s values. The chart's own six live in
# `chart_sources.TRACES`; these are the surface the window is drawn on.
BACKGROUND = "#F4F7FA"
PANEL = "#FFFFFF"
INK = "#243B53"
MUTED = "#59728A"
WARNING = "#8A4B08"
GRIDLINE = "#D9E2EC"
ONE_MAC_LINE_COLOR = "#334155"
MAC_AWAKE_BAND_COLOR = "#94A3B8"

# What the banner says, and it says it permanently rather than on a timer.
# This window draws real values from the real model, so a reader who came to
# it from a screenshot has no other way to know it is not the application -
# and "which interface am I looking at" is a mode question, which
# `.claude/rules/expert-review.md` asks to be answered on screen rather than
# by the reader's memory.
BANNER_TEXT = (
    "SPIKE — PySide6 + pyqtgraph, PL-55DH. Not the shipped interface and not a "
    "medical device: an experiment measuring frame cost. Values are the real model's; "
    "the interface around them is incomplete by design."
)

# How far the chart's newest point and the readout beside it may differ before
# `--self-check` calls it a mismatch, in percentage points. The two are the
# same compartment reached by two routes - the score's evaluation and the
# compartment's own canonical state - which `core/run_score.py` states are
# equal to floating-point composition rather than exactly. A hundredth of the
# displayed resolution is far tighter than any real disagreement and far
# looser than composition noise.
SELF_CHECK_TOLERANCE_PERCENT = 1e-4


class TimedPlot(pg.PlotWidget):
    """A plot widget that charges its own repaints to a timing stage.

    The term `PL-QXSB` could not measure. Timing `paintEvent` here catches the
    CPU cost of rendering the scene into the widget's backing store, which is
    the part of painting that happens in this process and the part a slow
    frame is made of.

    **It is not the whole of what a reader waits for**, and the panel says so:
    the compositor's work and the GPU's are outside this process and outside
    this measurement. What it does establish is the ceiling on the toolkit's
    own contribution, which is the number a port would be sized against.
    """

    def __init__(self, cost: FrameCost, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._cost = cost

    # Qt spells this method in camelCase; the override has to match.
    def paintEvent(self, event: QPaintEvent) -> None:
        with StageClock(self._cost.paint):
            super().paintEvent(event)


class SimulatedTimeAxis(pg.AxisItem):
    """The bottom axis, labelled the way the shipped chart labels it.

    pyqtgraph's default is a bare number, and a bare number is the one thing
    this axis must not show: it spans anything from a minute to half a day
    depending on the time base, so `600` means seconds on one width and would
    be read as minutes on another while looking identical on both.
    `format_chart_time_label` puts the unit on every tick - `45s`, `3m`,
    `1h30m` - which is why the shipped axis is readable without its caption
    and without knowing which base is selected.
    """

    def tickStrings(  # Qt/pyqtgraph spell this in camelCase; the override matches.
        self, values: list[float], scale: float, spacing: float
    ) -> list[str]:
        del scale, spacing

        return [format_chart_time_label(value) for value in values]


class Readout:
    """One panel of the readout row: a name, an optional hedge, and two values.

    The shipped row's shape, reduced to what a spike needs. The qualifier line
    is drawn even when a panel has no qualifier, so the seven panels are the
    same height and every reading in the row shares a baseline - which is the
    reason the shipped row splits its two longest labels, and the reason it can
    be read comparatively at all (`docs/MODEL.md` § "Displayed precision").
    """

    def __init__(self, name: str, qualifier: str | None) -> None:
        self.widget = QFrame()
        self.widget.setStyleSheet(f"QFrame {{ background: {PANEL}; border-radius: 8px; }}")
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(1)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {MUTED}; font-size: 11px; font-weight: 600;")

        # Drawn as a space rather than skipped where there is no qualifier, so
        # every panel keeps the same height. An empty string collapses the
        # label and pushes that panel's reading half a line above its
        # neighbours', which is the misalignment the shipped row exists to
        # avoid.
        self.qualifier_label = QLabel(qualifier or " ")
        self.qualifier_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")

        self.value_label = QLabel("—")
        value_font = QFont()
        value_font.setPointSize(17)
        value_font.setWeight(QFont.Weight.DemiBold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {INK};")

        self.secondary_label = QLabel(" ")
        self.secondary_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")

        for label in (name_label, self.qualifier_label, self.value_label, self.secondary_label):
            layout.addWidget(label)


class ParameterSlider:
    """One setting control, stepped at the resolution its readout displays.

    Qt sliders are integer-valued, and that is turned into a property here
    rather than worked around: the slider's steps are the display resolution,
    so the value applied to the model is exactly the value printed beside it.
    The shipped Flet slider is continuous and rounds only its drag label, which
    is why `PL-3TLK`'s comment had to reason about a dial reading "2%" over a
    readout reading "2.40%". Here that cannot arise.

    Attributes:
        widget: The labelled block to put in a layout.
        slider: The control itself, for connecting a handler.
    """

    def __init__(
        self,
        label: str,
        qualifier: str | None,
        minimum: float,
        maximum: float,
        value: float,
        decimals: int,
    ) -> None:
        self._scale = 10.0**decimals
        self.widget = QFrame()
        self.widget.setStyleSheet(f"QFrame {{ background: {PANEL}; border-radius: 8px; }}")
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(1)

        heading = QLabel(label)
        heading.setStyleSheet(f"color: {INK}; font-size: 12px; font-weight: 600;")
        layout.addWidget(heading)

        qualifier_label = QLabel(qualifier or " ")
        qualifier_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        layout.addWidget(qualifier_label)

        self.value_label = QLabel("—")
        self.value_label.setStyleSheet(f"color: {INK}; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.value_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(round(minimum * self._scale))
        self.slider.setMaximum(round(maximum * self._scale))
        self.slider.setValue(round(value * self._scale))
        layout.addWidget(self.slider)

    def value(self) -> float:
        """The slider's position as the quantity it sets."""

        return self.slider.value() / self._scale

    def set_maximum(self, maximum: float) -> None:
        """Move the ceiling, for a control whose range follows the agent."""

        self.slider.setMaximum(round(maximum * self._scale))


class SpikeWindow(QWidget):
    """The spike's whole interface, and the loop that drives it."""

    def __init__(self, controller: SimulationController) -> None:
        super().__init__()
        self._controller = controller
        self._cost = FrameCost()
        self._playback_rate: PlaybackRate = DEFAULT_PLAYBACK_RATE
        self._time_base: ChartTimeBase | None = None
        self._columns = CHART_COLUMN_BUDGET_PER_SERIES
        self._mac_axis_basis = 0.0
        self._last_render_at: float | None = None
        self._last_point_count = 0
        self._halted_reason: str | None = None

        snapshot = controller.snapshot()
        self.setWindowTitle("PL-55DH Qt spike — concentration chart")
        self.setStyleSheet(f"background: {BACKGROUND}; color: {INK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(self._build_banner())
        layout.addWidget(self._build_header(snapshot))
        layout.addLayout(self._build_readout_row())
        layout.addWidget(self._build_chart(snapshot), stretch=1)
        layout.addWidget(self._provenance_label)
        layout.addWidget(self._reference_label)
        layout.addLayout(self._build_transport())
        layout.addLayout(self._build_parameter_row(snapshot))
        layout.addWidget(self._build_instruments())

        self._apply_agent_scale(snapshot)
        self._render_frame()

        # Two timers, as the application has two loops. The simulation timer
        # is precise because the playback rate it serves is a claim about the
        # clock on screen; the render timer is precise because its lateness is
        # one of the three numbers this spike exists to report, and a coarse
        # timer would report its own coarseness as the interface's latency.
        self._step_timer = QTimer(self)
        self._step_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._step_timer.timeout.connect(self.step_tick)
        self._step_timer.start(round(SIMULATION_TICK_INTERVAL_S * 1000))

        self._render_timer = QTimer(self)
        self._render_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._render_timer.timeout.connect(self.render_tick)
        self._render_timer.start(round(RENDER_INTERVAL_S * 1000))

    # ---------------------------------------------------------------- layout

    def _build_banner(self) -> QLabel:
        banner = QLabel(BANNER_TEXT)
        banner.setWordWrap(True)
        banner.setStyleSheet(
            f"background: #FDF3E7; color: {WARNING}; border-radius: 6px; "
            "padding: 7px 10px; font-weight: 600;"
        )

        return banner

    def _build_header(self, snapshot: SimulationSnapshot) -> QLabel:
        # The same subtitle the application draws, and it carries the build
        # rather than the version: between two releases every build shares a
        # version string, which is what made a merged fix indistinguishable
        # from the code it replaced (`PL-QC38`). A spike being compared with
        # the application by eye needs that at least as much.
        header = QLabel(format_subtitle(snapshot.agent_display_name))
        header.setStyleSheet(f"color: {MUTED}; font-size: 11px;")

        return header

    def _build_readout_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self._elapsed_readout = Readout("Simulated time", None)
        row.addWidget(self._elapsed_readout.widget)
        self._trace_readouts = [Readout(trace.label, trace.qualifier) for trace in TRACES]

        for readout in self._trace_readouts:
            row.addWidget(readout.widget)

        return row

    def _build_chart(self, snapshot: SimulationSnapshot) -> QWidget:
        pg.setConfigOption("background", PANEL)
        pg.setConfigOption("foreground", MUTED)
        self._plot = TimedPlot(
            self._cost, axisItems={"bottom": SimulatedTimeAxis(orientation="bottom")}
        )
        item = self._plot.getPlotItem()
        item.setMenuEnabled(False)
        item.hideButtons()
        item.setMouseEnabled(x=False, y=False)
        item.setLabel("left", "% of 1 atm")
        item.setLabel("bottom", "Simulated time")
        item.showAxis("right")
        item.getAxis("right").setLabel("×MAC")

        # The band and the line are drawn under the traces, so a trace is
        # never hidden behind a reference. Both are placed from the snapshot's
        # own MAC and MAC-awake, so neither can be drawn at another agent's
        # height (`simulation_view._mac_awake_band_percent`).
        self._mac_awake_band = pg.LinearRegionItem(
            values=(0.0, 0.0),
            orientation="horizontal",
            movable=False,
            brush=pg.mkBrush(148, 163, 184, 45),
            pen=pg.mkPen(MAC_AWAKE_BAND_COLOR, width=1),
        )
        self._mac_awake_band.setZValue(-20)
        item.addItem(self._mac_awake_band)

        self._one_mac_line = pg.InfiniteLine(
            pos=0.0,
            angle=0,
            pen=pg.mkPen(ONE_MAC_LINE_COLOR, width=1.5, style=Qt.PenStyle.DashLine),
        )
        self._one_mac_line.setZValue(-10)
        item.addItem(self._one_mac_line)

        self._curves = []

        for trace in TRACES:
            pen = pg.mkPen(trace.color, width=trace.width)

            if trace.dash is not None:
                pen.setDashPattern(list(trace.dash))

            self._curves.append(item.plot([], [], pen=pen, name=trace.label, antialias=True))

        self._provenance_label = QLabel("")
        self._provenance_label.setWordWrap(True)
        self._provenance_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        self._reference_label = QLabel("")
        self._reference_label.setWordWrap(True)
        self._reference_label.setStyleSheet(f"color: {MUTED}; font-size: 10px;")

        return self._plot

    def _build_transport(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self._status_label = QLabel("Paused")
        self._status_label.setStyleSheet(f"color: {MUTED}; font-weight: 700;")
        row.addWidget(self._status_label)

        self._start_button = QPushButton("Start")
        self._start_button.clicked.connect(self._on_start)
        row.addWidget(self._start_button)

        self._pause_button = QPushButton("Pause")
        self._pause_button.clicked.connect(self._on_pause)
        row.addWidget(self._pause_button)

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self._on_reset)
        row.addWidget(reset_button)

        row.addWidget(QLabel("Rate"))
        self._rate_box = QComboBox()

        for rate in SUPPORTED_PLAYBACK_RATES:
            self._rate_box.addItem(format_playback_rate(rate.multiplier), rate.multiplier)

        self._rate_box.setCurrentIndex(SUPPORTED_PLAYBACK_RATES.index(DEFAULT_PLAYBACK_RATE))
        self._rate_box.currentIndexChanged.connect(self._on_rate_change)
        row.addWidget(self._rate_box)

        row.addWidget(QLabel("Window"))
        self._time_base_box = QComboBox()
        self._time_base_box.addItem("Fit run", FIT_RUN_KEY)

        for base in SELECTABLE_TIME_BASES:
            self._time_base_box.addItem(format_time_base(base.span_s), base.span_s)

        self._time_base_box.currentIndexChanged.connect(self._on_time_base_change)
        row.addWidget(self._time_base_box)

        # The successor to "would Qt make decimation optional". With M4 gone
        # the question is whether the column budget can be raised, and this is
        # the control that prices it.
        row.addWidget(QLabel("Columns"))
        self._columns_box = QComboBox()

        for budget in COLUMN_BUDGETS:
            shipped = " (shipped)" if budget == CHART_COLUMN_BUDGET_PER_SERIES else ""
            self._columns_box.addItem(f"{budget}{shipped}", budget)

        self._columns_box.currentIndexChanged.connect(self._on_columns_change)
        row.addWidget(self._columns_box)

        # Antialiasing is a paint-cost lever rather than a preference, so it is
        # a control: the difference between the two settings, read off the
        # panel below, is part of what a port would be sized on.
        self._antialias_box = QCheckBox("Antialias")
        self._antialias_box.setChecked(True)
        self._antialias_box.stateChanged.connect(self._on_antialias_change)
        row.addWidget(self._antialias_box)

        row.addStretch(1)

        return row

    def _build_parameter_row(self, snapshot: SimulationSnapshot) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        # "common gas outlet", never "Fresh gas flow" alone: a flowmeter reads
        # the carrier gas only, and this setting is the whole post-vaporizer
        # stream. `PL-71CF` records why the difference is a wrong clinical
        # inference from a correct number rather than a wording preference.
        self._fresh_gas_flow = ParameterSlider(
            "Fresh gas flow",
            "common gas outlet",
            MINIMUM_FRESH_GAS_FLOW_L_MIN,
            MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            snapshot.fresh_gas_flow_l_min,
            FLOW_DISPLAY_DECIMALS,
        )
        self._delivered = ParameterSlider(
            f"Delivered {snapshot.agent_display_name.lower()}",
            "vaporizer dial",
            0.0,
            snapshot.max_delivered_concentration_percent,
            snapshot.delivered_concentration_fraction * 100.0,
            CONCENTRATION_DISPLAY_DECIMALS,
        )
        self._alveolar_ventilation = ParameterSlider(
            "Alveolar ventilation",
            None,
            MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            snapshot.alveolar_ventilation_l_min,
            FLOW_DISPLAY_DECIMALS,
        )
        self._cardiac_output = ParameterSlider(
            "Cardiac output",
            None,
            MINIMUM_CARDIAC_OUTPUT_L_MIN,
            MAXIMUM_CARDIAC_OUTPUT_L_MIN,
            snapshot.cardiac_output_l_min,
            FLOW_DISPLAY_DECIMALS,
        )

        for control, handler in (
            (self._fresh_gas_flow, self._on_fresh_gas_flow),
            (self._delivered, self._on_delivered),
            (self._alveolar_ventilation, self._on_alveolar_ventilation),
            (self._cardiac_output, self._on_cardiac_output),
        ):
            control.slider.sliderPressed.connect(self._controller.begin_control_adjustment)
            control.slider.valueChanged.connect(handler)
            row.addWidget(control.widget)

        return row

    def _build_instruments(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background: {PANEL}; border-radius: 8px; }}")
        grid = QGridLayout(frame)
        grid.setContentsMargins(10, 8, 10, 8)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(2)
        grid.setColumnStretch(1, 1)

        for column in (2, 3, 4):
            grid.setColumnMinimumWidth(column, 80)

        for column, heading in enumerate(("Stage", "Flet counterpart", "last", "median", "p90")):
            label = QLabel(heading)
            label.setStyleSheet(f"color: {MUTED}; font-size: 10px; font-weight: 700;")
            grid.addWidget(label, 0, column)

        self._instrument_cells: list[tuple[QLabel, QLabel, QLabel]] = []

        for row, stage in enumerate(self._cost.stages(), start=1):
            name = QLabel(stage.label)
            name.setStyleSheet(f"color: {INK}; font-size: 11px;")
            counterpart = QLabel(stage.flet_counterpart or "— (Flet renders out of process)")
            counterpart.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
            grid.addWidget(name, row, 0)
            grid.addWidget(counterpart, row, 1)
            cells = (QLabel("—"), QLabel("—"), QLabel("—"))

            for column, cell in enumerate(cells, start=2):
                cell.setStyleSheet(f"color: {INK}; font-size: 11px;")
                grid.addWidget(cell, row, column)

            self._instrument_cells.append(cells)

        self._instrument_note = QLabel("")
        self._instrument_note.setWordWrap(True)
        self._instrument_note.setStyleSheet(f"color: {MUTED}; font-size: 10px;")
        grid.addWidget(self._instrument_note, len(self._cost.stages()) + 1, 0, 1, 5)

        return frame

    # ----------------------------------------------------------------- loops

    def step_tick(self) -> None:
        """Advance the run, at the rate selected, in one uninterrupted burst.

        The application's loop, transcribed: the rate is read once per tick so
        a tick is all-or-nothing at one rate, and a step that raises abandons
        the rest of the burst rather than the loop, so Reset can recover.
        """

        if not self._controller.is_running:
            return

        steps = self._playback_rate.steps_per_tick(
            tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
        )

        try:
            with StageClock(self._cost.advance):
                for _ in range(steps):
                    self._controller.advance(SIMULATION_STEP_S)
        except Exception as error:  # broad, as the shipped loop is
            # A loop that exited could never be restarted, and Reset would
            # leave the interface permanently dead. Halting clears the run
            # instead, so the timer idles until a fresh one is started.
            self._halt(f"{type(error).__name__}: {error}")

    def render_tick(self) -> None:
        """Draw a frame, and charge the wait before it to the latency stage.

        Lateness is measured against the interval the timer was asked for, so
        it is `PL-X9T3`'s "how long a callback that is ready to run waits" and
        directly comparable with Flet's 20-30 ms p90. A negative reading is
        clamped to zero: a timer firing early is not a latency, and letting one
        into the window would make the median describe the timer rather than
        the wait.
        """

        now = perf_counter()

        # Only while a timer is actually driving this. `--self-check` and
        # `--screenshot` call this method back to back with the timers
        # stopped, and the near-zero gaps that produces are not a latency -
        # recording them would print a measurement of nothing as 0.00 ms,
        # which is the stage reading as free rather than as unmeasured.
        if self._render_timer.isActive() and self._last_render_at is not None:
            self._cost.latency.record(max(0.0, now - self._last_render_at - RENDER_INTERVAL_S))

        self._last_render_at = now
        self._render_frame()

    def _render_frame(self) -> None:
        """One frame: read the run, format it, hand it to Qt."""

        with StageClock(self._cost.refresh):
            snapshot = self._controller.snapshot()

            if self._time_base is None:
                time_base = fit_to_run(snapshot.elapsed_s)
                first_s, last_s = fitted_window(time_base)
            else:
                time_base = self._time_base
                first_s, last_s = following_window(time_base, snapshot.elapsed_s)

            points = read_traces(self._controller, snapshot, first_s, last_s, self._columns)
            readings = self._format_readings(snapshot)

        with StageClock(self._cost.handoff):
            self._plot.getPlotItem().setXRange(first_s, last_s, padding=0)

            for curve, percents in zip(self._curves, points.percents, strict=True):
                curve.setData(points.times_s, percents)

            self._apply_readings(readings)

        self._last_point_count = points.point_count
        self._plot.getPlotItem().getAxis("bottom").setTickSpacing(
            major=time_base.tick_interval_s, minor=time_base.tick_interval_s
        )
        self._apply_agent_scale(snapshot)
        self._refresh_captions(snapshot, time_base)
        self._refresh_instruments()

    # ------------------------------------------------------------ formatting

    def _format_readings(self, snapshot: SimulationSnapshot) -> tuple[tuple[str, str], ...]:
        """Every readout's two lines, formatted through the shipped formatters.

        Built as a tuple and applied separately so that the formatting cost
        lands in `refresh` and the widget writes land in `handoff`, which is
        the split `PL-YSZN` measured on Flet. Every MAC multiple is produced
        from this snapshot's own divisor, so a frame cannot pair one agent's
        concentration with another agent's MAC.
        """

        mac_percent = snapshot.agent_mac_percent
        fractions = (
            snapshot.circuit_concentration_fraction,
            snapshot.alveolar_concentration_fraction,
            snapshot.mixed_venous_concentration_fraction,
            snapshot.vessel_rich_partial_pressure_fraction,
            snapshot.muscle_partial_pressure_fraction,
            snapshot.fat_partial_pressure_fraction,
        )

        return (
            (
                format_elapsed(snapshot.elapsed_s),
                format_playback_rate(self._playback_rate.multiplier),
            ),
            *(
                (format_percent(fraction), format_mac_multiple(fraction, mac_percent))
                for fraction in fractions
            ),
        )

    def _apply_readings(self, readings: tuple[tuple[str, str], ...]) -> None:
        """Write the formatted readings onto the row, in `TRACES` order."""

        elapsed, *compartments = readings
        self._elapsed_readout.value_label.setText(elapsed[0])
        self._elapsed_readout.secondary_label.setText(elapsed[1])

        for readout, (value, secondary) in zip(self._trace_readouts, compartments, strict=True):
            readout.value_label.setText(value)
            readout.secondary_label.setText(secondary)

    def _apply_agent_scale(self, snapshot: SimulationSnapshot) -> None:
        """Place the y axis, its rules, the MAC axis and the two references.

        All five come from one snapshot, so the axis a trace is drawn against
        and the ticks that label it cannot describe different agents. The MAC
        axis is rebuilt only when the divisor moves, because its ticks are the
        one part of this that costs anything.
        """

        mac_percent = snapshot.agent_mac_percent
        top_percent = chart_axis_top_percent(mac_percent)
        item = self._plot.getPlotItem()
        item.setYRange(0.0, top_percent, padding=0)
        item.getAxis("left").setTickSpacing(
            major=chart_grid_interval_percent(mac_percent), minor=top_percent
        )
        item.showGrid(x=True, y=True, alpha=0.25)
        self._one_mac_line.setPos(mac_percent)
        lower_percent, upper_percent = mac_awake_band_percent(
            fraction_of_mac=snapshot.agent_mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=(
                snapshot.agent_mac_awake.standard_deviation_fraction_of_mac
            ),
            mac_percent=mac_percent,
        )
        self._mac_awake_band.setRegion((lower_percent, upper_percent))

        if mac_percent != self._mac_axis_basis:
            self._mac_axis_basis = mac_percent
            item.getAxis("right").setTicks(
                [[(percent, label) for percent, label in mac_axis_ticks(top_percent, mac_percent)]]
            )

    def _refresh_captions(self, snapshot: SimulationSnapshot, time_base: ChartTimeBase) -> None:
        """Say what the plot drew and what its two references were drawn from."""

        self._provenance_label.setText(
            POINT_PROVENANCE.format(
                columns=self._columns, points=self._last_point_count, traces=len(TRACES)
            )
        )
        self._reference_label.setText(
            f"{format_mac_reference(snapshot.agent_display_name, snapshot.agent_mac_percent)}  "
            f"{
                format_mac_awake_reference(
                    snapshot.agent_display_name,
                    fraction_of_mac=snapshot.agent_mac_awake.fraction_of_mac,
                    standard_deviation_fraction_of_mac=(
                        snapshot.agent_mac_awake.standard_deviation_fraction_of_mac
                    ),
                    mac_percent=snapshot.agent_mac_percent,
                )
            }  Window: {format_time_base(time_base.span_s)}."
        )

        if self._halted_reason is not None:
            self._status_label.setText("Stopped — simulation error")
            self._status_label.setStyleSheet(f"color: {WARNING}; font-weight: 700;")
        elif snapshot.supported_limit_reason is not None:
            self._status_label.setText("Stopped — supported run length reached")
            self._status_label.setStyleSheet(f"color: {MUTED}; font-weight: 700;")
        elif snapshot.is_running:
            self._status_label.setText("Running")
            self._status_label.setStyleSheet("color: #127D71; font-weight: 700;")
        else:
            self._status_label.setText("Paused")
            self._status_label.setStyleSheet(f"color: {MUTED}; font-weight: 700;")

        self._start_button.setEnabled(
            not snapshot.is_running
            and self._halted_reason is None
            and snapshot.supported_limit_reason is None
        )
        self._pause_button.setEnabled(snapshot.is_running)
        self._fresh_gas_flow.value_label.setText(format_flow(snapshot.fresh_gas_flow_l_min))
        self._delivered.value_label.setText(
            format_percent(snapshot.delivered_concentration_fraction)
        )
        self._alveolar_ventilation.value_label.setText(
            format_flow(snapshot.alveolar_ventilation_l_min)
        )
        self._cardiac_output.value_label.setText(format_flow(snapshot.cardiac_output_l_min))

    def _refresh_instruments(self) -> None:
        """Write the frame-cost table, and state what it does and does not cover."""

        for cells, stage in zip(self._instrument_cells, self._cost.stages(), strict=True):
            # "not measured", never "0.00 ms". A stage with no samples reads as
            # a stage that costs nothing, and `paint` is exactly the stage that
            # records none when the platform delivers no paint events - which
            # is the offscreen case, and the one where a zero would be read as
            # the finding this spike exists to produce.
            if not stage.samples:
                for cell in cells:
                    cell.setText("not measured")

                continue

            cells[0].setText(f"{stage.last_ms:.2f} ms")
            cells[1].setText(f"{stage.median_ms:.2f} ms")
            cells[2].setText(f"{stage.p90_ms:.2f} ms")

        self._instrument_note.setText(
            f"{self._last_point_count} points over {len(TRACES)} traces, "
            f"{self._columns} columns, render budget {RENDER_INTERVAL_S * 1000:.0f} ms. "
            "paint is this widget's own paintEvent — CPU work in this process only, "
            "excluding the compositor and the GPU. Statistics are the last "
            "120 frames and reset when the rate, the window, the columns or "
            "antialiasing changes."
        )

    # ------------------------------------------------------- public surface

    @property
    def frame_cost(self) -> FrameCost:
        """The stage timings of the frames drawn so far.

        Public because the self-check reads them and because they are what the
        spike exists to produce; the panel and the check read the same object,
        so a number on screen and a number in a log cannot disagree.
        """

        return self._cost

    @property
    def point_count(self) -> int:
        """How many points the last frame put on the plot, across every trace."""

        return self._last_point_count

    def stop_timers(self) -> None:
        """Stop both loops, so a caller can drive the frames itself.

        What `--self-check` uses. Left running, the timers advance the run
        while the check is stepping it, so how far the run got would be a
        function of how long the process took rather than of what was asked
        for - and a check whose input depends on the host's scheduler proves
        less each time it passes.
        """

        self._step_timer.stop()
        self._render_timer.stop()

    def set_playback_rate(self, rate: PlaybackRate) -> None:
        """Select a playback rate, as the selector does.

        Resets the statistics for the reason the selector's own handler does:
        a window averaged across a rate change describes neither rate.
        """

        self._playback_rate = rate
        self._rate_box.setCurrentIndex(SUPPORTED_PLAYBACK_RATES.index(rate))
        self._cost.reset()

    # -------------------------------------------------------------- handlers

    def _on_start(self) -> None:
        try:
            self._controller.start()
        except AnesthesiaSimulationError as error:
            self._halt(str(error))
            return

        self._render_frame()

    def _on_pause(self) -> None:
        self._controller.pause()
        self._render_frame()

    def _on_reset(self) -> None:
        self._controller.reset()
        self._halted_reason = None
        self._cost.reset()
        self._render_frame()

    def _halt(self, reason: str) -> None:
        """Stop the run on a failed step, and say so rather than going quiet."""

        self._halted_reason = reason
        self._controller.pause()
        self._render_frame()

    def _on_rate_change(self, index: int) -> None:
        self._playback_rate = SUPPORTED_PLAYBACK_RATES[index]
        self._cost.reset()
        self._render_frame()

    def _on_time_base_change(self, index: int) -> None:
        data = self._time_base_box.itemData(index)
        self._time_base = (
            None
            if data == FIT_RUN_KEY
            else next(base for base in SELECTABLE_TIME_BASES if base.span_s == data)
        )
        self._cost.reset()
        self._render_frame()

    def _on_columns_change(self, index: int) -> None:
        self._columns = self._columns_box.itemData(index)
        self._cost.reset()
        self._render_frame()

    def _on_antialias_change(self) -> None:
        enabled = self._antialias_box.isChecked()

        for curve in self._curves:
            curve.setData(antialias=enabled)

        self._cost.reset()
        self._render_frame()

    def _on_fresh_gas_flow(self) -> None:
        self._controller.set_fresh_gas_flow(self._fresh_gas_flow.value())

    def _on_delivered(self) -> None:
        self._controller.set_delivered_concentration(self._delivered.value() / 100.0)

    def _on_alveolar_ventilation(self) -> None:
        self._controller.set_alveolar_ventilation(self._alveolar_ventilation.value())

    def _on_cardiac_output(self) -> None:
        self._controller.set_cardiac_output(self._cardiac_output.value())


def run_self_check(seconds: float, rate_multiplier: int) -> int:
    """Drive the window headlessly and assert what it drew, without a display.

    The spike ships no test - it is disposable, and a test of it in `tests/`
    would be a shipped asset for a throwaway tree. This is the substitute, and
    it is what proves the thing runs a real case end to end: it advances a run
    at a real playback rate, draws real frames through the real render path,
    and then checks that every trace's newest point agrees with the readout
    printed beneath it. A swapped compartment, a missing factor of a hundred
    or a chart drawn from a stale window all fail here.

    Args:
        seconds: How much simulated time to advance.
        rate_multiplier: The playback rate to advance it at.

    Returns:
        A process exit code: 0 when every check passed.
    """

    controller = SimulationController()
    window = SpikeWindow(controller)
    window.resize(1400, 950)
    window.stop_timers()
    window.show()
    rate = next(
        candidate
        for candidate in SUPPORTED_PLAYBACK_RATES
        if candidate.multiplier == rate_multiplier
    )
    window.set_playback_rate(rate)
    controller.start()
    ticks = round(seconds / (rate.multiplier * SIMULATION_TICK_INTERVAL_S))

    for tick in range(ticks):
        window.step_tick()

        # Two steps per frame, as the shipped cadence has: the render interval
        # is twice the tick interval.
        if tick % 2 == 1:
            window.render_tick()
            QApplication.processEvents()

    snapshot = controller.snapshot()
    failures = verify_trace_binding(controller, snapshot, SELF_CHECK_TOLERANCE_PERCENT)

    if window.point_count == 0:
        failures.append("the chart drew no points after a run")

    print(f"ran {snapshot.elapsed_s:.1f} s of simulated time at {rate.multiplier}x")
    print(f"chart drew {window.point_count} points over {len(TRACES)} traces")
    print(f"{'stage':<16}{'last ms':>10}{'median ms':>11}{'p90 ms':>10}")

    for stage in window.frame_cost.stages():
        print(
            f"{stage.label:<16}{stage.last_ms:>10.3f}{stage.median_ms:>11.3f}{stage.p90_ms:>10.3f}"
        )

    # Two of the five figures above mean nothing in this container, and saying
    # so beside them is the point: a number printed without its limitation is
    # read as a measurement. `paint` here is an offscreen software rasteriser
    # with no GPU, which `PL-QXSB` measured at 18-28 ms even for a frame where
    # nothing changed; `timer lateness` is zero because this check drives the
    # loop itself rather than waiting on a timer. Both are what `PL-X9T3` has
    # to run on real hardware to get.
    print(
        "paint is an offscreen software rasteriser here and is not a paint cost; "
        "timer lateness is zero because this check drives its own frames. "
        "Both are PL-X9T3's to measure on real hardware."
    )

    for failure in failures:
        print(f"FAIL {failure}")

    print("self-check passed" if not failures else f"self-check failed ({len(failures)})")

    return 1 if failures else 0


def save_screenshot(path: str) -> int:
    """Draw one frame of a short run and write the window to a PNG.

    `PL-2QMK` records that no session in this container can visually confirm a
    chart change, because Flet's web renderer fetches Flutter assets the egress
    proxy denies. `PL-QXSB` claims Qt removes that, since it renders offscreen
    in this very container. This is the claim being exercised rather than
    repeated: if it writes a picture of the real interface, headless screenshot
    review of a chart change is available to every future session, which is
    what `presentation-safety`'s open items are waiting on.

    Args:
        path: Where to write the PNG.

    Returns:
        A process exit code: 0 when the file was written.
    """

    controller = SimulationController()
    window = SpikeWindow(controller)
    window.resize(1400, 950)
    window.stop_timers()
    window.show()
    window.set_playback_rate(next(r for r in SUPPORTED_PLAYBACK_RATES if r.multiplier == 60))
    controller.set_delivered_concentration(0.02)
    controller.start()

    for tick in range(120):
        window.step_tick()

        if tick == 60:
            # A dial change mid-run, so the picture shows the feature the
            # chart is most often wrong about (`PL-4RBD`) rather than a smooth
            # curve that would look right either way.
            controller.begin_control_adjustment()
            controller.set_delivered_concentration(0.04)

        if tick % 2 == 1:
            window.render_tick()

    QApplication.processEvents()
    written = window.grab().save(path)
    print(f"{'wrote' if written else 'failed to write'} {path}")

    return 0 if written else 1


def main(argv: list[str] | None = None) -> int:
    """Run the spike, or check it."""

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="advance a run headlessly, assert what the chart drew, and exit",
    )
    parser.add_argument(
        "--seconds", type=float, default=1800.0, help="simulated seconds for --self-check"
    )
    parser.add_argument(
        "--rate", type=int, default=300, help="playback multiplier for --self-check"
    )
    parser.add_argument(
        "--screenshot",
        metavar="PATH",
        help="render one frame of a short run offscreen and write it to a PNG",
    )
    parser.add_argument(
        "--opengl",
        action="store_true",
        help="draw curves through OpenGL, a paint-cost lever worth measuring both ways",
    )
    arguments = parser.parse_args(argv)

    if arguments.opengl:
        pg.setConfigOption("useOpenGL", True)

    application = QApplication(sys.argv[:1])

    if arguments.self_check:
        return run_self_check(arguments.seconds, arguments.rate)

    if arguments.screenshot:
        return save_screenshot(arguments.screenshot)

    window = SpikeWindow(SimulationController())
    window.resize(1400, 950)
    window.show()

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
