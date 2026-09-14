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
every module under `app/` with `ast`, and the disabled grey is declared in none
of them - it is Material's, not this project's. A colour that
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
   by hand. Rule 1 holds each member to the pairing above, reading the
   `disabled` and `visible` writes inside the *class that holds the writer*:
   `self.X` names an attribute of that class, so a same-named attribute in
   another class is a different control and not the identity one.
2. A control given an agent colour where it is *constructed* must be in that
   set. This is what makes rule 1's coverage claim true rather than asserted -
   a control coloured in `__init__` and never re-written by
   `_apply_agent_color_scheme` is outside rule 1 entirely. It is also a bug in
   its own right: a control that keeps the colour it was built with shows the
   previous agent's identity over the current agent's numbers, which is the
   correct number under the wrong label. Rule 2 reads every class in every
   module, because the writer can only write its own class's attributes, so an
   agent-coloured control anywhere else is by construction outside the set.

**Every module under `app/` is read, and none is named by path (PL-V53R).**
Until then the tool parsed `app/simulation_view.py` alone, and `PL-B9PY` kept
both halves of the decomposed view in that one file so that this tool and
`tools/contrast_check.py` would go on seeing them. That was the right call for
one refactor and the wrong thing to be deciding module boundaries on: the Qt
port builds the view decomposed from the start, and a class moving to a module
this tool did not read was outside both rules with nothing printed. The writer
is now found in whichever module holds it, exactly once - none is the
empty-set error below, and two is a second writer of agent colour, which the
single-writer design exists to prevent - and the report says which module and
class it was found in.

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

**The measurement set has the same guard, since PL-0PJG.** Rule 1 reads two
*attribute assignments* - `self.X.disabled = EXPR` paired with
`self.X.visible = not EXPR` - and PySide6 spells both as calls, `setEnabled`
and `setVisible`. `PL-JRS3` measured what that did on 2026-09-14 by rewriting
`app/simulation_view.py` on the AST into those setters: `property_writes`
returned nothing, the pairing loop ran zero times, and this tool printed
`6 control(s) carry the agent colour, none of them rendered disabled` and
exited 0 - on a tree where all six are driven by `setEnabled()` with no paired
hide. That was worse than a silent pass, because the sentence is an
affirmative claim about a tree the check did not measure, and a reader had no
way to tell it from the same sentence earned. So a tree whose identity set is
non-empty but in which no `self.X.disabled = ...` assignment is read in any
class in any module is now an error naming the spelling this reads and the one
it does not, and the success line states the measurement it rests on - how
many disabled-state writes were read, across how many modules, how many of
them on identity controls. A tree that genuinely disables nothing anywhere
trips the same error, deliberately: this check cannot tell that tree from one
it cannot read, and saying so is the honest answer; the interface disables its
transport while a run is going, so it is not a tree this project has.

The port still owes rule 1 the setter spelling - the error above is what
makes it owe it loudly on the first commit rather than pass through. Porting
the colour writes to `setStyleSheet` trips rule 2 with a message that
*misdiagnoses*, reporting that the writer "never writes" controls it writes
through `setStyleSheet`; so rule 1 is part of the port's scope rather than
collateral, and it is the half to port first.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Every module under this tree is read; none is named by path (PL-V53R).
APP = Path("src/anesthesia_sim/app")

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

#: How the toolkit the interface is moving to spells the same write. Named so
#: that the empty-measurement error can say what it did not read (PL-0PJG).
UNREAD_SPELLING = "setEnabled()"


@dataclass(frozen=True)
class Module:
    """One parsed module under `APP`."""

    #: Relative to the repository root, POSIX-separated.
    path: str
    tree: ast.Module


@dataclass(frozen=True)
class Writer:
    """Where `IDENTITY_WRITER` was found: the module, the class and the method."""

    module: str
    owner: ast.ClassDef
    method: ast.FunctionDef | ast.AsyncFunctionDef

    @property
    def location(self) -> str:
        return f"{self.module}:{self.owner.name}.{self.method.name}"


