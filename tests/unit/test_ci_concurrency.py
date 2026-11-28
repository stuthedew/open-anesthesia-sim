"""Hold `.github/workflows/quality.yml`'s concurrency block to what its comment claims.

The claim is that every commit on `main` keeps its own quality run, which is
what makes a green `main` a fact about each commit rather than about whichever
merge happened to survive. For eleven days
the block did not deliver it and said it did: `cancel-in-progress: false`
protects the run already *in progress*, while the single pending slot behind it
is taken by whichever run arrives next. 31 of the 257 completed `main` push
runs in that window - 12.1% - were evicted from it, each having started no job
at all (`PL-SMN4`).

Nothing else in this tree would reliably catch that coming back. The expression
is configuration rather than code, GitHub evaluates it, and the failure is all
but silent by construction: an evicted run reports `cancelled`, which
`tools/main_ci_status.py` declines to read as a verdict and reports only until
a later run reaches one (`PL-JTHW`). Once the run that evicted it finishes, a
commit with no quality run looks exactly like a commit nobody has asked
about.

So these tests render the group the way GitHub would, for a `main` push and for
a pull request, and assert the property rather than the spelling. `_evaluate`
understands only the expression forms the block actually uses and raises on
anything else, deliberately: a rewrite into a shape this file cannot read is a
failure to report, not a pass to hand out.

The last tests hold the two required checks that run only on pull requests,
`merge-hold` and `pr-title`, to cancelling none of their runs, and `pr-title` to
checking the title the pull request holds when it runs (`PL-Q3DW`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "quality.yml"

#: A `${{ … }}` interpolation, capturing what is inside it.
# regex: GitHub's `${{ … }}` interpolation sits inside a YAML string, where no
# parser here finds it, and a lazy match finds each one in turn.
_EXPRESSION = re.compile(r"\$\{\{(.+?)\}\}")

# The three expression forms `_evaluate` reads. Each is a flat run of tokens
# from GitHub's expression syntax, which no parser here reads, and anything
# else must fail rather than be guessed at.
_PATH = r"[a-z_]+(?:\.[a-z_]+)*"
_LITERAL = r"'[^']*'"
_TERM = rf"(?:{_PATH}|{_LITERAL})"
# regex: a comparison of a context with a literal, in GitHub's expression syntax.
_COMPARISON = re.compile(rf"({_PATH})\s*(==|!=)\s*({_LITERAL})")
# regex: `a == 'b' && c || d`, GitHub's spelling of a choice between two terms.
_TERNARY = re.compile(rf"({_PATH})\s*(==|!=)\s*({_LITERAL})\s*&&\s*({_TERM})\s*\|\|\s*({_TERM})")
# regex: a context's dotted name, such as `github.ref`.
_LOOKUP = re.compile(_PATH)


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
    ternary = _TERNARY.fullmatch(fragment)
    if ternary is not None:
        left, operator, right, when_true, when_false = ternary.groups()
        chosen = when_true if _compare(left, operator, right, context) else when_false
        return _term(chosen, context)
    comparison = _COMPARISON.fullmatch(fragment)
    if comparison is not None:
        return _compare(*comparison.groups(), context)
    if _LOOKUP.fullmatch(fragment) is not None:
        return _term(fragment, context)
    raise AssertionError(
        f"quality.yml's concurrency block uses an expression this test cannot "
        f"evaluate: {fragment!r}. Extend `_evaluate` alongside the change rather "
        f"than deleting the assertion it protects."
    )


def _concurrency() -> dict[str, str]:
    """The `concurrency:` mapping's raw values, keyed by name, as PyYAML reads them.

    Each value must be text, so a value YAML reads as a boolean, such as a bare
    `false`, fails here instead of being read as an expression.
    """
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    block = workflow["concurrency"]
    assert isinstance(block, dict), f"`concurrency:` should be a mapping, not {block!r}"
    for name, value in block.items():
        assert isinstance(value, str), f"`concurrency.{name}` should be text, not {value!r}"
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

    GitHub's workflow-syntax page makes combining it with `cancel-in-progress:
    true` a workflow validation error, and the pull-request lane above evaluates
    to that. It is a fixed `single | max` enum with no expression form on
    SchemaStore's declaration, where GitHub's page is silent. Adopting it here
    would therefore break every pull request's run rather than only the one it
    was aimed at.
    """
    assert _concurrency().get("queue", "single") == "single"


def test_an_unrecognised_expression_fails_rather_than_passing() -> None:
    """The refusal in `_evaluate`, which is what keeps the assertions above honest."""
    with pytest.raises(AssertionError, match="cannot evaluate"):
        _evaluate("github.ref == 'refs/heads/main' && 1 || 2", _push("2ebe91e9"))


@pytest.mark.parametrize("name", ["merge-hold.yml", "pr-title.yml"])
def test_a_required_check_on_a_pull_request_cancels_none_of_its_runs(name: str) -> None:
    """Every run of `merge-hold` and `pr-title` finishes, so the newest has a verdict (`PL-Q3DW`).

    Branch protection reads the newest run of a required check on the head
    commit. Two runs that start in the same second can enter their lane in
    either order, so a lane that cancels a run can leave the newest one
    cancelled, and the pull request blocked with every check green, as #2322
    was for six hours. `queue: max` keeps up to 100 runs waiting and cancels
    none, and GitHub refuses it beside `cancel-in-progress: true`.
    """
    workflow = yaml.safe_load((WORKFLOW.parent / name).read_text(encoding="utf-8"))
    block = workflow["concurrency"]

    assert "cancel-in-progress" not in block, block
    assert block["queue"] == "max", block


def test_the_title_check_reads_the_pull_request_s_title_rather_than_its_event_s() -> None:
    """A run that finishes last checks the newest title, whatever its event carried (`PL-Q3DW`).

    `pr-title` runs queue rather than cancel. A run whose event carried an
    older title can finish after a title edit, or run after the edit's own run.
    Checking its event's title, it would pass the old title last, and auto-merge
    could land the new one unchecked. So the title step asks the pull request
    for its title, and reads nothing about the title from the event.
    """
    workflow = yaml.safe_load((WORKFLOW.parent / "pr-title.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["pr-title"]["steps"]
    (title_step,) = [step for step in steps if "pr_title_check.py" in step.get("run", "")]

    assert "pull_request.title" not in str(title_step), title_step
    assert "PR_TITLE" not in title_step.get("env", {}), title_step
    assert 'gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER" --jq .title' in title_step["run"]
    assert workflow["permissions"]["pull-requests"] == "read", workflow["permissions"]
