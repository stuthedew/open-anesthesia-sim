#!/usr/bin/env python3
"""Refuse a configuration fact whose copy no longer matches its home.

Some configuration facts must be written in more than one file, because the
files are read by tools that cannot read each other: a workflow cannot import
`pyproject.toml`, and the README is prose. `PL-K88Z`'s inventory found 23 such
facts that agreed but that no check enforced (`PL-SH0W`). Each one is listed
in `FACTS` below with its home, the file whose value is the answer, and the
places that repeat it. The check reads the value at each place and fails when
a copy differs from its home.

A copy that is no longer found also fails. Otherwise a reworded sentence or a
renamed key would leave the check passing while it checks nothing.

What this cannot decide stays a judgment: whether a sentence around a value is
still true, and whether a new file has started repeating a fact. A new copy is
added to `FACTS` by the session that writes it.

Standard library only and floor-parseable, like every tool under `tools/`. It
reads text and parses no Python, so it runs under bare `python3`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _as_is(text: str) -> str:
    return text


def _words(text: str) -> str:
    """Return `text` with each run of whitespace made one space, for prose that wraps."""

    return " ".join(text.split())


def _minor(text: str) -> str:
    """Return the major and minor parts of a version, such as 3.14 from 3.14.7."""

    return ".".join(text.split(".")[:2])


def _ruff_target(text: str) -> str:
    """Return ruff's `py314` as the version it names, 3.14."""

    digits = text.removeprefix("py")
    return f"{digits[0]}.{digits[1:]}"


def _quoted(text: str) -> str:
    """Return the quoted strings in a list or tuple literal, in order."""

    return ", ".join(re.findall(r'"([^"]*)"', text))


def _paths(text: str) -> str:
    """Return the backticked paths in a span of prose or a list, without trailing slashes."""

    found = re.findall(r'[`"]([^`"\s]+)[`"]', text)
    return ", ".join(sorted({path.rstrip("/") for path in found}))


def _tools(text: str) -> str:
    """Return the names of the scripts under `tools/` that a span names, sorted."""

    names = re.findall(r"(\w+)\.py", text)
    return ", ".join(sorted({name for name in names if (ROOT / "tools" / f"{name}.py").is_file()}))


@dataclass(frozen=True)
class Place:
    """Where one file states a fact.

    `path` may be a glob, and then every file it matches is read. `pattern`
    has one group, which holds the value. `read` turns the value into
    the form the home and its copies are compared in. Where `collect` is true,
    the value is every match taken together rather than each match on its own.
    """

    path: str
    pattern: str
    read: Callable[[str], str] = _as_is
    flags: int = re.MULTILINE
    collect: bool = False

    def values(self, root: Path) -> list[str]:
        """Return the value at each match, or one value for the matches taken together."""

        found = [
            match.group(1)
            for path in sorted(root.glob(self.path))
            for match in re.finditer(self.pattern, path.read_text(encoding="utf-8"), self.flags)
        ]

        if self.collect:
            return [self.read(" ".join(found))] if found else []

        return [self.read(value) for value in found]


@dataclass(frozen=True)
class Fact:
    """One configuration fact: the file that holds it, and the places that repeat it."""

    name: str
    home: Place
    copies: tuple[Place, ...]


_PROSE = re.MULTILINE | re.DOTALL


def _action(action: str) -> Fact:
    """Return the fact that every workflow pins `action` at the version `quality.yml` does."""

    pattern = rf"uses: {re.escape(action)}@(\S+)"
    return Fact(
        f"the version of {action}",
        Place(".github/workflows/quality.yml", pattern),
        (Place(".github/workflows/*.yml", pattern),),
    )


#: The workflow actions pinned in more than one workflow.
PINNED_ACTIONS = (
    "actions/checkout",
    "actions/setup-python",
    "astral-sh/setup-uv",
    "actions/upload-artifact",
)

_UV_SYNC = r"^(?:\t|\s*- run: )?uv sync (--[^\n`]*?)\s*$"

