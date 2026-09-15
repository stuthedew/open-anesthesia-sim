#!/usr/bin/env python3
"""Refuse a control that carries agent identity and can be rendered disabled.

`PL-61WW` is what this exists for. The agent selector was disabled for the
whole of a run, and the toolkit of the day (Flet/Material) painted a disabled
control's label in the theme's disabled-content grey - overriding the
`color=` and `text_style=` the agent scheme set, while `bgcolor=` kept the
saturated ISO 5360 fill. The agent's name was hardest to read at exactly the
moment every number beside it was agent-specific, which `CLAUDE.md`'s
presentation clause makes a safety failure rather than a styling one.

**Nothing went red.** `tools/contrast_check.py` reads colour constants out of
every module under `app/` with `ast`, and the disabled grey is declared in none
of them - it is the toolkit's, not this project's. A colour that
appears in no source file is not merely undeclared but unreachable, so the
requirement went on measuring the enabled pair and reporting a pass for a pair
that had stopped being rendered. That is the general shape rather than one
control's bug, and `PL-61WW` fixed the one control. Qt has the same shape: a
widget's disabled palette role is the style's, and a stylesheet colour set for
the enabled state says nothing about what `:disabled` draws.

**The rule, decided by the project owner (2026-09-08): never disabled.** No
control carrying agent identity may be *rendered* in a disabled state, so
W3C WCAG 2.2 SC 1.4.3's exemption for "text ... that is part of an inactive
user interface component" is never claimed here - the exemption settles a
conformance claim and not whether a reader can identify the running agent.
https://www.w3.org/TR/WCAG22/#contrast-minimum

Rendered is the load-bearing word. `_agent_dropdown` is still written
disabled while a run is going, and is also written hidden under the same
condition, so it draws nothing while disabled - the disabled write is there
because a control off screen must not be operable either. A check reading the
disabled write alone would fail that tree and teach the next session to delete
a defensive line to appease it. So the shape enforced is the pairing, in
whichever spelling the toolkit uses:

    self._agent_dropdown.disabled = snapshot.is_running
    self._agent_dropdown.visible = not snapshot.is_running

    self._agent_dropdown.setDisabled(snapshot.is_running)
    self._agent_dropdown.setHidden(snapshot.is_running)

    self._agent_dropdown.setEnabled(not snapshot.is_running)
    self._agent_dropdown.setVisible(not snapshot.is_running)

the same expression on both lines. A control written disabled with no such
hide beside it can be seen while the theme is recolouring it, and that is the
failure.

**Two spellings, one comparison.** The Flet build wrote `disabled` and
`visible` as attribute assignments; PySide6 spells the same state as the
setter calls `setDisabled`/`setEnabled` and `setHidden`/`setVisible`
(`PL-25KS`, which taught this check the second spelling as part of the port -
`PL-JRS3` had measured that until then a Qt tree passed through unread, below).
Both are read, and each write is reduced to the *condition* it states before
anything is compared: `disabled = E`, `setDisabled(E)` and `setEnabled(not E)`
all disable the control under `E`; `visible = not E`, `setHidden(E)` and
`setVisible(not E)` all hide it under `E`. The pairing holds when the two
conditions are structurally identical - `ast.dump` of one against the other -
and nothing infers that two differently written conditions mean the same
thing. Peeling one `not` is the whole of the normalisation, and it is there
so that `setEnabled(not E)` and `setDisabled(E)` are the same statement to
this check, as they are to the toolkit.

**The two rules, and why the second one is not scope creep.**

1. The identity set is every `self.X` that `_apply_agent_color_scheme` writes,
   whether as a property assignment (`self.X.color = ...`) or as a call
   statement on the control (`self.X.setStyleSheet(...)`). That method is
   already this project's single writer of agent colour and says so in its own
   docstring, so the set needs no second list kept in step by hand. Rule 1
   holds each member to the pairing above, reading the disabled and hiding
   writes inside the *class that holds the writer*: `self.X` names an
   attribute of that class, so a same-named attribute in another class is a
   different control and not the identity one.
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
because a coverage set that can silently go empty is worse than no check. A
call whose value is *used* - `x = self.X.palette()` - is a read and is not
counted as a write; only a call standing as its own statement is.

**The measurement set has the same guard, since PL-0PJG.** `PL-JRS3` measured
on 2026-09-14 what an unread spelling did, by rewriting `app/simulation_view.py`
on the AST into Qt's setters while this check read attributes only: the
pairing loop ran zero times and the tool printed `6 control(s) carry the agent
colour, none of them rendered disabled` and exited 0 - on a tree where all six
were driven by `setEnabled()` with no paired hide. That was worse than a silent
pass, because the sentence is an affirmative claim about a tree the check did
not measure, and a reader had no way to tell it from the same sentence earned.
So a tree whose identity set is non-empty but in which no disabled-state write
is read, in either spelling, in any class in any module is an error, and the
success line states the measurement it rests on - how many disabled-state
writes were read, across how many modules, how many of them on identity
controls. A tree that genuinely disables nothing anywhere trips the same
error, deliberately: this check cannot tell that tree from one written in a
spelling it has not been taught, and saying so is the honest answer; the
interface disables its transport while a run is going, so it is not a tree
this project has.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterator, Sequence
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

#: The attribute spelling: the property whose assignment makes a control's own
#: colour the theme's to choose, and the one whose assignment can take it off
#: screen instead.
DISABLED = "disabled"
VISIBLE = "visible"

#: The setter spelling of the same two states. `setEnabled` and `setVisible`
#: state the condition the other way round, which `_condition` undoes.
SET_DISABLED = "setDisabled"
SET_ENABLED = "setEnabled"
SET_HIDDEN = "setHidden"
SET_VISIBLE = "setVisible"


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
class DisabledWrite:
    """One write of a control's disabled state, in either spelling.

    Reduced to the condition it disables the control under, so that the
    pairing can be judged without caring which spelling stated it - and
    carrying the spelling anyway, so the error can name the exact hiding
    line that would pair with it.
    """

    control: str
    #: The expression under which the control is disabled.
    condition: ast.expr
    #: The write as it stands in source, e.g. `disabled = snapshot.is_running`.
    written: str
    #: The hiding write in the same spelling, e.g. `visible = not snapshot.is_running`.
    paired_hide: str


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
    #: Disabled-state writes read, in either spelling, in every class of every module.
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
    """The control an attribute expression reaches into: the `X` of `self.X.prop`.

    The same shape serves a call's callee, `self.X.method`, which is why the
    identity set and both spellings of rule 1 read through this one function.
    """
    if isinstance(target, ast.Attribute):
        return self_attribute(target.value)
    return None


def control_calls(scope: ast.AST) -> Iterator[tuple[str, str, ast.Call]]:
    """Every call statement on a control within one scope: `self.X.method(...)`.

    A call standing as its own statement, because that is a write; a call
    whose value is consumed - `x = self.X.palette()` - is a read and would
    put a control into a set it does not belong to.

    Yields:
        The control, the method name and the call, in walk order.
    """
    for node in ast.walk(scope):
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        callee = node.value.func
        if not isinstance(callee, ast.Attribute):
            continue
        control = written_control(callee)
        if control is not None:
            yield control, callee.attr, node.value


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
    follow the agent, and one written there does. A write is a property
    assignment on the control (`self.X.color = ...`, the attribute spelling)
    or a call statement on it (`self.X.setStyleSheet(...)`, the setter
    spelling); both count, so the set is the same whichever toolkit the
    writer is written for. Ordered by line so the report reads the way the
    method is written - `ast.walk` is breadth-first, which coincides with
    source order only while a body stays flat.
    """
    found: dict[str, int] = {}
    for statement in ast.walk(method):
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            control = written_control(target)
            if control is not None:
                found.setdefault(control, statement.lineno)
    for control, _, call in control_calls(method):
        found.setdefault(control, call.lineno)
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


