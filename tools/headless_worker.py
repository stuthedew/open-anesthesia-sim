"""Work delegable queue items headless, one per run, on the monthly API credit.

Max 20x carries $200 a month of Claude Platform API credit, which pays for
`claude -p` only when it runs with an API key from the linked Console
organization, and expires unused at the end of each billing cycle
(https://support.claude.com/en/articles/17154008, read 2026-10-19). This
script spends it on the queue (`PL-80R5`). For each item it clones the
repository, makes a branch named for the item, and starts one `claude -p`
run that follows `docs/worker.md` on that one item.

It runs on the project owner's machine, never in a cloud session: cloud
sessions bill the subscription whatever key is set
(https://code.claude.com/docs/en/authentication, "Authentication precedence").

**Why not `--bare`.** Bare mode reads only `ANTHROPIC_API_KEY`, so it would
make the billing certain, but it also skips `CLAUDE.md`, the skills and the
hooks, and the hooks are part of what makes a worker safe here. Without it,
the docs' precedence list decides the credential, and under `-p` "the key is
always used when present" (same page, read 2026-10-19). Only cloud-provider
selection and `ANTHROPIC_AUTH_TOKEN` rank above the key, so the child's
environment drops `OUTRANKING_CREDENTIALS` and the run is refused when no key
is set. A signed-in Claude apps gateway session also outranks every
credential; the owner's machine has none, and nothing here can detect one.

**What a run is trusted with.** It runs in auto mode with permission prompts
denied (`--permission-mode auto --permission-prompts none`), so nothing waits
on a person and the classifier still reviews each action. Where auto mode is
unavailable, as for a model that does not support it, Claude Code starts in
Manual instead and every prompt is denied; the `denials` count in the run's
record and its log shows that
(https://code.claude.com/docs/en/permission-modes, read 2026-10-19).

**The model and effort come from the project's one table.** Each run asks
`docket.toml`'s `[models]` table for the model and effort of its item, with
the role `worker`, and passes them as `--model` and `--effort` (`PL-0XDM`). So
the runner keeps no model or level of its own to fall out of step with the
sessions' (`PL-4N0K`). Without `--effort` every run took Opus 5.5's default,
`medium` (`PL-KFJY`). `--model` still overrides the model for one batch, as a
trial needs.

**`--no-push` is enforced, not asked for.** `PL-6FX6`'s trial runs Sonnet and
Haiku copies of an item whose work must never leave the machine. The clone's
push URL is set to a name no remote answers to, so a push fails whatever the
worker does.

**A pushed run commits its record to its branch.** After a run whose branch
reached the remote, the runner writes the run's record with
`tools/worker_runs.py`, commits it as `<id>: record the headless run` and
pushes it. The reviewing session adds the review's outcome, and `make check`
fails until it does, so the repository says which items a headless worker did
and how their reviews went (`PL-87BR`). The record is committed only where the
clone's `HEAD` is the pushed branch, so nothing the worker left unpushed is
published with it.

**A clone is removed once nothing in it is only on this machine.** A run
that succeeded and pushed its branch, where the remote's branch is the
clone's `HEAD` and the clone has nothing uncommitted, removes its clone and
keeps its log. Every other run keeps both, so a failure can be read where it
happened, and the report line names the clone (`PL-TX7K`). Each clone is a
full copy of the repository, so keeping every one filled the owner's disk.

**The credit left comes from the Console, typed in at each launch.** The
runner refuses to start without `--credit-left`, the figure the Console's
billing page shows. During the batch it subtracts each finished run's
reported cost from that figure, and it stops before a run that the rest
cannot cover. Nothing stores spend between launches, so the Console stays the
only record of it. This account cannot read the Console's Cost API, so the
owner reads the figure (project owner, 2026-10-20, ratified, over a ledger on
this machine, `PL-NQ0M`).

The cost is `total_cost_usd` from `--output-format json`, which Claude Code
calls a client-side estimate that can differ from the bill
(https://code.claude.com/docs/en/headless). A run whose cost could not be read
stops the batch, because the remaining credit is then unknown.

**Any failed run stops the batch.** An empty credit, a lost connection and a
Mac that slept each fail the next run the same way, so carrying on would
start and fail every item left, each leaving a clone behind. A failure that is
one item's own still wants a person to look before more credit is spent
(`PL-44SP`).

**On macOS the runner keeps the Mac awake.** It starts `caffeinate -i -w` with
its own process id. `-i` prevents idle sleep, and `-w` releases that when the
runner exits (caffeinate(8), mirrored at
https://www.sudo.is/docs/macos/man_caffeinate.html, read 2026-10-20). The
manual does not say that this holds when the lid is closed, so the runner says
to keep it open. Off macOS it says that nothing keeps the machine awake
(`PL-BT70`).

Standard library only, like every tool under `tools/`. It reads git through
`docket.vcs` and the delegable list through `bin/docket delegable --ids`, the
one place that list is computed.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

import docket.cli as docket_cli  # noqa: E402
from docket.checks import WORKER_ITEM_ENV  # noqa: E402
from docket.config import load as load_config  # noqa: E402
from docket.lines import record_text, split_lines  # noqa: E402
from docket.model_choice import Choice, item_facts  # noqa: E402
from docket.shell import BASH_FLOOR  # noqa: E402
from docket.store import read_items  # noqa: E402
from docket.vcs import REMOTE, call_git, default_base, read_git  # noqa: E402

sys.path.insert(0, str(ROOT / "tools"))

import worker_runs  # noqa: E402
from doc_check import GNU_MAKE_FLOOR  # noqa: E402
from open_pull_requests import origin_url  # noqa: E402

#: Variables Claude Code ranks above `--effort`, so a run that inherited one
#: would not run at the level chosen for it
#: (https://code.claude.com/docs/en/env-vars, `CLAUDE_CODE_EFFORT_LEVEL`).
OUTRANKING_EFFORT = ("CLAUDE_CODE_EFFORT_LEVEL",)

#: The credentials Claude Code ranks above `ANTHROPIC_API_KEY`, so a run that
#: inherited one would not bill the API credit
#: (https://code.claude.com/docs/en/authentication, "Authentication precedence").
OUTRANKING_CREDENTIALS = (
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_AUTH_TOKEN",
)

#: The push URL a `--no-push` clone gets: git refuses it as a repository.
NO_PUSH_URL = "no-push-trial-run"

#: How long one run may take before it is stopped and recorded as failed.
RUN_TIMEOUT_S = 3 * 60 * 60

#: How long a clone may take.
CLONE_TIMEOUT_S = 15 * 60

STATE_DIR = Path.home() / ".local" / "state" / "open-anesthesia-sim"


class Refused(Exception):
    """A reason this script will not start, or will not start another run."""


@dataclass(frozen=True)
class Run:
    """One headless run's outcome, as Claude Code reported it."""

    item: str
    model: str
    branch: str
    clone: str
    started: str
    finished: str
    pushed: bool
    exit_code: int | None
    cost_usd: float | None
    is_error: bool | None
    subtype: str | None
    turns: int | None
    denials: int | None
    #: Why a run failed, in Claude Code's words or its last line of stderr.
    reason: str | None = None
    #: Whether the clone was removed because everything in it was pushed.
    removed: bool = False
    #: The effort level the run was started at.
    effort: str | None = None
    #: The token counts from the result's `usage`, as Claude Code reported them.
    input_tokens: int | None = None
    cache_read_tokens: int | None = None
    cache_write_tokens: int | None = None
    output_tokens: int | None = None
    #: The record committed to the branch, as a path in the repository.
    record: str | None = None
    #: Why a pushed run's record could not be committed and pushed.
    record_failure: str | None = None