FACTS: tuple[Fact, ...] = (
    Fact(
        "the Python release the application targets",
        Place(".python-version", r"^(\d+\.\d+\.\d+)$", _minor),
        (
            Place("pyproject.toml", r'^target-version = "(py\d+)"$', _ruff_target),
            Place("pyproject.toml", r'^python_version = "(\d+\.\d+)"$'),
            Place("README.md", r"^- \*\*Python (\d+\.\d+)\*\*"),
        ),
    ),
    Fact(
        "the supported Python range",
        Place("pyproject.toml", r'^requires-python = "([^"]+)"$'),
        (Place(".github/workflows/drift.yml", r'`requires-python = "([^"]+)"`'),),
    ),
    Fact(
        "the lowest supported Python release",
        Place("pyproject.toml", r'^requires-python = ">=(\d+\.\d+)'),
        (Place(".github/workflows/drift.yml", r'^\s*relaxed = ">=(\d+\.\d+)"$'),),
    ),
    Fact(
        "the oldest uv the project accepts",
        Place("pyproject.toml", r'^required-version = ">=(\d+\.\d+\.\d+)"$'),
        (
            Place("pyproject.toml", r'"uv_build>=(\d+\.\d+\.\d+),'),
            Place("README.md", r"\*\*\[uv\]\([^)]*\) (\d+\.\d+\.\d+) or newer\.\*\*"),
            Place("docs/worker.md", r"Required uv version `>=(\d+\.\d+\.\d+)`"),
            Place("docs/worker.md", r"'uv>=(\d+\.\d+\.\d+)'"),
        ),
    ),
    Fact(
        "the mutmut release the mutation group pins",
        Place("pyproject.toml", r'"mutmut==(\d+\.\d+\.\d+)"'),
        (Place("docs/mutation-testing.md", r"mutmut is pinned to version (\d+\.\d+\.\d+)"),),
    ),
    *(_action(action) for action in PINNED_ACTIONS),
    Fact(
        "the system package Qt needs on Linux",
        Place(".github/workflows/quality.yml", r"apt-get install -y (\S+)$"),
        (
            Place(".github/workflows/drift.yml", r"apt-get install -y (\S+)$"),
            Place("README.md", r"\*\*On Linux, `(\S+)`\*\* \(`apt install (?:\S+)`\)"),
            Place("README.md", r"\*\*On Linux, `\S+`\*\* \(`apt install (\S+)`\)"),
        ),
    ),
    Fact(
        "the test trees pytest collects",
        Place("pyproject.toml", r"^testpaths = \[([^\]]*)\]$", _quoted),
        (
            Place("docket.toml", r"^collected_test_paths = \[([^\]]*)\]$", _quoted),
            Place("tools/ignore_check.py", r"^TREES = \(([^)]*)\)$", _quoted),
        ),
    ),
    Fact(
        "the clinical floor: the paths that produce clinical values",
        Place("docket.toml", r"^protected_paths = \[([^\]]*)\]$", _paths),
        (
            Place(
                "subprojects/docket/src/docket/arming.py",
                r"^SECOND_PASS_PATHS = \(([^)]*)\)$",
                _paths,
            ),
            Place("CLAUDE.md", r"A defect in\s+(.*?),\s+or any finding", _paths, _PROSE),
            Place("docs/worker.md", r"\*\*Never edit (`src/.*?)\.\*\*", _paths, _PROSE),
        ),
    ),
    Fact(
        "the simulator's paths, which the specialist standard applies to",
        Place(
            "CLAUDE.md",
            r"The simulator and the documentation a reader of it needs — (.*?) — are held",
            _paths,
            _PROSE,
        ),
        (
            Place(
                ".claude/rules/expert-review.md",
                r"the \*\*simulator\*\* — (.*?) — and for",
                _paths,
                _PROSE,
            ),
        ),
    ),
    Fact(
        "the apparatus's paths, which the apparatus standard applies to",
        Place(
            "CLAUDE.md",
            r"The workflow apparatus that exists so agent sessions can be productive"
            r" — (.*?) — is held",
            _paths,
            _PROSE,
        ),
        (
            Place(
                ".claude/rules/expert-review.md",
                r"apparatus \((.*?)\), which is held",
                _paths,
                _PROSE,
            ),
        ),
    ),
    Fact(
        "the command that installs the locked environment",
        Place("Makefile", r"^\tuv sync (--[^\n]*?)\s*$"),
        (
            Place(".github/workflows/quality.yml", _UV_SYNC),
            # `drift.yml`'s other two `uv sync` lines upgrade on purpose.
            Place(".github/workflows/drift.yml", r"^\s*- run: uv sync (--locked[^\n]*?)\s*$"),
            Place("README.md", _UV_SYNC),
            Place("CONTRIBUTING.md", _UV_SYNC),
            Place("docs/worker.md", _UV_SYNC),
        ),
    ),
    Fact(
        "the formatter's check command",
        Place("Makefile", r"^\tuv run (ruff format --check \.)$"),
        (Place(".github/workflows/quality.yml", r"^\s*- run: uv run (ruff format --check \.)$"),),
    ),
    Fact(
        "the type checker's command",
        Place("Makefile", r"^\tuv run (mypy)$"),
        (
            Place(".github/workflows/quality.yml", r"^\s*- run: uv run (mypy\b.*)$"),
            Place(".github/workflows/drift.yml", r"^\s*- run: uv run (mypy\b.*)$"),
        ),
    ),
    Fact(
        "the whole-suite run with no coverage",
        Place("Makefile", r"^\tuv run (pytest -n auto --dist worksteal)$"),
        # The `order` job adds `-p randomly` and a seed on purpose (`PL-75D9`).
        (
            Place(
                ".github/workflows/drift.yml",
                r"^\s*- run: uv run (pytest\b[^\n]*?)(?: -p randomly .*)?$",
            ),
        ),
    ),
    Fact(
        "the tools `make check` runs under `uv run python` rather than bare",
        Place("Makefile", r"^\tuv run python tools/(\w+\.py)", _tools, collect=True),
        (
            Place(
                "docs/apparatus.md",
                r"(Nine of them are nonetheless .*? are the exception, run both\s+ways)",
                _tools,
                _PROSE,
            ),
        ),
    ),
    Fact(
        "the quality job's time limit, in minutes",
        Place(
            ".github/workflows/quality.yml",
            r"^    # (\d+) minutes was sized against the single x64 job's times",
        ),
        (
            Place(
                ".github/workflows/quality.yml",
                r"^    timeout-minutes: (\d+)\n    # The fast path's answer",
            ),
            Place("tools/main_ci_status.py", r"a step the (\d+)-minute job"),
            Place(
                "tools/main_ci_status.py", r"(\d+) minutes after it was created, the same cutoff"
            ),
        ),
    ),
    Fact(
        "the quote check's fetch timeout, in seconds",
        Place("tools/doc_quote_check.py", r"^FETCH_TIMEOUT_S = (\d+)$"),
        (Place(".github/workflows/drift.yml", r"each read once with a (\d+) s timeout"),),
    ),
)