def setter_writes(scope: ast.AST, method: str) -> dict[str, list[ast.expr]]:
    """Every single argument passed to `self.<control>.<method>(...)` within one scope.

    A call with any other arity, or a keyword, is not the state write this
    reads and is skipped rather than guessed at.
    """
    writes: dict[str, list[ast.expr]] = {}
    for control, name, call in control_calls(scope):
        if name == method and len(call.args) == 1 and not call.keywords:
            writes.setdefault(control, []).append(call.args[0])
    return writes


def negated(expression: ast.expr) -> ast.expr:
    """`not expression`, with one `not` peeled rather than stacked.

    The one step of normalisation this check performs: `setEnabled(not E)`
    and `setDisabled(E)` state the same condition, and comparing them means
    turning one into the other. Nothing else about an expression is
    rewritten, so `visible = snapshot.is_paused` still does not satisfy
    `disabled = snapshot.is_running` - proving those equivalent would be the
    judgment half.
    """
    if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, ast.Not):
        return expression.operand
    return ast.UnaryOp(op=ast.Not(), operand=expression)


def disabled_writes(scope: ast.AST) -> list[DisabledWrite]:
    """Every write of a control's disabled state within one scope, in either spelling."""
    found: list[DisabledWrite] = []
    for control, values in property_writes(scope, DISABLED).items():
        for value in values:
            written = ast.unparse(value)
            found.append(
                DisabledWrite(
                    control,
                    value,
                    f"{DISABLED} = {written}",
                    f"{VISIBLE} = {ast.unparse(negated(value))}",
                )
            )
    for control, values in setter_writes(scope, SET_DISABLED).items():
        for value in values:
            written = ast.unparse(value)
            found.append(
                DisabledWrite(
                    control, value, f"{SET_DISABLED}({written})", f"{SET_HIDDEN}({written})"
                )
            )
    for control, values in setter_writes(scope, SET_ENABLED).items():
        for value in values:
            written = ast.unparse(value)
            found.append(
                DisabledWrite(
                    control,
                    negated(value),
                    f"{SET_ENABLED}({written})",
                    f"{SET_VISIBLE}({written})",
                )
            )
    return found