@dataclass(frozen=True)
class Report:
    """Everything one run decided, and what it measured to decide it."""

    problems: tuple[str, ...]
    #: The identity set, in the writer's source order.
    controls: tuple[str, ...]
    #: `module:Class.method`, empty when no writer was found.
    writer: str
    #: Modules read under `APP`.
    modules: int
    #: `self.X.disabled = ...` assignments read, in every class of every module.
    disabled_writes: int
    #: Of those, the ones on identity controls - the writes rule 1 judged.
    identity_disabled_writes: int


def read_modules(root: Path) -> tuple[Module, ...]:
    """Every module under `APP`, parsed, in path order."""
    found: list[Module] = []
    for path in sorted((root / APP).rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        found.append(
            Module(path.relative_to(root).as_posix(), ast.parse(source, filename=str(path)))
        )
    return tuple(found)


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


def classes(tree: ast.Module) -> tuple[ast.ClassDef, ...]:
    """Every class a module defines, outermost first, in source order."""
    return tuple(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def find_writers(modules: Sequence[Module]) -> tuple[Writer, ...]:
    """Every class, in every module, that defines `IDENTITY_WRITER` as a method.

    A method of a class rather than any function of that name anywhere,
    because the identity set is `self.X` writes and `self` is a class's. More
    than one is an error the caller reports; this only finds them.
    """
    found: list[Writer] = []
    for module in modules:
        for owner in classes(module.tree):
            for item in owner.body:
                if (
                    isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                    and item.name == IDENTITY_WRITER
                ):
                    found.append(Writer(module.path, owner, item))
    return tuple(found)


def identity_controls(method: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    """Every control the single writer of agent colour writes, in source order.

    Definitionally the identity set: a control not written there does not
    follow the agent, and one written there does. Ordered by line so the
    report reads the way the method is written - `ast.walk` is breadth-first,
    which coincides with source order only while a body stays flat.
    """
    found: dict[str, int] = {}
    for statement in ast.walk(method):
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


def constructed_with_agent_color(owner: ast.ClassDef) -> tuple[str, ...]:
    """Every `self.X` one class builds from an agent colour, in source order.

    Two passes per function, not one, because the locals that carry a colour
    are bound in the same scope that uses them and `ast.walk` does not promise
    to reach the binding first. Collecting them all before reading any
    assignment removes the ordering question rather than relying on a body
    staying flat.

    Nothing here resolves a name across scopes, deliberately: the pass answers
    "does this assignment reach an agent colour", not "what is this name".
    """
    found: dict[str, int] = {}
    for node in ast.walk(owner):
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


def property_writes(scope: ast.AST, prop: str) -> dict[str, list[ast.expr]]:
    """Every value assigned to `self.<control>.<prop>` within one scope, keyed by control."""
    writes: dict[str, list[ast.expr]] = {}
    for node in ast.walk(scope):
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


def analyze(root: Path) -> Report:
    """Every identity control that can be rendered disabled, every gap in the set,
    and the measurement those verdicts rest on."""
    modules = read_modules(root)
    if not modules:
        return Report(
            (
                f"{APP.as_posix()}/: no module can be read there, so there is no view to "
                f"check. A moved or renamed package leaves this passing over nothing, "
                f"which is why it is an error",
            ),
            (),
            "",
            0,
            0,
            0,
        )

    writers = find_writers(modules)
    if not writers:
        return Report(
            (
                f"no class in any of the {len(modules)} module(s) under {APP.as_posix()}/ "
                f"defines `{IDENTITY_WRITER}`, so the set this check measures is empty. "
                f"Either that method was renamed - point IDENTITY_WRITER at its new name - "
                f"or the class holding it moved out of app/, or agent colour has a second "
                f"writer under another name, which is the thing the single-writer design "
                f"exists to prevent",
            ),
            (),
            "",
            len(modules),
            0,
            0,
        )
    if len(writers) > 1:
        where = ", ".join(writer.location for writer in writers)
        return Report(
            (
                f"`{IDENTITY_WRITER}` is defined in {len(writers)} classes - {where} - and "
                f"the identity set is whatever the single writer of agent colour writes. A "
                f"second writer is the thing the single-writer design exists to prevent; "
                f"one class owns agent colour, and the others take it from there",
            ),
            (),
            where,
            len(modules),
            0,
            0,
        )

    (writer,) = writers
    controls = identity_controls(writer.method)
    if not controls:
        return Report(
            (
                f"`{writer.location}` writes no `self.<control>` property, so the set this "
                f"check measures is empty. A coverage set that can silently go empty is "
                f"worse than no check",
            ),
            (),
            writer.location,
            len(modules),
            0,
            0,
        )

    found: list[str] = []

    # Rule 1, inside the writer's own class: `self.X` names that class's
    # attribute, and a same-named attribute elsewhere is a different control.
    disabled_writes = property_writes(writer.owner, DISABLED)
    visible_writes = property_writes(writer.owner, VISIBLE)
    for control in controls:
        for expression in disabled_writes.get(control, []):
            written = ast.unparse(expression)
            if any(
                is_negation_of(candidate, expression)
                for candidate in visible_writes.get(control, [])
            ):
                continue
            found.append(
                f"`{writer.owner.name}.{control}` is assigned `{DISABLED} = {written}` and "
                f"carries the agent colour, but nothing assigns it "
                f"`{VISIBLE} = not {written}`. Disabled and on screen, its label is "
                f"the theme's disabled-content grey over the agent's own fill, which "
                f"is undeclared, unmeasurable by tools/contrast_check.py, and what "
                f"PL-61WW was. Either pair it with that exact line, or carry the "
                f"identity in a control that is never disabled"
            )

    # The measurement set (PL-0PJG): what rule 1 could have read at all. Every
    # class in every module, because the guard is about the *spelling* being
    # readable, and any control's `disabled` write proves that.
    read = sum(
        len(values)
        for module in modules
        for values in property_writes(module.tree, DISABLED).values()
    )
    identity_read = sum(len(disabled_writes.get(control, [])) for control in controls)
    if read == 0:
        found.append(
            f"no `self.<control>.{DISABLED} = ...` assignment was read in any class of the "
            f"{len(modules)} module(s) under {APP.as_posix()}/, so rule 1 measured nothing "
            f"and 'none of them rendered disabled' cannot be earned. Either nothing in the "
            f"interface is ever disabled, or disabling is spelled in a way this check does "
            f"not read - PySide6's `{UNREAD_SPELLING}` - and the pairing rule has to be "
            f"taught that spelling before it can pass (PL-0PJG)"
        )

    # Rule 2, every class in every module: the writer can only write its own
    # class's attributes, so an agent-coloured control anywhere else is
    # outside the set by construction.
    for module in modules:
        for owner in classes(module.tree):
            for control in constructed_with_agent_color(owner):
                if owner is writer.owner and control in controls:
                    continue
                found.append(
                    f"`{module.path}:{owner.name}.{control}` is built from an agent colour "
                    f"but `{writer.location}` never writes it, so it keeps the colour it "
                    f"was constructed with and this check cannot see it disabled. A control "
                    f"that does not follow the agent shows the previous agent's identity "
                    f"over the current agent's numbers"
                )

    return Report(tuple(found), controls, writer.location, len(modules), read, identity_read)


def problems(root: Path) -> list[str]:
    """Every problem `analyze` found, for callers that want only the verdict."""
    return list(analyze(root).problems)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args(argv)

    report = analyze(args.root)
    if not report.problems:
        print(
            f"agent-identity: {len(report.controls)} control(s) carry the agent colour, "
            f"written by {report.writer}; {report.disabled_writes} disabled-state write(s) "
            f"read across {report.modules} module(s) under {APP.as_posix()}/, "
            f"{report.identity_disabled_writes} of them on identity controls and each "
            f"paired with its hide; none rendered disabled"
        )
        return 0

    print(
        f"agent-identity: {len(report.problems)} problem(s) under {APP.as_posix()}/.\n"
        + "".join(f"  {problem}\n" for problem in report.problems)
        + "  No control carrying agent identity may be rendered in a disabled state "
        "(project owner, 2026-09-08). WCAG 2.2 SC 1.4.3 exempts an inactive component "
        "from any contrast requirement, which settles a conformance claim and not "
        "whether a reader can identify the running agent (`PL-61WW`, `PL-97VB`).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
