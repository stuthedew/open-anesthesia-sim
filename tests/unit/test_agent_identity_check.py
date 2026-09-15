"""Tests for `tools/agent_identity_check.py`, the rendered-disabled checker.

The tool exists to catch drift nobody remembered to look for, so each rule has
a test that breaks the view and asserts the tool notices, and a matching test
that asserts the correct form stays quiet. A checker that fires on correct work
gets disabled, which is the same as not having it.

Fixtures build a miniature `src/anesthesia_sim/app/` holding one view module,
or two where the test is about the view being split across modules, each
holding only what the rule under test is about. The real tree is checked once,
at the end, by the same entry point `make check` runs - which is what keeps
the miniature from drifting into a shape the tool handles and the shipped code
does not.

Nothing here imports a toolkit or constructs a control. The tool reads source
with `ast` and never runs it, so a fixture is a string - one in the attribute
spelling the Flet build used and one in the setter spelling PySide6 uses, since
the tool reads both (`PL-25KS`).
"""

from __future__ import annotations

from pathlib import Path

import agent_identity_check
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A view whose one identity control is hidden by the negation of the same
#: expression that disables it - the shape the shipped code is in.
PAIRED_SOURCE = '''"""Miniature view."""

AGENT_COLOR_SCHEMES = {"demoflurane": AgentColorScheme(fill="#111111", foreground="#FFFFFF")}
AGENT_RENDER_STYLES = {"demoflurane": RenderStyle(badge_border=None)}


class SimulationView:
    def __init__(self, initial_snapshot):
        colors = AGENT_COLOR_SCHEMES[initial_snapshot.agent_id]
        self._agent_dropdown = Dropdown(color=colors.foreground, bgcolor=colors.fill)

    def _refresh_view(self, snapshot):
        self._agent_dropdown.disabled = snapshot.is_running
        self._agent_dropdown.visible = not snapshot.is_running

    def _apply_agent_color_scheme(self, agent_id):
        scheme = AGENT_COLOR_SCHEMES[agent_id]
        self._agent_dropdown.color = scheme.foreground
'''

#: The same view in the setter spelling: the shape the PySide6 build is in.
#: `setDisabled(E)` beside `setHidden(E)` on the identity control, a hide on the
#: chip that replaces it, a plain `setEnabled` on the transport, and a writer
#: that colours through `setStyleSheet` calls rather than property assignments.
PAIRED_QT_SOURCE = '''"""Miniature view, Qt spelling."""

AGENT_COLOR_SCHEMES = {"demoflurane": AgentColorScheme(fill="#111111", foreground="#FFFFFF")}


class RunView:
    def __init__(self):
        self._agent_dropdown = QComboBox()
        self._running_agent_display = QFrame()
        self._start_button = QPushButton("Start")

    def refresh(self, snapshot):
        self._agent_dropdown.setDisabled(snapshot.is_running)
        self._agent_dropdown.setHidden(snapshot.is_running)
        self._running_agent_display.setVisible(snapshot.is_running)
        self._start_button.setEnabled(not snapshot.is_running)

    def _apply_agent_color_scheme(self, agent_id):
        scheme = AGENT_COLOR_SCHEMES[agent_id]
        self._agent_dropdown.setStyleSheet(f"color: {scheme.foreground};")
        self._running_agent_display.setStyleSheet(f"background-color: {scheme.fill};")
'''

#: A second module holding a class with no agent colour in it: the shape of a
#: view split across modules where the other half carries nothing.
PLAIN_PANEL_SOURCE = '''"""A panel with nothing agent-coloured in it."""


class ChartPanel:
    def __init__(self):
        self._legend = Text("legend")

    def _refresh(self, snapshot):
        self._legend.disabled = snapshot.is_running
'''


def _module(tmp_path: Path, name: str, source: str) -> Path:
    """Write one miniature module under `app/` and return the tree's root."""

    target = tmp_path / agent_identity_check.APP / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return tmp_path


def _view(tmp_path: Path, source: str) -> Path:
    """Write one miniature view into a throwaway tree and return its root."""

    return _module(tmp_path, "simulation_view.py", source)


def test_the_paired_shape_is_quiet(tmp_path: Path) -> None:
    """Disabled beside `visible = not <the same expression>` is the correct form."""

    assert agent_identity_check.problems(_view(tmp_path, PAIRED_SOURCE)) == []