def child_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """The run's environment: this one, less any credential that outranks the key.

    It also drops any effort setting that outranks `--effort`. Refuses when no
    API key is set, because the run would then bill the subscription login
    instead of the credit.
    """
    if not environ.get("ANTHROPIC_API_KEY", "").strip():
        raise Refused(
            "ANTHROPIC_API_KEY is not set. Without it the run would bill the "
            "subscription, not the API credit. Create a key in the Console "
            "organization linked to the credit and export it first."
        )
    dropped = (*OUTRANKING_CREDENTIALS, *OUTRANKING_EFFORT)
    return {key: value for key, value in environ.items() if key not in dropped}


def delegable_ids(docket: Callable[[], str]) -> list[str]:
    """The ids `bin/docket delegable --ids` offers, best-first."""
    return [line.strip() for line in split_lines(docket()) if line.strip()]


def run_docket_delegable() -> str:
    """`docket delegable --ids`'s output, or `Refused` when it fails.

    Run in this process rather than through `bin/docket`, which starts
    whatever `python3` is first on `PATH`. On the owner's Mac that was Xcode's
    3.9, below the 3.11 every tool here needs (`PL-W38C`).
    """
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = docket_cli.main(["delegable", "--ids"])
    if code:
        raise Refused(f"docket delegable --ids exited {code}; its reason is above.")
    return out.getvalue()


