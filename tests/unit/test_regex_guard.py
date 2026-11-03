"""`.claude/hooks/regex_guard.py` must refuse an edit that adds a regular expression with no reason.

The hook is the stop `PL-7JYV` asked for, so the failure that matters is an
edit it lets through when it should refuse: a tool it reads wrongly, or a
before-and-after it works out wrongly. The opposite failure, a refusal of an
edit that adds no new call, costs a session a retry each time it happens.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "regex_guard.py"


def _decision(tool: str, tool_input: Mapping[str, object], checkout: Path) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one call in `checkout`, or `None` for none."""
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(checkout)},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    decision: dict[str, str] = json.loads(result.stdout)["hookSpecificOutput"]
    return decision


def test_writing_a_new_file_with_a_regular_expression_is_refused_with_the_guidance(
    tmp_path: Path,
) -> None:
    target = tmp_path / "new.py"

    content = "import re\nre.compile('a')\n"

    decision = _decision("Write", {"file_path": str(target), "content": content}, tmp_path)

    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    assert "line 2, in <module>: re.compile('a')" in decision["permissionDecisionReason"]
    assert "Check whether a string method does it" in decision["permissionDecisionReason"]


def test_writing_one_with_a_reason_is_let_through(tmp_path: Path) -> None:
    content = "import re\n# regex: a single letter, no parser reads it\nre.compile('a')\n"

    target = tmp_path / "new.py"

    assert _decision("Write", {"file_path": str(target), "content": content}, tmp_path) is None


def test_an_edit_is_judged_on_the_whole_file_it_would_leave(tmp_path: Path) -> None:
    target = tmp_path / "mod.py"
    target.write_text(
        "import re\nA = re.compile('a')\n\ndef f(s):\n    return s\n", encoding="utf-8"
    )

    adds = {
        "file_path": str(target),
        "old_string": "return s",
        "new_string": "return re.sub('x', '', s)",
    }
    moves = {
        "file_path": str(target),
        "old_string": "A = re.compile('a')\n",
        "new_string": "A = re.compile(\n    'a'\n)\n",
    }

    assert _decision("Edit", adds, tmp_path) is not None
    assert _decision("Edit", moves, tmp_path) is None


def test_a_multi_edit_is_applied_in_order(tmp_path: Path) -> None:
    target = tmp_path / "mod.py"
    target.write_text("x = 1\n", encoding="utf-8")
    edits = [
        {"old_string": "x = 1", "new_string": "import re\nx = 1"},
        {"old_string": "x = 1", "new_string": "x = re.match('a', 'a')"},
    ]

    assert _decision("MultiEdit", {"file_path": str(target), "edits": edits}, tmp_path) is not None


def test_what_the_hook_cannot_judge_is_let_through(tmp_path: Path) -> None:
    target = tmp_path / "mod.py"
    target.write_text("x = 1\n", encoding="utf-8")
    regex = "import re\nre.compile('a')\n"

    notes = tmp_path / "notes.md"
    absent = {"file_path": str(target), "old_string": "absent", "new_string": regex}
    broken = regex + "def broken(:\n"

    assert _decision("Write", {"file_path": str(notes), "content": regex}, tmp_path) is None
    assert _decision("Edit", absent, tmp_path) is None
    assert _decision("Write", {"file_path": str(target), "content": broken}, tmp_path) is None
    assert _decision("Bash", {"command": "true"}, tmp_path) is None


def test_a_file_outside_the_checkout_is_let_through(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    scratch = tmp_path / "scratch.py"
    regex = "import re\nre.compile('a')\n"

    assert _decision("Write", {"file_path": str(scratch), "content": regex}, checkout) is None
    assert _decision("Write", {"file_path": str(checkout / "a.py"), "content": regex}, checkout)
