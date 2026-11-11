"""One run on the dashboard, with its controller, controls and readouts, in PySide6.

The dashboard has a part that all runs share and a part for each run
(`PL-B9PY`). `RunView` is the part for each run. It holds what two displayed
runs cannot share: a controller, seven readouts, the transport (the run's
playback controls), the agent identity, the notices and the control-change
panel. `SimulationView` holds what the runs do share. `RunView` can be
instantiated twice, and nothing in one instance refers to another run.

**A run's panel is the unconditional region's part of the run.** The setting
controls, the accounting panel, the compartment schematic and the agent cost
panel sit in Areas. The Views in `app/views.py` build and write them, from the
same `RunPresentation` that this class writes its own widgets from
(`PL-RF2S`). This class builds none of them and holds none of them. A View
asks for a change to a run's setting through the dashboard, which calls
`start_adjustment`, `request_setting`, `request_preview` or `end_preview` on
the run that the View named.

`app/dashboard_frame.py` decides every claim that this class displays, and
does so without a GUI toolkit. `app/run_presentation.py` calls that module's
functions once per tick and gathers the results into one value.
`show_presentation` writes that value into widgets that decide nothing
(`PL-25KS`, decision D2). No number is formatted here and no colour is
declared here. Colours come from `app/theme.py`, and they reach a widget
through the functions in `app/stylesheets.py` that compose stylesheets
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

**A halt is shown from the controller's record, before any attempt to draw a
frame.** `show_halt` writes the presentation that `presentation` builds when
it is given no snapshot. That presentation is built from the controller's
record, and reading that record builds no compartment value. The halt comes
before any attempt to draw a frame because the frame is drawn by a render
path that all runs share, and that path may be what raised. A halt reported
only through the frame would then leave every status word showing "Paused"
for a failed controller (`PL-25KS`). The halt comes from the record because
building a fresh snapshot builds compartment values. When building one of
those values was what raised, a halt reported from the snapshot was never
shown at all (`PL-7DJK`).

**Every widget of a run's panel is written by one method, from one value.**
`show_presentation` writes all of this class's widgets from one
`RunPresentation` (`app/run_presentation.py`). The run-state widgets show what
the run holds: the status word, the transport, the agent identity, the
delivered line, the control-change panel and the banner. The value widgets
show compartment values: the readouts and their clock. A drawn frame and a
halt each build a presentation, and `show_presentation` writes the same
widgets for both. On a halt the compartment values are the last frame's, or
are withheld together when the run has started over since that frame. An
earlier version of the halt code wrote to a list of widgets chosen by hand.
Each widget that the list missed went on showing the run as it was at the last
frame (`PL-X7D5`, `PL-RF2S`).

**Timers move the run and nothing else** (decision D7). Each run has one
`QTimer`, which drives `step_tick`. `step_tick` advances the controller by the
number of steps that the playback rate sets, and it never draws. The
dashboard's own render timer does the drawing. No wall clock is read.
Simulation time is a count of the steps taken. A tick takes no step while a
question is open in the window, because the question blocks the Pause button
(`hold_while`).
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

from anesthesia_sim.app.agent_cost import WITHHELD_DELIVERED
from anesthesia_sim.app.chart_frame import PreviewRequest
from anesthesia_sim.app.compartment_schematic import WITHHELD_SCHEMATIC
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import (
    AdjustmentGrouping,
    ControlAdjustment,
    wrapping_between_parts,
)
from anesthesia_sim.app.controller import (
    RunRecord,
    RunStatus,
    SettingPreview,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
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
    HaltDisposition,
    NewCaseQuestion,
    Transport,
    accounting,
    compared_panel_heading,
    halt_disposition,
    new_case_question,
    preview_label,
    readouts,
    refused_reset_exit,
    refused_setting_notice,
    run_label,
    status_word,
    substance_heading,
    timeline_panel,
    transport,
)
from anesthesia_sim.app.formatting import format_playback_rate, format_subtitle
from anesthesia_sim.app.halt_gate import halt_gate
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_widgets import NewCaseDialog, NoticeLabel, ReadoutRow, styled_label
from anesthesia_sim.app.run_presentation import (
    KeptValues,
    NotBuilt,
    RunPanelState,
    RunPresentation,
    RunValues,
    ValuesStanding,
    drawn_run,
    halted_run,
)
from anesthesia_sim.app.run_surfaces import emphasised, panel_frame
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

    Every part built here belongs to the unconditional region, which is
    always on screen, and there is one of each per run. The build methods
    return the same widgets on every call, laid out once when the run was
    built. Adding a widget to a Qt layout removes it from wherever it sat
    before. So an earlier version, which built a new container on each call,
    took the run's live widgets off the screen. It then deleted them when the
    container was dropped (`PL-N67T`, `PL-KZR1`).

    `dashboard_frame` decides what is rejected on each tick. Which setting
    values the core rejects, and how a raise is reported, are read from the
    exception and never guessed (`PL-V6M0`, `PL-Y5WR`, `PL-YK2V`; see the
    module docstring).

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
            trunk run, that starts a new case, so no branch taken from the old
            run can be compared with anything any more. The dashboard acts on
            the signal, because this view does not know which other runs are
            on screen.
    """

    presentation_requested = Signal(bool)
    case_restarted = Signal()

    def __init__(
        self,
        controller: SimulationController,
        parent: QWidget | None = None,
        *,
        run_id: RunId,
        branch_control: bool,
    ) -> None:
        """Build one run's controls and readouts from its first snapshot.

        Args:
            controller: The run this view drives and displays.
            parent: The Qt parent.
            run_id: The run's identity, minted by the dashboard that places it.
            branch_control: Whether the dashboard that places this run has a
                branch control. A dashboard with no case has none, so the
                banner never names a branch there (`_branch_offered`).

        Raises:
            TypeError: If `run_id` is not a `RunId`.
        """

        if not isinstance(run_id, RunId):
            raise TypeError(f"a run's identity is a RunId, not {type(run_id).__name__}")

        super().__init__(parent)
        self.controller = controller
        self.run_id = run_id
        self._branch_control = branch_control
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
        # The setting a reader is dragging on this run and has not applied,
        # or None while no thumb is held (`PL-5B1N`). It is held here rather
        # than in the controller for the same reason: nothing about the
        # simulation changes until the drag is released.
        self._preview: PreviewRequest | None = None
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
        # Whether this run must take no step. Until the dashboard says
        # otherwise (`hold_while`), the run holds while one of its own
        # questions is open.
        self._held: Callable[[], bool] = lambda: self.asks_a_question
        # Whether a frame has drawn this run yet. A coalesced slider change
        # rewrites this run's own labels at once, but only after the first
        # frame has written everything.
        self._presented = False
        # The run's record as this view last wrote it, through `show_presentation`. It is
        # `None` until the first write. The dashboard draws a frame whenever
        # the controller's record differs from it (`owes_a_frame`).
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
        # from (`run_presentation.halted_run`). Reading the name back from the widget would
        # make the banner's attribution depend on a label's text, which is a
        # display detail.
        self._run_name: str | None = None
        self._status_text = styled_label("", color=MUTED, bold=True)
        emphasised(
            self._status_text, status_word(snapshot, stopped_on_mark=snapshot.stopped_on_mark)
        )
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
        # These two labels sit on the heading line above the row. One shows the
        # delivered dial's setting in both units. The other shows the 1 MAC value
        # that divides every ×MAC number in the row. Both values are in
        # `docs/MODEL.md`'s per-substance tier. The dial and the chart's caption
        # cannot carry them, because each is now a View that a reader can close
        # (`PL-NWTM`). `show_presentation` writes both from one record on every
        # path, so the two cannot disagree.
        self._delivered_text = styled_label("", color=INK)
        self._one_mac_text = styled_label("", color=MUTED)
        self._readout_row = ReadoutRow(
            readouts(snapshot, self._playback_rate), reservations=READOUT_RESERVATIONS
        )
        # How many times the run has started over, by a Reset or an agent
        # change, and the compartment values of the last frame that drew, with
        # the count at that frame. Only a frame computes those values. When the
        # two counts differ, the kept values describe the run that was
        # discarded, and a halt withholds them (`run_presentation.halted_run`,
        # `PL-6RJ0`, adversarial review of `PL-J5GC`). Before any frame, the
        # kept readouts are the ones the readout row is built with. The
        # schematic and the delivered agent start withheld, because nothing
        # has been drawn yet (`PL-RNYV`, `PL-B396`).
        self._case = 0
        self._kept = KeptValues(
            self._case,
            RunValues(
                readouts=readouts(snapshot, self._playback_rate),
                schematic=WITHHELD_SCHEMATIC,
                delivered=WITHHELD_DELIVERED,
                accounting=replace(accounting(snapshot), detail=ACCOUNTING_INITIAL_DETAIL_TEXT),
            ),
        )

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

        The dashboard reads it once per frame and hands it back to `presentation`.
        So the readouts and the traces of a frame show one instant of one run.
        """

        return self.controller.snapshot()

    @property
    def is_running(self) -> bool:
        """Whether this run is advancing."""

        return self.controller.is_running

    @property
    def asks_a_question(self) -> bool:
        """Whether this run's Reset question or new-case question is open."""

        return self._reset_dialog is not None or self._new_case_dialog is not None

    def hold_while(self, held: Callable[[], bool]) -> None:
        """Take no step on any tick at which `held` returns True.

        A question that this run or the dashboard opens is window-modal, so
        while it is open the reader cannot press Pause on any run. The run
        therefore holds, and it carries on as it was once the question closes:
        a running run runs again, a paused run stays paused, and the playback
        rate is unchanged. The hold changes nothing in the controller. It only
        skips ticks, so the run's trajectory is the same as if the reader had
        answered at once (`PL-TPBH`, decided by the project owner on
        2026-10-31). Before this, a reader who read the question for ten
        seconds at 300× came back to a case 50 simulated minutes on.

        Args:
            held: Returns True while a question is open anywhere in the
                window. The dashboard passes one predicate to every run, so
                a question about one run holds all of them.
        """

        self._held = held

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

    @property
    def preview(self) -> PreviewRequest | None:
        """The setting a reader is dragging on this run, for the chart to preview, or `None`."""

        return self._preview

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

    def presentation(self, drawn: SimulationSnapshot | None = None) -> RunPresentation:
        """Build everything this run's panel shows now, for `show_presentation` to write.

        With a snapshot, the values are computed from it, and the banner is
        the one `dashboard_frame.notice` gives for a frame that drew. With
        none, the run is stated from `SimulationController.record()` alone,
        which builds no compartment value. A snapshot builds every
        compartment's fraction, and one of the halts stated this way is the
        refusal of one of those fractions (`PL-7DJK`). The values are then
        the last frame's, or withheld if the run has started over since
        that frame (`run_presentation.halted_run`).

        Args:
            drawn: The snapshot that this tick's frames were drawn from, read
                once by the caller. None when no frame can be drawn.

        Returns:
            The presentation. Building it writes nothing.

        Raises:
            TypeError: As `run_presentation.drawn_run` raises it.
            ValueError: As `run_presentation.drawn_run` raises it. Neither
                is raised when `drawn` is None.
        """

        state = RunPanelState(
            run_id=self.run_id,
            name=self._run_name,
            case=self._case,
            playback_rate=self._playback_rate,
            is_branch=self._is_branch,
            comparing=self._comparing,
            branch_offered=self._branch_offered,
            rejected_setting_notice=self._rejected_setting_notice,
            refused_reset_notice=self._refused_reset_notice,
            pending_agent_name=(
                None
                if self._new_case_dialog is None or self._pending_agent_id is None
                else AGENT_DISPLAY_NAMES[self._pending_agent_id]
            ),
        )

        if drawn is None:
            record = self.controller.record()

            return halted_run(record, self.adjustments(record), state, self._kept)

        return drawn_run(drawn, self.adjustments(drawn), state)

    def show_presentation(self, presentation: RunPresentation) -> None:
        """Write every widget of this run from one presentation, as their only writer.

        A drawn frame and a halt both come here, each with a
        `RunPresentation`, and this method writes the same widgets for both
        (`PL-X7D5`, `PL-RF2S`). A halt can follow a change that no frame has
        shown: a dial dragged into the halt (`PL-85LJ`), an agent changed
        just before it (`PL-1YDD`), or a drag that took a change off the
        record (`PL-DTJQ`). So a halt is written as fully as a frame is. A
        widget added here is written on both paths.

        The writes keep one order. The run-state widgets come first: the
        agent colour, which is written before anything that shows it, then
        the status word, the transport, the 1 MAC line, the delivered line
        and the banner. The readouts follow. So a halt is stated before any
        write that can fail. A frame whose readouts cannot be written halts
        the run, and that halt is then on screen even if the same write
        fails again (`PL-25KS`, `PL-7DJK`, `PL-85LJ`).

        Of the four compartment values, this panel writes only the readouts.
        The Views write the schematic, the delivered agent and the
        accounting panel from the same presentation (`app/views.py`). All
        four values of a drawn frame are kept for a later halt once the
        readouts have been written. So a halt rewrites the last frame that
        the panel showed.

        A 1 MAC line that could not be built (`NotBuilt`) is cleared, so
        that it cannot state another agent's MAC above this run's values
        (`PL-6RJ0`). Where the dials could not be built, the delivered line
        withholds its values (`PL-SV2Q`), and the setting controls View
        shows no dial for this run. Either refusal is raised once every
        widget has been written.

        Before writing anything, the method stores the presentation's record
        as the one this view last wrote. The render tick draws whenever a
        run's record differs from the stored one (`owes_a_frame`). So when a
        frame fails for a cause that is still there, the render tick does
        not retry it on every tick.

        Each chart writes the lines that depend on its window, such as which
        traces are above the axis, from its own frame (`PL-L59K`).

        Args:
            presentation: What `presentation` built for this run.

        Raises:
            ValueError: If the presentation was built for another run. Then
                nothing is written. Also if the presentation's dials could
                not be built (`NotBuilt`), for a control with no step of
                its resolution inside the range the run accepts (`PL-7CRY`).
                Every widget has been written by then.
            Exception: Whatever else building the 1 MAC line or the dials
                raised, such as a `TypeError` for a record whose MAC was not
                built as `MacPercent`. Every widget has been written by
                then.
        """

        if presentation.run_id != self.run_id:
            raise ValueError(
                f"a presentation built for {run_label(presentation.run_id)} was given to the "
                f"panel of {run_label(self.run_id)}: build it with that panel's `presentation`"
            )

        self._written_record = presentation.record
        drawn = presentation.standing is ValuesStanding.DRAWN

        if drawn:
            self._presented = True

        statement = presentation.statement
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
        # The 1 MAC line states the divisor of the delivered line beside it and of the
        # cards' ×MAC numbers. Both lines are written before the cards. So a refusal
        # raised for the cards cannot leave another agent's 1 MAC on screen, or
        # another run's delivered setting (`PL-6RJ0`, `PL-SV2Q`).
        one_mac = presentation.one_mac
        self._one_mac_text.setText("" if isinstance(one_mac, NotBuilt) else one_mac)
        self._delivered_text.setText(presentation.delivered_line)
        self._notice_text.set_notice(presentation.notice)

        values = presentation.values
        self._readout_row.set_readouts(values.readouts)

        if drawn:
            self._kept = KeptValues(presentation.case, values)

        if presentation.new_case is not None and self._new_case_dialog is not None:
            self._new_case_dialog.show_question(presentation.new_case)

        if drawn:
            self._restate_reset_question()

        for part in (one_mac, presentation.dials):
            if isinstance(part, NotBuilt):
                raise part.error

    def show_halt(self) -> None:
        """Write this run from its controller's record, when no frame can be drawn.

        Before the presentation is built, the record is stored as the one this
        view last wrote. So a halt that cannot be built is not tried again on
        every render tick, with its exception printed each time
        (`owes_a_frame`).

        Raises:
            Exception: As `show_presentation` raises it.
        """

        self._written_record = self.controller.record().run_record()
        self.show_presentation(self.presentation())

    def _refresh_against_last_frame(self, snapshot: SimulationSnapshot) -> None:
        """Rewrite this run's own widgets now, from `snapshot`, while the charts wait.

        After a coalesced slider change, what is shown beside the dial must
        be updated at once. It has to agree with the snapshot from the moment
        the setting is applied (`PL-018`). The frame itself waits for the
        render tick (`PL-R2YM`). The values written here are kept, and the
        dashboard hands them to every View when this run then asks for a
        coalesced frame. Before the first presentation this method rewrites
        nothing, because the first presentation writes everything.

        Args:
            snapshot: This run's state, read by `_apply_setting` after the change.
        """

        if self._presented:
            self.show_presentation(self.presentation(snapshot))

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

    @property
    def _branch_offered(self) -> bool:
        """Whether a branch can be taken from this run now, for the stopped run's banner.

        None can be taken on a dashboard with no branch control, which is one
        built with no case. None can be taken while two runs are compared,
        because `fork_offer` locks the branch control then. None can be taken
        from a run whose `fork_refusal` gives a reason: a branch, or a trunk
        whose dashboard failed. Otherwise the control offers at least the
        run's opening.
        """

        return self._branch_control and not self._comparing and self.controller.fork_refusal is None

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
        to the setting the run holds.

        The method leaves the frame for the render tick to draw only when two things
        are true: `coalesce` is set, and no refusal was in effect before the call or
        is in effect after it. When a setting is refused, or a refusal is cleared, the
        dial on screen and the simulation disagree, so neither may wait for a tick
        (`PL-R2YM`). A coalesced change still rewrites this run's own labels at once,
        from a snapshot read after the change. The dashboard then shows every View the
        runs at once, with no frame, so the dials and the other panels of the run move
        with its readouts (`SimulationView.present`). If reading that snapshot raises,
        the gate halts the run and shows the halt. Before `PL-V2HC`, the exception
        escaped the slot after the setting had been applied. After the halt, the
        dashboard draws a frame or halts every run, and either one hands every View the
        runs. So the halted run's dials show the settings it holds (`PL-85LJ`). The
        rewrite of the labels can raise too, as it does for a control that can offer no
        setting, whose dials cannot be built. The gate halts the run for that as well.
        So the status word, the transport controls and the banner show the halt first.
        Showing the halt then raises the same refusal again, and the exception escapes
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
    def start_adjustment(self) -> None:
        """Close any open adjustment, so the changes that follow are a new act.

        The dashboard calls this method when a View says that the reader
        pressed one of this run's dials. It does not go through
        `_apply_setting`, because it records nothing and changes no state.
        Without it, two drags of one dial would be one adjustment on the
        record.
        """

        self.controller.begin_control_adjustment()

    @halt_gate
    def request_preview(self, control: ControlInput, value: float) -> None:
        """Preview the value a held thumb stands at, or drop the preview if the run would refuse it.

        The dashboard calls this method when a View says where a held dial
        of this run stands. During the drag, the run keeps its current setting (`ParameterSlider`).
        The value is checked by building the settings it would give
        (`SimulationController.preview_settings`). The run refuses a value when
        the run has stopped or the value is outside the core's range. A value
        the run would refuse draws no preview, so the chart never predicts a
        future the run cannot have. The release then reports the refusal
        through `_apply_setting`, as it reports any refused setting. The chart
        is redrawn on the next render tick, as a dragged slider's frames always
        were (`PL-R2YM`).
        """

        setting = SettingPreview(control, value)

        try:
            self.controller.preview_settings(setting)
        except SimulationConfigurationError:
            self._preview = None
        else:
            self._preview = PreviewRequest(
                setting,
                preview_label(
                    control, value, self.controller.settings().agent_display_name, self._run_name
                ),
            )

        self.presentation_requested.emit(True)

    @halt_gate
    def end_preview(self) -> None:
        """Drop the preview when the held thumb is released, and redraw at once.

        The dashboard calls this method when a View says that a held dial of
        this run was released. A preview that outlived the drag could be mistaken for a run that
        happened, so it is gone from the frame drawn at the release. The slider
        has applied the released value by then (`ParameterSlider`), so that
        frame shows the run under its new setting (`PL-5B1N`).
        """

        self._preview = None
        self.presentation_requested.emit(False)

    @halt_gate
    def request_setting(self, control: ControlInput, value: float) -> None:
        """Apply the value that one of this run's dials was moved to, in whichever View holds it.

        The dashboard calls this method when a View asks for the change.
        """

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
        instant that branch has run to. Before `PL-TPBH`, a branch went on
        stepping while the question was open. So a question written only once,
        when it opened, understated the branch work that the reader was about
        to discard (`PL-WM5P`). Every run now holds while the question is open
        (`hold_while`), so the figures do not change. The question is still
        rewritten on each frame. That costs one callback per frame, and it
        keeps the question true to the runs even if a later change lets a run
        move while a question is open. The dashboard's `ask_before_reset`
        callback reads every branch's controller.

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
        self._announce_the_start_over()
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
        `show_presentation` puts the selector back to the agent that the controller's
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
        `show_presentation`. Signals are blocked while the selector is put back, so
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
            self._announce_the_start_over()

        self._apply_setting(switch)

    def _announce_the_start_over(self) -> None:
        """Record that the run has started over since the last frame drew, then say so.

        `_reset_now` and an accepted agent change call this method. Until a
        frame draws, every compartment value on screen describes the run that
        was discarded, so a halt withholds them
        (`run_presentation.halted_run`). After recording the start-over, this
        method emits `case_restarted` for the dashboard.
        """

        self._case += 1
        self.case_restarted.emit()

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
        halt, `_halt_run` and `SimulationView._halt_every_run` call `show_halt`
        after they call this method.

        Args:
            error: The exception that was raised.
            in_frame: True when the exception came from the dashboard that
                draws every run, either from its frame or from one of its own
                slots. False when it came from this run's own step or setting.
                The controller also records an exception from the dashboard,
                and a trunk with that record offers no branch
                (`SimulationController.record_failed_frame`).

        Raises:
            TypeError: If an `AgentSimulationValidationError` carries a check
                that is not a validation result (`rejected_check`). The run
                has failed by then.
        """

        disposition, reason = halt_disposition(error)

        if in_frame:
            self.controller.record_failed_frame(reason)

        if disposition is HaltDisposition.SUPPORTED_LIMIT:
            self.controller.halt_at_supported_limit(reason)
        elif isinstance(error, AgentSimulationValidationError):
            # The core rolled the step back, so only the error still holds the
            # rejected step's check (`PL-HF4B`). A check of the wrong type is a
            # defect in the code that raised the error, and it must not cancel
            # the halt. So the run fails first, and the `TypeError` that reports
            # the defect is raised afterwards.
            try:
                rejected = rejected_check(error)
            except TypeError:
                self.controller.fail(reason)
                raise

            self.controller.fail(reason, rejected_accounting=rejected)
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

        `show_presentation` can raise an exception after it has written the halt,
        when a dial cannot be written (`PL-M3M2`). The frame is still asked
        for, because the dashboard rewrites its own panels, such as "Branch
        here", only when it draws a frame. No frame used to be asked for here,
        so those panels kept offering the halted run as it was before the halt
        (blind review of `PL-HJKN`).

        Args:
            error: The exception that was raised.

        Raises:
            Exception: What `show_halt` raised, once the frame has been asked for.
        """

        self.halt(error)

        try:
            self.show_halt()
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
        no step is made up. A tick takes no step while `hold_while`'s
        predicate returns True, that is, while a question is open.
        """

        if not self.controller.is_running or self._held():
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
        """Name this view in its own header, its readouts and its control-change panel, or not.

        The dashboard decides the name by applying `dashboard_frame.run_label`
        to `run_id`. So this panel and the chart's legend call one run by the
        same name. A legend entry reading "Run 2" identifies a curve only if
        something that holds that run's settings also says "Run 2".

        **This method is the one writer of this run's name on its own
        panel.** That is why the control-change heading is written here
        rather than in `show_presentation`. What a run is called changes
        when the dashboard's set of runs changes, and at no other time.
        `SimulationView._place_run` renames every run the moment a branch is
        placed. So the heading names the run on the frame on which the
        branch appears, before any chart frame is drawn (`PL-C3GS`).

        The name is *stored* here as well as drawn, because every
        presentation carries it (`presentation`). The notice banner is named
        from it. That banner sits in a column that the runs share, and it is
        written on a path that has no frame to read a run count from
        (`PL-TSZM`). The Views name the accounting panel, the schematic and
        the agent cost panel from it too, on the tick that follows the
        change to the run set. Neither is written here, because
        `show_presentation` and the Views write them from the presentation
        that the change to the run set brings.

        Args:
            name: What to call the view, or `None` for no name. A lone run
                gets `None`, because there is no other run to tell it apart
                from.
        """

        self._run_name = name
        self._run_name_text.setText(name or "")
        self._run_name_text.setHidden(name is None)
        self._readout_row.set_run_name(name)
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
