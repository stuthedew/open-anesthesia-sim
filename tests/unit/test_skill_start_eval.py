"""Tests for `tools/skill_start_eval.py`, which measures whether a skill starts.

The script's answer decides whether procedures can leave the always-loaded
instructions (`PL-SN2Z`), so each test pins a way that answer could be wrong
without anything saying so.

A start is a `Skill` call naming the skill, and nothing else. A call to another
skill, or a session reading the skill's files with `Read`, would inflate the
rate if counted. A run the script could not read is reported apart and left
out of every rate, because counting it as "did not start" would turn a failure
to measure into a measurement. A run cut off by the turn limit is still read,
since the limit is the window being measured.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "skill_start_eval.py"

sys.path.insert(0, str(TOOL.parent))

import skill_start_eval  # noqa: E402

PROMPT = skill_start_eval.Prompt("pick-next", "What should I work on next?", should_start=True)


def call(name: str, **tool_input: str) -> dict:
    """One assistant event holding one tool call."""
    block = {"type": "tool_use", "name": name, "input": tool_input}
    return {"type": "assistant", "message": {"content": [block]}}


def stream(*events: dict, subtype: str = "success") -> str:
    """A session's stream-json output: the events, then its result line."""
    result = {"type": "result", "subtype": subtype, "total_cost_usd": 0.5}
    return "\n".join(json.dumps(e) for e in (*events, result))


def test_counts_a_docket_skill_call_as_a_start() -> None:
    run = skill_start_eval.classify(stream(call("Skill", skill="docket")), "docket", PROMPT, "on")
    assert run.started is True
    assert run.unread == ""


@pytest.mark.parametrize("name", ["/docket", "project:docket"])
def test_a_qualified_skill_name_is_still_a_start(name: str) -> None:
    run = skill_start_eval.classify(stream(call("Skill", skill=name)), "docket", PROMPT, "on")
    assert run.started is True


def test_another_skill_or_a_read_of_the_skill_file_is_not_a_start() -> None:
    output = stream(
        call("Skill", skill="run-the-app"),
        call("Read", file_path="/repo/.claude/skills/docket/SKILL.md"),
        call("Bash", command="bin/docket next"),
    )
    run = skill_start_eval.classify(output, "docket", PROMPT, "off")
    assert run.started is False
    assert run.read_skill_file is True
    assert run.ran_docket is True
    assert run.tool_calls == ("Skill", "Read", "Bash")


def test_a_run_cut_off_by_the_turn_limit_is_still_read() -> None:
    output = stream(call("Bash", command="ls"), subtype="error_max_turns")
    run = skill_start_eval.classify(output, "docket", PROMPT, "on")
    assert run.started is False
    assert run.unread == ""


@pytest.mark.parametrize(
    ("output", "reason"),
    [
        (json.dumps(call("Skill", skill="docket")) + "\nnot json", "not JSON"),
        (json.dumps(call("Skill", skill="docket")), "without a result"),
        (stream(subtype="error_during_execution"), "error_during_execution"),
    ],
)
def test_a_run_that_cannot_be_read_says_why_and_claims_nothing(output: str, reason: str) -> None:
    run = skill_start_eval.classify(output, "docket", PROMPT, "on")
    assert run.started is None
    assert reason in run.unread


def test_the_summary_leaves_unread_runs_out_of_the_rate() -> None:
    started = skill_start_eval.classify(
        stream(call("Skill", skill="docket")), "docket", PROMPT, "on"
    )
    missed = skill_start_eval.classify(stream(), "docket", PROMPT, "on")
    unread = skill_start_eval.classify("not json", "docket", PROMPT, "on")
    lines = skill_start_eval.summary([started, missed, unread])
    assert lines[0].startswith("should start, skill on: started 1 of 2,")
    assert lines[0].endswith("; 1 unread")
    assert any(line.startswith("unread: pick-next (on)") for line in lines)


def test_only_prompts_that_should_start_run_with_the_skill_off() -> None:
    quiet = skill_start_eval.Prompt("git-question", "merge or rebase?", should_start=False)
    runs = skill_start_eval.plan([PROMPT, quiet])
    assert runs == [(PROMPT, "on"), (quiet, "on"), (PROMPT, "off")]


def test_the_off_arm_turns_the_skill_off_through_skill_overrides() -> None:
    argv = skill_start_eval.command(PROMPT, "docket", "off", "claude-opus-5-5", 5)
    settings = json.loads(argv[argv.index("--settings") + 1])
    assert settings == {"skillOverrides": {"docket": "off"}}
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    assert "--settings" not in skill_start_eval.command(PROMPT, "docket", "on", "m", 5)


def test_the_shipped_prompt_set_has_both_groups() -> None:
    skill, prompts = skill_start_eval.load_prompts(skill_start_eval.PROMPTS)
    assert skill == "docket"
    assert sum(p.should_start for p in prompts) >= 3
    assert sum(not p.should_start for p in prompts) >= 3


def test_a_repeated_prompt_id_is_refused(tmp_path: Path) -> None:
    entry = {"id": "same", "prompt": "x", "should_start": True}
    path = tmp_path / "prompts.json"
    path.write_text(json.dumps({"skill": "docket", "prompts": [entry, entry]}))
    with pytest.raises(ValueError, match="repeat"):
        skill_start_eval.load_prompts(path)
