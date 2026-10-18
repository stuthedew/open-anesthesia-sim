"""`required_checks_check` reads generated workflows' triggers and steps as PyYAML does.

`tools/required_checks_check.py` reads a workflow by hand, because the gate runs
on the standard library alone. `triggers` reads which events the `on:` key names
and the filters on a pull-request event, and `steps` reads each step of each
job with the line and column of each key. Seven workflow misreads closed as
items before this test existed, and each was found after its form merged:
`PL-4T49`, `PL-848V`, `PL-CK3F`, `PL-GWQ7`, `PL-TMX9`, `PL-PZP7` and `PL-S3XS`.
This test fails the pull request that first writes such a form instead
(`PL-0MC5`).

The consumer is GitHub, whose workflow parser reads YAML with the `yaml` npm
package. PyYAML 6.0, a dev dependency, stands in for it here, as it does for
`docket.frontmatter` in `subprojects/docket/tests/test_frontmatter_reference.py`.
PyYAML implements YAML 1.1, so it loads the key `on` as `True`. The test reads
PyYAML's composed nodes rather than its loaded values, and a node keeps the
text `on`, so nothing has to be mapped back. PyYAML also departs from the YAML
Test Suite on tabs, flow-collection edge cases, anchors and tags, so the
strategy draws none of those.

Hypothesis draws the workflows, derandomized, so a red run reproduces exactly.
Each workflow is built from the forms the closed items name:

- `on:` as an event name, a flow list, a block list or a block or flow mapping,
  on the key's line or the line below it, with the key quoted or plain;
- a pull-request event as a list entry, a flow mapping or a block mapping, its
  filters written as one name or as a list;
- indentation of two or four spaces, and a step list at its key's column or
  indented under it;
- comment lines and trailing comments;
- a job name continued onto a second line;
- `run:` beside other keys, as a plain scalar or as a block scalar whose lines
  look like steps;
- a `defaults:` block holding a `run:` that is no step.

Where a reader raises `Undecidable`, or refuses a step, the test accepts the
decline. Where it answers, the answer must match PyYAML's reading.
"""

from __future__ import annotations

from pathlib import Path

import required_checks_check as rcc
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parents[2]

LETTERS = "abcdefghijklmnopqrstuvwxyz"
NAME = st.builds(
    lambda head, tail: head + tail,
    st.sampled_from(LETTERS),
    st.text(LETTERS + "0123456789-", max_size=6),
)
WORDS = st.lists(NAME, min_size=1, max_size=3).map(" ".join)
#: The events `on:` may name. Only the first two are pull-request events, whose filters are read.
EVENTS = ("pull_request", "pull_request_target", "push", "workflow_dispatch", "merge_group")
#: A branch, path or activity name a filter lists, plain or quoted.
FILTER_NAME = st.sampled_from(
    ("main", "release/**", "'v*'", '"**.md"', "docs/**", "opened", "synchronize", "labeled")
)
FILTERS = ("branches", "branches-ignore", "paths", "types")
INDENT = st.sampled_from((2, 4))
COMMENT = st.sampled_from(("", "", " # why"))
#: A line of a block scalar, some shaped like the keys and steps a reader could take it for.
SCRIPT_LINE = st.sampled_from(
    ("make check", "- run: fake", "steps:", "name: x", "echo 'a: b'", "# not a comment")
)


def _filter_value(draw: st.DrawFn, column: int, unit: int) -> list[str]:
    """A filter's value: one name on the key's line, a flow list, or a block list."""
    names = draw(st.lists(FILTER_NAME, min_size=1, max_size=3, unique=True))
    form = draw(st.sampled_from(("scalar", "flow", "block")))
    if form == "scalar":
        return [" " + names[0] + draw(COMMENT)]
    if form == "flow":
        return [" [" + ", ".join(names) + "]" + draw(COMMENT)]
    under = column + draw(st.sampled_from((0, unit)))
    return ["", *(" " * under + "- " + name for name in names)]


