"""`doc_check`'s Makefile readers read generated Makefiles as GNU make does.

`tools/doc_check.py` reads the Makefile by hand, because it runs on the
standard library alone. Three readers answer its questions about the file:

- `make_targets` returns every target a Makefile names and the subset with a
  recipe that runs a command;
- `_target_recipes` returns each target's own commands and its prerequisites;
- `_recipe_commands` returns every command a recipe hands the shell.

Nine Makefile misreads closed as items before this test existed, each found by
a sweep after its form could already have merged: `PL-4MLK`, `PL-5M36`,
`PL-BMZN`, `PL-G2FY`, `PL-GZXY`, `PL-HD96`, `PL-HR4V`, `PL-TDVJ` and `PL-X43T`.
No published corpus tests how a third party reads a Makefile, so GNU make is
the reference program here (`PL-WFPB`), as bash is for `docket.shell` in
`subprojects/docket/tests/test_shell.py`. Two of make's own outputs give its
reading:

- `make -pqRr -f - NO_SUCH_GOAL` prints make's database. That lists every file
  make knows, whether each is a target, its prerequisites and the line its
  recipe comes from. `-R` and `-r` leave out make's built-in variables and
  rules, and the goal that does not exist stops make before it runs anything.
- `make -n` prints the commands make would hand the shell for one target.
  `-o` names every other file as old, so the output holds that target's own
  recipe alone. `SHELL=/bin/true` keeps a `+` line, which make runs even under
  `-n`, from running anything.

Hypothesis draws the Makefiles, derandomized, so a red run reproduces exactly.
Each is built from the forms the closed items name: several targets on one
rule, a prerequisite list a backslash continues, a recipe after the rule's
`;`, recipe lines with make's `@`, `-` and `+` prefixes, a command a backslash
continues, a line holding only a tab, comment lines inside a rule at the first
column and after a tab, `define` blocks, assignments that end a rule, and
`.ONESHELL`. Where a reader raises `UnreadStatement`, the test accepts the
decline. Where it answers, the answer must match make's.

One form is left out of the generator because the readers decline it by name:
a Makefile that sets `.RECIPEPREFIX`, after which make opens a recipe line with
another character (`PL-GSJ6`). `KNOWN_DEPARTURES` pins any form the readers
read differently from make, recorded by the open item that will fix it, and
holds none today.

A conditional is drawn, and `make_targets` and `_target_recipes` decline a
recipe line inside one, since make runs it only in its branch (`PL-HSB3`).
`_recipe_commands` holds every command make might run, every branch's
included, so its commands are not compared for a Makefile holding one.

The test needs GNU make on `PATH`, as `make check`, which runs it, does.
CI's runners and the cloud containers both carry GNU make 4.3.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import doc_check
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


@cache
def _gnu_make() -> str:
    """The GNU make the comparison runs, found on `PATH`."""
    path = shutil.which("make")
    assert path is not None, "the comparison runs GNU make, and no make is on PATH"
    version = subprocess.run([path, "--version"], capture_output=True, text=True, check=True)
    assert version.stdout.startswith("GNU Make"), f"{path} is not GNU make"
    return path


#: make's message for the goal no Makefile here names, which is how the database is printed.
NO_GOAL = "make: *** No rule to make target 'NO_SUCH_GOAL'.  Stop.\n"
RECIPE_FROM = re.compile(r"#  recipe to execute \(from '.*', line (?P<line>\d+)\):")
#: A line make prints about its own progress, such as "Nothing to be done", which is no command.
MAKE_MESSAGE = re.compile(r"make(\[\d+\])?: ")

TARGETS = ("check", "lint", "test", "build", "docs", "fmt")
WORD = st.sampled_from(("ruff", "check", ".", "-q", "a#b", "'x y'", "src", "tests"))
COMMAND = st.builds(
    lambda program, words: " ".join((program, *words)),
    st.sampled_from(("echo", "python3", "uv run pytest", "bin/docket")),
    st.lists(WORD, max_size=3),
)
PREFIX = st.sampled_from(("", "", "", "@", "-", "@-", "-@", "+"))
COMMENT = st.sampled_from(("# a note", "# check: not a rule"))


@dataclass(frozen=True)
class Target:
    """What make's database says of one target: its prerequisites and its recipe's first line."""

    prerequisites: frozenset[str]
    recipe_line: int | None


def _make(text: str, directory: str, *argv: str) -> subprocess.CompletedProcess[str]:
    """Run GNU make on the Makefile `text`, read from standard input, in `directory`.

    The environment holds `PATH` alone, so a `MAKEFLAGS` that `make check` set
    for the suite cannot reach this make.
    """
    return subprocess.run(
        [_gnu_make(), "--no-print-directory", "-f", "-", *argv],
        input=text,
        capture_output=True,
        text=True,
        cwd=directory,
        env={"PATH": os.environ["PATH"], "LC_ALL": "C"},
        check=False,
    )


def _database(text: str, directory: str) -> tuple[dict[str, Target], frozenset[str]]:
    """make's targets in `text`, and every file it names, read from its printed database."""
    run = _make(text, directory, "-pqRr", "NO_SUCH_GOAL")
    assert run.stderr == NO_GOAL, f"make refuses the drawn Makefile:\n{run.stderr}\n{text}"
    files = run.stdout.split("\n# Files\n", 1)[1].split("\n# files hash-table stats:", 1)[0]
    targets: dict[str, Target] = {}
    names: set[str] = set()
    for entry in files.strip("\n").split("\n\n"):
        lines = entry.split("\n")
        is_target = lines[0] != "# Not a target:"
        if not is_target:
            lines = lines[1:]
        name, _, prerequisites = lines[0].partition(":")
        names.add(name)
        if not is_target or name.startswith("."):
            continue
        recipe_line = None
        for line in lines[1:]:
            if found := RECIPE_FROM.fullmatch(line):
                recipe_line = int(found["line"])
        targets[name] = Target(frozenset(prerequisites.split()), recipe_line)
    return targets, frozenset(names)


