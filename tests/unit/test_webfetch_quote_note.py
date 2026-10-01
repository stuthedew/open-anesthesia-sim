"""Tests for `.claude/hooks/webfetch-quote-note.sh`, which marks WebFetch results (`PL-B1BW`).

Every result is marked as a small model's answer about the page, not the page.

The hook decides nothing, so what can break is delivery: a matcher that names
no tool, or output Claude Code cannot parse, attaches nothing and fails no
other test. Both are pinned here, with the large payload a fetched page makes.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "webfetch-quote-note.sh"
SETTINGS = REPO / ".claude" / "settings.json"


def _note(payload: str) -> str:
    """The `additionalContext` the hook attaches to one result."""
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stderr
    output: dict[str, dict[str, str]] = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    return output["hookSpecificOutput"]["additionalContext"]


def test_it_is_wired_after_webfetch_by_exact_name() -> None:
    """A matcher of letters alone is an exact tool name, so it must spell `WebFetch` exactly."""
    matchers = [
        entry.get("matcher", "")
        for entry in json.loads(SETTINGS.read_text())["hooks"]["PostToolUse"]
        if any("webfetch-quote-note.sh" in hook["command"] for hook in entry["hooks"])
    ]
    assert matchers == ["WebFetch"]


def test_a_fetched_page_gets_the_note_that_sends_quotations_to_curl() -> None:
    page = "# Settings\n\n" + "A sentence of documentation. " * 20_000
    payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "WebFetch",
            "tool_input": {
                "url": "https://code.claude.com/docs/en/settings",
                "prompt": "Quote verbatim",
            },
            "tool_response": page,
        }
    )
    note = _note(payload)
    assert "not the page" in note
    assert "curl" in note
    assert ".md" in note


def test_an_empty_or_unreadable_payload_still_gets_the_note() -> None:
    """The note does not depend on the payload, so no payload can withhold it."""
    assert _note("") == _note("{not json")
