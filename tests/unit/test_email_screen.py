"""Tests for `tools/email_screen.py`, which keeps an email address off GitHub (`PL-7K31`).

The screen was part of `tools/pr_body_check.py` until `PL-NDY5` moved it so
that the guard running it before every MCP call no longer loads `docket`.
The last tests here pin that: the screen loads no `docket` module, and it
still refuses with `docket` unimportable.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import email_screen
import pytest

# A body is public as soon as GitHub has it, so the screen runs before the call.
# What is pinned is that a personal address is refused and named, that the
# addresses that are nobody's own and a version pin are not, that every MCP
# tool reaches the hook and the screen reads every field of each GitHub call
# whatever its tool or field is called (`PL-NZJG`, `PL-D16Y`), and that the hook
# script refuses when Claude Code starts it.
#
# The refused addresses are built when the test runs, because the reserved
# test domains are admitted and the git hook's push screen reads this file's
# own text when it is pushed.

REPO = Path(__file__).resolve().parents[2]

#: A person's address, and a second one, made here so this file's text holds none.
PERSON = "a.person" + "@" + "clinic.org"
OTHER = "me" + "@" + "hospital.net"


def _call(tool: str, **arguments: str) -> str:
    return json.dumps({"tool_name": tool, "tool_input": {"owner": "o", "repo": "r", **arguments}})


def test_an_email_address_in_a_pull_request_body_is_refused() -> None:
    refusal = email_screen.screen(
        _call("mcp__github__create_pull_request", title="t", body=f"Asked by {PERSON}.")
    )

    assert refusal is not None
    decision = json.loads(refusal)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert f"`{PERSON}`" in decision["permissionDecisionReason"]
    assert "`body`" in decision["permissionDecisionReason"]


def test_an_email_address_in_an_updated_title_is_refused() -> None:
    call = _call("mcp__github__update_pull_request", title=f"PL-K7QX: from {OTHER}")

    assert email_screen.screen(call) is not None


@pytest.mark.parametrize(
    "body",
    [
        "Co-authored-by: Claude <noreply@anthropic.com>",
        "Pins react@18.3.1 and @types/node.",
        "No address at all.",
        "Merged on the website by 3359688+stuthedew@users.noreply.github.com.",
        "GitHub <noreply@github.com>",
        "Clone git@github.com:stuthedew/open-anesthesia-sim.git",
        "Tests use t@example.com, a@bar.example.org, x@mail.example and y@z.invalid.",
    ],
)
def test_a_body_without_a_personal_address_is_let_through(body: str) -> None:
    assert email_screen.screen(_call("mcp__github__create_pull_request", body=body)) is None


@pytest.mark.parametrize("payload", ["not json", "[]", _call("mcp__github__merge_pull_request")])
def test_a_payload_the_screen_does_not_govern_is_let_through(payload: str) -> None:
    assert email_screen.screen(payload) is None


@pytest.mark.parametrize(
    ("tool", "extra"),
    [
        ("mcp__github__pull_request_write", {"method": "create", "title": "t"}),
        ("mcp__github__create_pr", {}),
        ("mcp__github__issue_write", {"method": "create", "title": "t"}),
        ("mcp__github__add_issue_comment", {"issue_number": "1931"}),
        ("mcp__github__pull_request_review_write", {"method": "create"}),
    ],
    ids=["folded-into-a-write-tool", "renamed", "issue", "comment", "review"],
)
def test_an_email_address_sent_to_github_under_any_tool_name_is_refused(
    tool: str, extra: dict[str, str]
) -> None:
    """The screen reads a call by its fields, not its tool's name, which GitHub owns (`PL-NZJG`).

    Before, only `create_pull_request` and `update_pull_request` were read, so
    a renamed tool, or a comment on the same pull request, published the
    address unread.
    """
    refusal = email_screen.screen(_call(tool, body=f"Asked by {PERSON}.", **extra))

    assert refusal is not None
    assert f"`{PERSON}`" in json.loads(refusal)["hookSpecificOutput"]["permissionDecisionReason"]


def _call_with(tool: str, arguments: dict[str, object]) -> str:
    return json.dumps({"tool_name": tool, "tool_input": {"owner": "o", "repo": "r", **arguments}})


@pytest.mark.parametrize(
    ("tool", "arguments", "field"),
    [
        (
            "mcp__github__merge_pull_request",
            {"pullNumber": 1, "commit_message": "Asked by {person}."},
            "commit_message",
        ),
        (
            "mcp__github__push_files",
            {"branch": "b", "message": "m", "files": [{"path": "a.md", "content": "{person}"}]},
            "files[0].content",
        ),
        (
            "mcp__github__create_or_update_file",
            {"path": "a.md", "content": "x", "message": "From {person}"},
            "message",
        ),
        ("mcp__github__issue_write", {"method": "create", "labels": ["{person}"]}, "labels[0]"),
    ],
    ids=["squash-message", "pushed-file", "commit-message", "nested-list"],
)
def test_an_address_in_any_field_github_publishes_is_refused_and_its_field_named(
    tool: str, arguments: dict[str, object], field: str
) -> None:
    """`PL-D16Y`: a merge's message and pushed file content were published unread.

    The screen read only `title` and `body`, so an address in a squash merge's
    `commit_message`, which becomes the commit on `main`, or in a file sent by
    `push_files` reached GitHub. Every string in the call is read now.
    """
    filled = json.loads(json.dumps(arguments).replace("{person}", PERSON))

    refusal = email_screen.screen(_call_with(tool, filled))

    assert refusal is not None
    reason = json.loads(refusal)["hookSpecificOutput"]["permissionDecisionReason"]
    assert f"`{PERSON}`" in reason
    assert f"`{field}`" in reason


@pytest.mark.parametrize(
    ("domain", "admitted"),
    [
        ("anthropic.com", False),
        ("github.com", False),
        ("noreply.github.com", False),
        ("users.noreply.github.com", True),
        ("example.com", True),
        ("sub.example.net", True),
        ("mail.example", True),
        ("host.invalid", True),
        ("host.test", True),
        ("localhost.localhost", True),
        ("example.com.attacker.org", False),
        ("notexample.com", False),
    ],
)
def test_an_address_under_a_domain_is_admitted_only_where_nobody_can_hold_it(
    domain: str, admitted: bool
) -> None:
    """Joined here, so that the refused addresses are not in this file's own text."""
    assert email_screen.admitted("t" + "@" + domain) is admitted