def role_choice(role: str, root: Path = ROOT) -> Choice:
    """The model and effort `docket.toml`'s `[models]` table chooses for `role`.

    Raises:
        Refused: the file has no `[models]` table, so no model is chosen and a
            run would silently take the account's default.
    """
    table = load_config(root).models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen.")
    return table.choose({"role": role})


def worker_choices(items: Sequence[str], root: Path = ROOT) -> dict[str, Choice]:
    """The model and effort the `[models]` table chooses for each item a worker runs.

    The table sees each item's own facts, such as its classes and areas, with
    the role `worker` in place of `delegable`. An item the store does not hold
    is asked with the role alone.

    Raises:
        Refused: the file has no `[models]` table.
    """
    config = load_config(root)
    table = config.models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen.")
    held = {item.identifier: item for item in read_items(root / config.items_dir)}
    chosen: dict[str, Choice] = {}
    for identifier in items:
        found = held.get(identifier)
        facts = item_facts(found, table, config.workflow_paths, delegable=True) if found else {}
        facts["role"] = "worker"
        chosen[identifier] = table.choose(facts)
    return chosen


#: Where `docs/maintainer.md` says how to install the bash and make a worker needs.
TOOLS_SECTION = 'docs/maintainer.md § "Spend the monthly API credit on delegable items"'


