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
    run_docket_delegable,
    work,
)

FAKE_CLAUDE = """\
import json, os, subprocess, sys
open(os.environ["FAKE_RECORD"], "w").write(json.dumps({"argv": sys.argv[1:]}))
head = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
branch = subprocess.run(head, capture_output=True, text=True).stdout.strip()
subprocess.run(["git", "commit", "--allow-empty", "-qm", "work"], check=True)
subprocess.run(["git", "push", "-q", "-u", "origin", branch], capture_output=True)
if os.environ.get("FAKE_OUTPUT") == "unpushed":
    subprocess.run(["git", "commit", "--allow-empty", "-qm", "later"], check=True)
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
                      "num_turns": 12, "total_cost_usd": 3.25, "permission_denials": [],
                      "usage": {"input_tokens": 40, "cache_read_input_tokens": 9000,
                                "cache_creation_input_tokens": 700, "output_tokens": 1200}}))
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
    assert _main(["--credit-left", "50"], environ={}) == 2
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


def test_a_pushed_run_commits_its_record_to_its_branch_for_review(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    """Nothing in the repository said which items a headless worker did (`PL-87BR`)."""
    run = _work(origin, fake_claude, tmp_path, no_push=False)
    stamp = run.started[:19].replace("-", "").replace(":", "")
    assert run.record == f"docs/worker-runs/pl-b7k2-worker-{stamp}.json"
    checkout = tmp_path / "checkout"
    _git("clone", "-q", "-b", run.branch, str(origin), str(checkout), cwd=tmp_path)
    subject = _git("log", "-1", "--format=%s", cwd=checkout).strip()
    assert subject == "PL-B7K2: record the headless run"
    record = json.loads((checkout / run.record).read_text(encoding="utf-8"))
    assert record["review"] is None
    assert "clone" not in record
    assert (record["cost_usd"], record["effort"], record["turns"]) == (3.25, "high", 12)
    tokens = ("input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens")
    assert [record[name] for name in tokens] == [40, 9000, 700, 1200]
    assert f"record: {run.record}" in headless_worker.describe(run)


def test_a_record_is_not_committed_over_work_the_worker_left_unpushed(
    origin: Path, fake_claude: Path, tmp_path: Path
) -> None:
    """Pushing the record would also have published the worker's unpushed commit."""
    run = _work(origin, fake_claude, tmp_path, no_push=False, output="unpushed")
    assert run.record is None
    assert run.record_failure == "the clone's HEAD is not the branch it pushed"
    assert not run.removed
    assert "no record committed" in headless_worker.describe(run)


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


def _run(cost: float | None, reason: str | None = None) -> Run:
    return Run(
        "PL-B7K2",
        "m",
        "b",
        "c",
        "2026-10-19T00:00:00+00:00",
        "f",
        True,
        0 if reason is None else 1,
        cost,
        reason is not None,
        "success",
        1,
        0,
        reason=reason,
    )


def _main(args: list[str], items: str = "PL-B7K2\n", **overrides: object) -> int:
    """`main` with no key, tools, queue or caffeinate of this machine's."""
    common: dict[str, object] = {
        "environ": {"ANTHROPIC_API_KEY": "sk-test"},
        "tools": lambda env: None,
        "docket": lambda: items,
        "effort_level": lambda: "high",
        "awake": lambda: "awake",
    }
    return headless_worker.main(args, **{**common, **overrides})  # type: ignore[arg-type]


def _recording(started: list[str], run: Run) -> object:
    """A stand-in for `work` that notes each item it was given and returns `run`."""

    def fake_work(item: str, **_: object) -> Run:
        started.append(item)
        return run

    return fake_work


@pytest.fixture
def no_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(headless_worker, "read_git", lambda *a, **k: "origin-url\n")


def test_the_runner_will_not_start_without_the_credit_left() -> None:
    """The Console holds the credit left, so the runner never guesses it (`PL-NQ0M`)."""
    with pytest.raises(SystemExit) as refused:
        _main([])
    assert refused.value.code == 2


@pytest.mark.parametrize("figure", ["-1", "nan", "inf"])
def test_a_credit_left_that_is_not_a_dollar_amount_is_refused(figure: str) -> None:
    with pytest.raises(SystemExit) as refused:
        _main(["--credit-left", figure])
    assert refused.value.code == 2


