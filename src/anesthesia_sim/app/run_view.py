"""One run on the dashboard: its controller, its controls and its readouts, in PySide6.

`RunView` is the per-run half of the dashboard along `PL-B9PY`'s seam: what
two displayed runs cannot share - a controller, seven readouts, four
settings, the transport, the agent identity, the notices, the accounting
and control-change panels - lives here, and `SimulationView` holds what
they do share. It is instantiable twice, and nothing in it reaches another
run.

Every claim it displays is settled by `app/dashboard_frame.py` without a
toolkit; this class calls those functions once per tick, in the order
`refresh` fixes, and writes the results into widgets that decide nothing
(`PL-25KS`, decision D2). No number is formatted here and no colour is
declared here: colours are `app/theme.py`'s and reach a widget as f-strings
over the theme names (decision D10).

**Agent colour has one writer.** `_apply_agent_color_scheme` is the only
method under `app/` that writes the ISO 5360 identity pair, and it writes
it on every tick to exactly six controls, whether or not each is on screen,
so the chip that replaces the selector when a run starts is already the
right colour the frame it appears (`PL-61WW`). `tools/agent_identity_check.py`
reads that method to learn the identity set and holds every member to the
rule that nothing carrying agent colour is rendered disabled: the selector
is written `setDisabled(locked)` beside `setHidden(locked)` with the same
operand, so it draws nothing while it cannot be used.

**A refusal is a notice; a raise is a halt.** `_apply_setting` is the one
gate every forwarded setting passes through. `SimulationConfigurationError`
means the core rejected the value and changed nothing, so the run goes on
under a "Setting refused" banner. Any other exception stops the run:
`SimulationDomainLimitError` as the supported run length, everything else as
a failure, per `dashboard_frame.halt_disposition` (`PL-V6M0`, `PL-Y5WR`,
`PL-YK2V`). A halted run says so from its own snapshot, through
`present_halt`, before any frame is attempted: the frame is the shared
render path, and when that is what raised, a halt reported only through it
would leave every status word reading "Paused" over a failed controller
(`PL-25KS`).

**Timers move the run and nothing else** (decision D7). One `QTimer` per
run drives `step_tick`, which advances the controller by the playback
rate's steps and never presents; the dashboard's own render timer draws.
No wall clock is read: simulation time is a count of steps taken.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Final

from PySide6.QtCore import QSignalBlocker, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.control_timeline import AdjustmentGrouping, ControlAdjustment
from anesthesia_sim.app.controller import SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    ACCOUNTING_INITIAL_DETAIL_TEXT,
    ACCOUNTING_UNIT_CAPTION,
    CONTROL_TIMELINE_CAPTION,
    CONTROL_TIMELINE_HEADING,
    INTERPRETATION_DISCLAIMER_TEXT,
    PAUSE_LABEL,
    PLAYBACK_LABEL,
    READOUT_PANELS,
    READOUT_RESERVATIONS,
    RESET_LABEL,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    START_LABEL,
    Emphasis,
    HaltDisposition,
    StatusWord,
    Transport,
    accounting,
    compared_panel_heading,
    compared_run_line,
    compared_run_notice,
    delivered_fraction,
    halt_disposition,
    new_case_question,
    notice,
    off_scale_notice,
    readouts,
    refused_setting_notice,
    setting_readouts,
    status_word,
    substance_heading,
    timeline_panel,
    transport,
    wash_in_state,
)
from anesthesia_sim.app.formatting import format_playback_rate, format_subtitle
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_widgets import (
    NewCaseDialog,
    NoticeLabel,
    ParameterSlider,
    ReadoutRow,
    popup_stylesheet,
    selector_stylesheet,
    styled_label,
    transport_button_stylesheet,
)
from anesthesia_sim.app.theme import (
    ACCENT_TEXT,
    ACCOUNTING_STATUS_SIZE,
    AGENT_COLOR_SCHEMES,
    AGENT_SELECTOR_WIDTH,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PANEL,
    PANEL_PADDING,
    PANEL_RADIUS,
    PLAYBACK_RATE_SELECTOR_WIDTH,
    RUNNING_AGENT_DISPLAY_PADDING,
    WARNING,
    AgentColorScheme,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters

# Adding a built-in agent without a verified identification colour would make
# the selector silently lose a safety cue (ISO 5360 Table 2, footnote b). Fail
# at import instead. This concerns presentation metadata only; the agent's
# scientific parameters stay in their validated data files.
if set(AGENT_COLOR_SCHEMES) != set(AGENT_DATA_FILENAMES):
    raise RuntimeError("AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents")

#: (agent_id, display_name) for every built-in agent, in `AGENT_DATA_FILENAMES`
#: order, read once from the data files so no display name is restated here.
AVAILABLE_AGENTS: Final[tuple[tuple[str, str], ...]] = tuple(
    (agent_id, load_agent_parameters(agent_id).display_name) for agent_id in AGENT_DATA_FILENAMES
)

#: The same names keyed by id, for the one lookup that has an agent id and no
#: snapshot to read the name off: the agent a reader has just selected, which
#: the controller is not answering for until they confirm it.
AGENT_DISPLAY_NAMES: Final[Mapping[str, str]] = dict(AVAILABLE_AGENTS)

#: The theme colour each status emphasis is drawn in. `dashboard_frame` names
#: the role so that it declares no colour; this is where the role meets the
#: palette, and the only place.
_EMPHASIS_COLOR: Final[Mapping[Emphasis, str]] = {
    Emphasis.MUTED: MUTED,
    Emphasis.ACCENT: ACCENT_TEXT,
    Emphasis.WARNING: WARNING,
}

#: The clock panel's index in the readout row, from the table the row is
#: built from rather than a literal position.
_CLOCK_PANEL_INDEX: Final = next(
    index for index, panel in enumerate(READOUT_PANELS) if panel.quantity is None
)

#: Milliseconds per second, for the timer interval `SIMULATION_TICK_INTERVAL_S`
#: states in seconds.
_MILLISECONDS_PER_SECOND: Final = 1000

#: The header badge's inset. Narrower than the chip's, which carries two lines
#: and sits among controls; a bare spacing literal is decision D9's interim.
_HEADER_BADGE_PADDING: Final = 6

#: Object names the agent-coloured surfaces are styled through, so a surface's
#: stylesheet reaches that frame and not the labels inside it.
_HEADER_BADGE_NAME: Final = "agentHeaderBadge"
_RUNNING_AGENT_DISPLAY_NAME: Final = "runningAgentDisplay"


def _surface_stylesheet(object_name: str, scheme: AgentColorScheme) -> str:
    """A frame filled in the agent's colour and edged in its foreground.

    The edge is the channel that keeps a sevoflurane badge visible at all:
    its fill is 1.27:1 against the page, so without a border the coloured
    region a reader is meant to recognise loses its shape (`PL-GNN1`).
    """

    return (
        f"QFrame#{object_name} {{ background-color: {scheme.fill}; color: {scheme.foreground}; "
        f"border: 1px solid {scheme.foreground}; border-radius: {PANEL_RADIUS}px; }}"
    )


def _text_stylesheet(scheme: AgentColorScheme) -> str:
    """A label in the agent's foreground over its fill."""

    return f"color: {scheme.foreground}; background-color: {scheme.fill};"


