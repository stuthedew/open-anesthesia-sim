"""Give a Claude Projects thread the repository's hooks, which it does not load.

Claude Code's Projects documentation says a cloud thread loads each
repository's `CLAUDE.md` and `.claude/rules/`, but not its
`.claude/settings.json`: the hooks there are "Not run"
(https://code.claude.com/docs/en/claude-projects.md, § "What threads pick up
from your repositories", read 2026-10-26). So a thread works without the
guards, the session-start digest and the stop-hook correction, and nothing
tells it so (`PL-CR81`). A thread does read the user settings in
`~/.claude/settings.json`, and reloads them when they change: a hook written
there mid-session fired on the next tool call, with `CLAUDE_PROJECT_DIR` set
to the checkout (measured 2026-10-26, `PL-CR81` § "Narrowed 2026-10-26").

This hook is the bridge (`PL-X6VN`). The cloud environment's setup script
writes one `SessionStart` entry into the user settings, which runs this file
from the checkout; `python3 .claude/hooks/thread_hooks.py --setup-script`
prints that script. At each session start in a Projects thread, this hook
copies the repository's `hooks` block into the user settings beside its own
entry, and Claude Code picks the copy up on its next tool call. The setup
script holds only the pointer, never a copy of the hooks. The environment's
snapshot keeps what the setup script wrote for about seven days, so a copy
written there would go stale, while the pointer reads `.claude/settings.json`
afresh in every session.

The first time it writes the hooks, it also runs the repository's own
`SessionStart` commands and prints what they print, because Claude Code has
already chosen which session-start hooks to run by then. After that the
copied entries run on their own, and this hook only checks that the copy is
current.

Outside a Projects thread it does nothing: an ordinary cloud session loads
`.claude/settings.json` itself, and a second copy would run every hook twice.
It exits 0 on every path, since a session start that fails helps no one.

Standard library only, since a hook runs before any virtualenv is known.
"""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from hook_input import project_root, write_atomically

#: The value of `CLAUDE_CODE_ENTRYPOINT` in a Claude Projects thread, read from
#: a thread's environment on 2026-10-26. An ordinary cloud session has
#: another, such as `remote_desktop`.
PROJECTS_ENTRYPOINT = "remote_projects"

#: The command the setup script binds to `SessionStart`. It tests for this
#: file first, so a checkout from before this hook, or a session with no
#: checkout, starts without an error.
BOOTSTRAP_COMMAND = (
    'test -f "$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py"'
    ' && python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py" || true'
)

#: The longest a repository `SessionStart` command may run when this hook runs
#: it, in seconds. It is Claude Code's own default for a command hook.
COMMAND_TIMEOUT_S = 60

#: What a session start prints when a repository command fails. Claude Code
#: adds a `SessionStart` hook's output to the session, so the session learns
#: that a hook it should have had did not run.
COMMAND_FAILED = (
    "thread_hooks.py: the repository's SessionStart command `{command}` failed ({reason})."
)


#: What a session start prints when the user settings cannot be written.
COULD_NOT_WRITE = (
    "thread_hooks.py: could not write {path} ({error}), so the repository's hooks are off.\n"
)


def user_settings_path() -> Path:
    """The user settings file Claude Code reads, which a Projects thread does not skip."""
    return Path.home() / ".claude" / "settings.json"


def setup_script() -> str:
    """The cloud environment's setup script, which adds this hook's entry to the user settings.

    It adds the entry beside whatever the file already holds, and adds it
    only once, so running it over existing settings loses nothing. It ends
    in `|| true` because a setup script that fails stops the session from
    starting at all.
    """
    group = json.dumps(_bootstrap_group())
    return (
        "mkdir -p ~/.claude\n"
        "python3 - <<'EOF' || true\n"
        "import json, pathlib\n"
        'path = pathlib.Path.home() / ".claude" / "settings.json"\n'
        "try:\n"
        "    data = json.loads(path.read_text())\n"
        "except (OSError, ValueError):\n"
        "    data = {}\n"
        f"group = {group}\n"
        'starts = data.setdefault("hooks", {}).setdefault("SessionStart", [])\n'
        "if group not in starts:\n"
        "    starts.append(group)\n"
        'path.write_text(json.dumps(data, indent=2) + "\\n")\n'
        "EOF\n"
    )


def _bootstrap_group() -> dict[str, object]:
    return {"hooks": [{"type": "command", "command": BOOTSTRAP_COMMAND}]}


def _is_bootstrap(group: object) -> bool:
    """Whether a `SessionStart` matcher group runs this file."""
    if not isinstance(group, dict):
        return False
    hooks = group.get("hooks")
    return isinstance(hooks, list) and any(
        isinstance(hook, dict) and "thread_hooks.py" in str(hook.get("command", ""))
        for hook in hooks
    )