@pytest.mark.usefixtures("no_origin")
def test_the_batch_stops_before_a_run_the_credit_cannot_cover(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(headless_worker, "work", lambda *a, **k: pytest.fail("a run started"))
    assert _main(["--credit-left", "10", "--per-run-usd", "15"]) == 0
    assert "$10.00 of credit left" in capsys.readouterr().out


@pytest.mark.usefixtures("no_origin")
def test_each_run_s_cost_comes_off_the_credit_left_before_the_next(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """$20 less a $6 run leaves $14, below the $15 cap, so the second item never starts."""
    started: list[str] = []
    monkeypatch.setattr(headless_worker, "work", _recording(started, _run(6.0)))
    args = ["--credit-left", "20", "--per-run-usd", "15", "--runs", "3"]
    assert _main(args, items="PL-B7K2\nPL-C8M3\nPL-D9N4\n") == 0
    assert started == ["PL-B7K2"]
    assert "$14.00 of credit left" in capsys.readouterr().out


@pytest.mark.usefixtures("no_origin")
def test_a_failed_run_stops_the_batch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty credit failed every later run the same way, each leaving a clone (`PL-44SP`)."""
    started: list[str] = []
    failed = _run(0.0, reason="Your credit balance is too low to access the Anthropic API.")
    monkeypatch.setattr(headless_worker, "work", _recording(started, failed))
    args = ["--credit-left", "100", "--runs", "3"]
    assert _main(args, items="PL-B7K2\nPL-C8M3\nPL-D9N4\n") == 1
    assert started == ["PL-B7K2"]
    out = capsys.readouterr().out
    assert "why: Your credit balance is too low" in out
    assert "Stopped: that run failed, with $100.00 of credit left" in out


@pytest.mark.usefixtures("no_origin")
def test_a_run_whose_cost_cannot_be_read_stops_the_batch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """With one cost unknown, the credit left is unknown, so no later run may start."""
    started: list[str] = []
    monkeypatch.setattr(headless_worker, "work", _recording(started, _run(None)))
    args = ["--credit-left", "100", "--runs", "2"]
    assert _main(args, items="PL-B7K2\nPL-C8M3\n") == 1
    assert started == ["PL-B7K2"]
    assert "cost could not be read" in capsys.readouterr().out


@pytest.mark.usefixtures("no_origin")
def test_a_batch_keeps_the_machine_awake_and_a_dry_run_does_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(headless_worker, "work", _recording([], _run(1.0)))

    def awake() -> str:
        calls.append("awake")
        return "awake"

    assert _main(["--credit-left", "100", "--dry-run"], awake=awake) == 0
    assert calls == []
    assert _main(["--credit-left", "100"], awake=awake) == 0
    assert calls == ["awake"]


def test_on_macos_caffeinate_holds_idle_sleep_off_until_the_runner_exits() -> None:
    """`-i` prevents idle sleep and `-w` ends it with this process (`PL-BT70`)."""
    started: list[list[str]] = []
    line = headless_worker.keep_awake("darwin", lambda name: f"/usr/bin/{name}", started.append)
    assert started == [["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())]]
    assert "Keep the lid open" in line


@pytest.mark.parametrize(
    ("platform", "found"), [("linux", "/usr/bin/caffeinate"), ("darwin", None)]
)
def test_without_caffeinate_the_runner_says_nothing_keeps_it_awake(
    platform: str, found: str | None
) -> None:
    started: list[list[str]] = []
    line = headless_worker.keep_awake(platform, lambda name: found, started.append)
    assert started == []
    assert line.startswith("Nothing keeps this machine awake")


def test_a_worker_runs_at_the_level_the_project_settings_hold(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every run takes the settings file's `effortLevel`, whatever its item's lane (`PL-4N0K`)."""
    settings = tmp_path / "settings.json"
    settings.write_text('{"effortLevel": "xhigh"}', encoding="utf-8")
    level = lambda: headless_worker.read_effort_level(settings)  # noqa: E731
    assert _main(["--dry-run", "--credit-left", "50"], effort_level=level) == 0
    out = capsys.readouterr().out
    assert "PL-B7K2 at xhigh effort" in out
    assert "$50.00 of credit left" in out


def test_the_project_settings_set_high_for_every_run() -> None:
    """The owner set `high` for all work on 2026-10-19 (`PL-6XZG`, `docs/maintainer.md`)."""
    assert headless_worker.read_effort_level() == "high"


def test_a_settings_file_with_no_effort_level_is_refused_before_any_spend(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")
    level = lambda: headless_worker.read_effort_level(settings)  # noqa: E731
    assert _main(["--dry-run", "--credit-left", "50"], effort_level=level) == 2


def test_an_item_the_queue_does_not_offer_is_refused() -> None:
    with pytest.raises(Refused, match="PL-ZZZZ"):
        choose(["PL-B7K2"], ["PL-ZZZZ"], 1)


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
