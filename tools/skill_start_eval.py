"""Measure whether a skill starts on the requests it should, in fresh headless sessions.

`PL-SN2Z` asks whether a procedure can leave the always-loaded instructions for
a skill and still be followed. That depends on Claude starting the skill when
the procedure's moment comes, with only a trigger sentence always loaded. The
`docket` skill is already in that shape: `CLAUDE.md` says to invoke it for any
queue workflow, and its body loads only when it starts. So this script measures
the `docket` skill, and its answer is the evidence `PL-S2NL` and `PL-Z90G` wait
on.

**Method.** The Claude Code skills page, § "Evaluate and iterate on a skill"
(https://code.claude.com/docs/en/skills, read 2026-10-24), says to run each
realistic prompt in a fresh session with the skill available, and again with it
turned off through `skillOverrides`. `tools/skill_start_prompts.json` holds the
prompts in two groups: requests that should start the skill and requests that
should not. Each prompt runs once with the skill on. A prompt that should start
it runs again with the skill off. That second run shows what the always-loaded
instructions do without the skill. An off run of a prompt that should not
start the skill cannot show anything, so it is not made.

**Each run may read but not act.** It runs in `dontAsk` mode with nobody to
answer a permission prompt, so any tool call that would need approval is
refused. A session in auto mode would act on the checkout and could reach
GitHub, and this question needs only the session's choice of tool. A refused
call still appears in the output, so a session that tries `bin/docket` first is
still seen trying it. Run it in a scratch clone with pushing disabled all the
same, never in the working tree:

    git clone https://github.com/stuthedew/open-anesthesia-sim /tmp/skill-eval
    git -C /tmp/skill-eval remote set-url --push origin no-push
    python3 tools/skill_start_eval.py --checkout /tmp/skill-eval \\
        --model claude-opus-5-5 --out /tmp/skill-eval.jsonl

`--model` has no default, so a run never falls back to whatever model the
account would choose. Pass the model the project's sessions run. Effort comes
from the clone's `.claude/settings.json`, as it does for a real session.

**What counts as a start.** A `Skill` tool call that names the skill, made
within the first `--max-turns` model requests. Two other signals are recorded
beside it and never counted as a start. `listed` says whether the session's
`init` event listed the skill, which is how a run shows that the off arm really
hid it. `read_skill_file` is a tool call whose input names a path under
`.claude/skills/<skill>/`. `ran_docket` is a Bash call that runs a `bin/docket`
command other than `branch`, which shows the queue workflow began even without
the skill. `branch` is left out because every reply runs it before its closing
block, as rule 14 of `.claude/rules/instruction-writing.md` requires.
`denied` names each tool call that `dontAsk` mode refused.

**What it refuses to guess.** A run that timed out, ended without a result, or
printed a line that is not JSON is marked `unread`, with the reason. It is left
out of every rate and counted on its own line. Counting it as "did not start"
would turn a failure to measure into a measurement.

**Cost.** Every run is a real model call billed to the account that the
clone's `claude` signs in with. In a cloud session that is the owner's
subscription, whatever key is set
(https://code.claude.com/docs/en/authentication, "Authentication precedence").
The result line of each run carries its cost, and the summary adds them up.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools" / "skill_start_prompts.json"
DOCKET_COMMAND = re.compile(r"bin/docket\s+([\w-]+)")


@dataclass(frozen=True)
class Prompt:
    id: str
    prompt: str
    should_start: bool


@dataclass(frozen=True)
class Run:
    """What one headless session did with one prompt, or why that is unknown."""

    prompt_id: str
    arm: str
    should_start: bool
    started: bool | None
    listed: bool | None
    read_skill_file: bool | None
    ran_docket: bool | None
    tool_calls: tuple[str, ...]
    denied: tuple[str, ...]
    cost_usd: float | None
    unread: str


def load_prompts(path: Path) -> tuple[str, list[Prompt]]:
    """Return the skill under test and its prompts, refusing a malformed file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    prompts = [Prompt(p["id"], p["prompt"], bool(p["should_start"])) for p in data["prompts"]]
    ids = [p.id for p in prompts]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{path}: prompt ids repeat")
    return data["skill"], prompts


