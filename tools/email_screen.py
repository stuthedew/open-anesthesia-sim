"""Keep a person's email address out of what this repository sends to GitHub (`PL-7K31`).

A body is public as soon as GitHub has it, it stays in a description's edit
history after the address is removed, and the squash merge copies a pull
request's body into `main`'s history. So the only point at which an address
can be kept out is before it is sent. Two routes are screened here:

- `decide` is the `pr-body-email-guard`, which `.claude/hooks/guard.py` runs
  before every MCP call (`PL-9KSJ`). It refuses a GitHub call whose text holds
  an address, and adds the read-back note beside a pull request call it lets
  through (`PL-S2NL`).
- `--screen-push` reads the commits a `git push` would publish, for the git
  hook `.claude/hooks/git/pre-push` (`PL-1ZZ0`).

**Why this is its own module** (`PL-NDY5`). The screen used to live in
`tools/pr_body_check.py`, the lost-squash-body check, whose other modes need
`docket`. Importing that file loaded `docket` before every MCP call, for a
screen that uses none of it. Run alone through `guard.py` on 2026-11-04, the
guard took a median of 131 ms with that import and 51 ms without it. A
rename inside `docket` could also make the import fail, which turned the guard
into a note saying it had not checked the call. This module imports only the
standard library and `.claude/hooks/hook_input.py`, and
`tests/unit/test_email_screen.py` runs it with `docket` unimportable.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))

from hook_input import deny, log_refusal

#: An email address as a person writes one: a local part, `@`, and a domain
#: ending in a label of letters. A version pin such as `react@18.3.1` ends in
#: digits, so it is not one.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

#: The addresses GitHub text may carry, because each is nobody's own. The
#: `Co-authored-by` trailer `CLAUDE.md` requires on every commit names the
#: first. GitHub commits a merge made on its website as the second. The third
#: is the user of GitHub's SSH address for a repository,
#: `git@github.com:owner/name`, which publishes no one's address (`PL-D16Y`).
ALLOWED_EMAILS = frozenset({"noreply@anthropic.com", "noreply@github.com", "git@github.com"})

#: The domains whose addresses are nobody's own, each with the domains below
#: it. GitHub gives every account an address under the first, and writes it
#: as the author of a squash merge made on its website, so `main`'s history
#: is full of `<login>@users.noreply.github.com` (`PL-D16Y`). The rest are
#: reserved for examples and tests, so no person can hold an address under
#: one: the second-level names in RFC 2606 § 3 and the top-level names in
#: § 2 (https://www.rfc-editor.org/rfc/rfc2606, read 2026-11-03). This
#: repository's tests use them for every address they need.
ALLOWED_DOMAINS = (
    "users.noreply.github.com",
    "example.com",
    "example.net",
    "example.org",
    "example",
    "invalid",
    "localhost",
    "test",
)

#: The fields `read_back` needs before it notes a call: a pull request's title
#: or its description.
DESCRIPTION_FIELDS = ("title", "body")

#: The fields by which a GitHub call names its repository. Every GitHub tool
#: that publishes text takes both, and a Projects thread's post or an email
#: takes neither.
REPOSITORY_FIELDS = ("owner", "repo")

#: The pull request tools whose body is not the pull request's description, so
#: there is nothing for the read-back note to send a session to compare.
NO_READ_BACK = frozenset({"pull_request_review_write", "add_reply_to_pull_request_comment"})

#: The note the hook adds beside a pull request call it lets through (`PL-S2NL`).
READ_BACK_NOTE = (
    "Read the published title and body back with pull_request_read and compare them with "
    "what was sent: the server can rewrite a body and still return success. "
    ".claude/skills/pull-request/SKILL.md, the pull-request skill, has the cases, and says "
    "when to ask `bin/docket arm` (`PL-S2NL`)."
)

#: The hook `screen` refuses for, as the guards' refusal log names it. The
#: refusal is built by `hook_input.deny`, so it is logged like every other
#: guard's and `PL-SG93`'s counts can see it (`PL-HHKC`).
GUARD = "pr-body-email-guard"

#: Why an address may not be published, which every refusal of this screen
#: gives, whichever route the text was taking.
WHY_NO_ADDRESS = (
    "GitHub publishes text as soon as it has it, keeps a description's edit history "
    "after an address is removed, and the squash merge copies a pull request's body into "
    "`main`'s history. Remove the address, or name the person by their GitHub login "
    "(`PL-7K31`)."
)


def admitted(address: str) -> bool:
    """Whether `address` is one GitHub text may carry, by `ALLOWED_EMAILS` and `ALLOWED_DOMAINS`."""
    address = address.lower()
    if address in ALLOWED_EMAILS:
        return True
    domain = address.rsplit("@", 1)[-1]
    return any(domain == name or domain.endswith("." + name) for name in ALLOWED_DOMAINS)


def addresses(text: str) -> list[str]:
    """Each email address in `text` that could be a person's, once, in the order found."""
    found: list[str] = []
    for address in EMAIL_RE.findall(text):
        if not admitted(address) and address not in found:
            found.append(address)
    return found