def test_a_disabled_identity_control_without_the_paired_hide_is_reported(tmp_path: Path) -> None:
    """The regression `PL-61WW` was, in the form a later change would reintroduce it.

    A control that follows the agent colour and is disabled while still on
    screen has its label painted in Flet/Material's disabled-content grey -
    a colour `app/theme.py` never declares and `tools/contrast_check.py`
    therefore cannot measure. The whole point is that nothing else in this
    repository goes red on it.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown.visible = not snapshot.is_running\n", ""
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "_agent_dropdown" in found[0]
    assert "visible = not snapshot.is_running" in found[0]


def test_a_control_that_is_never_disabled_is_quiet(tmp_path: Path) -> None:
    """The other correct answer: carry identity in a control with no disabled state.

    `_running_agent_display` is that answer in the shipped view, so a rule
    that demanded a `visible` line from every identity control would fire on
    the fix `PL-61WW` landed. The fixture keeps a `disabled` write on a
    control that is *not* agent-coloured, because a tree with no such write
    anywhere is the empty-measurement case below, which is a different answer
    and deliberately not a quiet one.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown.disabled = snapshot.is_running\n"
        "        self._agent_dropdown.visible = not snapshot.is_running\n",
        "        self._agent_dropdown.value = snapshot.agent_id\n"
        "        self._start_button.disabled = snapshot.is_running\n",
    )

    assert agent_identity_check.problems(_view(tmp_path, source)) == []


