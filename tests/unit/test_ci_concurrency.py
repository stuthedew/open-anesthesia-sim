"""Hold `.github/workflows/quality.yml`'s concurrency block to what its comment claims.

The claim is that every commit on `main` keeps its own quality run, which is
what makes the whole-store `bin/docket check --verify` a fact about the default
branch rather than about whichever merge happened to survive. For eleven days
the block did not deliver it and said it did: `cancel-in-progress: false`
protects the run already *in progress*, while the single pending slot behind it
is taken by whichever run arrives next. 31 of the 257 completed `main` push
runs in that window - 12.1% - were evicted from it, each having started no job
at all (`PL-SMN4`).

Nothing else in this tree would catch that coming back. The expression is
configuration rather than code, GitHub evaluates it, and the failure is silent
by construction: an evicted run reports `cancelled`, which
`tools/main_ci_status.py` correctly declines to read as a verdict, so a commit
with no whole-store check looks exactly like a commit nobody has asked about.

So these tests render the group the way GitHub would, for a `main` push and for
a pull request, and assert the property rather than the spelling. `_evaluate`
understands only the expression forms the block actually uses and raises on
anything else, deliberately: a rewrite into a shape this file cannot read is a
failure to report, not a pass to hand out.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "quality.yml"

#: A `${{ … }}` interpolation, capturing what is inside it.
_EXPRESSION = re.compile(r"\$\{\{(.+?)\}\}")

_PATH = r"[a-z_]+(?:\.[a-z_]+)*"
_LITERAL = r"'[^']*'"
_TERM = rf"(?:{_PATH}|{_LITERAL})"
_COMPARISON = re.compile(rf"^({_PATH})\s*(==|!=)\s*({_LITERAL})$")
_TERNARY = re.compile(rf"^({_PATH})\s*(==|!=)\s*({_LITERAL})\s*&&\s*({_TERM})\s*\|\|\s*({_TERM})$")
_LOOKUP = re.compile(rf"^{_PATH}$")


def _term(text: str, context: dict[str, str]) -> str:
    """A quoted literal's contents, or a context value - never a guess at a missing key."""
    if text.startswith("'"):
        return text[1:-1]
    assert text in context, f"{text} is not in this test's context: {sorted(context)}"
    return context[text]


def _compare(left: str, operator: str, right: str, context: dict[str, str]) -> bool:
    return (
        _term(left, context) == _term(right, context)
        if operator == "=="
        else _term(left, context) != _term(right, context)
    )


def _evaluate(fragment: str, context: dict[str, str]) -> str | bool:
    """Evaluate one `${{ … }}` body, or fail saying the form was not recognised.

    The three forms below are the ones the block uses. Refusing everything else
    is the point: silently returning something for an expression this file does
    not model would make the assertions meaningless exactly when the block has
    been rewritten, which is the only moment they matter.
    """
    fragment = fragment.strip()
    ternary = _TERNARY.match(fragment)
    if ternary is not None:
        left, operator, right, when_true, when_false = ternary.groups()
        chosen = when_true if _compare(left, operator, right, context) else when_false
        return _term(chosen, context)
    comparison = _COMPARISON.match(fragment)
    if comparison is not None:
        return _compare(*comparison.groups(), context)
    if _LOOKUP.match(fragment) is not None:
        return _term(fragment, context)
    raise AssertionError(
        f"quality.yml's concurrency block uses an expression this test cannot "
        f"evaluate: {fragment!r}. Extend `_evaluate` alongside the change rather "
        f"than deleting the assertion it protects."
    )


def _concurrency() -> dict[str, str]:
    """The `concurrency:` mapping's raw values, keyed by name.

    A four-line block of a known shape, read without PyYAML because the project
    environment does not carry it. Keys outside that block cannot reach here:
    collection stops at the first line that is neither indented nor blank.
    """
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = lines.index("concurrency:") + 1
    block: dict[str, str] = {}
    for line in lines[start:]:
        if not line.strip():
            continue
        entry = re.match(r"^  ([a-z-]+): (.+)$", line)
        if entry is None:
            break
        block[entry.group(1)] = entry.group(2).strip()
    return block


def _render(template: str, context: dict[str, str]) -> str:
    """Substitute every interpolation in a workflow value, as GitHub would."""
    return _EXPRESSION.sub(lambda match: str(_evaluate(match.group(1), context)), template)


def _flag(value: str, context: dict[str, str]) -> bool:
    """A value that is one whole expression, evaluated to the boolean it yields."""
    body = _EXPRESSION.fullmatch(value)
    assert body is not None, f"expected a single expression, got {value!r}"
    result = _evaluate(body.group(1), context)
    assert isinstance(result, bool), f"{value!r} evaluated to {result!r}, not a boolean"
    return result


def _push(sha: str) -> dict[str, str]:
    return {"github.workflow": "quality", "github.ref": "refs/heads/main", "github.sha": sha}


def _pull_request(number: int, sha: str) -> dict[str, str]:
    return {
        "github.workflow": "quality",
        "github.ref": f"refs/pull/{number}/merge",
        "github.sha": sha,
    }


def test_each_commit_on_main_gets_a_group_of_its_own() -> None:
    """The defect itself: two `main` merges sharing a group, so one evicts the other.

    `25abc218` and `17403970` are the real pair from 2026-09-15 22:59 UTC, whose
    runs were #2000 and #2001; #2000 was cancelled eight seconds in, having
    started no job.
    """
    group = _concurrency()["group"]
    assert _render(group, _push("25abc218")) != _render(group, _push("17403970"))


def test_pushes_to_one_pull_request_still_share_a_group() -> None:
    """The saving `PL-QD9K` bought, which a per-commit group everywhere would undo.

    `github.sha` is the merge commit under `pull_request` and moves on every
    push, so a group keyed on it would give each push its own lane and cancel
    nothing.
    """
    group = _concurrency()["group"]
    first = _render(group, _pull_request(612, "a0ffc9cc"))
    second = _render(group, _pull_request(612, "2fed8975"))
    assert first == second


def test_an_in_progress_run_survives_on_main_and_is_cancelled_on_a_pull_request() -> None:
    flag = _concurrency()["cancel-in-progress"]
    assert _flag(flag, _push("2ebe91e9")) is False
    assert _flag(flag, _pull_request(614, "2ebe91e9")) is True


def test_the_block_does_not_ask_for_the_larger_queue() -> None:
    """`queue: max` is the alternative shape, and it cannot be scoped to `main`.

    It is a fixed `single | max` enum with no expression form, and combining it
    with `cancel-in-progress: true` is rejected - which the pull-request lane
    above evaluates to. Adopting it here would therefore break every pull
    request's run rather than only the one it was aimed at.
    """
    assert _concurrency().get("queue", "single") == "single"


def test_an_unrecognised_expression_fails_rather_than_passing() -> None:
    """The refusal in `_evaluate`, which is what keeps the assertions above honest."""
    with pytest.raises(AssertionError, match="cannot evaluate"):
        _evaluate("github.ref == 'refs/heads/main' && 1 || 2", _push("2ebe91e9"))
