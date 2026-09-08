#!/usr/bin/env python3
"""Refuse a control that carries agent identity and can be rendered disabled.

`PL-61WW` is what this exists for. The agent selector was disabled for the
whole of a run, and Flet/Material paints a disabled control's label in the
theme's disabled-content grey - overriding the `color=` and `text_style=` the
agent scheme sets, while `bgcolor=` keeps the saturated ISO 5360 fill. The
agent's name was hardest to read at exactly the moment every number beside it
was agent-specific, which `CLAUDE.md`'s presentation clause makes a safety
failure rather than a styling one.

**Nothing went red.** `tools/contrast_check.py` reads colour constants out of
`app/theme.py` and `app/simulation_view.py` with `ast`, and the disabled grey
is declared in neither - it is Material's, not this project's. A colour that
appears in no source file is not merely undeclared but unreachable, so the
requirement went on measuring the enabled pair and reporting a pass for a pair
that had stopped being rendered. That is the general shape rather than one
control's bug, and `PL-61WW` fixed the one control.

**The rule, decided by the project owner (2026-09-08): never disabled.** No
control carrying agent identity may be *rendered* in a disabled state, so
W3C WCAG 2.2 SC 1.4.3's exemption for "text ... that is part of an inactive
user interface component" is never claimed here - the exemption settles a
conformance claim and not whether a reader can identify the running agent.
https://www.w3.org/TR/WCAG22/#contrast-minimum

Rendered is the load-bearing word. `_agent_dropdown` is still assigned
`disabled = snapshot.is_running`, and is also assigned
`visible = not snapshot.is_running`, so it draws nothing while disabled - the
`disabled` line is there because a control off screen must not be operable
either. A check reading `disabled` alone would fail that tree and teach the
next session to delete a defensive line to appease it. So the shape enforced
is the pairing:

    self._agent_dropdown.disabled = snapshot.is_running
    self._agent_dropdown.visible = not snapshot.is_running

the same expression, negated. A control assigned `disabled` with no such
`visible` beside it can be seen while the theme is recolouring it, and that is
the failure.

**The two rules, and why the second one is not scope creep.**

1. The identity set is every `self.X` that `_apply_agent_color_scheme` writes.
   That method is already this project's single writer of agent colour and
   says so in its own docstring, so the set needs no second list kept in step
   by hand. Rule 1 holds each member to the pairing above.
2. A control given an agent colour where it is *constructed* must be in that
   set. This is what makes rule 1's coverage claim true rather than asserted -
   a control coloured in `__init__` and never re-written by
   `_apply_agent_color_scheme` is outside rule 1 entirely. It is also a bug in
   its own right: a control that keeps the colour it was built with shows the
   previous agent's identity over the current agent's numbers, which is the
   correct number under the wrong label.

**What this must never decide.** Whether a control's identity is legible,
whether a particular pairing is the *right* one for that control, what colour
anything should be, or whether a control ought to be disabled at all. Those
are judgments; they live in the source and in `.claude/rules/ui-color.md`.
This answers "is this control both agent-coloured and disabled without the
paired hide", which the source answers by itself. `tools/contrast_check.py`
draws the same line, for the same reason: a tool that guesses at the judgment
half is worse than no tool, because its output looks authoritative and is not.

**Known limitation, stated rather than papered over.** A control coloured by
neither route - no agent colour where it is constructed and no write in
`_apply_agent_color_scheme` - is invisible to both rules. None exists today,
and rule 2 is what keeps the first route from opening one quietly. The check
also refuses a tree where the writer method is missing or writes nothing,
because a coverage set that can silently go empty is worse than no check.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VIEW = Path("src/anesthesia_sim/app/simulation_view.py")

#: The single writer of agent colour, and so the definition of the identity
#: set. Named here rather than inferred: if it is renamed, this check reports
#: that it cannot find it instead of quietly measuring nothing.
IDENTITY_WRITER = "_apply_agent_color_scheme"

#: The module-level tables an agent colour comes out of. A local name bound
#: from a subscript of either carries an agent colour into whatever it is
#: assigned to, which is how rule 2 finds a control coloured at construction.
COLOR_TABLES = ("AGENT_COLOR_SCHEMES", "AGENT_RENDER_STYLES")

#: The attribute whose assignment makes a control's own colour Material's to
#: choose, and the one whose assignment can take it off screen instead.
DISABLED = "disabled"
VISIBLE = "visible"


def self_attribute(node: ast.expr) -> str | None:
    """The `X` of a `self.X` expression, or None for anything else."""
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return node.attr
    return None


def written_control(target: ast.expr) -> str | None:
    """The control an assignment target writes a property of: `self.X.prop`."""
    if isinstance(target, ast.Attribute):
        return self_attribute(target.value)
    return None


def identity_controls(tree: ast.Module) -> tuple[str, ...]:
    """Every control the single writer of agent colour writes, in source order.

    Definitionally the identity set: a control not written there does not
    follow the agent, and one written there does. Ordered by line so the
    report reads the way the method is written - `ast.walk` is breadth-first,
    which coincides with source order only while a body stays flat.
    """
    found: dict[str, int] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name != IDENTITY_WRITER:
            continue
        for statement in ast.walk(node):
            if not isinstance(statement, ast.Assign):
                continue
            for target in statement.targets:
                control = written_control(target)
                if control is not None:
                    found.setdefault(control, statement.lineno)
    return tuple(sorted(found, key=found.__getitem__))


def _carries_agent_color(value: ast.expr, tracked: set[str]) -> bool:
    """Whether an expression reaches an agent colour, directly or through a local.

    Two ways, and both have to be read because the view uses both in one
    call: `AGENT_COLOR_SCHEMES[agent_id].fill` written inline, and
    `initial_agent_colors.foreground` where the local was bound from a
    subscript of the same table a few lines earlier.
    """
    for node in ast.walk(value):
        if isinstance(node, ast.Name) and node.id in COLOR_TABLES:
            return True
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in tracked:
                return True
    return False


def constructed_with_agent_color(tree: ast.Module) -> tuple[str, ...]:
    """Every `self.X` built from an agent colour, in source order.

    Two passes per function, not one, because the locals that carry a colour
    are bound in the same scope that uses them and `ast.walk` does not promise
    to reach the binding first. Collecting them all before reading any
    assignment removes the ordering question rather than relying on a body
    staying flat.

    Nothing here resolves a name across scopes, deliberately: the pass answers
    "does this assignment reach an agent colour", not "what is this name".
    """
    found: dict[str, int] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        assignments = [
            statement for statement in ast.walk(node) if isinstance(statement, ast.Assign)
        ]
        tracked = {
            target.id
            for statement in assignments
            if _from_color_table(statement.value)
            for target in statement.targets
            if isinstance(target, ast.Name)
        }
        for statement in assignments:
            for target in statement.targets:
                control = self_attribute(target)
                if control is None:
                    continue
                if _carries_agent_color(statement.value, tracked):
                    found.setdefault(control, statement.lineno)
    return tuple(sorted(found, key=found.__getitem__))


def _from_color_table(value: ast.expr) -> bool:
    """Whether a local is being bound from a subscript of one of the tables."""
    return (
        isinstance(value, ast.Subscript)
        and isinstance(value.value, ast.Name)
        and value.value.id in COLOR_TABLES
    )


def property_writes(tree: ast.Module, prop: str) -> dict[str, list[ast.expr]]:
    """Every value assigned to `self.<control>.<prop>`, keyed by control."""
    writes: dict[str, list[ast.expr]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Attribute) or target.attr != prop:
                continue
            control = written_control(target)
            if control is not None:
                writes.setdefault(control, []).append(node.value)
    return writes


def is_negation_of(candidate: ast.expr, expression: ast.expr) -> bool:
    """Whether `candidate` is exactly `not expression`.

    Structural rather than semantic: `ast.dump` compares the two operand
    trees and nothing infers that two differently written conditions mean the
    same thing. That is the point. The check enforces one canonical shape and
    says so when it fails, which keeps the judgment - is this control legible
    while disabled? - with the reader instead of in here.
    """
    return (
        isinstance(candidate, ast.UnaryOp)
        and isinstance(candidate.op, ast.Not)
        and ast.dump(candidate.operand) == ast.dump(expression)
    )


def problems(root: Path) -> list[str]:
    """Every identity control that can be rendered disabled, and every gap in the set."""
    path = root / VIEW
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"{VIEW.as_posix()}: cannot be read ({error})"]

    tree = ast.parse(source, filename=str(path))
    controls = identity_controls(tree)
    if not controls:
        return [
            f"{VIEW.as_posix()}: no control is written by `{IDENTITY_WRITER}`, so the "
            f"set this check measures is empty. Either that method was renamed - point "
            f"IDENTITY_WRITER at its new name - or agent colour has a second writer, "
            f"which is the thing the single-writer design exists to prevent"
        ]

    found: list[str] = []

    disabled_writes = property_writes(tree, DISABLED)
    visible_writes = property_writes(tree, VISIBLE)
    for control in controls:
        for expression in disabled_writes.get(control, []):
            written = ast.unparse(expression)
            if any(
                is_negation_of(candidate, expression)
                for candidate in visible_writes.get(control, [])
            ):
                continue
            found.append(
                f"`self.{control}` is assigned `{DISABLED} = {written}` and carries the "
                f"agent colour, but nothing assigns it "
                f"`{VISIBLE} = not {written}`. Disabled and on screen, its label is "
                f"the theme's disabled-content grey over the agent's own fill, which "
                f"is undeclared, unmeasurable by tools/contrast_check.py, and what "
                f"PL-61WW was. Either pair it with that exact line, or carry the "
                f"identity in a control that is never disabled"
            )

    for control in constructed_with_agent_color(tree):
        if control in controls:
            continue
        found.append(
            f"`self.{control}` is built from an agent colour but `{IDENTITY_WRITER}` "
            f"never writes it, so it keeps the colour it was constructed with and this "
            f"check cannot see it disabled. A control that does not follow the agent "
            f"shows the previous agent's identity over the current agent's numbers"
        )

    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()

    found = problems(args.root)
    if not found:
        controls = identity_controls(ast.parse((args.root / VIEW).read_text(encoding="utf-8")))
        print(
            f"agent-identity: {len(controls)} control(s) carry the agent colour, "
            f"none of them rendered disabled"
        )
        return 0

    print(
        f"agent-identity: {len(found)} problem(s) in {VIEW.as_posix()}.\n"
        + "".join(f"  {problem}\n" for problem in found)
        + "  No control carrying agent identity may be rendered in a disabled state "
        "(project owner, 2026-09-08). WCAG 2.2 SC 1.4.3 exempts an inactive component "
        "from any contrast requirement, which settles a conformance claim and not "
        "whether a reader can identify the running agent (`PL-61WW`, `PL-97VB`).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