def _commands(text: str, directory: str, target: str, names: frozenset[str]) -> str:
    """What `make -n` prints for `target`'s own recipe, each other file in `names` held as old."""
    old = [argument for name in sorted(names - {target}) for argument in ("-o", name)]
    run = _make(text, directory, "-n", "SHELL=/bin/true", *old, target)
    assert run.returncode == 0 and not run.stderr, f"{run.stderr}\n{text}"
    return "".join(line + "\n" for line in run.stdout.splitlines() if not MAKE_MESSAGE.match(line))


def _printed(commands: list[str]) -> str:
    """`commands` as `make -n` prints them, one after another, each ended by a newline."""
    return "".join(command + "\n" for command in commands)


def _recipe(draw: st.DrawFn) -> list[str]:
    """A rule's recipe lines, and the comment and blank lines a rule runs on past."""
    lines: list[str] = []
    for _ in range(draw(st.integers(0, 3))):
        form = draw(
            st.sampled_from(("command", "command", "continued", "tab", "comments", "conditional"))
        )
        if form == "conditional":
            lines.append("ifdef X")
            lines.extend("\t" + draw(COMMAND) for _ in range(draw(st.integers(0, 1))))
            if draw(st.booleans()):
                lines.append("else")
                lines.extend("\t" + draw(COMMAND) for _ in range(draw(st.integers(0, 1))))
            lines.append("endif")
        elif form == "command":
            lines.append("\t" + draw(PREFIX) + draw(COMMAND))
        elif form == "continued":
            lines.extend(["\t" + draw(PREFIX) + draw(COMMAND) + " \\", "\t  " + draw(COMMAND)])
        elif form == "tab":
            lines.append("\t")
        else:
            lines.append(draw(st.sampled_from(("", draw(COMMENT), "\t" + draw(COMMENT)))))
    return lines


def _rule(draw: st.DrawFn, defined: list[str], free: list[str]) -> list[str]:
    """A rule naming one or two targets not yet given a recipe, and its prerequisites."""
    targets = draw(st.lists(st.sampled_from(free), min_size=1, max_size=2, unique=True))
    # A prerequisite is a target defined before any of these, so no dependency is circular.
    first = min((defined.index(name) for name in targets if name in defined), default=len(defined))
    prerequisites = draw(
        st.lists(st.sampled_from([*defined[:first], "out.txt"]), max_size=2, unique=True)
    )
    head = " ".join(targets) + ":"
    lines = [head + "".join(" " + name for name in prerequisites)]
    if len(prerequisites) > 1 and draw(st.booleans()):
        lines = [head + " " + prerequisites[0] + " \\", "  " + " ".join(prerequisites[1:])]
    if draw(st.integers(0, 3)) == 0:
        lines[-1] += " ; " + draw(COMMAND)
    recipe = _recipe(draw)
    # A rule with no recipe may name a target again, as a second rule giving prerequisites.
    if any(line.startswith("\t") for line in recipe) or " ; " in lines[-1]:
        for target in targets:
            free.remove(target)
    defined.extend(name for name in targets if name not in defined)
    return [*lines, *recipe]