def _event_block(draw: st.DrawFn, event: str, column: int, unit: int) -> list[str]:
    """One event of a block mapping under `on:`, its key at `column`."""
    lead = " " * column + event + ":"
    if event in rcc.PULL_REQUEST_EVENTS and draw(st.booleans()):
        lines = [lead + draw(COMMENT)]
        for name in draw(st.lists(st.sampled_from(FILTERS), min_size=1, max_size=2, unique=True)):
            if name == "branches-ignore" and any("branches:" in line for line in lines):
                continue
            first, *under = _filter_value(draw, column + unit, unit)
            lines.extend([" " * (column + unit) + name + ":" + first, *under])
        return lines
    if event == "push" and draw(st.booleans()):
        return [lead, " " * (column + unit) + "branches: [main]"]
    if event == "workflow_dispatch" and draw(st.booleans()):
        inner = column + unit
        return [
            lead,
            " " * inner + "inputs:",
            " " * (inner + unit) + "reason:",
            " " * (inner + 2 * unit) + "description: |",
            " " * (inner + 3 * unit) + "pull_request:",
            " " * (inner + 3 * unit) + "- branches: [x]",
        ]
    return [lead + draw(st.sampled_from(("", " null", " # nothing")))]


def _event_flow(draw: st.DrawFn, event: str) -> str:
    """One entry of a flow mapping under `on:`."""
    if event in rcc.PULL_REQUEST_EVENTS and draw(st.booleans()):
        name = draw(st.sampled_from(FILTERS))
        names = draw(st.lists(FILTER_NAME, min_size=1, max_size=2, unique=True))
        value = (
            names[0] if len(names) == 1 and draw(st.booleans()) else "[" + ", ".join(names) + "]"
        )
        return f"{event}: {{{name}: {value}}}"
    return event + draw(st.sampled_from(("", ": null", ": {}")))


def _on(draw: st.DrawFn, unit: int) -> list[str]:
    """The top-level `on:` key and its value, in one of the forms GitHub's schema allows."""
    key = draw(st.sampled_from(("on:", "on:", '"on":', "'on':")))
    events = draw(st.lists(st.sampled_from(EVENTS), min_size=1, max_size=3, unique=True))
    form = draw(st.sampled_from(("scalar", "flow list", "block list", "block map", "flow map")))
    below = draw(st.booleans())
    if form == "scalar":
        value = events[0] + draw(COMMENT)
    elif form == "flow list":
        value = "[" + ", ".join(events) + "]" + draw(COMMENT)
    elif form == "flow map":
        value = "{" + ", ".join(_event_flow(draw, event) for event in events) + "}"
    elif form == "block list":
        column = draw(st.sampled_from((0, unit)))
        return [key + draw(COMMENT), *(" " * column + "- " + event for event in events)]
    else:
        lines = [key + draw(COMMENT)]
        for event in events:
            if draw(st.integers(0, 4)) == 0:
                lines.append(" " * unit + "# between events")
            lines.extend(_event_block(draw, event, unit, unit))
        return lines
    if below:
        return [key, " " * unit + value]
    return [key + " " + value]