@pytest.mark.parametrize(
    "address", ["noreply@anthropic.com", "NoReply@GitHub.com", "git@github.com"]
)
def test_the_three_addresses_that_are_nobodys_own_are_admitted(address: str) -> None:
    assert email_screen.admitted(address)


def test_the_push_screen_names_each_address_with_its_commit_and_place() -> None:
    """`--screen-push` reads the log the git `pre-push` hook hands it (`PL-1ZZ0`)."""
    log = (
        "\0" + "a" * 40 + "\nClaude <noreply@anthropic.com>\nClaude <noreply@anthropic.com>\n"
        f"Subject\n\nAsked by {PERSON}.\n\n"
        "diff --git a/n.md b/n.md\n--- a/n.md\n+++ b/n.md\n@@ -1 +1 @@\n"
        f"-Removed {OTHER}\n+Added {OTHER}\n"
        "\0" + "b" * 40 + f"\nSomeone <{PERSON}>\nClaude <noreply@anthropic.com>\nClean\n"
    )

    found = email_screen.screen_push(log)

    assert found == [
        f"`{PERSON}` in commit {'a' * 12}, its message",
        f"`{OTHER}` in commit {'a' * 12}, lines it adds to `n.md`",
        f"`{PERSON}` in commit {'b' * 12}, its author or committer",
    ]


def test_the_push_screen_lets_a_clean_log_through() -> None:
    log = "\0" + "a" * 40 + "\nClaude <noreply@anthropic.com>\nClaude <noreply@anthropic.com>\nOK\n"

    assert email_screen.screen_push(log) == []
    assert email_screen.screen_push("") == []