def _selector_stylesheet(scheme: AgentColorScheme) -> str:
    """The agent selector in the running agent's pair, edged in its foreground.

    The popup it opens is not in the agent's colours and does not vary with
    the agent: it lists all three, each row carrying its own ISO 5360 fill
    as item data, so the list's own surface is the interface's
    (`popup_stylesheet`). Appending it here rather than setting it once at
    construction is what makes it survive the selector being laid out
    (`PL-0NVN`).
    """

    return (
        f"QComboBox {{ background-color: {scheme.fill}; color: {scheme.foreground}; "
        f"border: 1px solid {scheme.foreground}; border-radius: {PANEL_RADIUS}px; "
        f"padding: 4px 8px; font-weight: bold; }} " + popup_stylesheet()
    )


def _panel(object_name: str) -> QFrame:
    """A PANEL-coloured, rounded frame scoped by name so its children keep their own colours."""

    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setStyleSheet(
        f"QFrame#{object_name} {{ background-color: {PANEL}; border-radius: {PANEL_RADIUS}px; }}"
    )

    return frame


def _emphasised(label: QLabel, word: StatusWord) -> None:
    """Write a status word and the colour of its emphasis."""

    label.setText(word.text)
    label.setStyleSheet(f"color: {_EMPHASIS_COLOR[word.emphasis]};")


