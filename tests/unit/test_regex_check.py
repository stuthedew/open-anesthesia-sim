"""`tools/regex_check.py` must find each regular expression and accept only a reasoned one.

The failure that matters most is the false pass: a call the walk misses, a
comment read as a reason when it is not one, or a baseline that grows without
failing. Each leaves the stop that `PL-7JYV` asked for in place on paper and
missing in practice.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from regex_check import GUIDANCE, KNOWN_READERS, added_uses, analyze, format_report, uses


def _calls(source: str) -> list[tuple[str, bool]]:
    return [(use.function, use.reasoned) for use in uses(source)]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("import re\nX = re.compile('a')\n", [("compile", False)]),
        (
            "import re\nre.search('a', s)\nre.sub('a', 'b', s)\n",
            [("search", False), ("sub", False)],
        ),
        ("import re as r\nr.fullmatch('a', s)\n", [("fullmatch", False)]),
        ("from re import compile as c\nc('a')\n", [("compile", False)]),
        ("import regex\nregex.findall('a', s)\n", [("findall", False)]),
        ("import re\nre.prefixmatch('a', s)\n", [("prefixmatch", False)]),
    ],
)
def test_each_spelling_of_a_pattern_call_is_found(
    source: str, expected: list[tuple[str, bool]]
) -> None:
    assert _calls(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "import re\nre.escape(s)\n",
        "import re\nflags = re.IGNORECASE | re.VERBOSE\n",
        "import re\ndef f(m: re.Match[str]) -> None: ...\n",
        "import re\nID_RE = re.compile('a')  # regex: token\nID_RE.match(s)\n",
        "s.split(',')\n",
        "import other\nother.compile('a')\n",
    ],
)
def test_calls_that_build_no_new_pattern_are_not_counted(source: str) -> None:
    assert [use for use in uses(source) if not use.reasoned] == []


@pytest.mark.parametrize(
    "source",
    [
        "import re\n# regex: a fixed-shape token\nX = re.compile('a')\n",
        "import re\nX = re.compile('a')  # regex: a fixed-shape token\n",
        "import re\nX = re.compile('a')  # noqa: E501  # regex: a fixed-shape token\n",
        "import re\n# regex: a fixed-shape token, which\n# no parser reads\nX = re.compile('a')\n",
        "import re\nX = re.compile(\n    'a'  # regex: a fixed-shape token\n)\n",
        (
            "import re\n# regex: free prose\nfound = [\n    m.group(0)\n"
            "    for m in re.finditer('a', s)\n]\n"
        ),
    ],
)
def test_a_reason_on_the_statement_or_directly_above_it_is_accepted(source: str) -> None:
    assert [use.reasoned for use in uses(source)] == [True]


@pytest.mark.parametrize(
    "source",
    [
        "import re\n# regex:\nX = re.compile('a')\n",
        "import re\n# regex:    \nX = re.compile('a')\n",
        "import re\n# regex: a token\n\nX = re.compile('a')\n",
        "import re\n# regex: a token\nY = 1\nX = re.compile('a')\n",
        "import re\nX = re.compile('a')\n# regex: a token\n",
        "import re\nX = re.compile('a')  # Regex is fine here\n",
        "import re\nX = re.compile('# regex: inside the pattern')\n",
    ],
)
def test_an_empty_distant_or_lookalike_reason_is_refused(source: str) -> None:
    assert [use.reasoned for use in uses(source)] == [False]


def test_a_call_in_an_if_test_does_not_borrow_a_reason_from_the_block_below() -> None:
    source = "import re\nif re.search('a', s):\n    # regex: belongs to the next line\n    pass\n"

    assert [use.reasoned for use in uses(source)] == [False]


def test_an_edit_that_adds_a_call_is_refused_and_one_that_moves_a_call_is_not() -> None:
    before = "import re\nA = re.compile('a')\n"

    assert added_uses(before, before + "B = re.compile('b')\n")[0].text == "re.compile('b')"
    assert added_uses(before, "import re\n\n\nA = re.compile(\n    'a',\n)\n") == []
    assert added_uses(before, "import re\nA = re.compile('a+')\n")[0].text == "re.compile('a+')"
    assert added_uses(before, "import re\nA = re.compile('a+')  # regex: a run of a\n") == []
    assert added_uses("", "import re\nA = re.compile('a')\n")[0].line == 2


def test_an_edit_that_does_not_parse_raises_rather_than_passing() -> None:
    with pytest.raises(SyntaxError):
        added_uses("import re\n", "import re\nre.compile(\n")


def _write(root: Path, name: str, source: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def test_a_new_call_in_the_tree_fails_naming_the_file_scope_and_guidance(tmp_path: Path) -> None:
    _write(tmp_path, "tools/a.py", "import re\ndef read(s):\n    return re.search('a', s)\n")

    report = analyze(tmp_path, {})
    text = format_report(report)

    assert report.errors == 1
    assert "tools/a.py: 1 search call(s) in read, and the baseline allows 0" in text
    assert "line 3, in read: re.search('a', s)" in text
    assert GUIDANCE in text


def test_the_baseline_allows_what_it_lists_and_fails_when_it_grows_or_goes_stale(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "a.py", "import re\nA = re.compile('a')\nB = re.compile('b')\n")

    assert analyze(tmp_path, {"a.py": {("<module>", "compile"): 2}}).errors == 0
    assert analyze(tmp_path, {"a.py": {("<module>", "compile"): 1}}).errors == 1

    stale = analyze(tmp_path, {"a.py": {("<module>", "compile"): 3}})

    assert stale.errors == 1
    assert "set it to 2" in format_report(stale)


def test_a_reasoned_call_needs_no_baseline_entry(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", "import re\nA = re.compile('a')  # regex: a single letter\n")

    report = analyze(tmp_path, {})

    assert (report.errors, report.reasoned) == (0, 1)


def test_a_file_that_does_not_parse_fails_rather_than_passing(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", "def broken(:\n")

    report = analyze(tmp_path, {})

    assert report.errors == 1
    assert "a.py: SyntaxError" in format_report(report)


@pytest.mark.parametrize(("module", "_what"), KNOWN_READERS)
def test_each_reader_the_guidance_names_exists(module: str, _what: str) -> None:
    importlib.import_module(module)
    assert f"`{module}`" in GUIDANCE


def test_the_tree_holds_no_regular_expression_beyond_the_baseline() -> None:
    root = Path(__file__).resolve().parents[2]

    report = analyze(root)

    assert report.errors == 0, format_report(report)