@pytest.mark.parametrize(
    "tool", ["mcp__hearthbot__post_message", "mcp__Gmail__send_message", "mcp__github__get_me"]
)
def test_a_call_that_names_no_repository_is_not_read(tool: str) -> None:
    """Every MCP call reaches the hook, and a thread's post or an email is not GitHub text."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"body": f"Write to {OTHER}."}})

    assert email_screen.screen(payload) is None
    assert email_screen.read_back(payload) is None


@pytest.mark.parametrize(
    ("tool", "arguments", "noted"),
    [
        ("mcp__github__create_pull_request", {"title": "t", "body": "b"}, True),
        ("mcp__github__update_pull_request", {"body": "b"}, True),
        ("mcp__github__pull_request_write", {"method": "update", "title": "t"}, True),
        ("mcp__github__update_pull_request", {"state": "closed"}, False),
        ("mcp__github__pull_request_review_write", {"method": "create", "body": "b"}, False),
        ("mcp__github__add_issue_comment", {"body": "b"}, False),
        ("mcp__github__pull_request_read", {"method": "get"}, False),
    ],
    ids=["create", "update", "folded", "no-text", "review", "comment", "read"],
)
def test_the_read_back_note_goes_on_a_pull_request_description_call_only(
    tool: str, arguments: dict[str, str], noted: bool
) -> None:
    """Every MCP call reaches the hook, so the note must not follow every call it lets through."""
    note = email_screen.read_back(_call(tool, **arguments))

    assert (note is not None) is noted


def test_the_hook_is_wired_on_every_mcp_tool_and_refuses_from_its_script() -> None:
    """The matcher is a regex over the whole tool name, as Claude Code reads one.

    https://code.claude.com/docs/en/hooks, read 2026-11-02: a matcher holding
    a character other than letters, digits, `_`, `-`, spaces, `,` and `|` is a
    JavaScript regular expression, tested unanchored. A matcher naming the two
    pull request tools stopped the guard silently once GitHub renamed one, so
    a renamed tool must reach it (`PL-NZJG`).
    """
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = {
        hook["command"]: entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
    }
    command = 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" pre-mcp'
    matcher = re.compile(commands[command])
    for tool in (
        "mcp__github__create_pull_request",
        "mcp__github__update_pull_request",
        "mcp__github__pull_request_write",
        "mcp__github__add_issue_comment",
    ):
        assert matcher.search(tool), tool
    assert not matcher.search("Bash")

    ran = subprocess.run(
        ["bash", str(REPO / ".claude" / "hooks" / "guard.sh"), "pr-body-email-guard"],
        input=_call("mcp__github__create_pull_request", body=OTHER),
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    )
    assert f"`{OTHER}`" in ran.stdout


def test_a_pull_request_call_the_guard_lets_through_names_the_read_back() -> None:
    """`PL-S2NL`: after a pull request is created or updated, its body is read back.

    The server rewrites a body and still returns success, so the guard puts the
    pointer to the `pull-request` skill beside the call's result. It is context,
    never a decision, so the call goes ahead.
    """
    ran = subprocess.run(
        ["bash", str(REPO / ".claude" / "hooks" / "guard.sh"), "pr-body-email-guard"],
        input=_call("mcp__github__update_pull_request", body="Plain body."),
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    )
    output = json.loads(ran.stdout)["hookSpecificOutput"]
    assert "permissionDecision" not in output
    assert ".claude/skills/pull-request/SKILL.md" in output["additionalContext"]
    assert output["additionalContext"].startswith("Read the published title and body back")


# --- the screen loads nothing it does not use (`PL-NDY5`) ----------------------


def _guard_without_docket(payload: str) -> str:
    """What `guard.py` prints for the email guard on `payload`, with `docket` unimportable."""
    script = (
        "import runpy, sys\n"
        'sys.modules["docket"] = None\n'
        f"sys.argv = [{str(REPO / '.claude' / 'hooks' / 'guard.py')!r}, 'pr-body-email-guard']\n"
        "runpy.run_path(sys.argv[0], run_name='__main__')\n"
    )
    ran = subprocess.run(
        [sys.executable, "-I", "-c", script],
        input=payload,
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    )
    return ran.stdout


def test_the_screen_still_refuses_with_docket_unimportable() -> None:
    """A rename inside `docket` can no longer switch the email guard off."""
    output = json.loads(
        _guard_without_docket(_call("mcp__github__create_pull_request", body=f"To {PERSON}."))
    )["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert f"`{PERSON}`" in output["permissionDecisionReason"]
    assert "could not check" not in json.dumps(output)


def test_the_screen_loads_no_docket_module() -> None:
    """Every MCP call pays for what the screen imports, so it imports no `docket` module."""
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(REPO / 'tools')!r})\n"
        "import email_screen\n"
        "print(sorted(name for name in sys.modules if name.split('.')[0] == 'docket'))\n"
    )
    ran = subprocess.run(
        [sys.executable, "-I", "-c", script], capture_output=True, text=True, check=True
    )
    assert ran.stdout.strip() == "[]"


def test_a_pre_push_hook_installed_before_the_move_still_screens() -> None:
    """A session keeps the `pre-push` hook it installed at its start, which ran pr_body_check.py."""
    author = "Claude <noreply@anthropic.com>"
    log = f"\0{'a' * 40}\n{author}\n{author}\nTo {PERSON}.\n"
    ran = subprocess.run(
        [sys.executable, str(REPO / "tools" / "pr_body_check.py"), "--screen-push"],
        input=log,
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert ran.returncode == 1
    assert f"`{PERSON}`" in ran.stderr
