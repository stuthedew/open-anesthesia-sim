"""Show whether a plugin's hooks run in a Claude Projects thread (`PL-SQV9`).

A Projects thread does not load the repository's `.claude/settings.json`, so
none of its hooks run there. Claude Code's Projects documentation says plugins
added in Project settings > Plugins "load into each new cloud thread"
(https://code.claude.com/docs/en/claude-projects.md, § "Get skills, plugins,
connectors, and tools into threads", read 2026-10-31), but it does not say
whether a plugin's hooks then run. This script is the test plugin's only hook.

At session start it prints one line, which Claude Code adds to the session.
The line names the directories the hook was given, and whether the
repository's `.claude/settings.json` can be read from there. A plugin that
replaced `PL-X6VN`'s setup script would need to read the hooks from that file
at run time, so that the plugin holds no second copy of them.

On a Bash call it refuses any command that contains `thread-probe-sentinel`,
and lets every other command through. A refusal is something the thread
cannot produce by itself, so it shows that the hook ran.

Standard library only, and it exits 0 on every path, since a hook that fails
helps no one.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

#: The text whose presence in a Bash command this hook refuses.
SENTINEL = "thread-probe-sentinel"


def context() -> str:
    """The environment the hook ran in, as one line."""
    project = os.environ.get("CLAUDE_PROJECT_DIR", "")
    settings = Path(project) / ".claude" / "settings.json" if project else None
    if settings is None:
        readable = "no CLAUDE_PROJECT_DIR"
    else:
        try:
            events = sorted(json.loads(settings.read_text()).get("hooks", {}))
            readable = f"readable, hook events {', '.join(events) or 'none'}"
        except (OSError, ValueError) as error:
            readable = f"not readable ({type(error).__name__})"
    return (
        f"CLAUDE_CODE_ENTRYPOINT={os.environ.get('CLAUDE_CODE_ENTRYPOINT', '')!r}; "
        f"CLAUDE_PROJECT_DIR={project!r}; "
        f"CLAUDE_PLUGIN_ROOT={os.environ.get('CLAUDE_PLUGIN_ROOT', '')!r}; "
        f"cwd={os.getcwd()!r}; "
        f"repository .claude/settings.json: {readable}"
    )


def main(event: str, payload: str) -> str:
    """Return what the hook prints for one event."""
    if event == "session-start":
        return f"thread-probe: the plugin's SessionStart hook ran. {context()}\n"
    if event != "pre-tool-use":
        return ""
    try:
        command = json.loads(payload).get("tool_input", {}).get("command", "")
    except ValueError:
        return ""
    if not isinstance(command, str) or SENTINEL not in command:
        return ""
    reason = f"thread-probe: the plugin's PreToolUse hook ran and refused this command. {context()}"
    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    return json.dumps(decision) + "\n"


if __name__ == "__main__":
    sys.stdout.write(main(sys.argv[1] if len(sys.argv) > 1 else "", sys.stdin.read()))
