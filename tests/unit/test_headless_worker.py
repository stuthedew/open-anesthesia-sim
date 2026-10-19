"""Tests for `tools/headless_worker.py`, the runner that spends the API credit on the queue.

No session holds an API key, so each run here starts a fake `claude`: a script
that records what it was given, tries to push as a worker would, and prints a
result in the shape `--output-format json` gives.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import headless_worker
import pytest
from docket.lines import split_lines
from docket.store import ID_RE
from headless_worker import (
    NO_PUSH_URL,
    OUTRANKING_CREDENTIALS,
    OUTRANKING_EFFORT,
    Refused,
    Run,
    check_tools,
    child_environment,
    choose,
    cycle_start,
    run_docket_delegable,
    spent_since,
    work,
)

FAKE_CLAUDE = """\
import json, os, subprocess, sys
open(os.environ["FAKE_RECORD"], "w").write(json.dumps({"argv": sys.argv[1:]}))
head = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
branch = subprocess.run(head, capture_output=True, text=True).stdout.strip()
subprocess.run(["git", "commit", "--allow-empty", "-qm", "work"], check=True)
subprocess.run(["git", "push", "-q", "-u", "origin", branch], capture_output=True)
if os.environ.get("FAKE_OUTPUT") == "dirty":
    open("left-behind.txt", "w").write("not committed")
if os.environ.get("FAKE_OUTPUT") == "refused":
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True,
                      "result": "Invalid API key", "total_cost_usd": 0, "num_turns": 1}))
    sys.exit(1)
if os.environ.get("FAKE_OUTPUT") == "junk":
    print("not json")
else:
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False,
                      "num_turns": 12, "total_cost_usd": 3.25, "permission_denials": []}))
"""


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def origin(tmp_path: Path) -> Path:
    """A bare remote with one commit on its default branch."""
    remote = tmp_path / "origin.git"
    _git("init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp_path)
    seed = tmp_path / "seed"
    _git("init", "-q", "-b", "main", str(seed), cwd=tmp_path)
    _git(
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "--allow-empty",
        "-qm",
        "seed",
        cwd=seed,
    )
    _git("push", "-q", str(remote), "main", cwd=seed)
    return remote


@pytest.fixture
def fake_claude(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An executable standing in for `claude`, and the file it records into."""
    script = tmp_path / "claude"
    script.write_text(f"#!{sys.executable}\n{FAKE_CLAUDE}", encoding="utf-8")
    script.chmod(0o755)
    for name, value in (
        ("GIT_AUTHOR_NAME", "t"),
        ("GIT_AUTHOR_EMAIL", "t@t"),
        ("GIT_COMMITTER_NAME", "t"),
        ("GIT_COMMITTER_EMAIL", "t@t"),
    ):
        monkeypatch.setenv(name, value)
    return script


def _work(
    origin: Path, fake_claude: Path, tmp_path: Path, *, no_push: bool, output: str = "json"
) -> Run:
    env = {
        "PATH": "/usr/bin:/bin",
        "ANTHROPIC_API_KEY": "sk-test",
        "FAKE_RECORD": str(tmp_path / "record.json"),
        "FAKE_OUTPUT": output,
        **{k: v for k, v in os.environ.items() if k.startswith("GIT_")},
    }
    return work(
        "PL-B7K2",
        model="claude-sonnet-5-5",
        effort="high",
        per_run_usd=15.0,
        no_push=no_push,
        origin=str(origin),
        workdir=tmp_path / "workers",
        claude=str(fake_claude),
        env=env,
    )


def test_a_run_without_an_api_key_is_refused(capsys: pytest.CaptureFixture[str]) -> None:
    """Without a key the run would bill the subscription, so nothing starts."""
    assert headless_worker.main([], environ={}, docket=lambda: "PL-B7K2\n") == 2
    assert "ANTHROPIC_API_KEY is not set" in capsys.readouterr().err


def test_the_child_environment_drops_every_credential_that_outranks_the_key() -> None:
    environ = {
        "ANTHROPIC_API_KEY": "sk-test",
        "HOME": "/h",
        **dict.fromkeys(OUTRANKING_CREDENTIALS, "1"),
        **dict.fromkeys(OUTRANKING_EFFORT, "low"),
    }
    assert child_environment(environ) == {"ANTHROPIC_API_KEY": "sk-test", "HOME": "/h"}