@st.composite
def makefiles(draw: st.DrawFn) -> str:
    """A Makefile's text: rules, `.PHONY`, assignments, `define` blocks and comments."""
    defined: list[str] = []
    free = list(TARGETS)
    lines: list[str] = []
    if draw(st.integers(0, 4)) == 0:
        lines.append(".ONESHELL:")
    for _ in range(draw(st.integers(1, 5))):
        form = draw(st.sampled_from(("rule", "rule", "rule", "assign", "define", "comment")))
        if form == "rule" and free:
            lines.extend(_rule(draw, defined, free))
        elif form == "assign":
            lines.append(draw(st.sampled_from(("X = 1", "Y := two words", "Z ?= a\\", "W += b"))))
            if lines[-1].endswith("\\"):
                lines.append("  continued")
            if draw(st.integers(0, 2)) == 0:
                lines.append("\tV = tab-led")
        elif form == "define":
            lines.extend(["define BODY", "\techo no", "check: not a rule", "endef"])
        else:
            lines.append(draw(COMMENT))
    if defined and draw(st.booleans()):
        phony = draw(st.lists(st.sampled_from([*defined, "ghost"]), min_size=1, unique=True))
        at = 0 if draw(st.booleans()) else len(lines)
        lines.insert(at, ".PHONY: " + " ".join(phony))
    return "\n".join(lines) + "\n"


def _held_to_make(text: str, commands_compared: bool = True) -> None:
    """Assert that each reader answers as make reads `text`, or declines.

    Where `commands_compared` is false, only the targets and prerequisites are
    compared, for a Makefile whose commands use variables.
    """
    with tempfile.TemporaryDirectory() as directory:
        targets, names = _database(text, directory)
        printed = {name: _commands(text, directory, name, names) for name in targets}
    try:
        declared, with_recipe = doc_check.make_targets(text)
    except doc_check.UnreadStatement:
        pass
    else:
        assert {name for name in declared if not name.startswith(".")} == set(targets), text
        ran = {name for name, output in printed.items() if output}
        assert {name for name in with_recipe if not name.startswith(".")} == ran, text
    try:
        recipes, prerequisites = doc_check._target_recipes(text)
    except doc_check.UnreadStatement:
        pass
    else:
        for name, target in targets.items():
            assert set(prerequisites.get(name, [])) == target.prerequisites, (name, text)
            if commands_compared:
                assert _printed(recipes.get(name, [])) == printed[name], (name, text)
    if not commands_compared or "\nifdef X\n" in f"\n{text}":
        return
    try:
        commands = [command for command, _ in doc_check._recipe_commands(text)]
    except doc_check.UnreadStatement:
        return
    # A recipe shared by the targets of one rule is handed over once, at the line it opens on.
    by_line = {
        target.recipe_line: printed[name]
        for name, target in targets.items()
        if target.recipe_line is not None
    }
    assert _printed(commands) == "".join(output for _, output in sorted(by_line.items())), text


@settings(derandomize=True, database=None, deadline=None, max_examples=300)
@given(makefiles())
def test_the_makefile_readers_read_generated_makefiles_as_make_does(text: str) -> None:
    _held_to_make(text)


def test_the_makefile_readers_read_the_tracked_makefile_as_make_does() -> None:
    """The repository's own Makefile, compared on its targets and prerequisites alone.

    Its commands are not compared. The readers keep make's own spelling of a
    command, `$$` and `$(MAKE)` included, as the gate's checks compare it,
    where `make -n` prints each expanded. The generator draws no `$`, so its
    Makefiles' commands are compared whole.
    """
    text = (Path(__file__).resolve().parents[2] / "Makefile").read_text(encoding="utf-8")
    _held_to_make(text, commands_compared=False)


#: Makefiles the readers read differently from make today: each row's Makefile, its item,
#: the commands make runs for `check`, and the commands `_target_recipes` reads under it.
KNOWN_DEPARTURES: list[object] = []


@pytest.mark.parametrize(("text", "make", "reader"), KNOWN_DEPARTURES)
def test_each_known_departure_from_make_reads_as_its_row_records(
    text: str, make: str, reader: list[str]
) -> None:
    """A form the generator leaves out still reads as its item says, in make and in the reader.

    A row whose reading has changed is fixed or has moved. Either way its item,
    and the generator's exclusion of the form, want revisiting.
    """
    with tempfile.TemporaryDirectory() as directory:
        _, names = _database(text, directory)
        assert _commands(text, directory, "check", names) == make
    assert doc_check._target_recipes(text)[0]["check"] == reader