def _step_value(draw: st.DrawFn, key: str, column: int, unit: int) -> list[str]:
    """What follows `key:` in a step whose keys sit at `column`.

    That is the rest of the key's line, then the lines under it.
    """
    if key == "run":
        if draw(st.booleans()):
            header = draw(st.sampled_from(("|", ">", "|-", "| # why")))
            content = column + draw(st.sampled_from((2, unit)))
            lines = draw(st.lists(SCRIPT_LINE, min_size=1, max_size=3))
            return [" " + header, *(" " * content + line for line in lines)]
        return [" " + draw(WORDS) + draw(COMMENT)]
    if key == "name":
        form = draw(st.sampled_from(("plain", "quoted", "continued")))
        if form == "quoted":
            return [f' "{draw(WORDS)}: step"' + draw(COMMENT)]
        if form == "continued":
            return [
                " " + draw(WORDS),
                " " * (column + draw(st.sampled_from((1, 2, 4)))) + draw(WORDS),
            ]
        return [" " + draw(WORDS) + draw(COMMENT)]
    if key in ("with", "env"):
        names = draw(st.lists(NAME, min_size=1, max_size=2, unique=True))
        return ["", *(" " * (column + unit) + f"{name}: {draw(NAME)}" for name in names)]
    if key == "if":
        return [" " + draw(st.sampled_from(("github.event_name == 'push'", "${{ always() }}")))]
    return [" " + draw(st.sampled_from(("actions/checkout@v4", "./local", "true", "5")))]


def _step(draw: st.DrawFn, dash: int, unit: int) -> list[str]:
    """One entry of a `steps:` list, its `-` at column `dash`."""
    keys = draw(
        st.lists(
            st.sampled_from(("name", "run", "uses", "with", "env", "if", "id")),
            min_size=1,
            max_size=4,
            unique=True,
        )
    )
    column = dash + 2
    lines: list[str] = []
    for key in keys:
        first, *under = _step_value(draw, key, column, unit)
        lines.extend([" " * column + key + ":" + first, *under])
    if draw(st.integers(0, 3)):
        lines[0] = " " * dash + "- " + lines[0][column:]
    else:
        lines.insert(0, " " * dash + "-" + draw(COMMENT))
    return lines


def _job(draw: st.DrawFn, job: str, unit: int) -> list[str]:
    """One job under `jobs:`, its key at one indentation and its keys at two."""
    body = 2 * unit
    lines = [" " * unit + job + ":" + draw(COMMENT)]
    if draw(st.integers(0, 5)) == 0:
        return [*lines, " " * body + "uses: ./.github/workflows/called.yml"]
    if draw(st.booleans()):
        first, *under = _step_value(draw, "name", body, unit)
        lines.extend([" " * body + "name:" + first, *under])
    lines.append(" " * body + "runs-on: ubuntu-latest")
    if draw(st.integers(0, 2)) == 0:
        lines.extend(
            [
                " " * body + "defaults:",
                " " * (body + unit) + "run:",
                " " * (body + 2 * unit) + "shell: bash",
            ]
        )
    lines.append(" " * body + "steps:")
    dash = body + draw(st.sampled_from((0, unit)))
    for index in range(draw(st.integers(1, 3))):
        if index and draw(st.integers(0, 3)) == 0:
            lines.append(" " * dash + "# between steps")
        lines.extend(_step(draw, dash, unit))
    if draw(st.integers(0, 3)) == 0:
        lines.append(" " * body + "timeout-minutes: 5")
    return lines


@st.composite
def workflows(draw: st.DrawFn) -> list[str]:
    """A workflow's lines: a name, `on:`, perhaps `permissions:`, and `jobs:`, in a drawn order."""
    unit = draw(INDENT)
    blocks = [["name: " + draw(WORDS)], _on(draw, unit)]
    if draw(st.booleans()):
        blocks.append(["permissions:", " " * unit + "contents: read"])
    jobs = ["jobs:"]
    for job in draw(st.lists(NAME, min_size=1, max_size=2, unique=True)):
        jobs.extend(_job(draw, job, unit))
    blocks.append(jobs)
    lines = ["# a workflow"] if draw(st.booleans()) else []
    for block in draw(st.permutations(blocks)):
        lines.extend(block)
    return lines


def _document(lines: list[str]) -> yaml.MappingNode:
    """The mapping PyYAML composes from `lines`."""
    document = yaml.compose("\n".join(lines) + "\n", Loader=yaml.SafeLoader)
    assert isinstance(document, yaml.MappingNode), "the strategy drew no mapping"
    return document