def tool_version(argv: Sequence[str], prefix: str) -> tuple[int, int] | None:
    """The major and minor version that `argv` prints after `prefix`, or None.

    None means the command could not run or printed no version after `prefix`.
    """
    try:
        done = subprocess.run(list(argv), capture_output=True, check=False, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    text = record_text(done.stdout).strip()
    if not text.startswith(prefix):
        return None
    found = re.match(r"(\d+)\.(\d+)", text[len(prefix) :])
    return (int(found[1]), int(found[2])) if found else None


def _refuse_older(
    path: str, name: str, version: tuple[int, int] | None, floor: tuple[int, int]
) -> None:
    """Refuse a run whose `name` at `path` is older than `floor` or prints no version."""
    wanted = ".".join(map(str, floor))
    if version is None:
        raise Refused(
            f"{path} printed no {name} version, and make check needs {name} {wanted} "
            f"or newer. Install it as {TOOLS_SECTION} says."
        )
    if version < floor:
        shown = ".".join(map(str, version))
        raise Refused(
            f"{path} is {name} {shown}, older than the {name} {wanted} that make check "
            f"needs, so every run would report a red gate. Install a newer one as "
            f"{TOOLS_SECTION} says, and put it first on PATH."
        )


def check_tools(env: Mapping[str, str]) -> None:
    """Refuse before any spend when a run would fail on a missing or old tool.

    A worker runs `claude`, `uv` and the bare `python3` that `bin/docket` and
    the hooks start, all from the run's `PATH`. A `python3` older than 3.11
    fails on its first `bin/docket` call, after the run has started paying.
    A worker also runs `make check`, whose tests compare the readers with the
    bash and GNU make on `PATH`. An older bash or make fails those tests on
    every run, so the worker cannot tell its own failures from the host's
    (`PL-TSH9`, `PL-44R1`).
    """
    path = env.get("PATH", "")
    missing = [
        name
        for name in ("claude", "uv", "python3", "bash", "make")
        if shutil.which(name, path=path) is None
    ]
    if missing:
        raise Refused(f"not found on PATH: {', '.join(missing)}. Install them first.")
    python3 = shutil.which("python3", path=path)
    floor = subprocess.run(
        [str(python3), "-c", "import sys; sys.exit(sys.version_info < (3, 11))"],
        capture_output=True,
        check=False,
    )
    if floor.returncode:
        raise Refused(
            f"{python3} is older than Python 3.11, which bin/docket and the hooks need. "
            "Start the runner with `uv run python tools/headless_worker.py`, which puts "
            "the project's Python first on PATH."
        )
    bash = str(shutil.which("bash", path=path))
    _refuse_older(bash, "bash", tool_version([bash, "-c", "echo $BASH_VERSION"], ""), BASH_FLOOR)
    make = str(shutil.which("make", path=path))
    _refuse_older(make, "GNU make", tool_version([make, "--version"], "GNU Make "), GNU_MAKE_FLOOR)


def choose(offered: Sequence[str], asked: Sequence[str], runs: int) -> list[str]:
    """The items to run: those asked for, each of which must be offered, or the first `runs`."""
    if not asked:
        return list(offered[:runs])
    refused = [item for item in asked if item not in offered]
    if refused:
        raise Refused(
            f"not delegable now: {', '.join(refused)}. Only what "
            "`bin/docket delegable` lists may go to a worker."
        )
    return list(asked)


def branch_for(item: str, model: str, no_push: bool) -> str:
    """The run's branch, named for its item so every in-flight guard can see it."""
    name = f"claude/{item.lower()}-worker"
    if no_push:
        # Trial copies of one item on several models each need their own name.
        name += "-" + model.removeprefix("claude-").split("-")[0]
    return name


def prompt_for(item: str, branch: str, no_push: bool) -> str:
    """The instruction one run starts from."""
    ending = (
        "Do not push. This is a trial run: its work is scored and then "
        "discarded, and this clone cannot push."
        if no_push
        else f"When the item is committed, push with `git push -u {REMOTE} {branch}`. "
        "Do not open a pull request."
    )
    return (
        "You are a worker on this repository, running headless: nobody can answer "
        "a question during this run. Read docs/worker.md in full before your first "
        f"edit, and follow it. Your list is one item, {item}; its brief is the file "
        f"in docs/items/ whose name starts with {item}. You are already on branch "
        f"{branch}, made for this run, so use it instead of making the batch branch "
        f"that the loop describes. {ending} End with the report that "
        "docs/worker.md's section 'Before you finish' asks for."
    )


def claude_argv(claude: str, prompt: str, model: str, effort: str, per_run_usd: float) -> list[str]:
    """The `claude -p` command for one run."""
    return [
        claude,
        "-p",
        prompt,
        "--model",
        model,
        "--effort",
        effort,
        "--max-budget-usd",
        f"{per_run_usd:.2f}",
        "--output-format",
        "json",
        "--permission-mode",
        "auto",
        "--permission-prompts",
        "none",
    ]


def git_or_refuse(args: Sequence[str], root: Path, timeout: float = CLONE_TIMEOUT_S) -> None:
    """Run git, or raise `Refused` with git's reason."""
    call = call_git(args, root, timeout=timeout)
    if call.code != 0:
        raise Refused(call.reason)


def prepare_clone(origin: str, clone: Path, branch: str, no_push: bool) -> None:
    """Clone `origin`, borrowing this checkout's objects, onto a new branch from its base.

    The objects are borrowed from the repository's shared git directory, not
    from the checkout. A linked worktree's `.git` is a file, which `git clone
    --reference` refuses (`PL-29DJ`).
    """
    clone.parent.mkdir(parents=True, exist_ok=True)
    shared = read_git(["rev-parse", "--path-format=absolute", "--git-common-dir"], ROOT).strip()
    git_or_refuse(["clone", "--reference", shared, "--dissociate", origin, str(clone)], ROOT)
    git_or_refuse(["checkout", "-b", branch, default_base(clone)], clone)
    if no_push:
        git_or_refuse(["remote", "set-url", "--push", REMOTE, NO_PUSH_URL], clone)


def log_for(clone: Path) -> Path:
    """The file beside `clone` that keeps its run's whole output."""
    return clone.with_name(clone.name + ".log")


def remote_tip(clone: Path, branch: str) -> str | None:
    """The commit the remote's `branch` points at, or `None` where it has none or git failed."""
    call = call_git(["ls-remote", "--heads", REMOTE, branch], clone)
    fields = call.answer.split() if call.code == 0 else []
    return fields[0] if fields else None


def only_on_remote(clone: Path, tip: str | None) -> bool:
    """Whether removing `clone` loses nothing: its `HEAD` is `tip` and nothing is uncommitted.

    Untracked files count as uncommitted, and a git call that fails answers
    False, so a clone is kept whenever this cannot be shown.
    """
    head = call_git(["rev-parse", "HEAD"], clone)
    status = call_git(["status", "--porcelain"], clone)
    return (
        tip is not None
        and head.code == 0
        and head.answer.strip() == tip
        and status.code == 0
        and not status.answer.strip()
    )


def read_result(stdout: bytes) -> dict[str, object] | None:
    """The run's JSON result, or `None` where the output holds none."""
    try:
        result = json.loads(stdout)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return result if isinstance(result, dict) else None


def number(value: object) -> float | None:
    """A JSON number as a float, or `None` for anything else."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def work(
    item: str,
    *,
    model: str,
    effort: str,
    per_run_usd: float,
    no_push: bool,
    origin: str,
    workdir: Path,
    claude: str,
    env: Mapping[str, str],
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> Run:
    """Clone, run one worker on `item`, and return what the run reported.

    The worker's environment names `item` in `WORKER_ITEM_ENV`, so its own
    `make check` reads the item's passing `verify:` as the work done rather
    than as an item left open (`PL-WJJ8`).
    """
    branch = branch_for(item, model, no_push)
    started = now()
    clone = workdir / f"{branch.removeprefix('claude/')}-{started:%Y%m%dT%H%M%S}"
    prepare_clone(origin, clone, branch, no_push)
    argv = claude_argv(claude, prompt_for(item, branch, no_push), model, effort, per_run_usd)
    try:
        process = subprocess.run(
            argv,
            cwd=clone,
            env={**env, WORKER_ITEM_ENV: item},
            capture_output=True,
            timeout=RUN_TIMEOUT_S,
            check=False,
        )
        exit_code: int | None = process.returncode
        result = read_result(process.stdout)
        stdout, stderr = process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        exit_code, result, stdout, stderr = None, None, b"", b"stopped at the run's time limit"
    # The whole output is kept beside the clone, so a failure can be read in full (PL-MZCN).
    log_for(clone).write_bytes(stdout + b"\n--- stderr ---\n" + stderr)
    result = result or {}
    denials = result.get("permission_denials")
    turns = number(result.get("num_turns"))
    subtype = result.get("subtype")
    is_error = result.get("is_error")
    reason = failure_reason(result, exit_code, stderr)
    usage = result.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    tip = None if no_push else remote_tip(clone, branch)
    run = Run(
        item=item,
        model=model,
        branch=branch,
        clone=str(clone),
        started=started.isoformat(),
        finished=now().isoformat(),
        pushed=tip is not None,
        exit_code=exit_code,
        cost_usd=number(result.get("total_cost_usd")),
        is_error=is_error if isinstance(is_error, bool) else None,
        subtype=subtype if isinstance(subtype, str) else None,
        turns=None if turns is None else int(turns),
        denials=len(denials) if isinstance(denials, list) else None,
        reason=reason,
        effort=effort,
        input_tokens=whole(usage.get("input_tokens")),
        cache_read_tokens=whole(usage.get("cache_read_input_tokens")),
        cache_write_tokens=whole(usage.get("cache_creation_input_tokens")),
        output_tokens=whole(usage.get("output_tokens")),
    )
    if tip is not None:
        run = commit_record(run, clone, tip)
        tip = remote_tip(clone, branch)
    removed = reason is None and only_on_remote(clone, tip)
    if removed:
        shutil.rmtree(clone)
    return replace(run, removed=removed)


def whole(value: object) -> int | None:
    """A JSON whole number as an int, or `None` for anything else.

    The token counts come from the result's `usage`, whose keys are the
    Messages API's (https://platform.claude.com/docs/en/api/messages, `usage`).
    """
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def commit_record(run: Run, clone: Path, tip: str) -> Run:
    """Commit the run's record to its branch and push it, or say why that failed.

    Only where the clone's `HEAD` is the pushed `tip`, so a commit the worker
    left unpushed is never published by the runner.
    """
    head = call_git(["rev-parse", "HEAD"], clone)
    if head.code != 0 or head.answer.strip() != tip:
        return replace(run, record_failure="the clone's HEAD is not the branch it pushed")
    path = worker_runs.write(clone, {name: getattr(run, name) for name in worker_runs.RUN_FIELDS})
    relative = path.relative_to(clone).as_posix()
    message = f"{run.item}: record the headless run"
    for args in (
        ["add", "--", relative],
        ["commit", "-q", "-m", message, "--", relative],
        ["push", "-q", REMOTE, f"HEAD:refs/heads/{run.branch}"],
    ):
        # The push goes to GitHub, which can take longer than git's local default.
        call = call_git(args, clone, timeout=CLONE_TIMEOUT_S)
        if call.code != 0:
            return replace(run, record_failure=" ".join(call.reason.split())[:300])
    return replace(run, record=relative)


def failure_reason(
    result: Mapping[str, object], exit_code: int | None, stderr: bytes
) -> str | None:
    """Why a run failed, shortened to one line, or `None` for a run that succeeded."""
    if result.get("is_error") is not True and exit_code == 0:
        return None
    text = result.get("result")
    if not isinstance(text, str) or not text.strip():
        lines = [line for line in split_lines(stderr.decode("utf-8", "replace")) if line.strip()]
        text = lines[-1] if lines else f"exit status {exit_code}, and nothing on stderr"
    return " ".join(text.split())[:300]


def describe(run: Run) -> str:
    """One line a person reads for one run."""
    cost = "cost unknown" if run.cost_usd is None else f"${run.cost_usd:.2f}"
    where = "pushed" if run.pushed else "not pushed"
    outcome = "error" if run.is_error or run.exit_code != 0 else "finished"
    log = log_for(Path(run.clone))
    kept = f"clone removed, log in {log}" if run.removed else f"in {run.clone}, log in {log}"
    line = (
        f"{run.item} on {run.model} at {run.effort} effort: "
        f"{outcome}, {cost}, {where}, {run.branch}, {kept}"
    )
    if run.record:
        line += f"\n  record: {run.record}, to review before the branch merges"
    elif run.record_failure:
        line += f"\n  no record committed: {run.record_failure}"
    return f"{line}\n  why: {run.reason}" if run.reason else line


def keep_awake(
    platform: str = sys.platform,
    which: Callable[[str], str | None] = shutil.which,
    start: Callable[[list[str]], object] = subprocess.Popen,
) -> str:
    """Hold an idle-sleep assertion until this process exits, and say what was done.

    On macOS it starts `caffeinate -i -w <this pid>`. `-i` prevents idle sleep,
    and `-w` releases the assertion once this process exits, so nothing is left
    to stop (caffeinate(8), https://www.sudo.is/docs/macos/man_caffeinate.html,
    read 2026-10-20). The manual does not say that this holds when the lid is
    closed, so the line asks the owner to keep it open (`PL-BT70`).
    """
    caffeinate = which("caffeinate") if platform == "darwin" else None
    if caffeinate is None:
        return (
            "Nothing keeps this machine awake: caffeinate is macOS's, and it was not "
            "found. If the machine sleeps, the run in progress fails and the batch stops."
        )
    start([caffeinate, "-i", "-w", str(os.getpid())])
    return "Keeping this Mac awake with caffeinate until the batch ends. Keep the lid open."


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--credit-left",
        type=float,
        required=True,
        help="the credit left, in US dollars, as the Console's billing page shows it now",
    )
    parser.add_argument(
        "--model", default=None, help="override the model docket.toml's [models] table chooses"
    )
    parser.add_argument("--item", action="append", default=[], help="an item to run; repeatable")
    parser.add_argument("--runs", type=int, default=1, help="without --item, how many to run")
    parser.add_argument("--per-run-usd", type=float, default=15.0, help="cap on one run")
    parser.add_argument("--no-push", action="store_true", help="a trial run: the clone cannot push")
    parser.add_argument("--workdir", type=Path, default=STATE_DIR / "workers")
    parser.add_argument("--claude", default="claude", help="the claude executable")
    parser.add_argument("--dry-run", action="store_true", help="say what would run, and stop")
    args = parser.parse_args(argv)
    if not math.isfinite(args.credit_left) or args.credit_left < 0:
        parser.error("--credit-left must be a dollar amount of 0 or more")
    return args


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] = os.environ,
    docket: Callable[[], str] = run_docket_delegable,
    models: Callable[[Sequence[str]], Mapping[str, Choice]] = worker_choices,
    tools: Callable[[Mapping[str, str]], None] = check_tools,
    awake: Callable[[], str] = keep_awake,
) -> int:
    args = parse_args(argv)
    try:
        env = child_environment(environ)
        tools(env)
        items = choose(delegable_ids(docket), args.item, args.runs)
        choices = models(items)
        chosen_models = {item: args.model or choices[item].model for item in items}
        efforts = {item: choices[item].effort for item in items}
        origin = origin_url(ROOT)
        if not origin:
            raise Refused(f"git could not name {REMOTE}'s URL, so there is nothing to clone.")
        left = args.credit_left
        if args.dry_run:
            chosen = (
                ", ".join(
                    f"{item} on {chosen_models[item]} at {efforts[item]} effort" for item in items
                )
                or "nothing"
            )
            print(f"Would run {chosen}; ${left:.2f} of credit left.")
            return 0
        print(awake())
        for item in items:
            if left < args.per_run_usd:
                print(f"Stopped: ${left:.2f} of credit left, below one run's cap.")
                break
            run = work(
                item,
                model=chosen_models[item],
                effort=efforts[item],
                per_run_usd=args.per_run_usd,
                no_push=args.no_push,
                origin=origin,
                workdir=args.workdir,
                claude=args.claude,
                env=env,
            )
            print(describe(run))
            if run.cost_usd is None:
                print("Stopped: that run's cost could not be read, so the credit left is unknown.")
                return 1
            left -= run.cost_usd
            if run.reason is not None:
                print(
                    f"Stopped: that run failed, with ${left:.2f} of credit left. An empty "
                    "credit, a lost connection or a sleeping Mac fails every later run "
                    "too, so read the reason above before starting again."
                )
                return 1
    except Refused as refusal:
        print(f"headless_worker: {refusal}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
