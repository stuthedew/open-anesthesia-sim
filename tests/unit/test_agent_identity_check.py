"""Tests for `tools/agent_identity_check.py`, the rendered-disabled checker.

The tool exists to catch drift nobody remembered to look for, so each rule has
a test that breaks the view and asserts the tool notices, and a matching test
that asserts the correct form stays quiet. A checker that fires on correct work
gets disabled, which is the same as not having it.

Fixtures build a miniature `src/anesthesia_sim/app/simulation_view.py` holding
only what the rule under test is about. The real view is checked once, at the
end, by the same entry point `make check` runs - which is what keeps the
miniature from drifting into a shape the tool handles and the shipped code does
not.

Nothing here imports Flet or constructs a control. The tool reads source with
`ast` and never runs it, so a fixture is a string.
"""

from __future__ import annotations

import ast
from pathlib import Path

import agent_identity_check

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


def _view(tmp_path: Path, source: str) -> Path:
    """Write one miniature view into a throwaway tree and return its root."""

    target = tmp_path / agent_identity_check.VIEW
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return tmp_path


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
    the fix `PL-61WW` landed.
    """

    source = PAIRED_SOURCE.replace(
        "        self._agent_dropdown.disabled = snapshot.is_running\n"
        "        self._agent_dropdown.visible = not snapshot.is_running\n",
        "        self._agent_dropdown.value = snapshot.agent_id\n",
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


def test_a_view_that_cannot_be_read_is_reported(tmp_path: Path) -> None:
    """An absent view is a failure, not a tree with nothing to check."""

    found = agent_identity_check.problems(tmp_path)

    assert len(found) == 1
    assert agent_identity_check.VIEW.as_posix() in found[0]


def test_the_shipped_view_carries_every_identity_control_it_declares() -> None:
    """The six controls the real `_apply_agent_color_scheme` writes.

    Named rather than counted, so that dropping one from the single writer -
    which would take it out of the checked set silently - fails here instead
    of quietly shrinking what `make check` covers.
    """

    tree = ast.parse((REPO_ROOT / agent_identity_check.VIEW).read_text(encoding="utf-8"))

    assert set(agent_identity_check.identity_controls(tree)) == {
        "_agent_header_badge",
        "_subtitle_text",
        "_running_agent_display",
        "_running_agent_text",
        "_running_agent_lock_text",
        "_agent_dropdown",
    }


def test_the_shipped_view_renders_no_identity_control_disabled() -> None:
    """The real tree, through the entry point `make check` runs."""

    assert agent_identity_check.problems(REPO_ROOT) == []