def test_a_differently_written_hide_does_not_satisfy_the_pairing(tmp_path: Path) -> None:
    """The comparison is structural, and that is deliberate rather than a limitation.

    `visible = snapshot.is_paused` may well be correct, but nothing here can
    know it is - proving two conditions equivalent is the judgment half, and a
    tool that guessed at it would report an authoritative pass it could not
    support. One canonical shape, and a failure that says which shape.
    """

    source = PAIRED_SOURCE.replace(
        "self._agent_dropdown.visible = not snapshot.is_running",
        "self._agent_dropdown.visible = snapshot.is_paused",
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "visible = not snapshot.is_running" in found[0]


def test_a_control_coloured_at_construction_must_follow_the_agent(tmp_path: Path) -> None:
    """Rule 2: what keeps rule 1's coverage claim true rather than asserted.

    A control built from an agent colour that `_apply_agent_color_scheme`
    never writes is outside rule 1 entirely - and is a stale-label bug in its
    own right, showing the previous agent's identity over the current agent's
    numbers.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown = Dropdown(color=colors.foreground, bgcolor=colors.fill)\n",
        "        self._agent_dropdown = Dropdown(color=colors.foreground, bgcolor=colors.fill)\n"
        "        self._stale_badge = Container(bgcolor=colors.fill)\n",
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "_stale_badge" in found[0]
    assert agent_identity_check.IDENTITY_WRITER in found[0]


def test_a_colour_taken_from_the_table_inline_is_seen_too(tmp_path: Path) -> None:
    """Rule 2 reads both spellings, because the shipped view uses both.

    The dropdown's options take `AGENT_COLOR_SCHEMES[agent_id].fill` written
    out in place, inside the same call whose other arguments come through a
    local. Reading only the local would miss a control coloured the other way.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown = Dropdown(color=colors.foreground, bgcolor=colors.fill)\n",
        "        self._agent_dropdown = Dropdown(color=colors.foreground, bgcolor=colors.fill)\n"
        '        self._swatch = Container(bgcolor=AGENT_COLOR_SCHEMES["demoflurane"].fill)\n',
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "_swatch" in found[0]


def test_a_missing_writer_is_an_error_rather_than_an_empty_pass(tmp_path: Path) -> None:
    """A coverage set that can silently go empty is worse than no check.

    Renaming `_apply_agent_color_scheme` would otherwise leave this tool
    measuring nothing and printing a pass, which is the "looks authoritative
    and is not" failure `tools/contrast_check.py`'s docstring names.
    """

    source = PAIRED_SOURCE.replace(
        f"    def {agent_identity_check.IDENTITY_WRITER}(self, agent_id):",
        "    def _apply_agent_colours(self, agent_id):",
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert agent_identity_check.IDENTITY_WRITER in found[0]


def test_an_app_tree_with_no_modules_is_reported(tmp_path: Path) -> None:
    """An absent package is a failure, not a tree with nothing to check."""

    found = agent_identity_check.problems(tmp_path)

    assert len(found) == 1
    assert agent_identity_check.APP.as_posix() in found[0]


# --- the view split across modules (PL-V53R) ---------------------------------


def test_the_writer_is_found_in_whichever_app_module_holds_it(tmp_path: Path) -> None:
    """`PL-B9PY` kept both classes in one file so this tool would see them; the port will not.

    The writer's class in a module of its own, and the old module holding a
    class with nothing agent-coloured in it: the shape the decomposed Qt view
    leaves, and a correct tree, so quiet.
    """

    root = _module(tmp_path, "run_view.py", PAIRED_SOURCE)
    _module(root, "simulation_view.py", PLAIN_PANEL_SOURCE)

    report = agent_identity_check.analyze(root)

    assert report.problems == ()
    assert (
        report.writer
        == "src/anesthesia_sim/app/run_view.py:SimulationView._apply_agent_color_scheme"
    )
    assert report.modules == 2


def test_rule_two_reaches_a_class_in_another_module(tmp_path: Path) -> None:
    """The silent case `PL-V53R` was filed for: an agent-coloured control the tool never read.

    A class in a module other than the writer's builds a control from the
    colour table. The writer cannot write another class's attribute, so the
    control is outside the identity set by construction, and until every
    module was read nothing said so.
    """

    root = _module(tmp_path, "run_view.py", PAIRED_SOURCE)
    _module(
        root,
        "chart_panel.py",
        PLAIN_PANEL_SOURCE.replace(
            '        self._legend = Text("legend")\n',
            '        self._legend = Text("legend")\n'
            '        self._swatch = Container(bgcolor=AGENT_COLOR_SCHEMES["demoflurane"].fill)\n',
        ),
    )

    found = agent_identity_check.problems(root)

    assert len(found) == 1
    assert "chart_panel.py:ChartPanel._swatch" in found[0]


def test_a_second_writer_in_another_module_is_an_error(tmp_path: Path) -> None:
    """Two classes defining the writer is two writers of agent colour, which the design forbids."""

    root = _module(tmp_path, "run_view.py", PAIRED_SOURCE)
    _module(
        root, "simulation_view.py", PAIRED_SOURCE.replace("class SimulationView", "class Other")
    )

    found = agent_identity_check.problems(root)

    assert len(found) == 1
    assert "2 classes" in found[0]
    assert "run_view.py:SimulationView" in found[0]
    assert "simulation_view.py:Other" in found[0]


def test_a_same_named_control_in_another_class_is_not_the_identity_control(tmp_path: Path) -> None:
    """Rule 1 reads the writer's class; `self.X` elsewhere is a different control.

    Another class disabling its own `_agent_dropdown` with no paired hide is
    not the identity control being rendered disabled, because that attribute
    is not the one the writer colours. Keyed by name alone across modules it
    would be a false positive, and the fix to a false positive is what
    disables a checker.
    """

    root = _module(tmp_path, "run_view.py", PAIRED_SOURCE)
    _module(
        root,
        "simulation_view.py",
        PLAIN_PANEL_SOURCE.replace(
            "        self._legend.disabled = snapshot.is_running\n",
            "        self._legend.disabled = snapshot.is_running\n"
            "        self._agent_dropdown.disabled = snapshot.is_running\n",
        ),
    )

    assert agent_identity_check.problems(root) == []


# --- the empty measurement set (PL-0PJG) -------------------------------------


def test_an_identity_set_with_no_disabled_write_read_anywhere_is_an_error(tmp_path: Path) -> None:
    """A tree that disables nothing, in either spelling, is an empty measurement.

    The affirmative sentence "none of them rendered disabled" cannot be told
    from the same sentence earned when the pairing loop ran zero times, so
    the empty set is the error rather than a pass (`PL-0PJG`). This check
    cannot tell a tree that genuinely disables nothing from one written in a
    spelling it has not been taught, and says so.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown.disabled = snapshot.is_running\n"
        "        self._agent_dropdown.visible = not snapshot.is_running\n",
        "        self._agent_dropdown.value = snapshot.agent_id\n",
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "measured nothing" in found[0]
    assert "setEnabled" in found[0]


def test_a_setter_spelled_disabled_write_is_read_rather_than_measured_as_nothing(
    tmp_path: Path,
) -> None:
    """`PL-JRS3`'s probe B, which printed "none of them rendered disabled" and exited 0.

    Every identity control driven by `setEnabled()` with no paired hide. Until
    `PL-25KS` taught rule 1 the setter spelling that tree was an empty
    measurement; now the write is read and the missing hide is the finding,
    named in the same spelling.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown.disabled = snapshot.is_running\n"
        "        self._agent_dropdown.visible = not snapshot.is_running\n",
        "        self._agent_dropdown.setEnabled(not snapshot.is_running)\n",
    )

    found = agent_identity_check.problems(_view(tmp_path, source))

    assert len(found) == 1
    assert "measured nothing" not in found[0]
    assert "_agent_dropdown" in found[0]
    assert "setVisible(not snapshot.is_running)" in found[0]


def test_the_success_line_states_what_it_measured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The sentence carries its evidence, so it cannot be printed from nothing."""

    root = _module(tmp_path, "run_view.py", PAIRED_SOURCE)
    _module(root, "simulation_view.py", PLAIN_PANEL_SOURCE)

    assert agent_identity_check.main(["--root", str(root)]) == 0
    out = capsys.readouterr().out
    assert "1 control(s) carry the agent colour" in out
    assert "2 disabled-state write(s) read across 2 module(s)" in out
    assert "1 of them on identity controls" in out
    # The dropdown built from `colors` in `__init__`; nothing coloured by a call.
    assert "1 construction-time and 0 call-time agent colouring(s)" in out


# --- the setter spelling (PL-25KS) -------------------------------------------


def test_the_paired_qt_shape_is_quiet(tmp_path: Path) -> None:
    """`setDisabled(E)` beside `setHidden(E)` is the correct form in the setter spelling."""

    assert agent_identity_check.problems(_module(tmp_path, "run_view.py", PAIRED_QT_SOURCE)) == []


def test_an_unpaired_qt_disabled_write_is_reported_in_its_own_spelling(tmp_path: Path) -> None:
    """The `PL-61WW` regression as a PySide6 build would reintroduce it.

    The finding names the hiding line in the spelling the write used, so the
    fix is a line to add rather than a spelling to translate.
    """

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n", ""
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "_agent_dropdown" in found[0]
    assert "setDisabled(snapshot.is_running)" in found[0]
    assert "setHidden(snapshot.is_running)" in found[0]


def test_a_writer_colouring_through_set_style_sheet_yields_its_controls(tmp_path: Path) -> None:
    """The identity set counts a call statement on a control as a write.

    A Qt writer assigns no property - it colours through `setStyleSheet` -
    and a reader of assignments alone saw an empty set, which is the
    "coverage set that can silently go empty" failure.
    """

    report = agent_identity_check.analyze(_module(tmp_path, "run_view.py", PAIRED_QT_SOURCE))

    assert report.problems == ()
    assert report.controls == ("_agent_dropdown", "_running_agent_display")
    assert report.writer == "src/anesthesia_sim/app/run_view.py:RunView._apply_agent_color_scheme"


def test_set_enabled_pairs_with_set_visible(tmp_path: Path) -> None:
    """`setEnabled(not E)` beside `setVisible(not E)`: the other Qt spelling of the pair."""

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setDisabled(snapshot.is_running)\n"
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n",
        "        self._agent_dropdown.setEnabled(not snapshot.is_running)\n"
        "        self._agent_dropdown.setVisible(not snapshot.is_running)\n",
    )

    assert agent_identity_check.problems(_module(tmp_path, "run_view.py", source)) == []


def test_the_two_setter_spellings_of_one_condition_pair_with_each_other(tmp_path: Path) -> None:
    """`setEnabled(not E)` and `setHidden(E)` state one condition, and are read as one.

    The normalisation peels exactly one `not`, which is what makes the two
    setters comparable at all; nothing further is inferred.
    """

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setDisabled(snapshot.is_running)\n",
        "        self._agent_dropdown.setEnabled(not snapshot.is_running)\n",
    )

    assert agent_identity_check.problems(_module(tmp_path, "run_view.py", source)) == []


def test_a_mismatched_qt_operand_still_fails(tmp_path: Path) -> None:
    """The comparison stays structural in the setter spelling.

    `setHidden(snapshot.is_paused)` may well be correct, and nothing here can
    know it is: one canonical shape, and a failure that names it.
    """

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n",
        "        self._agent_dropdown.setHidden(snapshot.is_paused)\n",
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "setHidden(snapshot.is_running)" in found[0]


def test_a_call_whose_value_is_used_is_a_read_and_not_an_identity_write(tmp_path: Path) -> None:
    """`x = self.X.palette()` inside the writer reads X; it does not colour it."""

    source = PAIRED_QT_SOURCE.replace(
        "        scheme = AGENT_COLOR_SCHEMES[agent_id]\n",
        "        scheme = AGENT_COLOR_SCHEMES[agent_id]\n"
        "        palette = self._start_button.palette()\n",
    )

    report = agent_identity_check.analyze(_module(tmp_path, "run_view.py", source))

    assert "_start_button" not in report.controls


def test_the_success_line_counts_setter_spelled_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The measurement the sentence rests on includes both spellings."""

    root = _module(tmp_path, "run_view.py", PAIRED_QT_SOURCE)
    _module(root, "simulation_view.py", PLAIN_PANEL_SOURCE)

    assert agent_identity_check.main(["--root", str(root)]) == 0
    out = capsys.readouterr().out
    assert "2 control(s) carry the agent colour" in out
    # The dropdown's setDisabled, the transport's setEnabled, and the panel's
    # attribute write in the other module; the chip's setVisible is a hide.
    assert "3 disabled-state write(s) read across 2 module(s)" in out
    assert "1 of them on identity controls" in out
    # The Qt fixture colours nothing outside the writer, and the line says so
    # rather than leaving an empty rule-2 measurement indistinguishable from
    # one earned.
    assert "0 construction-time and 0 call-time agent colouring(s)" in out


# --- rule 2 in the setter spelling (PL-25KS port review) ----------------------


def test_a_control_coloured_by_a_call_outside_the_writer_must_follow_the_agent(
    tmp_path: Path,
) -> None:
    """Rule 2's Qt half: a `setStyleSheet` in `__init__` on a control the writer never writes.

    The port review found rule 2 reading `self.X = ...` alone, so on a tree
    that colours by call statement it measured nothing while its docstring
    said it kept rule 1's coverage claim true. This is the stale-badge bug
    in the spelling the PySide6 build would reintroduce it in.
    """

    source = PAIRED_QT_SOURCE.replace(
        '        self._start_button = QPushButton("Start")\n',
        '        self._start_button = QPushButton("Start")\n'
        '        scheme = AGENT_COLOR_SCHEMES["demoflurane"]\n'
        "        self._swatch = QLabel()\n"
        '        self._swatch.setStyleSheet(f"background-color: {scheme.fill};")\n',
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "run_view.py:RunView._swatch" in found[0]
    assert "self._swatch.setStyleSheet(...)" in found[0]
    assert "RunView.__init__" in found[0]
    assert agent_identity_check.IDENTITY_WRITER in found[0]


def test_a_call_colouring_of_an_identity_control_outside_the_writer_is_quiet(
    tmp_path: Path,
) -> None:
    """The same call on a control the writer does write is inside the set, and is counted."""

    source = PAIRED_QT_SOURCE.replace(
        '        self._start_button = QPushButton("Start")\n',
        '        self._start_button = QPushButton("Start")\n'
        '        scheme = AGENT_COLOR_SCHEMES["demoflurane"]\n'
        '        self._agent_dropdown.setStyleSheet(f"color: {scheme.foreground};")\n',
    )

    report = agent_identity_check.analyze(_module(tmp_path, "run_view.py", source))

    assert report.problems == ()
    assert report.constructed_colorings == 0
    assert report.call_colorings == 1


def test_a_scheme_local_handed_whole_to_a_helper_is_read(tmp_path: Path) -> None:
    """`setStyleSheet(_text_stylesheet(scheme))`: the colour travels inside the local.

    The shipped writer colours every control this way, so a rule 2 that read
    only `scheme.fill` - the attribute access - would see a helper call as
    colourless and let the Qt build's own idiom past it.
    """

    source = PAIRED_QT_SOURCE.replace(
        '        self._start_button = QPushButton("Start")\n',
        '        self._start_button = QPushButton("Start")\n'
        '        scheme = AGENT_COLOR_SCHEMES["demoflurane"]\n'
        "        self._swatch = QLabel()\n"
        "        self._swatch.setStyleSheet(_text_stylesheet(scheme))\n",
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "_swatch" in found[0]


def test_a_per_item_colouring_through_set_item_data_is_read(tmp_path: Path) -> None:
    """The selector's items take the table inline as a keyword-free positional `QColor`."""

    source = PAIRED_QT_SOURCE.replace(
        '        self._start_button = QPushButton("Start")\n',
        '        self._start_button = QPushButton("Start")\n'
        "        self._other_selector = QComboBox()\n"
        "        self._other_selector.setItemData(\n"
        '            0, QColor(AGENT_COLOR_SCHEMES["demoflurane"].fill), BACKGROUND_ROLE\n'
        "        )\n",
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "_other_selector" in found[0]
    assert "setItemData" in found[0]


def test_the_writers_own_calls_are_the_identity_set_and_not_a_rule_two_finding(
    tmp_path: Path,
) -> None:
    """Rule 2 skips the writer: its body defines the set it would otherwise be judged against."""

    report = agent_identity_check.analyze(_module(tmp_path, "run_view.py", PAIRED_QT_SOURCE))

    assert report.problems == ()
    assert report.call_colorings == 0
    assert set(report.controls) == {"_agent_dropdown", "_running_agent_display"}


def test_a_keyword_argument_setter_is_read_by_rule_one(tmp_path: Path) -> None:
    """`setEnabled(enabled=not E)` is a disabled write, and one with no hide is the finding.

    The port review found the keyword form skipped, which is a disabled
    write read as nothing - the `PL-JRS3` failure on a narrower door.
    """

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setDisabled(snapshot.is_running)\n"
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n",
        "        self._agent_dropdown.setEnabled(enabled=not snapshot.is_running)\n",
    )

    found = agent_identity_check.problems(_module(tmp_path, "run_view.py", source))

    assert len(found) == 1
    assert "_agent_dropdown" in found[0]
    assert "setVisible(not snapshot.is_running)" in found[0]


def test_a_keyword_argument_hide_pairs_with_its_disabled_write(tmp_path: Path) -> None:
    """The hiding side reads a keyword too, so a pairing spelled that way is quiet."""

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n",
        "        self._agent_dropdown.setHidden(hidden=snapshot.is_running)\n",
    )

    assert agent_identity_check.problems(_module(tmp_path, "run_view.py", source)) == []


def test_an_unpacked_argument_is_not_guessed_at(tmp_path: Path) -> None:
    """`setEnabled(**flags)` states no condition this check can read, so it is skipped.

    Skipped rather than read as a write with no hide: a finding naming a
    condition the source never wrote would be the check inventing evidence.
    The fixture keeps the transport's plain `setEnabled` so the measurement
    set stays non-empty and the answer is about the unpacking alone.
    """

    source = PAIRED_QT_SOURCE.replace(
        "        self._agent_dropdown.setDisabled(snapshot.is_running)\n"
        "        self._agent_dropdown.setHidden(snapshot.is_running)\n",
        "        self._agent_dropdown.setDisabled(**flags)\n",
    )

    assert agent_identity_check.problems(_module(tmp_path, "run_view.py", source)) == []


# --- the shipped tree --------------------------------------------------------


def test_the_shipped_view_carries_every_identity_control_it_declares() -> None:
    """The six controls the real `_apply_agent_color_scheme` writes.

    Named rather than counted, so that dropping one from the single writer -
    which would take it out of the checked set silently - fails here instead
    of quietly shrinking what `make check` covers.
    """

    report = agent_identity_check.analyze(REPO_ROOT)

    assert set(report.controls) == {
        "_agent_header_badge",
        "_subtitle_text",
        "_running_agent_display",
        "_running_agent_text",
        "_running_agent_lock_text",
        "_agent_dropdown",
    }
    assert report.writer.endswith(":RunView._apply_agent_color_scheme")


def test_the_shipped_view_gives_rule_two_something_to_read() -> None:
    """The selector's per-item colours are set by call in `__init__`, and rule 2 reads them.

    A zero here would mean the shipped tree colours by a spelling rule 2 does
    not read, which is the empty measurement the port review found and is
    not a state to pass through quietly.
    """

    report = agent_identity_check.analyze(REPO_ROOT)

    assert report.problems == ()
    assert report.call_colorings > 0


def test_the_shipped_view_renders_no_identity_control_disabled() -> None:
    """The real tree, through the entry point `make check` runs."""

    assert agent_identity_check.problems(REPO_ROOT) == []
