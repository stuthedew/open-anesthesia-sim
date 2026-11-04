"""Run the copy editor on one file that `tools/new_prose.py` wrote, and print its reply.

Close-out step 8, the pull-request skill and reply rule 16 in
`.claude/rules/instruction-writing.md` hand the copy editor a file of passages.
The copy editor's instructions are the body of `.claude/agents/copy-editor.md`,
which is their one home. A Projects thread cannot start that agent, because a
thread does not load `.claude/agents/`. The fallback, a general-purpose agent
given the agent file's text, loads every resident instruction that the copy
editor is meant to run without (`PL-TQ4J`).

So this tool runs the copy editor as its own `claude -p` process, the same
way in every kind of session. The process starts in an empty directory that
holds only the request, so no `CLAUDE.md` or rule is found and loaded. Run
inside the repository, even `claude -p --agent copy-editor` loads the resident
instructions. Its system prompt is the agent file's body, its one tool is Read,
and it loads no settings file.

The model and effort are the ones `docket.toml`'s `[models]` table chooses
for the role `copy-editor`. The run is billed to the account that `claude`
signs in with, as an Agent call would be.

Prints the reply on standard output and one line of counts on standard
error. Exits 0 when the copy editor replied, and 1 with the reason when
`claude` is missing, fails, times out or returns an error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load as load_config  # noqa: E402
from docket.model import FRONT_MATTER_RE  # noqa: E402

from new_prose import PROMPT  # noqa: E402

#: The role `docket.toml`'s `[models]` table is asked about.
ROLE = "copy-editor"
#: The name the request takes inside the copy editor's empty directory.
REQUEST_NAME = "request.txt"
#: A run that takes longer than this is stopped. The longest copy edit measured
#: so far read 29 passages in about 15 minutes (`PL-22T5`), so 40 minutes leaves
#: room for a larger branch while still ending a run that has stalled.
COPY_EDIT_TIMEOUT_S = 40 * 60
#: Turns off the memory index that a session would otherwise load, so the
#: copy editor's context is its instructions and the request alone.
QUIET_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}


class Refused(Exception):
    """The copy editor could not be run, or did not reply, with the reason."""


def instructions(prompt: str) -> str:
    """The copy editor's instructions: the agent file's text without its front matter."""
    match = FRONT_MATTER_RE.match(prompt)
    if match is None:
        raise Refused(f"{PROMPT} has no front matter, so its instructions cannot be found")
    return match.group(2).lstrip("\n")


def claude_argv(claude: str, system_prompt: Path, model: str, effort: str) -> list[str]:
    """The `claude -p` command that runs the copy editor on `REQUEST_NAME`."""
    return [
        claude,
        "-p",
        f"Copy-edit the passages in {REQUEST_NAME}.",
        "--model",
        model,
        "--effort",
        effort,
        "--tools",
        "Read",
        "--system-prompt-file",
        str(system_prompt),
        "--setting-sources",
        "",
        "--output-format",
        "json",
    ]


def reply_of(output: str) -> tuple[str, str]:
    """The reply in `claude -p`'s JSON `output`, and one line of what the run read and cost."""
    try:
        data = json.loads(output[output.index("{") :])
    except ValueError as error:
        raise Refused(f"claude printed no JSON result: {error}") from error
    if data.get("is_error") or not isinstance(data.get("result"), str):
        raise Refused(f"claude returned an error: {data.get('result')!r}")
    usage = data.get("usage", {})
    read = sum(
        usage.get(key, 0)
        for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )
    counts = (
        f"copy_edit: read {read} tokens, wrote {usage.get('output_tokens', 0)}, "
        f"{data.get('num_turns', '?')} turns, ${data.get('total_cost_usd', 0):.2f}"
    )
    return data["result"], counts


def run(request: Path, root: Path = ROOT, env: Mapping[str, str] | None = None) -> tuple[str, str]:
    """Run the copy editor on the file at `request`, and return its reply and the counts."""
    claude = shutil.which("claude")
    if claude is None:
        raise Refused("no `claude` on PATH")
    table = load_config(root).models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen")
    choice = table.choose({"role": ROLE})
    text = instructions(PROMPT.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as held, tempfile.TemporaryDirectory() as work:
        system_prompt = Path(held) / "copy-editor.md"
        system_prompt.write_text(text, encoding="utf-8")
        shutil.copyfile(request, Path(work) / REQUEST_NAME)
        try:
            done = subprocess.run(
                claude_argv(claude, system_prompt, choice.model, choice.effort),
                cwd=work,
                env={**(os.environ if env is None else env), **QUIET_ENV},
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=COPY_EDIT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as error:
            raise Refused(f"claude did not finish within {COPY_EDIT_TIMEOUT_S} s") from error
    if done.returncode:
        raise Refused(f"claude exited {done.returncode}: {done.stderr.strip()[-500:]}")
    return reply_of(done.stdout)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("request", type=Path, help="the file tools/new_prose.py wrote")
    args = parser.parse_args(argv)
    try:
        reply, counts = run(args.request)
    except (Refused, OSError) as error:
        print(f"copy_edit: no reply: {error}", file=sys.stderr)
        return 1
    print(reply)
    print(counts, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
