#!/usr/bin/env python3
"""PreToolUse hook on an edit: refuse a regular expression written without a reason.

The project owner asked on 2026-11-03 that a session stop each time it reaches
for a regular expression, consider whether a parser or a string method does the
job better, look up the best practice for the task, and use the regular
expression only where it is still the right tool (`PL-7JYV`). This hook is the
stop. It runs before an `Edit`, `MultiEdit` or `Write` of a Python file. It
works out what the file would hold after the edit, and refuses the edit where
that text holds a call to the `re` or `regex` module that the file did not hold
before and that has no `regex:` comment giving a reason. The refusal carries
`regex_check.GUIDANCE`, which says what to consider and how to write the
reason. The session then either writes the code another way or sends the edit
again with the reason beside the call.

`tools/regex_check.py` decides what a call is and what a reason is, through
`added_uses`, so the hook and `make check` cannot disagree. A call counts as the
same call when `ast.unparse` writes it the same way. Moving or reformatting one
is therefore not refused, and changing the pattern of one that has no reason
is.

The hook lets the edit through, saying nothing, where the file is not this
repository's Python: a file that is not Python, or one outside the checkout,
such as a scratch script. It does the same where it cannot tell: a payload it
cannot read, an `old_string` the file does not hold (the edit fails on its
own), or a text that does not parse. The last case
covers a file that uses syntax newer than the bare `python3` running the hook.
`make check` and CI run `tools/regex_check.py` under the project's interpreter,
so a call that passes here unseen is still refused there.

What goes unchecked: an edit made through a Bash command, a `NotebookEdit`,
and every edit in a thread where the repository's hooks do not run. The hook
is wired on the three tool names Claude Code uses today. If Claude Code renames
one, the hook stops running for that tool and nothing reports it, because
checking every tool call would put a Python start-up in front of each one. CI
is the backstop in each case.

Standard library only, as every hook here is.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))

import regex_check  # noqa: E402

import hook_input  # noqa: E402

#: The guard's name in the log of refusals that `hook_input.deny` keeps.
GUARD_NAME = "regex_guard"

#: The file endings the hook reads as Python source.
PYTHON_SUFFIXES = frozenset({".py", ".pyi"})


def _replaced(text: str, old: object, new: object, every: object) -> str | None:
    """Return `text` with one edit applied, or `None` where the edit cannot apply."""

    if not isinstance(old, str) or not isinstance(new, str) or not old or old not in text:
        return None

    return text.replace(old, new) if every is True else text.replace(old, new, 1)


def proposed(payload: str) -> tuple[str, str] | None:
    """Return a Python file's text before and after the edit `payload` describes.

    `None` where the payload names no Python file, describes no edit this hook
    reads, or describes an edit that cannot apply.
    """

    try:
        data = json.loads(payload)
    except ValueError:
        return None

    if not isinstance(data, dict):
        return None

    tool = data.get("tool_name")
    tool_input = data.get("tool_input")

    if not isinstance(tool_input, dict):
        return None

    file_path = tool_input.get("file_path")

    if not isinstance(file_path, str) or Path(file_path).suffix not in PYTHON_SUFFIXES:
        return None

    if not Path(file_path).resolve().is_relative_to(hook_input.project_root().resolve()):
        return None

    try:
        before = Path(file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        before = ""
    except (OSError, UnicodeDecodeError):
        return None

    after: str | None

    if tool == "Write":
        content = tool_input.get("content")
        after = content if isinstance(content, str) else None
    elif tool == "Edit":
        after = _replaced(
            before,
            tool_input.get("old_string"),
            tool_input.get("new_string"),
            tool_input.get("replace_all"),
        )
    elif tool == "MultiEdit":
        edits = tool_input.get("edits")
        after = before if isinstance(edits, list) else None

        for edit in edits if isinstance(edits, list) else []:
            if after is None or not isinstance(edit, dict):
                after = None
                break

            after = _replaced(
                after, edit.get("old_string"), edit.get("new_string"), edit.get("replace_all")
            )
    else:
        after = None

    return None if after is None else (before, after)


def refusal(added: list[regex_check.Use]) -> str:
    """Return the reason the session reads, naming each call the edit would add."""

    named = "\n".join(f"  {regex_check.describe(use)}" for use in added)
    return (
        "This edit adds a regular expression with no `regex:` reason beside it:\n"
        f"{named}\n\n{regex_check.GUIDANCE}\n\n"
        "Then send the edit again, written another way or with the reason beside each call."
    )


def main() -> int:
    payload = sys.stdin.read()
    texts = proposed(payload)

    if texts is None:
        return 0

    try:
        added = regex_check.added_uses(*texts)
    except (SyntaxError, ValueError):
        return 0

    if added:
        print(hook_input.deny(GUARD_NAME, "regex-without-reason", refusal(added), payload))

    return 0


if __name__ == "__main__":
    sys.exit(main())