def _value(mapping: yaml.MappingNode, name: str) -> yaml.Node:
    """The node `mapping` holds under the key whose text is `name`."""
    found: yaml.Node = next(value for key, value in mapping.value if key.value == name)
    return found


def _is_null(node: yaml.Node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag == "tag:yaml.org,2002:null"


def _pyyaml_triggers(lines: list[str]) -> dict[str, tuple[int, dict[str, tuple[str, ...]] | None]]:
    """Each event PyYAML reads under `on:`, with its line, counted from 1, and its filters.

    The filters are `None` for an event other than a pull-request one, as
    `triggers` gives them.
    """
    on = _value(_document(lines), "on")
    named: list[tuple[yaml.ScalarNode, yaml.Node | None]] = []
    if isinstance(on, yaml.ScalarNode):
        named = [(on, None)]
    elif isinstance(on, yaml.SequenceNode):
        named = [(item, None) for item in on.value]
    else:
        named = list(on.value)
    found: dict[str, tuple[int, dict[str, tuple[str, ...]] | None]] = {}
    for event, held in named:
        filters: dict[str, tuple[str, ...]] | None = None
        if event.value in rcc.PULL_REQUEST_EVENTS:
            filters = {}
            if held is not None and not _is_null(held):
                assert isinstance(held, yaml.MappingNode), "the strategy drew no filter mapping"
                for key, value in held.value:
                    items = value.value if isinstance(value, yaml.SequenceNode) else [value]
                    filters[key.value] = tuple(item.value for item in items)
        found[event.value] = (event.start_mark.line + 1, filters)
    return found


def _dash_line(lines: list[str], column: int, key_line: int) -> int:
    """The index of the line whose `-` at `column` opens the step whose first key is on `key_line`.

    The `-` is on that line or on a line above it.
    """
    at = key_line
    while lines[at][column : column + 1] != "-" or lines[at][:column].strip():
        at -= 1
    return at


def _pyyaml_steps(lines: list[str]) -> list[tuple[int, dict[str, tuple[int, int]]]]:
    """Each step PyYAML reads under each job's `steps:`: its `-` line, counted from 1, and its keys.

    Each key comes with the index of the line it opens on and its column, as
    `steps` gives them.
    """
    found = []
    for _, job in _value(_document(lines), "jobs").value:
        for key, value in job.value:
            if key.value != "steps":
                continue
            column = value.start_mark.column
            for step in value.value:
                first = step.value[0][0].start_mark.line
                read = {k.value: (k.start_mark.line, k.start_mark.column) for k, _ in step.value}
                found.append((_dash_line(lines, column, first) + 1, read))
    return found


def _held_to_pyyaml(lines: list[str]) -> None:
    """Assert that each reader answers as PyYAML reads `lines`, or declines."""
    text = "\n".join(lines)
    try:
        read = rcc.triggers(lines)
    except rcc.Undecidable:
        pass
    else:
        found = {event: (trigger.line, trigger.filters) for event, trigger in read.items()}
        assert found == _pyyaml_triggers(lines), text
    try:
        read_steps = rcc.steps(lines)
    except rcc.Undecidable:
        return
    if any(step.refused is not None for step in read_steps):
        return
    assert [(step.line, step.keys) for step in read_steps] == _pyyaml_steps(lines), text


@settings(derandomize=True, database=None, deadline=None, max_examples=1000)
@given(workflows())
def test_required_checks_reads_generated_workflows_as_yaml_does(lines: list[str]) -> None:
    _held_to_pyyaml(lines)


def test_required_checks_reads_the_tracked_workflows_as_yaml_does() -> None:
    """The workflows in the tree, on which the reader and PyYAML agreed on 2026-10-12."""
    paths = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert paths, "no workflow to read"
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert rcc.triggers(lines), path
        assert all(step.refused is None for step in rcc.steps(lines)), path
        _held_to_pyyaml(lines)