@dataclass(frozen=True)
class Finding:
    """A place whose value is missing or differs from its fact's home."""

    fact: str
    path: str
    expected: str
    found: str | None

    def __str__(self) -> str:
        if self.found is None:
            return f"{self.path}: {self.fact} is no longer found where this check reads it"

        return f"{self.path}: {self.fact} is {self.found!r} here, and {self.expected!r} at its home"


def check(root: Path, facts: Sequence[Fact] = FACTS) -> tuple[list[Finding], int]:
    """Return the findings, and how many copies were compared."""

    findings: list[Finding] = []
    compared = 0

    for fact in facts:
        home = fact.home.values(root)

        if not home or len(set(home)) != 1:
            found = None if not home else ", ".join(sorted(set(home)))
            findings.append(Finding(fact.name, fact.home.path, "one value", found))
            continue

        expected = home[0]

        for copy in fact.copies:
            values = copy.values(root)

            if not values:
                findings.append(Finding(fact.name, copy.path, expected, None))

            for value in values:
                compared += 1

                if value != expected:
                    findings.append(Finding(fact.name, copy.path, expected, value))

    return findings, compared


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="path to the repository")
    args = parser.parse_args(argv)
    findings, compared = check(args.root.resolve())

    for finding in findings:
        print(finding, file=sys.stderr)

    print(
        f"config homes: {len(FACTS)} facts, {compared} copies compared with their homes, "
        f"{len(findings)} errors"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