def merged(user: dict[str, object], project_hooks: dict[str, object]) -> dict[str, object]:
    """The user settings `user`, with the repository's hooks and this hook's entry.

    Every key other than `hooks` is kept as the user file has it. The
    `hooks` block becomes the repository's, plus the entry that runs this
    file. That entry is taken from the user file where it is there, so the
    setup script's wording is the one that stays, and is otherwise built from
    `BOOTSTRAP_COMMAND`.
    """
    old_hooks = user.get("hooks")
    old_start = old_hooks.get("SessionStart") if isinstance(old_hooks, dict) else None
    found = (
        [group for group in old_start if _is_bootstrap(group)]
        if isinstance(old_start, list)
        else []
    )
    hooks = copy.deepcopy(project_hooks)
    start = hooks.get("SessionStart")
    groups = (
        [group for group in start if not _is_bootstrap(group)] if isinstance(start, list) else []
    )
    hooks["SessionStart"] = [*groups, found[0] if found else _bootstrap_group()]
    return {**user, "hooks": hooks}


def _matches(group: dict[str, object], source: str) -> bool:
    """Whether a `SessionStart` matcher group applies to a start of kind `source`.

    A group with no matcher, an empty one or `*` applies to every start.
    Otherwise the matcher is a regular expression over the kind, such as
    `startup|resume`. A matcher that is not a valid expression applies to
    none, as a group that cannot be read should not run.
    """
    matcher = group.get("matcher")
    if not isinstance(matcher, str) or matcher in ("", "*"):
        return True
    try:
        return re.fullmatch(matcher, source) is not None
    except re.error:
        return False


def start_commands(project_hooks: dict[str, object], source: str) -> list[tuple[str, float]]:
    """Each repository `SessionStart` command that applies to `source`, with its timeout."""
    groups = project_hooks.get("SessionStart")
    commands: list[tuple[str, float]] = []
    for group in groups if isinstance(groups, list) else []:
        if not isinstance(group, dict) or _is_bootstrap(group) or not _matches(group, source):
            continue
        for hook in group.get("hooks") or []:
            if isinstance(hook, dict) and hook.get("type") == "command":
                timeout = hook.get("timeout")
                limit = timeout if isinstance(timeout, int | float) else COMMAND_TIMEOUT_S
                commands.append((str(hook.get("command", "")), float(limit)))
    return commands


def _run(command: str, timeout_s: float, payload: str, root: Path) -> str:
    """What `command` prints, run as Claude Code runs a command hook."""
    environment = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    try:
        result = subprocess.run(
            command,
            shell=True,
            input=payload,
            capture_output=True,
            text=True,
            cwd=str(root),
            env=environment,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return COMMAND_FAILED.format(command=command, reason=f"no result in {timeout_s:g} s") + "\n"
    except OSError as error:
        return COMMAND_FAILED.format(command=command, reason=str(error)) + "\n"
    if result.returncode != 0:
        reason = f"exit {result.returncode}"
        return result.stdout + COMMAND_FAILED.format(command=command, reason=reason) + "\n"
    return result.stdout


def _read_json(path: Path) -> dict[str, object] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _source_of(payload: str) -> str:
    """The kind of start a `SessionStart` payload names.

    Claude Code names four: `startup`, `resume`, `clear` and `compact`.
    """
    try:
        data = json.loads(payload)
    except ValueError:
        return "startup"
    source = data.get("source") if isinstance(data, dict) else None
    return source if isinstance(source, str) else "startup"


def main(payload: str, *, entrypoint: str | None, root: Path, user_path: Path) -> str:
    """Bring the user settings up to date, and return what the session start prints."""
    if entrypoint != PROJECTS_ENTRYPOINT:
        return ""
    project = _read_json(root / ".claude" / "settings.json")
    project_hooks = project.get("hooks") if project else None
    if not isinstance(project_hooks, dict):
        return ""
    user = _read_json(user_path) or {}
    wanted = merged(user, project_hooks)
    if wanted == user:
        return ""
    try:
        user_path.parent.mkdir(parents=True, exist_ok=True)
        write_atomically(user_path, json.dumps(wanted, indent=2) + "\n")
    except OSError as error:
        return COULD_NOT_WRITE.format(path=user_path, error=error)
    source = _source_of(payload)
    return "".join(
        _run(command, timeout_s, payload, root)
        for command, timeout_s in start_commands(project_hooks, source)
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["--setup-script"]:
        sys.stdout.write(setup_script())
        raise SystemExit(0)
    try:
        stdin = "" if sys.stdin.isatty() else sys.stdin.read()
        sys.stdout.write(
            main(
                stdin,
                entrypoint=os.environ.get("CLAUDE_CODE_ENTRYPOINT"),
                root=project_root(),
                user_path=user_settings_path(),
            )
        )
    except Exception as error:
        # A session start must never fail, whatever went wrong.
        sys.stdout.write(f"thread_hooks.py: {error}\n")
    raise SystemExit(0)
