"""One run on the dashboard, with its controller, controls and readouts, in PySide6.

`PL-B9PY` divided the dashboard into a part that all runs share and a part
for each run. `RunView` is the part for each run. It holds what two displayed
runs cannot share: a controller, seven readouts, four settings, the
transport (the run's playback controls), the agent identity, the notices, and
the accounting and control-change panels. `SimulationView` holds what the runs
do share. `RunView` can be instantiated twice, and nothing in one instance
refers to another run.

`app/dashboard_frame.py` decides every claim that this class displays, and
does so without a GUI toolkit. This class calls that module's functions once
per tick, in the order that `refresh` sets. It writes the results into widgets
that decide nothing (`PL-25KS`, decision D2). No number is formatted here and
no colour is declared here. Colours come from `app/theme.py`, and they reach a
widget through the functions in `app/stylesheets.py` that compose stylesheets
(decision D10, `PL-Y4YX`).

**Agent colour has one writer.** `_apply_agent_color_scheme` is the only
method under `app/` that writes the ISO 5360 identity pair. It writes the pair
on every tick to exactly six controls, whether or not each is on screen. So
the chip that replaces the selector when a run starts already has the right
colour on the frame where it appears (`PL-61WW`).
`tools/agent_identity_check.py` reads the source of that method to learn which
controls carry the identity. It enforces one rule on each of them: nothing that
carries agent colour is drawn disabled. So the selector's `setDisabled(locked)`
call sits beside a `setHidden(locked)` call with the same argument, and the
selector is hidden whenever it cannot be used.

**A rejected setting shows a notice, and any other exception halts the run.**
Every setting forwarded to the run passes through `_apply_setting`.
`SimulationConfigurationError` means that the core rejected the value and
changed nothing, so the run goes on under a "Setting refused" banner. Any
other exception stops the run. Every slot of this view, and `_apply_setting`
itself, is wrapped in `halt_gate` from `app/halt_gate.py`. So an exception
raised in any of them halts the run through `_halt_run`. It does not escape to
the toolkit and leave the run still showing "Paused" (`PL-HJKN`).
`dashboard_frame.halt_disposition` decides how the stop is reported. A
`SimulationDomainLimitError` is reported as reaching the supported run length,
and anything else as a failure (`PL-V6M0`, `PL-Y5WR`, `PL-YK2V`).
`present_halt` shows a halted run before any attempt to draw a frame. It works
from the controller's record, and reading that record builds no compartment
value. There are two reasons for this. First, the frame is drawn by a render
path that all runs share, and that path may be what raised. A halt reported
only through the frame would then leave every status word showing "Paused" for
a failed controller (`PL-25KS`). Second, building a fresh snapshot builds
compartment values. When building one of those values was what raised, a halt
reported from the snapshot was never shown at all (`PL-7DJK`).

**The run-state widgets have one writer.** Every widget that a run shows is
written from one of two sources. The run-state widgets show what the run
holds: the status word, the transport, the agent identity, the dials, the
control-change panel and the banner. The snapshot widgets show the snapshot
that the frames were drawn from: the readouts, their clock and the accounting
panel. `_write_statement` writes the run-state widgets from
`dashboard_frame.run_statement`. Both `refresh` and `present_halt` call it, so
a halted run looks the same as a drawn run in the same state. An earlier
version of the halt code wrote to a list of widgets chosen by hand. Each widget
that the list missed went on showing the run as it was at the last frame
(`PL-X7D5`).

**Timers move the run and nothing else** (decision D7). Each run has one
`QTimer`, which drives `step_tick`. `step_tick` advances the controller by the
number of steps that the playback rate sets, and it never draws. The
dashboard's own render timer does the drawing. No wall clock is read.
Simulation time is a count of the steps taken.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Final

from PySide6.QtCore import QSignalBlocker, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import (
    AdjustmentGrouping,
    ControlAdjustment,
    wrapping_between_parts,
)
from anesthesia_sim.app.controller import (
    RunRecord,
    RunSettings,
    RunStatus,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    ACCOUNTING_INITIAL_DETAIL_TEXT,
    BRANCH_AGENT_LOCK_TEXT,
    COMPARING_AGENT_LOCK_TEXT,
    CONTROL_TIMELINE_CAPTION,
    CONTROL_TIMELINE_HEADING,
    INTERPRETATION_DISCLAIMER_TEXT,
    PAUSE_LABEL,
    PLAYBACK_LABEL,
    READOUT_PANELS,
    READOUT_RESERVATIONS,
    RESET_LABEL,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    START_LABEL,
    WITHHELD_CONCENTRATION_TEXT,
    WITHHELD_MAC_MULTIPLE_TEXT,
    HaltDisposition,
    NewCaseQuestion,
    Transport,
    accounting,
    compared_panel_heading,
    compared_run_notice,
    delivered_line,
    halt_disposition,
    halt_notice,
    new_case_question,
    notice,
    readouts,
    refused_reset_exit,
    refused_setting_notice,
    run_statement,
    setting_readouts,
    status_word,
    substance_heading,
    timeline_panel,
    transport,
)
from anesthesia_sim.app.formatting import (
    format_mac_reference,
    format_playback_rate,
    format_subtitle,
)
from anesthesia_sim.app.halt_gate import halt_gate
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_widgets import NewCaseDialog, NoticeLabel, ReadoutRow, styled_label
from anesthesia_sim.app.run_surfaces import (
    AccountingPanel,
    ParameterControls,
    emphasised,
    keep_until_destroyed,
    panel_frame,
)
from anesthesia_sim.app.stylesheets import (
    agent_selector_stylesheet,
    agent_surface_stylesheet,
    agent_text_stylesheet,
    selector_stylesheet,
    transport_button_stylesheet,
)
from anesthesia_sim.app.theme import (
    AGENT_COLOR_SCHEMES,
    AGENT_SELECTOR_WIDTH,
    CONTROL_ROW_SPACING,
    CONTROL_TIMELINE_ROW_SPACING,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PANEL_PADDING,
    PLAYBACK_RATE_SELECTOR_WIDTH,
    READOUT_HEADING_SPACING,
    READOUT_SECTION_SPACING,
    RUNNING_AGENT_DISPLAY_PADDING,
)
from anesthesia_sim.app.unconditional_set import UnconditionalValue, compartment_value
from anesthesia_sim.core.agent_simulation_validation import rejected_check
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
)
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND
from anesthesia_sim.layout.run_identity import RunId

# Adding a built-in agent without a verified identification colour would make
# the selector silently lose a safety cue (ISO 5360 Table 2, footnote b). So
# the module fails at import instead. This check concerns presentation
# metadata only. The agent's scientific parameters stay in their validated
# data files.
if set(AGENT_COLOR_SCHEMES) != set(AGENT_DATA_FILENAMES):
    raise RuntimeError("AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents")

#: The (agent_id, display_name) pair for every built-in agent, in
#: `AGENT_DATA_FILENAMES` order. The pairs are read once from the data files,
#: so no display name is restated here.
AVAILABLE_AGENTS: Final[tuple[tuple[str, str], ...]] = tuple(
    (agent_id, load_agent_parameters(agent_id).display_name) for agent_id in AGENT_DATA_FILENAMES
)

#: The same names keyed by id. They serve the one lookup that has an agent id
#: and no snapshot to read the name from. That lookup is for the agent that a
#: reader has just selected, which the controller does not report until the
#: reader confirms it.
AGENT_DISPLAY_NAMES: Final[Mapping[str, str]] = dict(AVAILABLE_AGENTS)

#: The clock panel's index in the readout row. It is found from the table that
#: the row is built from, not written as a literal position.
_CLOCK_PANEL_INDEX: Final = next(
    index for index, panel in enumerate(READOUT_PANELS) if panel.quantity is None
)

#: The header badge's inset. It is narrower than the chip's inset, because the
#: chip carries two lines and sits among controls. This bare spacing literal
#: is an interim measure under decision D9.
_HEADER_BADGE_PADDING: Final = 6

#: Every caption that the agent chip can carry under the agent's name. This
#: is `dashboard_frame.transport`'s set of lock reasons. While two runs are
#: compared, the chip is as wide as the widest caption on one line. So both
#: runs' chips have one width, and the controls after them line up.
_LOCK_CAPTIONS: Final = (RUNNING_AGENT_LOCK_TEXT, BRANCH_AGENT_LOCK_TEXT, COMPARING_AGENT_LOCK_TEXT)

#: The gap between the agent's name and the lock caption, when the chip puts
#: them on one line while two runs are compared. This bare spacing literal is
#: an interim measure under decision D9.
_CHIP_CAPTION_GAP: Final = 8

#: The inset above and below the chip's text and the badge's text while two
#: runs are compared. With this inset, neither the chip nor the badge is
#: taller than the selector beside the chip, and each compared run's line is
#: one control high. This bare spacing literal is an interim measure under
#: decision D9.
_FOLDED_VERTICAL_PADDING: Final = 2

#: The object names through which the agent-coloured surfaces are styled.
#: They make a surface's stylesheet apply to that frame and not to the labels
#: inside it.
_HEADER_BADGE_NAME: Final = "agentHeaderBadge"
_RUNNING_AGENT_DISPLAY_NAME: Final = "runningAgentDisplay"


class RunView(QWidget):
    """One run's widgets, controller, handlers, refresh and halt.

    A new `RunView` draws nothing. The dashboard presents every run once its
    charts exist. So the first frame is drawn from one window and one
    snapshot per run, not from whatever state each run was built from. The
    build methods return widgets for `SimulationView` to place, because the
    dashboard decides where one run's parts sit relative to another run's.

    Two surfaces may sit in an Area: the setting controls and the accounting
    panel. Their build methods build a new copy on every call, and the new
    copy starts from what the existing copies show. Each copy is an instance
    of a class in `app/run_surfaces.py`. Every writer here writes every copy
    that Qt has not destroyed, so two Areas can show one run (`PL-9LNF`). The
    other parts belong to the unconditional region, which is always on
    screen, and stay one per run. Their build methods return the same widgets
    on every call, laid out once when the run was built. A Qt layout takes a
    widget from wherever it sits. So an earlier version, which built a new
    container on each call, took the run's live widgets off the screen. It
    then deleted them when the container was dropped (`PL-N67T`, `PL-KZR1`).

    At construction, it rejects only a first snapshot that `setting_readouts`
    cannot draw controls for, by raising that function's `ValueError`. No
    shipped profile produces such a snapshot (`PL-7CRY`). `dashboard_frame`
    decides what is rejected on each tick. Which setting values the core
    rejects, and how a raise is reported, are read from the exception and
    never guessed (`PL-V6M0`, `PL-Y5WR`, `PL-YK2V`; see the module docstring).

    Attributes:
        controller: The run.
        run_id: The run's identity, which the run's name displays
            (`PL-7Z84`). It lasts as long as this view. It survives the run's
            own Reset and a change of agent, which each begin a new run
            definition in the same place. It ends when the dashboard drops
            the run.
        presentation_requested: Emitted with the coalesce flag when an action
            on this run means the dashboard must draw a frame. `True`, as for
            a slider drag, leaves the frame to the next render tick. `False`
            asks for a frame now. `SimulationView.present` handles the signal
            (`PL-R2YM`).
        case_restarted: Emitted when this run has started over from
            induction, after a Reset or an accepted change of agent. On a
            trunk run, that starts a new case, so every branch
            taken from the old run no longer compares with anything. The
            dashboard acts on the signal, because this view does not know
            which other runs are on screen.
    """

    presentation_requested = Signal(bool)
    case_restarted = Signal()

    def __init__(
        self, controller: SimulationController, parent: QWidget | None = None, *, run_id: RunId
    ) -> None:
        """Build one run's controls and readouts from its first snapshot.

        Args:
            controller: The run this view drives and displays.
            parent: The Qt parent.
            run_id: The run's identity, minted by the dashboard that places it.

        Raises:
            TypeError: If `run_id` is not a `RunId`.
        """

        if not isinstance(run_id, RunId):
            raise TypeError(f"a run's identity is a RunId, not {type(run_id).__name__}")

        super().__init__(parent)
        self.controller = controller
        self.run_id = run_id
        snapshot = controller.snapshot()

        # The reason the last setting change did not take effect, or None if
        # it did. It is held here rather than in the controller, because a
        # refused setting changes nothing about the simulation. So there is no
        # core state for it to belong to.
        self._rejected_setting_notice: str | None = None
        # The way out that the banner names when the core refused Reset
        # itself, or None while Reset is the way out. It is held beside the
        # refused setting for the same reason. The refusal changed nothing in
        # the simulation, so there is no core state for it to belong to
        # (`PL-M4M0`).
        self._refused_reset_notice: str | None = None
        self._playback_rate: PlaybackRate = DEFAULT_PLAYBACK_RATE
        self._adjustment_grouping = AdjustmentGrouping()
        # The agent that a reader has asked for and not yet confirmed, and the
        # dialog that asks them. Together they are the state "a destructive
        # confirmation is open". `_resolve_new_case` clears the agent before
        # acting, and that makes answering the dialog idempotent.
        self._pending_agent_id: str | None = None
        self._new_case_dialog: NewCaseDialog | None = None
        # What this run's Reset must ask before it discards work in another
        # run, and the dialog that asks it while the dialog is open. The
        # dashboard sets the question on the trunk (`ask_before_reset`).
        # `_resolve_reset` clears the dialog before acting, so the answer is
        # acted on once.
        self._reset_question: Callable[[], NewCaseQuestion | None] | None = None
        self._reset_dialog: NewCaseDialog | None = None
        # Whether a frame has drawn this run yet. A coalesced slider change
        # rewrites this run's own labels at once, but only after the first
        # frame has written everything.
        self._presented = False
        # The run's record as this view last wrote it, through `refresh` or
        # `present_halt`. It is `None` until the first write. The dashboard
        # draws a frame whenever the controller's record differs from it
        # (`owes_a_frame`).
        self._written_record: RunRecord | None = None
        # Whether a second run is on the chart. The dashboard writes it
        # through `set_comparing`, because how many runs are displayed is the
        # dashboard's fact and not this view's. The transport uses it as the
        # third reason that the chip may replace an agent selector.
        self._comparing = False
        # The run whose readout heading also states this run's substance and
        # 1 MAC. It is set while this run's readouts are drawn in that run's
        # panels (`show_readings_of`). Both runs use one agent, so the one
        # heading is true of both (`PL-QLZ5`).
        self._heading_shown_by: RunView | None = None

        # What this run is called, matching what the chart's legend calls it.
        # The name has its own label rather than a word inside the agent
        # badge. The badge carries the ISO 5360 identity pair, and
        # `_apply_agent_color_scheme` is the only writer of that pair
        # (`.claude/rules/ui-color.md`). A run's name is not agent identity
        # and must not take an agent's colour. The label is hidden while one
        # run is displayed. Then nothing is ambiguous, and a name would be
        # permanent text repeating what the single panel already says.
        #
        # `set_run_name` is deliberately not named for a chart or a run. Every
        # view will owe an area a name in its own header
        # (`.claude/rules/ui-areas.md`, `PL-TH35`). So the method has a name
        # that the next view could use too.
        self._run_name_text = styled_label("", color=INK, bold=True)
        self._run_name_text.setHidden(True)
        # The name is stored beside the label because the banner needs it too.
        # The banner is written on a path that has no frame to read the name
        # from (`_write_notice`). Reading the name back from the widget would
        # make the banner's attribution depend on a label's text, which is a
        # display detail.
        self._run_name: str | None = None
        self._status_text = styled_label("", color=MUTED, bold=True)
        emphasised(self._status_text, status_word(snapshot))
        self._notice_text = NoticeLabel(self)

        self._subtitle_text = styled_label(format_subtitle(snapshot.agent_display_name), color=INK)
        self._subtitle_text.setFont(_bold(self._subtitle_text.font()))
        self._agent_header_badge = QFrame()
        self._agent_header_badge.setObjectName(_HEADER_BADGE_NAME)
        badge = QHBoxLayout(self._agent_header_badge)
        self._badge_layout = badge
        badge.setContentsMargins(
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
            _HEADER_BADGE_PADDING,
        )
        badge.addWidget(self._subtitle_text)

        # Every widget whose visibility is written here is built with this
        # view as its parent. A widget shown without a parent is a top-level
        # window of its own, even for the instant before a layout adopts it.
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

        # The running agent's identity. A control that is never disabled
        # carries it, so the theme never recolours it. The control takes the
        # selector's place, at the selector's width, so the transport controls
        # beside it do not move when a run starts (`PL-61WW`).
        self._running_agent_text = styled_label(snapshot.agent_display_name, color=INK, bold=True)
        # Blank until something locks the selector. `_write_transport` is the
        # only writer of this line. It writes the reason in the same call that
        # reveals the chip. So the caption a reader sees is always the lock
        # actually in force, not whichever lock came first.
        self._running_agent_lock_text = styled_label("", color=INK, size_px=METRIC_QUALIFIER_SIZE)
        self._running_agent_display = QFrame(self)
        self._running_agent_display.setObjectName(_RUNNING_AGENT_DISPLAY_NAME)
        self._running_agent_display.setFixedWidth(AGENT_SELECTOR_WIDTH)
        chip = QVBoxLayout(self._running_agent_display)
        self._chip_layout: QBoxLayout = chip
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

        # The transport's colours are the interface's own, not the host
        # appearance's (`PL-DHBX`). `transport_button_stylesheet` explains why.
        for button in (self._start_button, self._pause_button, self._reset_button):
            button.setStyleSheet(transport_button_stylesheet())

        self._write_transport(self._transport_lock(snapshot))
        self._start_button.clicked.connect(self._handle_start)
        self._pause_button.clicked.connect(self._handle_pause)
        self._reset_button.clicked.connect(self._handle_reset)

        # How fast the run is played. This view control decides how many
        # steps a tick takes, and never how large a step is. It is never
        # disabled, and Reset leaves it alone, as it does every other setting.
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
        # These two labels sit on the heading line above the row. One shows the dial's
        # setting in both units. The other shows the 1 MAC value that divides every
        # ×MAC number in the row. Both values are in `docs/MODEL.md`'s per-substance
        # tier. The dial and the chart's caption cannot carry them, because each is now
        # a View that a reader can close (`PL-NWTM`). `_write_statement` writes both
        # from one record on every path, so the two cannot disagree.
        self._delivered_text = styled_label("", color=INK)
        self._one_mac_text = styled_label("", color=MUTED)
        self._readout_row = ReadoutRow(
            readouts(snapshot, self._playback_rate), reservations=READOUT_RESERVATIONS
        )
        # The agent whose MAC divided the ×MAC numbers on the readout cards.
        # Only a frame writes the cards, so after a halt that follows an agent
        # change they still hold another agent's multiples (`PL-6RJ0`).
        self._cards_agent_id = snapshot.agent_id

        # The values last shown by this run's two surfaces that may sit in an
        # Area, and the copies of each surface that Qt has not destroyed. A
        # copy built later starts from these values, so it matches the copies
        # already on screen. Every writer writes every copy (`PL-9LNF`).
        self._settings_shown = setting_readouts(snapshot)
        self._setting_controls: list[ParameterControls] = []
        self._accounting_shown = replace(
            accounting(snapshot), detail=ACCOUNTING_INITIAL_DETAIL_TEXT
        )
        self._accounting_panels: list[AccountingPanel] = []

        # The control-change panel's heading. It is an instance label rather
        # than a widget built inside `_lay_out_control_record`, because it has
        # to gain and lose this run's name as the dashboard's set of runs
        # changes. `set_run_name` is the one writer of that name (`PL-C3GS`).
        self._control_timeline_heading_text = styled_label(
            CONTROL_TIMELINE_HEADING, color=INK, bold=True
        )

        # The text wraps, because the record column is narrower than its
        # longest lines. It wraps only between the parts of a line
        # (`wrapping_between_parts`).
        self._control_timeline_text = styled_label(
            wrapping_between_parts(timeline_panel(()).entries),
            color=MUTED,
            size_px=METRIC_QUALIFIER_SIZE,
            wrap=True,
        )
        self._control_timeline_overflow_text = styled_label(
            "", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self._control_timeline_overflow_text.setHidden(True)

        # These sections are laid out once, here, so that the build methods
        # return the containers these widgets are already in (`PL-N67T`,
        # `PL-KZR1`).
        self._transport_row = self._lay_out_transport_row()
        self._readout_section = self._lay_out_readout_section()
        self._control_record_panel = self._lay_out_control_record()

        self._apply_agent_color_scheme(snapshot.agent_id)

        self._step_timer = QTimer(self)
        self._step_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._step_timer.setInterval(round(SIMULATION_TICK_INTERVAL_S * MILLISECONDS_PER_SECOND))
        self._step_timer.timeout.connect(self.step_tick)

    # ------------------------------------------------------------ reading

    def snapshot(self) -> SimulationSnapshot:
        """Return this run's state at this instant.

        The dashboard reads it once per frame and hands it back to `refresh`.
        So the readouts and the traces of a frame show one instant of one run.
        """

        return self.controller.snapshot()

    @property
    def is_running(self) -> bool:
        """Whether this run is advancing."""

        return self.controller.is_running

    @property
    def owes_a_frame(self) -> bool:
        """Whether the run holds a record that this view has not yet written.

        This is true for a run that nothing has written yet. It is also true
        for a run that changed while nothing asked for a frame: one that
        halted on a mark, or reached the supported run length inside
        `step_tick` (`PL-T995`). Either change alters `is_running` and nothing that asks
        for a frame. The dashboard's render tick draws while any run owes a
        frame. So the screen follows the run, and no path that changes the run
        has to ask for a frame (`PL-X7D5`). Reading this property builds no
        compartment value (`SimulationController.record`).
        """

        return self.controller.record() != self._written_record

    def adjustments(self, record: RunRecord) -> tuple[ControlAdjustment, ...]:
        """The run's control changes grouped into acts, regrouped only when the record changed.

        Args:
            record: The snapshot read for this frame, or the controller's
                record where no frame draws.

        Returns:
            What `control_timeline.group_adjustments` returns for its
            timeline, from this run's own `AdjustmentGrouping` (`PL-1PSX`).
        """

        return self._adjustment_grouping.of(record.control_timeline)

    @property
    def _elapsed_time_text(self) -> QLabel:
        """The clock panel's value line."""

        return self._readout_row.panels[_CLOCK_PANEL_INDEX].value_label

    @property
    def _playback_rate_text(self) -> QLabel:
        """The clock panel's second line, which carries the playback rate."""

        return self._readout_row.panels[_CLOCK_PANEL_INDEX].secondary_label

    # ---------------------------------------------------------- refreshing

    def refresh(self, snapshot: SimulationSnapshot) -> None:
        """Write every widget of this run from the snapshot the tick's frames were drawn from.

        The snapshot widgets are written first: the readouts, their clock and
        the accounting panel. The run-state widgets follow, through
        `_write_statement`, which `present_halt` also calls. On this path the
        banner shows the text that `dashboard_frame.notice` gives for a frame
        that was drawn.
        Each chart writes the lines that depend on its window, such as which
        traces are above the axis, from its own frame (`PL-L59K`).

        Args:
            snapshot: The run's state this tick, read once by the caller.

        Raises:
            ValueError: If `setting_readouts` rejects the snapshot. That
                happens for a control with no step of its resolution inside
                the range the run accepts (`PL-7CRY`).
        """

        self._presented = True
        self._readout_row.set_readouts(readouts(snapshot, self._playback_rate))
        self._cards_agent_id = snapshot.agent_id
        self._restate_new_case_question(snapshot)
        self._restate_reset_question()

        self._accounting_shown = accounting(snapshot)

        for accounting_panel in self._accounting_panels:
            accounting_panel.show_accounting(self._accounting_shown)

        self._write_statement(
            snapshot,
            banner=notice(
                snapshot, self._rejected_setting_notice, refused_reset=self._refused_reset_notice
            ),
        )

    def _write_statement(self, record: RunRecord, *, banner: str | None) -> None:
        """Write every run-state widget from one record, as their only writer (`PL-X7D5`).

        `refresh` calls it with the snapshot that a frame drew from.
        `present_halt` calls it with the controller's record. So a halt shows
        the run on every widget that a frame would. A widget added to the
        statement is written on both paths or on neither.

        This method also writes the playback line under the clock. That line
        sits in the readout row, which `refresh` writes from the snapshot and
        a halt does not write. But the line states the run's playback rate,
        not a compartment value. Before `PL-P58M`, only the readout row wrote
        it, so a rate chosen on a halted run reached the dropdown but not the
        clock. On `refresh`, the readout row first writes the same text from
        the same rate.

        Both paths write in one order. The agent colour comes first, before
        anything that shows it. The dials come last, because
        `setting_readouts` can raise for a control that can offer no setting.
        The status word, the transport and the banner must be on screen
        before that can happen (`PL-25KS`, `PL-7DJK`, `PL-85LJ`).

        Before writing anything, the method stores the record as the one this
        view last wrote. The render tick draws whenever a run's record differs
        from the stored one (`owes_a_frame`). So when a frame fails for a
        cause that is still there, the render tick does not retry it on every
        tick.

        Args:
            record: The snapshot a frame drew from, or
                `SimulationController.record()` when no frame draws.
            banner: The banner text for the caller's path. It comes from
                `notice` for a frame that drew, and from `halt_notice` for a
                halt that no frame has been drawn for.

        Raises:
            ValueError: If `setting_readouts` rejects the record, as
                described under `refresh`.
        """

        self._written_record = record.run_record()
        statement = run_statement(
            record,
            self.adjustments(record),
            is_branch=self._is_branch,
            comparing=self._comparing,
            banner=banner,
        )

        self._apply_agent_color_scheme(statement.agent_id)
        self._write_transport(statement.transport)

        with QSignalBlocker(self._agent_dropdown):
            self._agent_dropdown.setCurrentIndex(self._agent_dropdown.findData(statement.agent_id))

        self._running_agent_text.setText(statement.agent_name)
        emphasised(self._status_text, statement.status)
        self._subtitle_text.setText(statement.subtitle)
        self._compartment_substance_text.setText(statement.substance_heading)
        self._control_timeline_text.setText(wrapping_between_parts(statement.timeline.entries))
        self._control_timeline_overflow_text.setText(statement.timeline.overflow)
        self._control_timeline_overflow_text.setHidden(not statement.timeline.overflow)
        self._playback_rate_text.setText(format_playback_rate(self._playback_rate.multiplier))
        # The 1 MAC line states the divisor of the delivered line beside it and of the
        # cards' ×MAC numbers. It is written on both the frame path and the halt path,
        # and before the dials. So an exception raised in `setting_readouts` cannot
        # leave another agent's 1 MAC on screen. When a halt finds cards that were
        # divided by another agent's MAC, it withholds their values (`present_halt`,
        # `PL-6RJ0`).
        self._one_mac_text.setText(
            format_mac_reference(record.agent_display_name, record.agent_mac_percent)
        )
        self._write_notice(statement.banner)
        self._write_settings(record)

    def _write_notice(self, banner: str | None) -> None:
        """Write the banner for this run, naming the run while a second run is drawn.

        This method is kept apart from `_write_statement`, its one caller,
        because naming the run in the banner follows a rule of its own.
        `refresh` has a frame and words the banner with
        `dashboard_frame.notice`. `present_halt` deliberately has no frame and
        words the banner with `dashboard_frame.halt_notice`. On both paths, the
        run's name comes from `set_run_name` rather than from the frame.
        `dashboard_frame.compared_run_notice` gives the full argument.

        Args:
            banner: The banner's text, or None to show none.
        """

        self._notice_text.set_notice(compared_run_notice(banner, self._run_name))

    def _refresh_against_last_frame(self, snapshot: SimulationSnapshot) -> None:
        """Rewrite this run's own widgets now, from `snapshot`, while the charts wait.

        After a coalesced slider change, what is shown beside the dial must
        be updated at once. It has to agree with the snapshot from the moment
        the setting is applied (`PL-018`). The frame itself waits for the
        render tick (`PL-R2YM`). Before the first presentation this method
        rewrites nothing, because the first presentation writes everything.

        Args:
            snapshot: This run's state, read by `_apply_setting` after the change.
        """

        if self._presented:
            self.refresh(snapshot)

    def present_halt(self) -> None:
        """Say this run has stopped, from its controller's record alone, with no frame drawn.

        This method writes every run-state widget, through `_write_statement`,
        before any frame is attempted, because the frame may be what is
        failing. Suppose the shared render path raised, and the halt were shown
        only through that path. Every status word would then read "Paused"
        over a failed controller, and no banner would name the exception
        (`PL-25KS`). The frame widgets keep what the last frame drew. They show
        compartment values, and the first frame that draws rewrites them.

        It writes every widget that a frame would write, because a halt can
        follow a change that no frame has shown. A dial dragged into a halt
        has changed what the run holds (`PL-85LJ`). An agent changed just
        before a halt has changed what every identity widget names
        (`PL-1YDD`). A drag that returns a dial to where it started has taken
        a change off the record (`PL-DTJQ`). A halt that wrote only a
        hand-picked set of widgets left each of these showing the run as it
        was before the change, with no frame to follow.

        Everything is read once, from `SimulationController.record()` and not
        from a snapshot. A snapshot builds every compartment's fraction, and
        one of the halts shown here is the rejection of one of those
        fractions. When this method read a fresh snapshot, that halt raised
        out of the method and was never shown. The screen went on reading
        "Running", with Pause offered, over a failed controller (`PL-7DJK`).
        The banner comes from `dashboard_frame.halt_notice`. It says that no
        frame of the stopped run has been drawn, and the first frame that
        draws replaces it.

        Raises:
            ValueError: If `setting_readouts` rejects the record. By then
                `_write_statement` has put everything else on screen.
        """

        record = self.controller.record()
        self._write_statement(
            record,
            banner=halt_notice(
                record, self._rejected_setting_notice, refused_reset=self._refused_reset_notice
            ),
        )

        if self._cards_agent_id != record.agent_id:
            self._withhold_card_values()

    def _withhold_card_values(self) -> None:
        """Replace each compartment card's percent and ×MAC number with a withheld text.

        `present_halt` calls this when the agent has changed and no frame has yet
        been drawn for the new agent. The cards then hold the last frame's values:
        the old agent's concentrations, divided by the old agent's MAC. The heading
        above them, the 1 MAC line and the delivered line already name the new
        agent. Showing either number would put a value on screen under a substance
        or a divisor that did not produce it. `PL-6RJ0` withheld the multiples, and
        `PL-J5GC`'s guard found the percents still under the new agent's heading.
        The clock keeps the last frame's instant, which the halt banner states. The
        next frame writes every card again.
        """

        for index, panel in enumerate(self._readout_row.panels):
            if index != _CLOCK_PANEL_INDEX:
                panel.value_label.setText(WITHHELD_CONCENTRATION_TEXT)
                panel.secondary_label.setText(WITHHELD_MAC_MULTIPLE_TEXT)

    def _write_settings(self, settings: RunSettings) -> None:
        """Write the four setting controls from the settings in force.

        `_write_statement` calls this method last. It passes either the
        snapshot that a frame drew from, or `SimulationController.record()`
        when no frame draws. Both carry the agent and the four settings, and
        `dashboard_frame.setting_readouts` builds the same readouts from
        either. So a dial shows the same text whichever path wrote it
        (`PL-85LJ`).

        Args:
            settings: The agent and the settings in force on the run.
        """

        self._settings_shown = setting_readouts(settings)

        for controls in self._setting_controls:
            controls.show_settings(self._settings_shown)

        for setting in self._settings_shown:
            if setting.control is ControlInput.DELIVERED:
                self._delivered_text.setText(delivered_line(setting))

    def _transport_lock(self, status: RunStatus) -> Transport:
        """Return this run's transport enablement, adding two facts `dashboard_frame` cannot read.

        The two facts are whether this run is a branch and whether runs are
        being compared. The method reads `opened_from` from the controller
        each time rather than caching it at construction. Whether a run is a
        branch is the controller's fact to state, and nothing here would
        learn of a change to it.

        Args:
            status: The run's status this tick. It is either the snapshot that
                a frame drew from, or the controller's bare status when no
                frame is involved.

        Returns:
            What `dashboard_frame.transport` returns for this run.
        """

        return transport(status, is_branch=self._is_branch, comparing=self._comparing)

    @property
    def _is_branch(self) -> bool:
        """Whether this run was opened from another, read live from the controller."""

        return self.controller.opened_from is not None

    def set_comparing(self, comparing: bool) -> None:
        """Record whether a second run is on the chart, and rewrite the transport at once.

        The dashboard calls this method whenever its set of runs changes. So
        a selector that a fork locks is locked from the frame on which the
        branch appears, not from the next tick. The method also moves the
        values that each run states once into the run's own transport row,
        or moves them back (`_fold_heading_into_transport`).

        Args:
            comparing: Whether more than one run is displayed.
        """

        if comparing != self._comparing:
            self._fold_heading_into_transport(comparing)

        self._comparing = comparing
        self._write_transport(self._transport_lock(self.controller.status()))

    def _fold_heading_into_transport(self, folded: bool) -> None:
        """Give each compared run one line, or give a lone run its two lines back.

        Without folding, each compared run's transport row sits above its
        readout heading line. The two runs' four lines then take the height
        that the concentration chart needs on a 1366 by 700 laptop screen
        (`PL-JG82`). When folded, a run's transport row also carries its
        delivered concentration, which is the one heading value that differs
        between the runs. The agent chip puts its caption beside the agent's
        name rather than under it, at one width for every run. The chip and
        the badge lose most of their inset above and below. The values that
        the runs share stay on the first run's heading line, above the paired
        readouts. They are the substance, the interpretation line, the
        agent's 1 MAC and the version-and-model badge. `add_run` refuses a run
        on another agent, and a branch's MAC is checked against its trunk's
        MAC when the branch is opened. So one statement of each shared value
        is true of both runs (`PL-QLZ5`).

        Args:
            folded: Whether to fold, which is whether more than one run is displayed.
        """

        if folded:
            self._heading_layout.removeWidget(self._delivered_text)
            self._transport_layout.removeWidget(self._agent_header_badge)
            self._transport_layout.addWidget(self._delivered_text)
            self._heading_layout.addWidget(self._agent_header_badge)
            self._chip_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._chip_layout.setSpacing(_CHIP_CAPTION_GAP)
            self._running_agent_display.setFixedWidth(self._one_line_chip_width())
            chip_vertical = badge_vertical = _FOLDED_VERTICAL_PADDING
        else:
            self._transport_layout.removeWidget(self._delivered_text)
            self._heading_layout.removeWidget(self._agent_header_badge)
            self._heading_layout.insertWidget(
                self._heading_layout.indexOf(self._one_mac_text), self._delivered_text
            )
            self._transport_layout.addWidget(self._agent_header_badge)
            self._chip_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self._chip_layout.setSpacing(0)
            self._running_agent_display.setFixedWidth(AGENT_SELECTOR_WIDTH)
            chip_vertical = RUNNING_AGENT_DISPLAY_PADDING
            badge_vertical = _HEADER_BADGE_PADDING

        self._chip_layout.setContentsMargins(
            RUNNING_AGENT_DISPLAY_PADDING,
            chip_vertical,
            RUNNING_AGENT_DISPLAY_PADDING,
            chip_vertical,
        )
        self._badge_layout.setContentsMargins(
            _HEADER_BADGE_PADDING, badge_vertical, _HEADER_BADGE_PADDING, badge_vertical
        )

    def _one_line_chip_width(self) -> int:
        """Return the chip's width with the widest agent name and widest caption on one line.

        The width is measured from the two labels' own fonts. So every
        compared run's chip has one width, whichever agent it runs and
        whichever caption it carries.
        """

        name = QFontMetrics(self._running_agent_text.font())
        caption = QFontMetrics(self._running_agent_lock_text.font())
        widest_name = max(
            name.size(0, display_name).width() for _, display_name in AVAILABLE_AGENTS
        )
        widest_caption = max(caption.size(0, text).width() for text in _LOCK_CAPTIONS)

        return 2 * RUNNING_AGENT_DISPLAY_PADDING + widest_name + _CHIP_CAPTION_GAP + widest_caption

    def _write_transport(self, lock: Transport) -> None:
        """Write the transport's enablement, and show either the selector or the chip.

        The selector's `setDisabled` call sits beside a `setHidden` call with
        the same operand, so the selector draws nothing while it cannot be
        used. `tools/agent_identity_check.py` requires that pairing of every
        control in the identity set.

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

        This method is the single writer of agent colour. It writes on every
        tick, whether or not each control is on screen. So the chip that the
        next state change reveals already has the running agent's colour. It
        makes one `setStyleSheet` call per control, so that
        `tools/agent_identity_check.py` can read the identity set from this
        method.

        Args:
            agent_id: The running agent, from this tick's snapshot.
        """

        scheme = AGENT_COLOR_SCHEMES[agent_id]
        self._agent_header_badge.setStyleSheet(agent_surface_stylesheet(_HEADER_BADGE_NAME, scheme))
        self._subtitle_text.setStyleSheet(agent_text_stylesheet(scheme))
        self._running_agent_display.setStyleSheet(
            agent_surface_stylesheet(_RUNNING_AGENT_DISPLAY_NAME, scheme)
        )
        self._running_agent_text.setStyleSheet(agent_text_stylesheet(scheme))
        self._running_agent_lock_text.setStyleSheet(agent_text_stylesheet(scheme))
        self._agent_dropdown.setStyleSheet(agent_selector_stylesheet(scheme))

    # ------------------------------------------------------------ settings

    @halt_gate
    def _apply_setting(self, apply: Callable[[], None], *, coalesce: bool = False) -> None:
        """Forward one setting to the run, and report how it was received.

        A `SimulationConfigurationError` is a refusal. It means that the core rejected
        the value and changed nothing, so the run goes on and the banner says which
        setting was refused. Any other exception halts the run, because this method
        is wrapped in the halt gate (`PL-HJKN`).
        That includes an exception from outside the project's own exception classes,
        because the run still cannot continue (`PL-YK2V`). An accepted setting clears
        a refusal that is in effect. It also clears the way out that a refused Reset
        left on the banner (`PL-M4M0`). A refused Reset leaves the run failed, and a
        failed run refuses every dial (`PL-3B34`), so the setting that clears that
        way out is an agent switch, which starts a new case. On a stopped run the
        refusal is stated inside the stopped run's banner, and the dial springs back
        to the setting the stopped values ran under.

        The method leaves the frame for the render tick to draw only when two things
        are true: `coalesce` is set, and no refusal was in effect before the call or
        is in effect after it. When a setting is refused, or a refusal is cleared, the
        dial on screen and the simulation disagree, so neither may wait for a tick
        (`PL-R2YM`). A coalesced change still rewrites this run's own labels at once,
        from a snapshot read after the change. If reading that snapshot raises, the
        gate halts the run and shows the halt. Before `PL-V2HC`, the exception escaped
        the slot after the setting had been applied. The halted run also has its dials
        written from the settings it holds, because no frame follows to write them
        (`PL-85LJ`). The rewrite of the labels can raise too, as `setting_readouts`
        does for a control that can offer no setting. The gate halts the run for that
        as well. So the status word, the transport controls and the banner show the
        halt before writing the dials raises again and the exception escapes
        (`PL-M3M2`).

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
        else:
            self._rejected_setting_notice = None
            self._refused_reset_notice = None

        deferred = coalesce and settled_notice is None and self._rejected_setting_notice is None

        if deferred:
            self._refresh_against_last_frame(self.snapshot())

        self.presentation_requested.emit(deferred)

    @halt_gate
    def _handle_adjustment_start(self) -> None:
        """Close any open adjustment, so the changes that follow are a new act.

        This handler does not go through `_apply_setting`, because it records
        nothing and changes no state. Without it, two drags of one dial would
        be one adjustment on the record.
        """

        self.controller.begin_control_adjustment()

    @halt_gate
    def _handle_setting_request(self, control: ControlInput, value: float) -> None:
        """Apply the value a slider in any copy of the setting controls was moved to."""

        handlers: Mapping[ControlInput, Callable[[float], None]] = {
            ControlInput.FRESH_GAS_FLOW: self._handle_fresh_gas_flow_change,
            ControlInput.DELIVERED: self._handle_delivered_concentration_change,
            ControlInput.ALVEOLAR_VENTILATION: self._handle_alveolar_ventilation_change,
            ControlInput.CARDIAC_OUTPUT: self._handle_cardiac_output_change,
        }
        handlers[control](value)

    # Each dial's value is built into its checked type inside the call that
    # `_apply_setting` makes. So a value that the model refuses is refused
    # inside that call, and is reported as a refused setting. The vaporizer
    # dial's `Percent` below works the same way (`PL-0YYV`).

    def _handle_fresh_gas_flow_change(self, flow_l_min: float) -> None:
        self._apply_setting(
            lambda: self.controller.set_fresh_gas_flow(FreshGasFlow(flow_l_min)), coalesce=True
        )

    def _handle_delivered_concentration_change(self, percent: float) -> None:
        self._apply_setting(
            lambda: self.controller.set_delivered_concentration_percent(
                Percent(percent, name="delivered_concentration_percent")
            ),
            coalesce=True,
        )

    def _handle_alveolar_ventilation_change(self, flow_l_min: float) -> None:
        self._apply_setting(
            lambda: self.controller.set_alveolar_ventilation(AlveolarVentilation(flow_l_min)),
            coalesce=True,
        )

    def _handle_cardiac_output_change(self, flow_l_min: float) -> None:
        self._apply_setting(
            lambda: self.controller.set_cardiac_output(CardiacOutput(flow_l_min)), coalesce=True
        )

    # ----------------------------------------------------------- transport

    @halt_gate
    def _handle_start(self) -> None:
        """Start the run, and show a notice if the controller refuses the start."""

        self._apply_setting(self.controller.start)

    @halt_gate
    def _handle_pause(self) -> None:
        self.controller.pause()
        self.presentation_requested.emit(False)

    def ask_before_reset(self, question: Callable[[], NewCaseQuestion | None]) -> None:
        """Make this run's Reset ask first whenever `question` returns a question.

        The dashboard sets it on the trunk, whose Reset discards every branch
        with it (`PL-W5WX`). This view cannot see those branches, so the
        dashboard decides whether there is anything to ask about. `question`
        is called on each press rather than once, because what a branch holds
        changes while it runs.

        Args:
            question: Returns what to ask, or None where the Reset discards
                nothing outside this run and so asks nothing.
        """

        self._reset_question = question

    @halt_gate
    def _handle_reset(self) -> None:
        """Respond to a press of Reset by starting over at once, or by asking first.

        It asks only when the dashboard says that this Reset would discard
        work in another run (`ask_before_reset`). Starting this run over needs
        no question, because pressing its own Reset is the request to discard
        it (`docs/MODEL.md` § "Agent-change behavior").
        """

        question = None if self._reset_question is None else self._reset_question()

        if question is None:
            self._reset_now()
            return

        dialog = NewCaseDialog(question, self)
        dialog.finished.connect(self._handle_reset_finished)
        # The dialog is deleted once answered, for the same reason as the
        # new-case dialog.
        dialog.finished.connect(dialog.deleteLater)
        self._reset_dialog = dialog
        dialog.open()

    def _restate_reset_question(self) -> None:
        """Rewrite an open Reset question from the runs as they stand now.

        The trunk's Reset question names each branch it discards and the
        instant that branch has run to. Reset stays enabled while the runs
        step, and a branch goes on stepping while the question is open. So a
        question written only once, when it opened, understated the branch
        work that the reader was about to discard (`PL-WM5P`). The
        dashboard's `ask_before_reset` callback reads every branch's
        controller, and each controller has already stepped by the time this
        run is refreshed.

        If the callback now returns no question, the dialog is left as it
        is. That case does not arise, because a branch's work only grows
        while the question is open. Closing the dialog under the reader
        would also be a surprise.
        """

        if self._reset_dialog is None or self._reset_question is None:
            return

        question = self._reset_question()

        if question is not None:
            self._reset_dialog.show_question(question)

    @halt_gate
    def _handle_reset_finished(self, result: int) -> None:
        self._resolve_reset(result == QDialog.DialogCode.Accepted)

    def _resolve_reset(self, confirmed: bool) -> None:
        """Act on the answer to the Reset question once, however many times it is reported.

        Args:
            confirmed: True to start the case over and discard the branches.
                False to keep every run as it is.
        """

        if self._reset_dialog is None:
            return

        self._reset_dialog = None

        if confirmed:
            self._reset_now()
            return

        self.presentation_requested.emit(False)

    def _reset_now(self) -> None:
        """Start over, clearing the run and any refusal in effect, but not the playback rate.

        `case_restarted` is emitted before the frame is asked for. So by the
        time the frame is assembled, the dashboard has already dropped any
        branch of the run that just ended. If a branch were still drawn beside
        a trunk that is back at induction, the two curves would claim to show
        one case when they no longer do.

        **A Reset that the core refuses halts the run instead.**
        `SimulationController.reset()` refuses before it clears anything. It
        refuses when the settings record is one on which the next step would
        also be refused. So the run is left exactly as it was, and it is
        stopped through the failed-step path. That path records the refusal,
        and the status word, the transport controls and the banner show it. In
        any other halt, the banner names Reset as the way out. For this halt,
        the way out is `REFUSED_RESET_WAY_OUT_TEXT`, which says that no setting
        can repair the refusal (`PL-01GY`). Every exception from `reset()`
        halts the run, just as an exception from a step does. A
        `SimulationConfigurationError` here is not treated as a refused
        setting, because the run it leaves cannot be cleared (`PL-M4M0`).
        `case_restarted` is not emitted, since no case restarted. The frame is
        asked for, as after any halt.

        The exit text is chosen before the halt records the refusal, because
        its wording depends on what the banner's reason will be. A controller
        keeps the first reason it was given. So on a run that had already
        failed for something else, the banner's reason stays that earlier
        failure, and the exit text itself has to state the refusal.
        `refused_reset_exit` tells that run apart from a run that this same
        refusal stopped on an earlier press (`PL-M4M0`). This method then
        raises the refusal again, to the halt gate of the slot that called it,
        and that gate halts the run once. This method used to halt the run
        itself. When showing that halt raised an exception, the gate caught
        the new exception and halted the run a second time (blind review of
        `PL-HJKN`).

        Raises:
            Exception: What `SimulationController.reset()` raised, once the exit
                text is chosen.
        """

        try:
            self.controller.reset()
        except Exception as error:
            self._refused_reset_notice = refused_reset_exit(
                error, recorded_failure_reason=self.controller.status().failure_reason
            )
            raise

        self._rejected_setting_notice = None
        self._refused_reset_notice = None
        self.case_restarted.emit()
        self.presentation_requested.emit(False)

    @halt_gate
    def _handle_playback_rate_change(self, index: int) -> None:
        """Store the playback rate that the reader chose, for the next tick to read.

        If the control offers a multiplier that is not in `SUPPORTED_PLAYBACK_RATES`,
        `playback_rate_for` raises `SimulationConfigurationError`. A mismatch between
        the control's multipliers and `SUPPORTED_PLAYBACK_RATES` is a defect. The halt
        gate halts the run for it, so the defect is shown on screen. The selector keeps
        the rate that the reader picked. The run keeps the rate that it held before,
        and the line beside the selector names that rate.
        """

        multiplier = self._playback_rate_dropdown.itemData(index)

        if multiplier is None:
            return

        self._playback_rate = playback_rate_for(int(multiplier))
        self.presentation_requested.emit(False)

    # ---------------------------------------------------- the new-case flow

    @halt_gate
    def _handle_agent_change(self, index: int) -> None:
        """Respond to a selection by doing nothing, starting a new case at once, or asking.

        Selecting the same agent is no change. A run that has recorded
        nothing has nothing to lose, so it switches at once. Otherwise the
        selector is put back to the running agent and the reader is asked,
        because the switch discards the case (`PL-R3KB`). While that question
        is open, a further selection is put back and gets no response. The
        open dialog names one agent, and its answer must start that agent and
        no other (`PL-25KS`).

        When reading the run's snapshot raises, the response to the selection is to
        show the halt for that exception again. The gate halts the run. Then
        `present_halt` puts the selector back to the agent that the controller's
        record names, because the snapshot that would name it is what raised
        (`PL-V2HC`). Reset is the way out that the halt banner names, unless a
        refused Reset has left its own way out in effect.
        """

        agent_id = self._agent_dropdown.itemData(index)

        if agent_id is None:
            return

        snapshot = self.snapshot()

        if self._pending_agent_id is not None:
            self._show_running_agent(snapshot.agent_id)
            return

        if agent_id == snapshot.agent_id:
            return

        if not snapshot.has_recorded_run:
            self._start_new_case(agent_id)
            return

        self._confirm_new_case(snapshot, agent_id)

    def _show_running_agent(self, agent_id: str) -> None:
        """Put the selector back on `agent_id`, this run's agent, without responding to the pick.

        The combo box changes to the reader's pick before the handler runs.
        So a pick that is not acted on leaves the selector naming an agent
        that the run is not using, until the selector is put back. This
        method puts back a pick made while a question is open. On a run whose
        snapshot raises, the halt puts the selector back instead, through
        `present_halt`. Signals are blocked while the selector is put back, so
        that the change is not treated as a second pick.
        """

        with QSignalBlocker(self._agent_dropdown):
            self._agent_dropdown.setCurrentIndex(self._agent_dropdown.findData(agent_id))

    def _start_new_case(self, agent_id: str) -> None:
        """Switch the run to `agent_id` through `_apply_setting`, like any other setting.

        `SimulationController.set_agent` refuses to switch the agent of a branch
        (`PL-TFX5`), and that refusal reaches the reader as a refused-setting notice.
        `set_agent` also carries the settings over from the run's snapshot. So
        if reading the snapshot raises, `set_agent` raises too, and
        `_apply_setting` would record that exception as a refused setting.
        This method therefore reads the snapshot first, outside
        `_apply_setting`. If that read raises, the exception reaches the halt
        gate of the slot that called this method. The gate treats it as the
        halt that it is and shows that halt again, and nothing is recorded as
        refused (`PL-V2HC`). The confirmation path reaches this method holding
        a snapshot that was read when the question was asked. A halt since
        then makes that snapshot out of date.

        **An accepted switch emits `case_restarted`**, as Reset does, because
        it too starts a new case. The signal is emitted inside the setting
        call, after `set_agent` returns and before the frame is requested.
        So the dashboard drops everything that belonged to the old case
        before it draws, including a refusal on the branch panel
        (`PL-BM6X`). A refused switch changes nothing and emits nothing.
        """

        self.snapshot()

        def switch() -> None:
            self.controller.set_agent(agent_id)
            self.case_restarted.emit()

        self._apply_setting(switch)

    def _confirm_new_case(self, snapshot: SimulationSnapshot, agent_id: str) -> None:
        """Ask before discarding a recorded run, with the selector already put back.

        While the question is open, the selector shows the agent that is
        actually running. The changes that would be lost are counted in the
        same groups that the timeline panel lists.

        The pending agent is recorded only once the dialog is built. While an
        agent is pending, the selector puts back every later pick. The pending
        agent used to be recorded before the dialog was built. So when building
        the dialog raised an exception, the selector kept putting back every
        pick, even after the Reset that the halt names as the way out (blind
        review of `PL-HJKN`).
        """

        self._show_running_agent(snapshot.agent_id)

        question = new_case_question(
            snapshot, AGENT_DISPLAY_NAMES[agent_id], len(self.adjustments(snapshot))
        )
        dialog = NewCaseDialog(question, self)
        self._pending_agent_id = agent_id
        dialog.finished.connect(self._handle_new_case_finished)
        # The dialog is deleted once answered. Otherwise every question asked
        # would stay a child of this view, with its title in
        # `interface_strings` and its widgets in every walk of the widget
        # tree (`PL-25KS`).
        dialog.finished.connect(dialog.deleteLater)
        self._new_case_dialog = dialog
        dialog.open()

    def _restate_new_case_question(self, snapshot: SimulationSnapshot) -> None:
        """Rewrite an open new-case question from the frame's snapshot.

        The question states how much run time and how many control changes
        the new case discards. The run is not paused while the question is
        open, so a running run goes on stepping. A question written only
        once, when it opened, therefore understated what the reader was
        about to lose (`PL-WM5P`). A halt does not rewrite the question. A
        halted run does not step, so the figure from the last frame is still
        correct.

        Args:
            snapshot: The snapshot the frame drew from.
        """

        if self._new_case_dialog is None or self._pending_agent_id is None:
            return

        self._new_case_dialog.show_question(
            new_case_question(
                snapshot,
                AGENT_DISPLAY_NAMES[self._pending_agent_id],
                len(self.adjustments(snapshot)),
            )
        )

    @halt_gate
    def _handle_new_case_finished(self, result: int) -> None:
        self._resolve_new_case(result == QDialog.DialogCode.Accepted)

    def _resolve_new_case(self, confirmed: bool) -> None:
        """Act on the reader's answer once, however many times the dialog reports it.

        The pending agent is cleared before anything else. So a second
        report, such as a dialog reporting its close after the button that
        closed it, finds nothing to act on. It cannot undo a switch that has
        already started.

        Args:
            confirmed: True to discard the case and start the new one. False
                to keep the case, which rebuilds nothing.
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

    def halt(self, error: BaseException, *, in_frame: bool = False) -> None:
        """Stop the run for an exception, and record the disposition that it calls for.

        This method draws nothing and writes nothing on screen. To show the
        halt, `_halt_run` and `SimulationView._halt_every_run` call
        `present_halt` after they call this method.

        Args:
            error: The exception that was raised.
            in_frame: True when the exception came from the dashboard that
                draws every run, either from its frame or from one of its own
                slots. False when it came from this run's own step or setting.
                The controller also records an exception from the dashboard,
                and a trunk with that record offers no branch
                (`SimulationController.record_failed_frame`).
        """

        disposition, reason = halt_disposition(error)

        if in_frame:
            self.controller.record_failed_frame(reason)

        if disposition is HaltDisposition.SUPPORTED_LIMIT:
            self.controller.halt_at_supported_limit(reason)
        elif isinstance(error, AgentSimulationValidationError):
            # The core rolled the step back, so only the error still holds the
            # rejected step's check (`PL-HF4B`).
            self.controller.fail(reason, rejected_accounting=rejected_check(error))
        else:
            self.controller.fail(reason)

    def _halt_run(self, error: BaseException) -> None:
        """Halt the run, show the halt from its controller's record, then ask for the frame.

        The halt comes first, so a presentation that fails cannot undo it.
        When `SimulationView.present` cannot draw a frame, it halts every run.
        A controller keeps the first reason it was given, so this run still
        reports the exception that stopped it. The run's own status word and
        banner are written before the frame is asked for. So a run whose
        frame cannot be drawn still says that it stopped.

        `present_halt` can raise an exception after it has written the halt,
        when a dial cannot be written (`PL-M3M2`). The frame is still asked
        for, because the dashboard restates its own panels, such as "Branch
        here", only when it draws a frame. Before this change, no frame was
        asked for here, so those panels kept offering the halted run as it was
        before the halt (blind review of `PL-HJKN`).

        Args:
            error: The exception that was raised.

        Raises:
            ValueError: What `present_halt` raised, once the frame has been asked for.
        """

        self.halt(error)

        try:
            self.present_halt()
        finally:
            self.presentation_requested.emit(False)

    def halt_for_slot(self, error: Exception) -> None:
        """Halt this run for an exception that one of its slots raised, through `_halt_run`.

        `app/halt_gate.py`'s `halt_gate` calls this method. A slot of this view
        acts on this run alone, so no other run stops.

        Args:
            error: The exception that the slot raised.

        Raises:
            ValueError: What `_halt_run` raises once the halt is shown.
        """

        self._halt_run(error)

    # -------------------------------------------------------------- timing

    @halt_gate
    def step_tick(self) -> None:
        """Advance the run by one tick's worth of steps, and never draw.

        The method reads the playback rate once and takes the number of steps that
        it sets, each `SIMULATION_STEP_S` long, with nothing else serviced between
        them. So a setting changed while the run plays takes effect on a tick
        boundary (`PL-NBWP`). If the core refuses a step, the rest of that tick's
        steps are abandoned, and the gate halts the run on the last completed step.
        The slot keeps working afterwards, so Reset can restart the run. A tick that
        fires late costs the run real time but never changes its trajectory, because
        no step is made up.
        """

        if not self.controller.is_running:
            return

        steps = self._playback_rate.steps_per_tick(
            tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
        )

        for _ in range(steps):
            self.controller.advance(SIMULATION_STEP_S)

    def start_simulation_timer(self) -> None:
        """Start the tick timer, which only `stop_timers` stops and a failure never does."""

        self._step_timer.start()

    def stop_timers(self) -> None:
        """Stop the tick timer. The dashboard's `stop_timers` calls this for every run."""

        self._step_timer.stop()

    # -------------------------------------------------------------- layout

    def build_transport_row(self) -> QWidget:
        """This run's agent selector or chip, Start/Pause/Reset, playback rate, status and badge.

        There is one row per run rather than one for the dashboard. Each
        control acts on a particular controller, and a shared transport would
        leave a reader unable to say which run a press acted on.
        """

        return self._transport_row

    def _lay_out_transport_row(self) -> QWidget:
        """Build the transport row around this run's controls, once, for the constructor.

        Only the constructor calls this method. A second call would move the
        controls out of the row on screen (`PL-KZR1`).
        """

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(CONTROL_ROW_SPACING)
        self._transport_layout = layout
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
        # The version-and-model badge sits at the row's right end, beside the
        # run state that it qualifies. The in-page title row that it used to
        # sit in is gone (`PL-J8K2` Q2).
        layout.addWidget(self._agent_header_badge)

        return row

    def set_run_name(self, name: str | None) -> None:
        """Name this view in its own header, its readouts and both its record panels, or not at all.

        The dashboard decides the name by applying `dashboard_frame.run_label`
        to `run_id`. So this panel and the chart's legend call one run by the
        same name. A legend entry reading "Run 2" identifies a curve only if
        something that holds that run's settings also says "Run 2".

        **This method is the one writer of this run's name.** That is why the
        two sidebar headings are written here rather than in `refresh`. What
        a run is called changes when the dashboard's set of runs changes, and
        at no other time. `SimulationView._place_run` renames every run the
        moment a branch is placed. So the headings name the run on the frame
        on which the branch appears, before any chart frame is drawn
        (`PL-C3GS`).

        The name is also *stored* here, as well as drawn, because the notice
        banner is named from it too (`_write_notice`). That banner also sits
        in a column that the runs share. It is written on a path that has no
        frame to read a run count from (`PL-TSZM`). Unlike the headings, the
        banner is not written here, because something else already writes
        it. `refresh` rewrites every banner on the presentation that a fork
        triggers, and the Reset that drops a branch clears the notice
        outright. So a write here would make no difference that any scenario
        could detect. Nothing else writes the headings.

        Args:
            name: What to call the view, or `None` for no name. A lone run
                gets `None`, because there is no other run to tell it apart
                from.
        """

        self._run_name = name
        self._run_name_text.setText(name or "")
        self._run_name_text.setHidden(name is None)
        self._readout_row.set_run_name(name)

        for accounting_panel in self._accounting_panels:
            accounting_panel.show_heading(compared_panel_heading(ACCOUNTING_HEADING, name))

        self._control_timeline_heading_text.setText(
            compared_panel_heading(CONTROL_TIMELINE_HEADING, name)
        )

    def build_notice(self) -> QWidget:
        """The banner for a halted run or a refused setting, placed above every value."""

        return self._notice_text

    def build_readout_section(self) -> QWidget:
        """Return the substance heading with the interpretation line beside it, then the readouts.

        The heading says whose concentrations the seven panels under it show
        (`PL-TCD1`). The interpretation line sits on the same row, once,
        beside the values it qualifies (`PL-2K1R`). The delivered
        concentration and the agent's 1 MAC close the same row (`PL-NWTM`).
        """

        return self._readout_section

    def show_readings_of(self, other: RunView) -> tuple[QWidget, ...]:
        """Show `other`'s readouts in this run's panels, as one block for both runs.

        `docs/MODEL.md` § "Minimum displayed outputs" pairs two runs' values
        under one compartment name. So comparing them means reading one row
        rather than two (`PL-F2YS`). `other` keeps writing its own values, and
        only the place where they are drawn changes. The other run's own row
        is hidden, and this run's heading line states the other run's
        substance and 1 MAC. So nothing in the other run's readout section is
        left for the dashboard to show (`PL-QLZ5`).

        Args:
            other: The run being compared with this one.

        Returns:
            The widgets moved into this run's panels. Deleting them, as
            removing `other` does, takes them out again.
        """

        moved = self._readout_row.add_readings(other._readout_row)
        other._heading_shown_by = self

        return moved

    def _lay_out_readout_section(self) -> QWidget:
        """Build the section around this run's heading and readouts, once, for the constructor.

        Only the constructor calls this method. A second call would move the
        heading and readouts out of the section on screen (`PL-KZR1`).
        """

        section = QWidget()
        column = QVBoxLayout(section)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(READOUT_SECTION_SPACING)
        heading_row = QWidget()
        heading = QHBoxLayout(heading_row)
        heading.setContentsMargins(0, 0, 0, 0)
        heading.setSpacing(READOUT_HEADING_SPACING)
        self._heading_layout = heading
        heading.addWidget(self._compartment_substance_text)
        heading.addWidget(self._interpretation_text)
        heading.addStretch(1)
        heading.addWidget(self._delivered_text)
        heading.addWidget(self._one_mac_text)
        column.addWidget(heading_row)
        column.addWidget(self._readout_row)

        return section

    def build_parameter_controls(self) -> ParameterControls:
        """A new copy of the four setting controls in a row, in `PARAMETER_CONTROLS` order.

        Every call builds another copy showing the settings in force, and
        every copy forwards a moved slider to this run (`PL-9LNF`).
        """

        controls = ParameterControls(self._settings_shown, parent=self)
        controls.adjustment_started.connect(self._handle_adjustment_start)
        controls.setting_requested.connect(self._handle_setting_request)

        return keep_until_destroyed(self._setting_controls, controls)

    def build_accounting_panel(self) -> AccountingPanel:
        """A new copy of this run's mass-balance panel, for the sidebar beside the charts.

        `docs/MODEL.md` requires it to be reachable rather than always
        visible, so it is the one record of a run that may sit in a surface a
        reader can close (`PL-50PZ`). Every call builds another copy showing
        what the copies already built show (`PL-9LNF`).
        """

        return keep_until_destroyed(
            self._accounting_panels,
            AccountingPanel(
                self._accounting_shown,
                compared_panel_heading(ACCOUNTING_HEADING, self._run_name),
                parent=self,
            ),
        )

    def build_control_record(self) -> QWidget:
        """This run's control-change panel, for the unconditional region.

        The record of what was changed during the run is unconditional
        (`docs/MODEL.md` § "Minimum displayed outputs"), so it is never
        placed in a surface a reader can close (`PL-NWTM`).
        """

        return self._control_record_panel

    def unconditional_widgets(self) -> Mapping[UnconditionalValue, QWidget]:
        """The widget that draws each value of this run's unconditional set.

        `SimulationView` builds its unconditional region from this, and
        refuses a run whose set names a value this mapping lacks, so the
        declaration in `app/unconditional_set.py` is what decides what the
        region must hold (`PL-NWTM`). While another run's panels carry this
        run's readouts, that run's heading line draws this run's substance
        and 1 MAC, because the two runs share them (`PL-QLZ5`).

        Returns:
            One widget per value of `unconditional_set(INHALED_AGENT)`.
        """

        clock = self._readout_row.panels[_CLOCK_PANEL_INDEX]
        heading = self._heading_shown_by or self
        widgets: dict[UnconditionalValue, QWidget] = {
            UnconditionalValue.SIMULATED_TIME: clock.value_label,
            UnconditionalValue.PLAYBACK_RATE: self._playback_rate_text,
            UnconditionalValue.RUN_STATE: self._status_text,
            UnconditionalValue.HALT_REASON: self._notice_text,
            UnconditionalValue.ADMINISTERED_SUBSTANCE: heading._compartment_substance_text,
            UnconditionalValue.DELIVERED_CONCENTRATION: self._delivered_text,
            UnconditionalValue.ONE_MAC: heading._one_mac_text,
            UnconditionalValue.CONTROL_INPUT_RECORD: self._control_record_panel,
        }

        for panel, readout_panel in zip(self._readout_row.panels, READOUT_PANELS, strict=True):
            if readout_panel.quantity is not None:
                widgets[compartment_value(readout_panel.quantity)] = panel.value_label

        return widgets

    def _lay_out_control_record(self) -> QWidget:
        """Build the control-change panel, once, for the constructor.

        Only the constructor calls this method. A second call would move the
        labels out of the panel on screen (`PL-N67T`).
        """

        timeline_panel_frame = panel_frame("controlTimelinePanel")
        timeline_column = QVBoxLayout(timeline_panel_frame)
        timeline_column.setContentsMargins(
            PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING
        )
        timeline_column.setSpacing(CONTROL_TIMELINE_ROW_SPACING)
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

        return timeline_panel_frame


def _bold(font: QFont) -> QFont:
    bold = QFont(font)
    bold.setBold(True)

    return bold