def _github_call(payload: str) -> tuple[str, dict[str, object]] | None:
    """The tool name and arguments of a call to GitHub, or `None`.

    A call to GitHub is one that names a repository by `REPOSITORY_FIELDS`.
    The tool's name is not read, because the GitHub server owns it and
    changes it without notice (`PL-NZJG`). Anything else, including a payload
    that cannot be read, is `None`.
    """
    try:
        call = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(call, dict):
        return None
    tool = call.get("tool_name")
    arguments = call.get("tool_input")
    if not isinstance(arguments, dict):
        return None
    if not all(isinstance(arguments.get(field), str) for field in REPOSITORY_FIELDS):
        return None
    return (tool if isinstance(tool, str) else ""), arguments


def _strings(value: object, where: str) -> list[tuple[str, str]]:
    """Every string inside `value`, each with the path of fields that leads to it."""
    if isinstance(value, str):
        return [(where, value)]
    if isinstance(value, dict):
        return [
            found
            for key, item in value.items()
            for found in _strings(item, f"{where}.{key}" if where else str(key))
        ]
    if isinstance(value, list):
        return [
            found for at, item in enumerate(value) for found in _strings(item, f"{where}[{at}]")
        ]
    return []


def screen(payload: str) -> str | None:
    """The PreToolUse refusal for a GitHub call that would publish an email address.

    `payload` is the JSON a hook receives on stdin. A body is public as soon
    as it is sent, it stays in the description's edit history after it is
    removed, and the squash merge copies a pull request's body into `main`'s
    history. So the only point at which an address can be kept out is before
    the call (`PL-7K31`, found when `#1480` opened with the owner's address).
    Every MCP call reaches this screen, and it reads each one `_github_call`
    picks out, whatever the tool is called (`PL-NZJG`).

    **Every string the call carries is read, whatever its field is called**
    (`PL-D16Y`, `PL-1ZZ0`). The screen read only a title and a body, so a
    merge's `commit_message`, which becomes the squash commit on `main`, and
    the file content of `push_files` published an address unread. A field
    GitHub does not publish, such as a branch name, holds no address, so
    reading it costs nothing.

    The result is the JSON for the hook to print, which names each address
    and the field it was found in, or `None` to let the call through. A
    refusal is logged to the guards' refusal log, as every guard's is. A
    payload that cannot be read is let through, because a false refusal
    blocks correct work.
    """
    call = _github_call(payload)
    if call is None:
        return None
    _, arguments = call
    found: list[str] = []
    fields: list[str] = []
    for where, text in _strings(arguments, ""):
        for address in addresses(text):
            if address not in found:
                found.append(address)
            if where not in fields:
                fields.append(where)
    if not found:
        return None
    reason = (
        "Refused: this call holds the email address(es) "
        + ", ".join(f"`{address}`" for address in found)
        + ", in "
        + ", ".join(f"`{field}`" for field in fields)
        + ". "
        + WHY_NO_ADDRESS
        + " Then send the call again."
    )
    return deny(GUARD, "email-address", reason, payload)