def hidden_conditions(scope: ast.AST) -> dict[str, list[ast.expr]]:
    """The condition under which each control is hidden, per hiding write, in either spelling."""
    conditions: dict[str, list[ast.expr]] = {}
    for control, values in property_writes(scope, VISIBLE).items():
        conditions.setdefault(control, []).extend(negated(value) for value in values)
    for control, values in setter_writes(scope, SET_VISIBLE).items():
        conditions.setdefault(control, []).extend(negated(value) for value in values)
    for control, values in setter_writes(scope, SET_HIDDEN).items():
        conditions.setdefault(control, []).extend(values)
    return conditions


def is_same_condition(candidate: ast.expr, condition: ast.expr) -> bool:
    """Whether two conditions are the same expression, structurally.

    `ast.dump` compares the two trees and nothing infers that two differently
    written conditions mean the same thing. That is the point. The check
    enforces one canonical shape and says so when it fails, which keeps the
    judgment - is this control legible while disabled? - with the reader
    instead of in here.
    """
    return ast.dump(candidate) == ast.dump(condition)


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
                f"`{writer.location}` writes no `self.<control>` property and calls no "
                f"`self.<control>` method, so the set this check measures is empty. A "
                f"coverage set that can silently go empty is worse than no check",
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
    owner_writes = disabled_writes(writer.owner)
    hidden = hidden_conditions(writer.owner)
    identity_read = 0
    for write in owner_writes:
        if write.control not in controls:
            continue
        identity_read += 1
        if any(
            is_same_condition(candidate, write.condition)
            for candidate in hidden.get(write.control, [])
        ):
            continue
        found.append(
            f"`{writer.owner.name}.{write.control}` is written `{write.written}` and "
            f"carries the agent colour, but nothing writes it `{write.paired_hide}`. "
            f"Disabled and on screen, its label is the theme's disabled-content grey "
            f"over the agent's own fill, which is undeclared, unmeasurable by "
            f"tools/contrast_check.py, and what PL-61WW was. Either pair it with that "
            f"exact line, or carry the identity in a control that is never disabled"
        )

    # The measurement set (PL-0PJG): what rule 1 could have read at all. Every
    # class in every module, because the guard is about the *spelling* being
    # readable, and any control's disabled-state write proves that.
    read = sum(len(disabled_writes(module.tree)) for module in modules)
    if read == 0:
        found.append(
            f"no disabled-state write - `self.<control>.{DISABLED} = ...`, "
            f"`.{SET_DISABLED}(...)` or `.{SET_ENABLED}(...)` - was read in any class of "
            f"the {len(modules)} module(s) under {APP.as_posix()}/, so rule 1 measured "
            f"nothing and 'none of them rendered disabled' cannot be earned. Either "
            f"nothing in the interface is ever disabled, or disabling is spelled in a way "
            f"this check does not read, and the pairing rule has to be taught that "
            f"spelling before it can pass (PL-0PJG)"
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