def tool_uses(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return every tool call the session made, in order."""
    calls: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                calls.append(block)
    return calls


def is_skill_call(call: dict[str, Any], skill: str) -> bool:
    """Return whether a tool call starts `skill` through the Skill tool."""
    if call.get("name") != "Skill":
        return False
    name = str(call.get("input", {}).get("skill", ""))
    return name.lstrip("/").split(":")[-1] == skill


def classify(stream: str, skill: str, prompt: Prompt, arm: str) -> Run:
    """Read one session's stream-json output into a `Run`."""
    events: list[dict[str, Any]] = []
    bad = 0
    for line in stream.split("\n"):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    result = next((e for e in events if e.get("type") == "result"), None)
    unread = ""
    if bad:
        unread = f"{bad} output line(s) were not JSON"
    elif result is None:
        unread = "the session ended without a result"
    elif result.get("subtype") not in ("success", "error_max_turns"):
        unread = f"the session ended with {result.get('subtype')}"
    if unread or result is None:
        return Run(
            prompt.id, arm, prompt.should_start, None, None, None, None, (), (), None, unread
        )
    calls = tool_uses(events)
    init: dict[str, Any] = next((e for e in events if e.get("subtype") == "init"), {})
    skills = init.get("skills")
    skill_dir = f".claude/skills/{skill}/"
    return Run(
        prompt_id=prompt.id,
        arm=arm,
        should_start=prompt.should_start,
        started=any(is_skill_call(c, skill) for c in calls),
        listed=None if skills is None else skill in skills,
        read_skill_file=any(
            c.get("name") != "Skill" and skill_dir in json.dumps(c.get("input", {})) for c in calls
        ),
        ran_docket=any(
            name != "branch"
            for c in calls
            if c.get("name") == "Bash"
            for name in DOCKET_COMMAND.findall(str(c.get("input", {}).get("command", "")))
        ),
        tool_calls=tuple(str(c.get("name")) for c in calls),
        denied=tuple(str(d.get("tool_name")) for d in result.get("permission_denials", [])),
        cost_usd=result.get("total_cost_usd"),
        unread="",
    )


def command(prompt: Prompt, skill: str, arm: str, model: str, max_turns: int) -> list[str]:
    """Return the `claude` command line for one run."""
    argv = [
        "claude",
        "-p",
        prompt.prompt,
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(max_turns),
        "--permission-mode",
        "dontAsk",
        "--permission-prompts",
        "none",
        "--session-id",
        str(uuid.uuid4()),
    ]
    if arm == "off":
        argv += ["--settings", json.dumps({"skillOverrides": {skill: "off"}})]
    return argv


def plan(prompts: list[Prompt]) -> list[tuple[Prompt, str]]:
    """Return each run to make: every prompt with the skill on, and should-start ones off."""
    runs = [(p, "on") for p in prompts]
    runs += [(p, "off") for p in prompts if p.should_start]
    return runs


def summary(runs: list[Run]) -> list[str]:
    """Return the lines that state each group's start rate and every miss."""
    lines = []
    for should_start, arm in ((True, "on"), (False, "on"), (True, "off")):
        group = [r for r in runs if r.should_start == should_start and r.arm == arm]
        if not group:
            continue
        read = [r for r in group if not r.unread]
        started = sum(bool(r.started) for r in read)
        listed = sum(bool(r.listed) for r in read)
        file_read = sum(bool(r.read_skill_file) for r in read)
        docket = sum(bool(r.ran_docket) for r in read)
        label = "should start" if should_start else "should not start"
        lines.append(
            f"{label}, skill {arm}: started {started} of {len(read)}, listed in {listed}, "
            f"read a skill file {file_read}, ran bin/docket {docket}"
            + (f"; {len(group) - len(read)} unread" if len(read) < len(group) else "")
        )
    misses = [r.prompt_id for r in runs if r.arm == "on" and r.should_start and r.started is False]
    false_starts = [r.prompt_id for r in runs if r.arm == "on" and not r.should_start and r.started]
    lines.append("missed: " + (", ".join(misses) or "none"))
    lines.append("started when it should not: " + (", ".join(false_starts) or "none"))
    for r in runs:
        if r.unread:
            lines.append(f"unread: {r.prompt_id} ({r.arm}): {r.unread}")
    costs = [r.cost_usd for r in runs if r.cost_usd is not None]
    lines.append(
        f"cost at list price: ${sum(costs):.2f} over {len(costs)} run(s) that reported one"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--checkout", type=Path, required=True, help="a scratch clone to run in")
    parser.add_argument("--model", required=True, help="the model the project's sessions run")
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="JSON lines, one per run; each run's raw stream is written beside it",
    )
    parser.add_argument("--max-turns", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=600, help="seconds per run")
    parser.add_argument("--only", action="append", default=[], help="run only this prompt id")
    args = parser.parse_args(argv)

    if args.checkout.resolve() == ROOT:
        print("refusing to run in the working tree; pass a scratch clone", file=sys.stderr)
        return 2
    skill, prompts = load_prompts(PROMPTS)
    if args.only:
        prompts = [p for p in prompts if p.id in args.only]
    runs = []
    for prompt, arm in plan(prompts):
        argv_ = command(prompt, skill, arm, args.model, args.max_turns)
        try:
            done = subprocess.run(
                argv_, cwd=args.checkout, capture_output=True, timeout=args.timeout
            )
            run = classify(done.stdout.decode("utf-8", errors="replace"), skill, prompt, arm)
            raw = args.out.with_name(f"{args.out.stem}.{prompt.id}.{arm}.stream.jsonl")
            raw.write_bytes(done.stdout)
        except subprocess.TimeoutExpired:
            run = Run(
                prompt.id,
                arm,
                prompt.should_start,
                None,
                None,
                None,
                None,
                (),
                (),
                None,
                "timed out",
            )
        runs.append(run)
        with args.out.open("a", encoding="utf-8") as out:
            out.write(json.dumps(asdict(run) | {"prompt": prompt.prompt}) + "\n")
        print(f"{prompt.id} ({arm}): started={run.started} {run.unread}", flush=True)
    print("\n".join(summary(runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