def screen_push(log: str) -> list[str]:
    """Where each email address sits in the commits a push is about to publish (`PL-1ZZ0`).

    `log` is what `.claude/hooks/git/pre-push` hands over: `git log -p -U0`
    of the commits no remote-tracking ref holds, each commit opening with a
    NUL and then its hash, its author, its committer and its message. A
    commit's diff begins at its first `diff --git` line. In the diff, only a
    line the commit adds is read, so a line it removes or a file's name is
    not. A merge's changes are not in `log` at all, because `git log -p`
    shows none for a merge. Each result line names the address, the commit
    and where in it the address is, and an empty list lets the push through.
    """
    found: list[str] = []
    for commit in log.split("\0")[1:]:
        lines = commit.split("\n")
        sha = lines[0][:12]
        place = "its author or committer"
        in_diff = False
        for at, line in enumerate(lines[1:]):
            if line.startswith("diff --git "):
                in_diff = True
                place = "its changes"
                continue
            if in_diff:
                if line.startswith("+++ "):
                    place = "lines it adds to `" + line[4:].removeprefix("b/") + "`"
                if not line.startswith("+") or line.startswith("+++ "):
                    continue
                text = line[1:]
            else:
                if at == 2:
                    place = "its message"
                text = line
            for address in addresses(text):
                entry = f"`{address}` in commit {sha}, {place}"
                if entry not in found:
                    found.append(entry)
    return found


def read_back(payload: str) -> str | None:
    """The note for a pull request call that `screen` let through, or `None` (`PL-S2NL`).

    The server can rewrite a pull request's title or body and still return
    success, so a session reads it back. The note goes on a call that
    `_github_call` picks out, that carries a string in one of
    `DESCRIPTION_FIELDS`, and whose tool name contains `pull_request`, except
    the tools in `NO_READ_BACK`. A pull request tool renamed without
    `pull_request` in its name gets no note. That loses a reminder and refuses
    nothing, so the name is read here and not in `screen`.
    """
    call = _github_call(payload)
    if call is None:
        return None
    tool, arguments = call
    if not any(isinstance(arguments.get(field), str) for field in DESCRIPTION_FIELDS):
        return None
    name = tool.rsplit("__", 1)[-1]
    if "pull_request" not in name or name in NO_READ_BACK:
        return None
    note = {"hookEventName": "PreToolUse", "additionalContext": READ_BACK_NOTE}
    return json.dumps({"hookSpecificOutput": note})


def decide(payload: str) -> str:
    """The hook output for an MCP call: `screen`'s refusal, else `read_back`'s note, else "".

    `.claude/hooks/guard.py` runs this as the `pr-body-email-guard` on every
    MCP call (`PL-9KSJ`). It is wired on every MCP tool, not on the GitHub
    tools by name, because the GitHub server owns its tool names and changes
    them without notice. It has already folded its issue tools into one
    `issue_write`, and a matcher that named the old tools would have stopped
    this guard silently (`PL-NZJG`). A call that names no repository by
    `owner` and `repo`, such as a Projects thread's post or an email, is not
    read. `.claude/rules/apparatus-standard.md` § "The floor" has the rule, in
    its paragraph on a guard keyed on names that another system owns.

    Text sent to GitHub another way is screened where it is sent. `gh` in Bash
    is kept to reads by `.claude/hooks/gh_write_guard.py`, so its writes come
    back to an MCP call (`PL-3986`). A commit reaches GitHub by `git push`, and
    the `pre-push` hook in `.claude/hooks/git/` screens a session's new
    commits with `screen_push` (`PL-1ZZ0`).

    A payload `screen` cannot read is let through, since a false refusal
    blocks correct work.
    """
    return screen(payload) or read_back(payload) or ""


def main(argv: list[str]) -> int:
    """Run `--screen-push`, the email half of the git `pre-push` hook in `.claude/hooks/git/`.

    It reads the log that hook hands it on standard input, prints a refusal and
    exits 1 where `screen_push` finds an address, and exits 0 where it finds
    none. Any other use exits 2, which the hook reports as a screen that could
    not run.
    """
    if "--screen-push" not in argv:
        print("usage: email_screen.py --screen-push < log", file=sys.stderr)
        return 2
    found = screen_push(sys.stdin.read())
    if not found:
        return 0
    log_refusal(GUARD, "email-address-push", os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
    print(
        "Refused: the commits this push would publish hold an email address, and nothing "
        "was sent:\n\n"
        + "\n".join(f"    {entry}" for entry in found)
        + "\n\n"
        + WHY_NO_ADDRESS
        + " Rewrite each commit that holds one, with `git commit --amend` for the last "
        "commit, or `git reset --soft` to the commit before an earlier one and a new "
        "commit, and push again.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