class RunView(QWidget):
    """One run's widgets, controller, handlers, refresh and halt.

    Built with nothing drawn: the dashboard presents every run once its
    charts exist, so the first frame is drawn from one window and one
    snapshot per run rather than from whatever each run built itself from.
    The build methods return widgets for `SimulationView` to place, because
    where a run's parts sit relative to another run's is the dashboard's
    decision.

    Refuses nothing at construction. What it refuses per tick is decided
    by `dashboard_frame`: which setting values the core rejects, and how a
    raise is reported, are read from the exception and never guessed at
    (`PL-V6M0`, `PL-Y5WR`, `PL-YK2V`; see the module docstring).

    Attributes:
        controller: The run.
        presentation_requested: Emitted with the coalesce flag when this
            run's action owes the dashboard a frame. `True` leaves the frame
            to the render tick - a slider drag - and `False` asks for one
            now; `SimulationView.present` is what answers (`PL-R2YM`).
        case_restarted: Emitted when this run has started over from
            induction. On a trunk that is a new case, so every branch taken
            from the run that no longer exists stops being a comparison of
            anything; the dashboard is what acts on it, because which other
            runs are on screen is not this view's to know.
    """

    presentation_requested = Signal(bool)
    case_restarted = Signal()

    def __init__(self, controller: SimulationController, parent: QWidget | None = None) -> None:
        """Build one run's controls and readouts from its first snapshot.

        Args:
            controller: The run this view drives and displays.
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.controller = controller
        snapshot = controller.snapshot()

        # Why the last setting change did not take, or None if it did. Held
        # here rather than in the controller because a refused setting
        # changes nothing about the simulation, so there is no core state
        # for it to belong to.
        self._rejected_setting_notice: str | None = None
        self._playback_rate: PlaybackRate = DEFAULT_PLAYBACK_RATE
        self._adjustment_grouping = AdjustmentGrouping()
        # The agent a reader has asked for and not yet confirmed, and the
        # dialog asking them. Together they are the state "a destructive
        # confirmation is open"; `_resolve_new_case` clears the first before
        # acting, which is what makes answering the dialog idempotent.
        self._pending_agent_id: str | None = None
        self._new_case_dialog: NewCaseDialog | None = None
        # The frame this run was last refreshed from and its place in it,
        # so a coalesced slider change can rewrite this run's own labels at
        # once against the picture still on screen.
        self._frame: ChartFrame | None = None
        self._run_index = 0
        # Whether a second run is on the chart. The dashboard writes it
        # through `set_comparing`, because how many runs are displayed is its
        # fact and not this view's; it reaches the transport as the third
        # reason an agent selector may be replaced by the chip.
        self._comparing = False

        # What this run is called, where the chart's legend calls it that.
        # Its own label rather than a word inside the agent badge, because the
        # badge carries the ISO 5360 identity pair and `_apply_agent_color_scheme`
        # is the only writer of it (`.claude/rules/ui-color.md`); a run's name
        # is not agent identity and must not take an agent's colour. Hidden
        # while one run is displayed, where nothing is ambiguous and a name
        # would be standing text saying what the single panel already says.
        #
        # `set_run_name` is deliberately not a chart-shaped or run-shaped
        # method: naming the view in its own header is what every view will
        # owe an area (`.claude/rules/ui-areas.md`, `PL-TH35`), so it is given
        # a name the next view could take.
        self._run_name_text = styled_label("", color=INK, bold=True)
        self._run_name_text.setHidden(True)
        # Kept beside the label because the banner needs it too, and the
        # banner is written on a path that has no frame to read it from
        # (`_write_notice`). Reading it back off the widget would make the
        # attribution depend on a label's text, which is a display detail.
        self._run_name: str | None = None
        self._status_text = styled_label("", color=MUTED, bold=True)
        _emphasised(self._status_text, status_word(snapshot))
        self._notice_text = NoticeLabel(self)

        self._subtitle_text = styled_label(format_subtitle(snapshot.agent_display_name), color=INK)
        self._subtitle_text.setFont(_bold(self._subtitle_text.font()))
        self._agent_header_badge = QFrame()
        self._agent_header_badge.setObjectName(_HEADER_BADGE_NAME)
        badge = QHBoxLayout(self._agent_header_badge)
        badge.setContentsMargins(
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
        )
        badge.addWidget(self._subtitle_text)

        # Every widget whose visibility is written here is built with this
        # view as its parent: shown parentless, even for the instant before
        # a layout adopts it, a widget is a top-level window of its own.
        self._agent_dropdown = QComboBox(self)
        self._agent_dropdown.setFixedWidth(AGENT_SELECTOR_WIDTH)

        for index, (agent_id, display_name) in enumerate(AVAILABLE_AGENTS):
            scheme = AGENT_COLOR_SCHEMES[agent_id]
            self._agent_dropdown.addItem(display_name, userData=agent_id)
            self._agent_dropdown.setItemData(
                index, QColor(scheme.fill), Qt.ItemDataRole.BackgroundRole
            )
            self._agent_dropdown.setItemData(
                index, QColor(scheme.foreground), Qt.ItemDataRole.ForegroundRole
            )

        self._agent_dropdown.setCurrentIndex(self._agent_dropdown.findData(snapshot.agent_id))
        self._agent_dropdown.currentIndexChanged.connect(self._handle_agent_change)

        # The running agent's identity, carried by a control that is never
        # disabled and so never recoloured by the theme; it stands where the
        # selector stood, at the selector's width, so the transport controls
        # beside it do not move when a run starts (`PL-61WW`).
        self._running_agent_text = styled_label(snapshot.agent_display_name, color=INK, bold=True)
        # Blank until something locks the selector. `_write_transport` is
        # the only writer of this line and it writes the reason in the same
        # call that reveals the chip, so the caption a reader sees is always
        # the lock actually in force rather than whichever came first.
        self._running_agent_lock_text = styled_label("", color=INK, size_px=METRIC_QUALIFIER_SIZE)
        self._running_agent_display = QFrame(self)
        self._running_agent_display.setObjectName(_RUNNING_AGENT_DISPLAY_NAME)
        self._running_agent_display.setFixedWidth(AGENT_SELECTOR_WIDTH)
        chip = QVBoxLayout(self._running_agent_display)
        chip.setContentsMargins(
            RUNNING_AGENT_DISPLAY_PADDING,
            RUNNING_AGENT_DISPLAY_PADDING,
            RUNNING_AGENT_DISPLAY_PADDING,
            RUNNING_AGENT_DISPLAY_PADDING,
        )
        chip.setSpacing(0)
        chip.addWidget(self._running_agent_text)
        chip.addWidget(self._running_agent_lock_text)

        self._start_button = QPushButton(START_LABEL)
        self._pause_button = QPushButton(PAUSE_LABEL)
        self._reset_button = QPushButton(RESET_LABEL)

        # The transport's colours are the interface's rather than the host
        # appearance's (`PL-DHBX`); `transport_button_stylesheet` carries why.
        for button in (self._start_button, self._pause_button, self._reset_button):
            button.setStyleSheet(transport_button_stylesheet())

        self._write_transport(self._transport_lock(snapshot))
        self._start_button.clicked.connect(self._handle_start)
        self._pause_button.clicked.connect(self._handle_pause)
        self._reset_button.clicked.connect(self._handle_reset)

        # How fast the run is played: a view control that decides how many
        # steps a tick takes and never how large a step is. It is never
        # disabled, and Reset leaves it alone like every other setting.
        self._playback_rate_dropdown = QComboBox()
        self._playback_rate_dropdown.setFixedWidth(PLAYBACK_RATE_SELECTOR_WIDTH)
        self._playback_rate_dropdown.setStyleSheet(selector_stylesheet())

        for rate in SUPPORTED_PLAYBACK_RATES:
            self._playback_rate_dropdown.addItem(
                format_playback_rate(rate.multiplier), userData=rate.multiplier
            )

        self._playback_rate_dropdown.setCurrentIndex(
            self._playback_rate_dropdown.findData(self._playback_rate.multiplier)
        )
        self._playback_rate_dropdown.currentIndexChanged.connect(self._handle_playback_rate_change)

        self._compartment_substance_text = styled_label(
            substance_heading(snapshot), color=INK, bold=True
        )
        self._interpretation_text = styled_label(
            INTERPRETATION_DISCLAIMER_TEXT, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True
        )
        self._readout_row = ReadoutRow(
            readouts(snapshot, self._playback_rate), reservations=READOUT_RESERVATIONS
        )

        (
            self._fresh_gas_flow_slider,
            self._delivered_concentration_slider,
            self._alveolar_ventilation_slider,
            self._cardiac_output_slider,
        ) = (ParameterSlider(setting) for setting in setting_readouts(snapshot))
        handlers: tuple[tuple[ParameterSlider, Callable[[float], None]], ...] = (
            (self._fresh_gas_flow_slider, self._handle_fresh_gas_flow_change),
            (self._delivered_concentration_slider, self._handle_delivered_concentration_change),
            (self._alveolar_ventilation_slider, self._handle_alveolar_ventilation_change),
            (self._cardiac_output_slider, self._handle_cardiac_output_change),
        )

        for slider, handler in handlers:
            slider.adjustment_started.connect(self._handle_adjustment_start)
            slider.value_changed.connect(handler)

        # The two sidebar panels' headings. Instance labels rather than
        # widgets built inside `build_sidebar_panels`, because each has to
        # gain and lose this run's name as the dashboard's run set changes,
        # and `set_run_name` is the one writer of that name (`PL-C3GS`).
        self._accounting_heading_text = styled_label(ACCOUNTING_HEADING, color=INK, bold=True)
        self._control_timeline_heading_text = styled_label(
            CONTROL_TIMELINE_HEADING, color=INK, bold=True
        )

        initial_accounting = accounting(snapshot)
        self._agent_accounting_status_text = styled_label(
            "", color=ACCENT_TEXT, size_px=ACCOUNTING_STATUS_SIZE, bold=True
        )
        _emphasised(self._agent_accounting_status_text, initial_accounting.status)
        self._agent_accounting_detail_text = styled_label(
            ACCOUNTING_INITIAL_DETAIL_TEXT, color=MUTED, wrap=True
        )
        self._agent_amounts_text = styled_label(initial_accounting.amounts, color=MUTED)

        self._control_timeline_text = styled_label(
            timeline_panel((), 0).entries, color=MUTED, size_px=METRIC_QUALIFIER_SIZE
        )
        self._control_timeline_overflow_text = styled_label(
            "", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self._control_timeline_overflow_text.setParent(self)
        self._control_timeline_overflow_text.setHidden(True)

        # This run's rather than the chart's: whether a trace is clipped is
        # a property of the samples this run drew, and one line over two
        # runs could not say whose trace left the plot.
        self._off_scale_text = styled_label(
            "", color=WARNING, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self._off_scale_text.setParent(self)
        self._off_scale_text.setHidden(True)
        self._wash_in_state_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE)

        self._apply_agent_color_scheme(snapshot.agent_id)

        self._step_timer = QTimer(self)
        self._step_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._step_timer.setInterval(round(SIMULATION_TICK_INTERVAL_S * _MILLISECONDS_PER_SECOND))
        self._step_timer.timeout.connect(self.step_tick)

    # ------------------------------------------------------------ reading

    def snapshot(self) -> SimulationSnapshot:
        """This run's state at this instant.

        Read by the dashboard once per frame and handed back to `refresh`,
        so the readouts and the traces of a frame are one instant of one run.
        """

        return self.controller.snapshot()

    @property
    def is_running(self) -> bool:
        """Whether this run is advancing."""

        return self.controller.is_running

    def adjustments(self, snapshot: SimulationSnapshot) -> tuple[ControlAdjustment, ...]:
        """The run's control changes grouped into acts, regrouped only when the record changed.

        Args:
            snapshot: The snapshot read for this frame.

        Returns:
            What `control_timeline.group_adjustments` returns for its
            timeline, from this run's own `AdjustmentGrouping` (`PL-1PSX`).
        """

        return self._adjustment_grouping.of(snapshot.control_timeline)

    @property
    def _elapsed_time_text(self) -> QLabel:
        """The clock panel's value line."""

        return self._readout_row.panels[_CLOCK_PANEL_INDEX].value_label

    @property
    def _playback_rate_text(self) -> QLabel:
        """The clock panel's second line, which carries the playback rate."""

        return self._readout_row.panels[_CLOCK_PANEL_INDEX].secondary_label

    # ---------------------------------------------------------- refreshing

    def refresh(self, snapshot: SimulationSnapshot, frame: ChartFrame, run_index: int) -> None:
        """Write every widget of this run from one snapshot and the frame drawn from it.

        The order is fixed and two of its steps depend on it: the agent
        colour is written before anything that shows it, and the notice
        banner last, so that it describes the state every other widget is
        already showing.

        Args:
            snapshot: The run's state this tick, read once by the caller.
            frame: The chart frame assembled from that same snapshot.
            run_index: This run's index in `frame.runs`.

        Raises:
            IndexError: If `run_index` is not one of the frame's runs
                (`dashboard_frame.off_scale_notice`).
        """

        self._frame = frame
        self._run_index = run_index
        run_frame = frame.runs[run_index]
        lock = self._transport_lock(snapshot)

        self._apply_agent_color_scheme(snapshot.agent_id)
        self._write_transport(lock)

        with QSignalBlocker(self._agent_dropdown):
            self._agent_dropdown.setCurrentIndex(self._agent_dropdown.findData(snapshot.agent_id))

        self._running_agent_text.setText(snapshot.agent_display_name)
        _emphasised(self._status_text, status_word(snapshot))
        self._subtitle_text.setText(format_subtitle(snapshot.agent_display_name))
        self._compartment_substance_text.setText(substance_heading(snapshot))
        self._readout_row.set_readouts(readouts(snapshot, self._playback_rate))

        for slider, setting in zip(self._sliders(), setting_readouts(snapshot), strict=True):
            slider.set_setting(setting)

        panel = accounting(snapshot)
        _emphasised(self._agent_accounting_status_text, panel.status)
        self._agent_accounting_detail_text.setText(panel.detail)
        self._agent_amounts_text.setText(panel.amounts)

        # Both lines go into a column the runs share, so each is named while
        # more than one run is drawn: the value is this run's, and nothing
        # else in that column says so (`PL-25DD`).
        off_scale = off_scale_notice(frame, run_index)
        self._off_scale_text.setText(
            compared_run_line(off_scale, frame, run_index) if off_scale is not None else ""
        )
        self._off_scale_text.setHidden(off_scale is None)
        self._wash_in_state_text.setText(
            compared_run_line(
                wash_in_state(snapshot, run_frame.undrawn_wash_in_stretches), frame, run_index
            )
        )

        timeline = timeline_panel(self.adjustments(snapshot), run_frame.undrawn_control_marks)
        self._control_timeline_text.setText(timeline.entries)
        self._control_timeline_overflow_text.setText(timeline.overflow)
        self._control_timeline_overflow_text.setHidden(not timeline.overflow)

        self._write_notice(snapshot)

    def _write_notice(self, snapshot: SimulationSnapshot) -> None:
        """Write the banner for this run, named while a second run is drawn.

        The one writer of it, because there are two callers and the
        attribution must not be a thing either could forget: `refresh` has a
        frame and `present_halt` deliberately has none. That is also why the
        run's name comes from `set_run_name` rather than from the frame -
        `dashboard_frame.compared_run_notice` carries the argument.

        Args:
            snapshot: The run's state this tick.
        """

        self._notice_text.set_notice(
            compared_run_notice(notice(snapshot, self._rejected_setting_notice), self._run_name)
        )

    def _refresh_against_last_frame(self) -> None:
        """Rewrite this run's own widgets now, against the frame still on screen.

        What a coalesced slider change owes at once is the view beside the
        dial, which has to agree with the snapshot the moment the setting is
        applied (`PL-018`); the frame itself waits for the render tick
        (`PL-R2YM`). Before the first presentation there is no frame to
        refresh against, and the first presentation writes everything.
        """

        if self._frame is not None:
            self.refresh(self.snapshot(), self._frame, self._run_index)

    def present_halt(self) -> None:
        """Say this run has stopped, from its snapshot alone, with no frame drawn.

        The status word, the transport and the notice banner are the three
        widgets that state whether the run is going and why it is not, and
        none of them needs a chart frame to be written. So they are written
        here, before any frame is attempted, because the frame is what may
        be failing: a halt for a raise out of the shared render path
        presented only through that path would leave every status word
        reading "Paused" over a failed controller, and no banner naming the
        exception (`PL-25KS`). `refresh` rewrites the same three on the next
        frame that can be drawn.
        """

        snapshot = self.snapshot()
        _emphasised(self._status_text, status_word(snapshot))
        self._write_transport(self._transport_lock(snapshot))
        self._write_notice(snapshot)

    def _transport_lock(self, snapshot: SimulationSnapshot) -> Transport:
        """This run's transport enablement, with both facts `dashboard_frame` cannot read.

        `opened_from` is read live rather than cached at construction,
        because a run's kind is the controller's to state and nothing here
        would learn of a change to it.

        Args:
            snapshot: The run's state this tick.

        Returns:
            `dashboard_frame.transport`'s answer for this run.
        """

        return transport(
            snapshot, is_branch=self.controller.opened_from is not None, comparing=self._comparing
        )

    def set_comparing(self, comparing: bool) -> None:
        """Say whether a second run is on the chart, and rewrite the transport at once.

        Called by the dashboard whenever its run set changes, so a selector
        locked by a fork is locked from the frame the branch appears rather
        than from the next tick.

        Args:
            comparing: Whether more than one run is displayed.
        """

        self._comparing = comparing
        self._write_transport(self._transport_lock(self.snapshot()))

    def _write_transport(self, lock: Transport) -> None:
        """Write the transport's enablement and which of the selector and the chip is shown.

        The selector is written `setDisabled` beside `setHidden` with the
        same operand, which is what `tools/agent_identity_check.py` holds
        the identity set to: it draws nothing while it cannot be used.

        Args:
            lock: `dashboard_frame.transport`'s result for this snapshot.
        """

        self._agent_dropdown.setDisabled(lock.selector_locked)
        self._agent_dropdown.setHidden(lock.selector_locked)
        self._running_agent_display.setVisible(lock.selector_locked)
        self._running_agent_lock_text.setText(lock.selector_lock_reason)
        self._start_button.setEnabled(lock.start_enabled)
        self._pause_button.setEnabled(lock.pause_enabled)
        self._reset_button.setEnabled(lock.reset_enabled)

    def _apply_agent_color_scheme(self, agent_id: str) -> None:
        """Write the agent's ISO 5360 pair to the six controls that carry it, and to nothing else.

        The single writer of agent colour. Written on every tick, whether or
        not each control is on screen, so the chip revealed on the next
        state change is already the running agent's colour. One
        `setStyleSheet` per control, so `tools/agent_identity_check.py` can
        read the identity set off this method.

        Args:
            agent_id: The running agent, from this tick's snapshot.
        """

        scheme = AGENT_COLOR_SCHEMES[agent_id]
        self._agent_header_badge.setStyleSheet(_surface_stylesheet(_HEADER_BADGE_NAME, scheme))
        self._subtitle_text.setStyleSheet(_text_stylesheet(scheme))
        self._running_agent_display.setStyleSheet(
            _surface_stylesheet(_RUNNING_AGENT_DISPLAY_NAME, scheme)
        )
        self._running_agent_text.setStyleSheet(_text_stylesheet(scheme))
        self._running_agent_lock_text.setStyleSheet(_text_stylesheet(scheme))
        self._agent_dropdown.setStyleSheet(_selector_stylesheet(scheme))

    def _sliders(self) -> tuple[ParameterSlider, ...]:
        """The four setting controls in `dashboard_frame.PARAMETER_CONTROLS` order."""

        return (
            self._fresh_gas_flow_slider,
            self._delivered_concentration_slider,
            self._alveolar_ventilation_slider,
            self._cardiac_output_slider,
        )

    # ------------------------------------------------------------ settings

    def _apply_setting(self, apply: Callable[[], None], *, coalesce: bool = False) -> None:
        """Forward one setting to the run, and report how it was received.

        A `SimulationConfigurationError` is a refusal: the core rejected the
        value and changed nothing, so the run goes on and the banner says
        which setting was refused. Any other exception halts the run through
        `_halt_run`; a raise from outside the project's hierarchy is still a
        run that cannot continue (`PL-YK2V`). An accepted setting clears a
        standing refusal.

        The frame is left to the render tick only when `coalesce` is set
        and no refusal was standing before or is standing after: a refusal,
        and the clearing of one, are the states in which the dial on screen
        and the simulation disagree, and neither may wait a tick
        (`PL-R2YM`). A coalesced change still rewrites this run's own
        labels at once.

        Args:
            apply: The controller call that applies the setting.
            coalesce: Whether the caller reports continuously, as a dragged
                slider does.
        """

        settled_notice = self._rejected_setting_notice

        try:
            apply()
        except SimulationConfigurationError as error:
            self._rejected_setting_notice = refused_setting_notice(error)
        except Exception as error:
            self._halt_run(error)
            return
        else:
            self._rejected_setting_notice = None

        deferred = coalesce and settled_notice is None and self._rejected_setting_notice is None

        if deferred:
            self._refresh_against_last_frame()

        self.presentation_requested.emit(deferred)

    def _handle_adjustment_start(self) -> None:
        """Close any open adjustment, so the changes that follow are a new act.

        Not through `_apply_setting`: it records nothing and changes no
        state. Without it two drags of one dial are one adjustment on the
        record.
        """

        self.controller.begin_control_adjustment()

    def _handle_fresh_gas_flow_change(self, flow_l_min: float) -> None:
        self._apply_setting(lambda: self.controller.set_fresh_gas_flow(flow_l_min), coalesce=True)

    def _handle_delivered_concentration_change(self, percent: float) -> None:
        fraction = delivered_fraction(percent)
        self._apply_setting(
            lambda: self.controller.set_delivered_partial_pressure_fraction(fraction), coalesce=True
        )

    def _handle_alveolar_ventilation_change(self, flow_l_min: float) -> None:
        self._apply_setting(
            lambda: self.controller.set_alveolar_ventilation(flow_l_min), coalesce=True
        )

    def _handle_cardiac_output_change(self, flow_l_min: float) -> None:
        self._apply_setting(lambda: self.controller.set_cardiac_output(flow_l_min), coalesce=True)

    # ----------------------------------------------------------- transport

    def _handle_start(self) -> None:
        """Start the run; a start the controller refuses becomes a notice."""

        self._apply_setting(self.controller.start)

    def _handle_pause(self) -> None:
        self.controller.pause()
        self.presentation_requested.emit(False)

    def _handle_reset(self) -> None:
        """Start over: clears the run and a standing refusal, and leaves the playback rate alone.

        `case_restarted` is emitted before the frame is asked for, so the
        dashboard has already dropped any branch of the run that just ended
        by the time the frame is assembled - a branch drawn beside a trunk
        standing back at induction would be two curves asserting one case
        while no longer being one.
        """

        self.controller.reset()
        self._rejected_setting_notice = None
        self.case_restarted.emit()
        self.presentation_requested.emit(False)

    def _handle_playback_rate_change(self, index: int) -> None:
        """Take the rate the reader chose; the next tick reads it.

        Raises:
            SimulationConfigurationError: If the control offers a multiplier
                `SUPPORTED_PLAYBACK_RATES` does not (`playback_rate_for`) -
                a divergence between the two tables is a defect to surface.
        """

        multiplier = self._playback_rate_dropdown.itemData(index)

        if multiplier is None:
            return

        self._playback_rate = playback_rate_for(int(multiplier))
        self.presentation_requested.emit(False)

    # ---------------------------------------------------- the new-case flow

    def _handle_agent_change(self, index: int) -> None:
        """Answer a selection: nothing, a new case at once, or a question.

        The same agent is no change. A run that has recorded nothing has
        nothing to lose and switches at once. Otherwise the selector is
        reverted to the running agent and the reader is asked, because the
        switch discards the case (`PL-R3KB`). While that question is open a
        further selection is reverted and not answered: the open dialog
        names one agent, and its answer must start that agent and no other
        (`PL-25KS`).
        """

        agent_id = self._agent_dropdown.itemData(index)

        if agent_id is None:
            return

        snapshot = self.snapshot()

        if self._pending_agent_id is not None:
            with QSignalBlocker(self._agent_dropdown):
                self._agent_dropdown.setCurrentIndex(
                    self._agent_dropdown.findData(snapshot.agent_id)
                )

            return

        if agent_id == snapshot.agent_id:
            return

        if not snapshot.has_recorded_run:
            self._start_new_case(agent_id)
            return

        self._confirm_new_case(snapshot, agent_id)

    def _start_new_case(self, agent_id: str) -> None:
        """Switch the run to `agent_id` through the setting gate.

        `SimulationController.set_agent` refuses a branch (`PL-TFX5`), and
        that refusal reaches the reader as a refused-setting notice.
        """

        self._apply_setting(lambda: self.controller.set_agent(agent_id))

    def _confirm_new_case(self, snapshot: SimulationSnapshot, agent_id: str) -> None:
        """Ask before discarding a recorded run, with the selector already reverted.

        The selector reads the agent that is actually running for as long
        as the question is open, and the count of changes about to be lost
        is the same grouping the timeline panel lists.
        """

        self._pending_agent_id = agent_id

        with QSignalBlocker(self._agent_dropdown):
            self._agent_dropdown.setCurrentIndex(self._agent_dropdown.findData(snapshot.agent_id))

        question = new_case_question(
            snapshot, AGENT_DISPLAY_NAMES[agent_id], len(self.adjustments(snapshot))
        )
        dialog = NewCaseDialog(question, self)
        dialog.finished.connect(self._handle_new_case_finished)
        # Deleted once answered, or every question asked stays a child of
        # this view: its title on `interface_strings` and its widgets in
        # every walk of the tree (`PL-25KS`).
        dialog.finished.connect(dialog.deleteLater)
        self._new_case_dialog = dialog
        dialog.open()

    def _handle_new_case_finished(self, result: int) -> None:
        self._resolve_new_case(result == QDialog.DialogCode.Accepted)

    def _resolve_new_case(self, confirmed: bool) -> None:
        """Act on the reader's answer once, however many times the dialog reports it.

        The pending agent is cleared before anything else, so a second
        arrival - a dialog reporting its close after the button that closed
        it - finds nothing to act on and cannot undo a switch that has
        already started.

        Args:
            confirmed: True to discard the case and start the new one; False
                to keep it, which rebuilds nothing.
        """

        agent_id = self._pending_agent_id
        self._pending_agent_id = None

        if agent_id is None:
            return

        self._new_case_dialog = None

        if confirmed:
            self._start_new_case(agent_id)
            return

        self.presentation_requested.emit(False)

    # ---------------------------------------------------------------- halt

    def halt(self, error: BaseException) -> None:
        """Stop the run for a raise, recording it as the disposition the raise earns.

        Draws nothing and writes nothing; `_halt_run` and
        `SimulationView._halt_every_run` call `present_halt` after halting.

        Args:
            error: What was raised.
        """

        disposition, reason = halt_disposition(error)

        if disposition is HaltDisposition.SUPPORTED_LIMIT:
            self.controller.halt_at_supported_limit(reason)
        else:
            self.controller.fail(reason)

    def _halt_run(self, error: BaseException) -> None:
        """Halt the run, say so from its own snapshot, then ask for the frame.

        The halt comes first, so a presentation that fails cannot unwind it:
        `SimulationView.present` answers a frame it cannot draw by halting
        every run, and a controller keeps the first reason it was given, so
        this run still reports the raise that stopped it. Its own status
        word and banner are written before the frame is asked for, so a run
        whose frame cannot be drawn still says it stopped.

        Args:
            error: What was raised.
        """

        self.halt(error)
        self.present_halt()
        self.presentation_requested.emit(False)

    # -------------------------------------------------------------- timing

    def step_tick(self) -> None:
        """Advance the run by one tick's worth of steps, and never draw.

        Reads the playback rate once and takes that many steps of
        `SIMULATION_STEP_S` with nothing serviced between them, so a
        setting changed while the run plays lands on a tick boundary
        (`PL-NBWP`). A step the core refuses abandons the rest of the burst
        and halts the run on the last completed step; the slot keeps
        working afterwards, so Reset can restart it. A late tick costs the
        run real time and never changes its trajectory: no step is made up.
        """

        if not self.controller.is_running:
            return

        steps = self._playback_rate.steps_per_tick(
            tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
        )

        try:
            for _ in range(steps):
                self.controller.advance(SIMULATION_STEP_S)
        except Exception as error:
            self._halt_run(error)

    def start_simulation_timer(self) -> None:
        """Start the tick timer; it is never stopped by a failure, only by `stop_timers`."""

        self._step_timer.start()

    def stop_timers(self) -> None:
        """Stop the tick timer; the dashboard's `stop_timers` calls this for every run."""

        self._step_timer.stop()

    # -------------------------------------------------------------- layout

    def build_header_badge(self) -> QWidget:
        """The badge naming the agent this run is on, for the dashboard's header."""

        return self._agent_header_badge

    def build_transport_row(self) -> QWidget:
        """This run's agent selector or chip, Start/Pause/Reset, playback rate and status.

        One row per run rather than one for the dashboard: each control
        reaches a particular controller, and a shared transport would leave
        a reader unable to say which run a press acted on.
        """

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._run_name_text)
        layout.addWidget(self._agent_dropdown)
        layout.addWidget(self._running_agent_display)
        layout.addWidget(self._start_button)
        layout.addWidget(self._pause_button)
        layout.addWidget(self._reset_button)
        layout.addWidget(styled_label(PLAYBACK_LABEL, color=MUTED))
        layout.addWidget(self._playback_rate_dropdown)
        layout.addWidget(self._status_text)
        layout.addStretch(1)

        return row

    def set_run_name(self, name: str | None) -> None:
        """Name this view in its own header and on both its sidebar panels, or not at all.

        The dashboard decides the name, from `dashboard_frame.run_label`, so
        that this panel and the chart's legend call one run the same thing -
        a legend entry reading "Run 2" attributes a curve only if something
        holding that run's settings also says "Run 2".

        **The one writer of this run's name**, which is why the two sidebar
        headings are written here rather than in `refresh`: what a run is
        called changes when the dashboard's run set changes and at no other
        time, and `SimulationView._place_run` renames every run the moment a
        branch is placed - so the headings are attributed on the frame the
        branch appears on, before any chart frame is drawn (`PL-C3GS`).

        The name is *recorded* here as well as drawn, because the notice
        banner is named from it too (`_write_notice`): that banner also sits
        in a column the runs share, and is written on a path with no frame to
        read a run count off (`PL-TSZM`). It is not written here, unlike the
        headings, and the difference is that something else already writes
        it - `refresh` rewrites every banner on the presentation a fork
        drives, and the Reset that drops a branch clears the notice outright,
        so a write here would be one no scenario could tell from its absence.
        Nothing else writes the headings.

        Args:
            name: What to call it, or `None` for no name - which is what a
                lone run gets, having nothing to be told apart from.
        """

        self._run_name = name
        self._run_name_text.setText(name or "")
        self._run_name_text.setHidden(name is None)
        self._accounting_heading_text.setText(compared_panel_heading(ACCOUNTING_HEADING, name))
        self._control_timeline_heading_text.setText(
            compared_panel_heading(CONTROL_TIMELINE_HEADING, name)
        )

    def build_notice(self) -> QWidget:
        """The banner for a halted run or a refused setting, placed above every value."""

        return self._notice_text

    def build_readout_section(self) -> QWidget:
        """The substance heading with the interpretation line beside it, then the readouts.

        The heading says whose concentrations the seven panels under it are
        (`PL-TCD1`); the interpretation line sits on the same row, once,
        beside the values it qualifies (`PL-2K1R`).
        """

        section = QWidget()
        column = QVBoxLayout(section)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)
        heading_row = QWidget()
        heading = QHBoxLayout(heading_row)
        heading.setContentsMargins(0, 0, 0, 0)
        heading.setSpacing(12)
        heading.addWidget(self._compartment_substance_text)
        heading.addWidget(self._interpretation_text)
        heading.addStretch(1)
        column.addWidget(heading_row)
        column.addWidget(self._readout_row)

        return section

    def build_parameter_controls(self) -> QWidget:
        """The four setting controls in a row, in `PARAMETER_CONTROLS` order."""

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for slider in self._sliders():
            layout.addWidget(slider, 1)

        return row

    def build_sidebar_panels(self) -> tuple[QWidget, QWidget]:
        """This run's accounting panel and its control-change panel, in that order.

        Both are records of one run: the mass-balance diagnostic is of this
        run's own agent, and the timeline is what was changed during it.
        """

        accounting_panel = _panel("accountingPanel")
        accounting_column = QVBoxLayout(accounting_panel)
        accounting_column.setContentsMargins(
            PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING
        )
        accounting_column.addWidget(self._accounting_heading_text)
        accounting_column.addWidget(self._agent_accounting_status_text)
        accounting_column.addWidget(self._agent_accounting_detail_text)
        accounting_column.addWidget(
            styled_label(
                ACCOUNTING_UNIT_CAPTION, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True
            )
        )
        accounting_column.addWidget(self._agent_amounts_text)

        timeline_panel_frame = _panel("controlTimelinePanel")
        timeline_column = QVBoxLayout(timeline_panel_frame)
        timeline_column.setContentsMargins(
            PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING
        )
        timeline_column.setSpacing(4)
        timeline_column.addWidget(self._control_timeline_heading_text)
        timeline_column.addWidget(
            styled_label(
                CONTROL_TIMELINE_CAPTION,
                color=MUTED,
                size_px=METRIC_QUALIFIER_SIZE,
                italic=True,
                wrap=True,
            )
        )
        timeline_column.addWidget(self._control_timeline_text)
        timeline_column.addWidget(self._control_timeline_overflow_text)

        return accounting_panel, timeline_panel_frame

    def build_off_scale_notice(self) -> QWidget:
        """The line naming this run's traces that are above the plot."""

        return self._off_scale_text

    def build_wash_in_state(self) -> QWidget:
        """The line stating what this run's F_A/F_I plot is showing."""

        return self._wash_in_state_text


def _bold(font: QFont) -> QFont:
    bold = QFont(font)
    bold.setBold(True)

    return bold