def test_a_no_push_clone_cannot_push_even_when_the_worker_tries(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    """The trial's cheaper runs must never leave the machine, whatever the worker does."""
    run = _work(origin, fake_claude, tmp_path, no_push=True)
    assert not run.pushed
    assert not _git("ls-remote", "--heads", str(origin), run.branch, cwd=tmp_path).strip()
    assert _git("remote", "get-url", "--push", "origin", cwd=Path(run.clone)).strip() == NO_PUSH_URL
    assert run.branch == "claude/pl-b7k2-worker-sonnet"


def test_a_pushed_run_records_its_cost_and_the_remote_branch(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    run = _work(origin, fake_claude, tmp_path, no_push=False)
    assert run.pushed
    assert (run.cost_usd, run.turns, run.denials, run.is_error) == (3.25, 12, 0, False)
    record = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    argv = record["argv"]
    assert argv[argv.index("--model") + 1] == "claude-sonnet-5-5"
    assert argv[argv.index("--effort") + 1] == "high"
    assert argv[argv.index("--max-budget-usd") + 1] == "15.00"
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "PL-B7K2" in argv[argv.index("-p") + 1]


@pytest.mark.parametrize(
    ("no_push", "output", "removed"),
    [
        (False, "json", True),
        (True, "json", False),
        (False, "refused", False),
        (False, "dirty", False),
    ],
    ids=["pushed", "trial-run", "failed-after-pushing", "uncommitted-file"],
)
def test_a_pushed_run_removes_its_clone_and_a_failed_run_keeps_it(
    origin: Path, fake_claude: Path, tmp_path: Path, no_push: bool, output: str, removed: bool
) -> None:
    """Every run used to leave a full clone behind until the owner deleted it (`PL-TX7K`).

    Only a run that succeeded and pushed everything it made removes its clone.
    A trial run, a failure and a clone holding a file the remote lacks are kept
    for reading. Every run keeps its log.
    """
    run = _work(origin, fake_claude, tmp_path, no_push=no_push, output=output)
    assert run.removed is removed
    assert Path(run.clone).is_dir() is not removed
    assert Path(run.clone + ".log").is_file()
    line = headless_worker.describe(run)
    kept = f"in {run.clone}, log in {run.clone}.log"
    assert ("clone removed, log in" in line, kept in line) == (removed, not removed)


def test_a_checkout_that_is_a_linked_worktree_can_still_clone(
    origin: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A worktree's `.git` is a file, which `git clone --reference` refused (`PL-29DJ`)."""
    checkout = tmp_path / "checkout"
    _git("clone", "-q", str(origin), str(checkout), cwd=tmp_path)
    worktree = tmp_path / "worktree"
    _git("worktree", "add", "-q", "--detach", str(worktree), cwd=checkout)
    monkeypatch.setattr(headless_worker, "ROOT", worktree)
    clone = tmp_path / "workers" / "run"
    headless_worker.prepare_clone(str(origin), clone, "claude/pl-b7k2-worker", no_push=True)
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=clone).strip() == "claude/pl-b7k2-worker"


def test_output_that_is_not_a_result_records_no_cost(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    assert _work(origin, fake_claude, tmp_path, no_push=True, output="junk").cost_usd is None


def _ledger(path: Path, *costs: float | None, started: str = "2026-10-05T12:00:00+00:00") -> Path:
    lines = [
        json.dumps({"item": "PL-B7K2", "started": started, "cost_usd": cost}) for cost in costs
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(cost: float | None) -> Run:
    return Run(
        "PL-B7K2",
        "m",
        "b",
        "c",
        "2026-10-19T00:00:00+00:00",
        "f",
        True,
        0,
        cost,
        False,
        "success",
        1,
        0,
    )


def test_the_batch_stops_before_a_run_the_credit_cannot_cover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = _ledger(tmp_path / "ledger.jsonl", 120.0, 70.0)
    monkeypatch.setattr(headless_worker, "read_git", lambda *a, **k: "origin-url\n")
    monkeypatch.setattr(headless_worker, "work", lambda *a, **k: pytest.fail("a run started"))
    code = headless_worker.main(
        ["--ledger", str(ledger), "--per-run-usd", "15"],
        environ={"ANTHROPIC_API_KEY": "sk-test"},
        tools=lambda env: None,
        docket=lambda: "PL-B7K2\n",
        lanes=lambda: {"PL-B7K2": "workflow"},
        today=lambda: date(2026, 10, 19),
    )
    assert code == 0
    assert "$10.00 of credit left" in capsys.readouterr().out


def test_a_run_whose_cost_cannot_be_read_stops_the_batch_and_the_next_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """With one cost unknown, the credit left is unknown, so no later run may start."""
    ledger = tmp_path / "ledger.jsonl"
    started: list[str] = []
    monkeypatch.setattr(headless_worker, "read_git", lambda *a, **k: "origin-url\n")
    monkeypatch.setattr(
        headless_worker, "work", lambda item, **k: started.append(item) or _run(None)
    )
    args = ["--ledger", str(ledger), "--runs", "2"]
    common = {
        "environ": {"ANTHROPIC_API_KEY": "sk-test"},
        "tools": lambda env: None,
        "docket": lambda: "PL-B7K2\nPL-C8M3\n",
        "lanes": lambda: {"PL-B7K2": "workflow", "PL-C8M3": "product"},
        "today": lambda: date(2026, 10, 19),
    }
    assert headless_worker.main(args, **common) == 1
    assert started == ["PL-B7K2"]
    assert headless_worker.main(args, **common) == 2
    assert "cost could not be read" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("lane", "effort"), [("product", "max"), ("crossing", "max"), ("workflow", "high")]
)
def test_a_worker_runs_at_the_effort_the_owner_chose_for_its_lane(
    lane: str, effort: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Simulator work runs at `max`, apparatus work at `high`, never the default (`PL-KFJY`)."""
    code = headless_worker.main(
        ["--dry-run", "--ledger", str(tmp_path / "ledger.jsonl")],
        environ={"ANTHROPIC_API_KEY": "sk-test"},
        tools=lambda env: None,
        docket=lambda: "PL-B7K2\n",
        lanes=lambda: {"PL-B7K2": lane},
        today=lambda: date(2026, 10, 19),
    )
    assert code == 0
    assert f"PL-B7K2 at {effort} effort" in capsys.readouterr().out


def test_an_item_docket_gives_no_lane_is_refused_before_any_spend(tmp_path: Path) -> None:
    code = headless_worker.main(
        ["--dry-run", "--ledger", str(tmp_path / "ledger.jsonl")],
        environ={"ANTHROPIC_API_KEY": "sk-test"},
        tools=lambda env: None,
        docket=lambda: "PL-B7K2\n",
        lanes=lambda: {},
        today=lambda: date(2026, 10, 19),
    )
    assert code == 2


def test_spend_counts_only_the_current_cycle(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path / "l.jsonl", 50.0, started="2026-09-30T23:00:00+00:00")
    with ledger.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"item": "x", "started": "2026-10-01T00:30:00+00:00", "cost_usd": 4.0})
            + "\n"
        )
    assert spent_since(ledger, date(2026, 10, 1)) == 4.0


@pytest.mark.parametrize(
    ("today", "day", "start"),
    [
        (date(2026, 10, 19), 1, date(2026, 10, 1)),
        (date(2026, 10, 19), 25, date(2026, 9, 25)),
        (date(2026, 1, 5), 10, date(2025, 12, 10)),
    ],
)
def test_cycle_start(today: date, day: int, start: date) -> None:
    assert cycle_start(today, day) == start


def test_an_item_the_queue_does_not_offer_is_refused() -> None:
    with pytest.raises(Refused, match="PL-ZZZZ"):
        choose(["PL-B7K2"], ["PL-ZZZZ"], 1)


def test_run_lines_are_json_the_ledger_reads_back(tmp_path: Path) -> None:
    ledger = tmp_path / "l.jsonl"
    ledger.write_text(_run(2.5).line() + "\n", encoding="utf-8")
    assert spent_since(ledger, datetime(2026, 10, 1, tzinfo=UTC).date()) == 2.5


@pytest.mark.reads_item_store
def test_the_delegable_list_is_read_without_the_bash_launcher() -> None:
    """`bin/docket` is a bash script, so starting it with Python failed (`PL-W38C`)."""
    ids = split_lines(run_docket_delegable())
    assert all(ID_RE.fullmatch(line) for line in ids if line)


def _path_with(tmp_path: Path, scripts: dict[str, str]) -> str:
    for name, body in scripts.items():
        script = tmp_path / name
        script.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        script.chmod(0o755)
    return str(tmp_path)


def test_a_python3_older_than_the_tools_floor_is_refused_before_any_spend(tmp_path: Path) -> None:
    """Xcode's 3.9 was first on the owner's PATH, and bin/docket cannot run under it."""
    path = _path_with(tmp_path, {"claude": "exit 0", "uv": "exit 0", "python3": "exit 1"})
    with pytest.raises(Refused, match="older than Python 3.11"):
        check_tools({"PATH": path})


def test_a_missing_claude_is_refused_by_name(tmp_path: Path) -> None:
    path = _path_with(tmp_path, {"uv": "exit 0", "python3": "exit 0"})
    with pytest.raises(Refused, match="claude"):
        check_tools({"PATH": path})


def test_a_failed_run_says_why_and_keeps_its_output(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    """The first real run printed only "error, $0.00", with no reason (`PL-MZCN`)."""
    run = _work(origin, fake_claude, tmp_path, no_push=True, output="refused")
    assert run.reason == "Invalid API key"
    assert "why: Invalid API key" in headless_worker.describe(run)
    assert b"Invalid API key" in Path(run.clone + ".log").read_bytes()


def test_a_run_that_succeeded_has_no_reason(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    assert _work(origin, fake_claude, tmp_path, no_push=True).reason is None
