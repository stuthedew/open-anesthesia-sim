"""Reconcile the jobs that report a status check on `pull_request` against the required list.

Branch protection matches a required status check by **name**, and that list
lives in repository settings rather than in the tree. So the two sides drift
independently, in two directions, and this repository has been hurt by both:

- **Removing or renaming** a reporting job orphans the requirement named after
  it. Nothing reports it, so every pull request waits forever on a check that
  cannot arrive - pending rather than failing, which does not look like a
  break. `PL-D551` deleting `quality.yml`'s `floor` job did exactly that; it
  cost the project owner a manual merge and cost a session a wrong diagnosis
  (`PL-KPP1`, `#377`).
- **Adding** one creates a check that nothing makes required. `PL-3V8K` split
  the title check out of `checks` into its own job, for a correct and unrelated
  reason, and thereby moved it out from behind the only requirement that had
  been gating it. It stayed ungated for eleven releases, and `#654` merged on a
  failed `pr-title` because of it (`PL-H8YD`).

Until this check, the whole remedy was a comment beside each job key, and both
comments said the same thing: "the required list lives in repository settings,
which no script here can read, so nothing in `make check` or CI will catch the
next one."

**That premise was true of `make check` and false of CI, and it was false for a
narrower reason than anyone had looked for.** `PL-XZD0` was filed expecting the
answer to turn on a credential - `GET /repos/{owner}/{repo}/branches/{branch}/protection`
needs the `administration` permission, which an Actions `GITHUB_TOKEN` can
never hold, because `administration` is not one of the keys a workflow's
`permissions:` block may set. That route is genuinely closed, and `PL-N5WZ` is
this project's recorded dead end on adjacent terrain.

The route that is open needs no credential at all. `GET /repos/{owner}/{repo}/branches/{branch}`
carries `protection.required_status_checks.contexts`, and on a public
repository it answers **unauthenticated**. Measured 2026-09-19 against this
repository with every token stripped from the environment:

    $ env -u GH_TOKEN -u GITHUB_TOKEN curl -s \\
        https://api.github.com/repos/stuthedew/open-anesthesia-sim/branches/main
    "protection": {"required_status_checks": {"contexts": ["checks", "pr-title"], ...

while `.../branches/main/protection` returned 403 `Resource not accessible by
integration` to the same non-admin token in the same minute. So the guard costs
no secret, no permission grant, and no widening of anything - which is what
decided `PL-XZD0` in favour of building it rather than leaving the comments to
stand.

**Both settings surfaces are read, because only one of them holds the answer
today and GitHub is steering the other way.** This repository has one active
ruleset (`Base`, created 2026-08-23) that carries `deletion`, `pull_request`
and `non_fast_forward` rules and **no** `required_status_checks` rule, so the
required contexts live in classic branch protection. Move that setting into the
ruleset - which the GitHub UI encourages - and the classic block would go empty
while the ruleset filled. A check reading only one surface would then report
"nothing is required" and pass, which is the failure `CLAUDE.md` names
explicitly: a check that keeps passing while the guarantee it stands for is
void. So both are read and unioned, and **an empty union is a hard failure**
rather than a quiet pass: a repository whose workflows carry two load-bearing
job names while its settings require nothing is either a real regression or a
blind spot, and neither deserves silence.

**Why it is a step inside `checks` rather than a job of its own.** A new job
reports a new status check, which would itself have to be added to the required
list - the exact trap `PL-H8YD` records. Run as a step, it inherits the
requirement `checks` already carries and adds no name to reconcile. The check
that guards the list is therefore not an entry in it.

**Why it is not wired into `make check`.** Its input is not in the tree. `make
check` runs offline in a bare checkout, and a network call there would be slow,
flaky and wrong-headed; a tool whose answer lives in repository settings is a
CI tool by nature. Run it by hand with `python3 tools/required_checks_check.py`
when changing a job name.

**What it refuses to decide.** Matrix jobs expand into one check per
combination and reusable workflows report as `<caller> / <called>`; this parser
handles neither, and says so and exits non-zero rather than guessing a name.
So with a job's `name:`: it is read where it sits on the key's line, and one
YAML carries past that line, or resolves there before GitHub reports it, is
refused rather than read as its first line (`PL-TMX9`). Likewise an
unreachable API is reported as unreachable and fails - distinctly from a
genuine disagreement - rather than passing on the assumption that nothing has
changed. `CLAUDE.md`: prefer an obvious failure to a plausible
answer when correctness cannot be established.

**Which pull requests a workflow runs for is read once, here** (`PL-848V`).
`triggers` is the one reader of a workflow's `on:`, and `doc_check`'s gate
parity asks it too. Before it, this file and `doc_check` each read a few of the
spellings YAML allows and took the rest for no trigger, and the items `PL-848V`
heads found them one at a time. It reads each form GitHub's workflow schema
gives `on:` - an event name, a list of them, or a mapping keyed by them, block
or flow, on the key's line or the next - and refuses by name and line the YAML
it does not read: a block scalar, an alias, a tag, an explicit key, and a
scalar or flow collection carried past its line.

`reports_on` asks the question both tools have of it: whether every pull
request onto the protected branch runs the workflow. A filter can leave one
out, and then "checks associated with that workflow will remain in a "Pending"
state. A pull request that requires those checks to be successful will be
blocked from merging" (*Workflow syntax for GitHub Actions*, docs.github.com,
read 2026-10-05) - `PL-KPP1`'s pending-forever merge, with both lists agreeing
(`PL-NWSK`). So each filter under `pull_request` or `pull_request_target` is
read for what it leaves out:

- `branches:` and `branches-ignore:` are matched against the branch whose
  protection is read, `--branch`, since GitHub matches them against the branch
  a pull request targets. A filter leaving that branch out makes the workflow
  report nothing there, so a requirement named after one of its jobs reads as
  orphaned rather than agreed (`PL-C72H`). Patterns are matched as that page's
  filter pattern cheat sheet documents them, and one it does not document is
  refused.
- `paths:` and `paths-ignore:` are refused: the name is knowable, but which
  pull requests the filter admits turns on what each one changes, so agreement
  would be false.
- `types:` is refused when it leaves out `opened`, `synchronize` or `reopened`,
  the three a pull-request workflow runs for by default (*Events that trigger
  workflows*, docs.github.com, read 2026-10-05), since the commit a left-out
  activity brings is then never checked.

**A workflow's steps are read once here too** (`PL-S3XS`). `steps` walks
`jobs:` to each job's `steps:` list and gives each step's keys with the line
and column each opens on, so `doc_check` reads a `run:` where a step holds one
rather than wherever a line looks like one: its line regex took a `run:` inside
another block scalar, or under `defaults:`, for a step's shell. A job or step
in a form it does not read - a flow collection, or a job or `steps:` written on
its key's line - comes back refused by name and line, and the steps around it
are read on.

**What agreement here does and does not prove.** It proves that every job
reporting onto a pull request is in the required list, and that every name in
that list is reported by a job. It does not prove that the list blocks a merge:
this repository's protection is set to `non_admins`, so an administrator can
merge past a red required check - which is how `PL-KPP1`'s orphaned `floor`
requirement was recovered from at all. That is a deliberate escape hatch on a
solo project rather than a defect, and it is recorded here so the check is not
read as a guarantee it does not make.

**The escape hatch is declared in the tree, where a reviewer reads it.** A job
that reports a check and is deliberately *not* required carries a
`# not-required: <reason>` line in the comment block above its key. Without one,
the first advisory-only job would make this check fire on every run, which is a
defect in the check rather than a finding - and a check nobody can act on is one
`CLAUDE.md` retires. With one, the exemption is a sentence a reviewer can weigh
instead of a silence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import record_text, split_lines  # noqa: E402
from docket.vcs import REMOTE, default_branch, github_slug, github_token  # noqa: E402

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"

# The events that make a job report a status check onto a pull request.
# `push` is deliberately absent: a job triggered only by `push` reports against
# the commit, never against the pull request, so a requirement naming it would
# never be satisfied on a branch. `drift.yml` is the worked example - it runs on
# `schedule` and `workflow_dispatch` and reports on no pull request at all.
PULL_REQUEST_EVENTS = frozenset({"pull_request", "pull_request_target"})

# What GitHub's workflow schema allows under either of those events: its
# `pull-request-mapping` and `pull-request-target-mapping`, in
# https://github.com/actions/languageservices/blob/main/workflow-parser/src/workflow-v1.0.json
# (read 2026-10-05). Each takes one name or a list of them.
PULL_REQUEST_FILTERS = ("types", "branches", "branches-ignore", "paths", "paths-ignore")

# The activity types a pull-request workflow runs for when `types:` names none:
# "By default, a workflow only runs when a `pull_request` event's activity type
# is `opened`, `synchronize`, or `reopened`", and so with `pull_request_target`
# (*Events that trigger workflows*, docs.github.com, read 2026-10-05).
DEFAULT_TYPES = frozenset({"opened", "synchronize", "reopened"})

NOT_REQUIRED = re.compile(r"#\s*not-required:\s*(?P<reason>\S.*?)\s*$")

# A comment closing a plain scalar on its line: a `#` after white space
# (YAML 1.2.2 § 6.6), which is no part of the value.
TRAILING_COMMENT = re.compile(r"[ \t]+#.*$")

# What opens a value other than a plain scalar (YAML 1.2.2 § 5.3): a block
# scalar's header, a quote, an anchor, alias or tag, a flow collection, or a
# reserved indicator.
NODE_INDICATORS = frozenset("|>\"'&*![]{}%@`")

# Each indicator `triggers` refuses where a node opens, with what it opens there
# (YAML 1.2.2 § 5.3). An anchor is read past on a key's line, where it names the
# value and changes nothing in it, and refused anywhere else.
REFUSED_OPENERS = {
    "|": "a block scalar (`|`), which this reader does not fold",
    ">": "a block scalar (`>`), which this reader does not fold",
    "*": "an alias (`*`), which this reader does not resolve",
    "!": "a tag (`!`), which this reader does not apply",
    "&": "an anchor (`&`) inside its value, which this reader does not read",
    "%": "a directive (`%`), which opens no node",
    "@": "a reserved indicator (`@`), which opens no node",
    "`": "a reserved indicator (a backtick), which opens no node",
    "?": "an explicit key (`?`), which this reader does not read",
    "-": "a block list entry (`-`) where none can open",
    ":": "a value with no key before its `:`",
    ",": "an empty entry before a `,`",
    "]": "a `]` that closes nothing",
    "}": "a `}` that closes nothing",
}

# The spellings of null (YAML 1.2.2 § 10.3.2).
NULLS = frozenset({"", "~", "null", "Null", "NULL"})

# A value `triggers` passes over unread, since no question here turns on it.
UNREAD = object()


class Undecidable(Exception):
    """The tree holds a shape whose check name this parser will not guess.

    `line` is where, counted from 1, wherever the reader knows it, so
    `doc_check` names a declined trigger the way it names its own declines.
    """

    def __init__(self, why: str, line: int | None = None) -> None:
        super().__init__(why)
        self.why = why
        self.line = line


@dataclass(frozen=True)
class Trigger:
    """One event a workflow's `on:` names, at the line naming it.

    `filters` holds what narrows a pull-request event: each key under it, with
    the names it lists in the order written, and nothing where it carries none.
    It is `None` for every other event, whose value no question here turns on
    and nothing reads.
    """

    event: str
    line: int
    filters: dict[str, tuple[str, ...]] | None


@dataclass(frozen=True)
class ReportingJob:
    """A job that reports a status check onto a pull request."""

    workflow: str
    job_id: str
    check_name: str
    not_required: str | None


@dataclass(frozen=True)
class _Line:
    """A line holding more than white space and a comment: its index, indentation and text."""

    index: int
    indent: int
    text: str


def _uncommented(text: str) -> str:
    """`text` without its comment: a `#` opening it or after white space, outside quotes.

    YAML 1.2.2 § 6.6. A quote opens a quoted scalar only where a node can open
    (§ 7.3), so the `'` in `don't` is a character and a `#` after it ends the line.
    """
    quote = ""
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\" and quote == '"':
                index += 1
            elif char == quote:
                if quote == "'" and text[index + 1 : index + 2] == "'":
                    index += 1
                else:
                    quote = ""
        elif char == "#" and (index == 0 or text[index - 1] in " \t"):
            return text[:index]
        elif char in "'\"" and (index == 0 or text[index - 1] in " \t[{,"):
            quote = char
        index += 1
    return text


def _next(lines: Sequence[str], index: int) -> _Line | None:
    """The first line from `index` holding more than white space and a comment.

    Raises `Undecidable` where a tab indents it, which YAML forbids (§ 6.1).
    """
    for at in range(index, len(lines)):
        body = lines[at].lstrip(" ")
        text = _uncommented(body).strip()
        if text:
            if body[:1] == "\t":
                raise Undecidable("a tab indents this line, where YAML takes only spaces", at + 1)
            return _Line(at, len(lines[at]) - len(body), text)
    return None


def _closing_quote(text: str, start: int = 0) -> int:
    """Where the quote closing the scalar `text[start]` opens sits, or -1 past the line's end."""
    quote = text[start]
    index = start + 1
    while index < len(text):
        if quote == '"' and text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            if quote == "'" and text[index + 1 : index + 2] == "'":
                index += 2
                continue
            return index
        index += 1
    return -1


def _quoted(token: str, line: int, what: str) -> str:
    """The scalar a quoted `token` holds, read between its quotes (§ 7.3.1, § 7.3.2)."""
    body = token[1:-1]
    if token[0] == "'":
        return body.replace("''", "'")
    if "\\" in body:
        raise Undecidable(
            f"{what} holds a double-quoted scalar with an escape, which this reader does not "
            "decode",
            line,
        )
    return body


def _item(text: str) -> bool:
    """Whether `text` opens a block list entry (§ 8.2.1)."""
    return text == "-" or text[:2] in ("- ", "-\t")


def _refuse_opener(text: str, line: int, what: str) -> None:
    """Raise `Undecidable` where `text` opens with an indicator this reader does not read."""
    opener = text[:1]
    if opener in "-?:" and text[1:2] not in ("", " ", "\t"):
        return
    if opener and opener in REFUSED_OPENERS:
        raise Undecidable(f"{what} holds {REFUSED_OPENERS[opener]}", line)


def _key(text: str, line: int) -> tuple[str, str] | None:
    """The key a block mapping entry opens `text` with, and what follows its `:`.

    A plain or quoted scalar ended by a `:` that white space or the line's end
    follows (§ 7.3, § 8.2.2), so `on :` and `"on":` name the key `on`. `None`
    where `text` opens no key; a key YAML writes some other way raises
    `Undecidable`, naming it.
    """
    if text[:1] in "'\"":
        end = _closing_quote(text)
        after = text[end + 1 :].lstrip(" \t") if end >= 0 else ""
        if after[:1] != ":" or after[1:2] not in ("", " ", "\t"):
            return None
        return _quoted(text[: end + 1], line, "a key"), after[1:].strip()
    for index, char in enumerate(text):
        if char == ":" and text[index + 1 : index + 2] in ("", " ", "\t"):
            key = text[:index].rstrip()
            _refuse_opener(key or ":", line, "a key")
            return key, text[index + 1 :].strip()
    return None


def _blank(text: str, at: int) -> int:
    """The index of the first character from `at` that is not white space."""
    while at < len(text) and text[at] in " \t":
        at += 1
    return at


def _flow_scalar(text: str, at: int, line: int, what: str) -> tuple[object, int]:
    """The scalar opening at `text[at]` inside a flow collection, and the index past it (§ 7.3)."""
    if text[at] in "'\"":
        end = _closing_quote(text, at)
        if end < 0:
            raise Undecidable(
                f"{what} holds a quoted scalar carried past its line, which this reader does "
                "not join - write it on one line",
                line,
            )
        return _quoted(text[at : end + 1], line, what), end + 1
    if text[at] in "[{":
        raise Undecidable(
            f"{what} holds a collection as a key, which this reader does not read", line
        )
    _refuse_opener(text[at:], line, what)
    end = at
    while end < len(text) and text[end] not in ",[]{}":
        if text[end] == ":" and text[end + 1 : end + 2] in ("", " ", "\t", ",", "]", "}"):
            break
        end += 1
    value = text[at:end].rstrip()
    return (None if value in NULLS else value), end


def _flow(text: str, at: int, line: int, what: str) -> tuple[object, int]:
    """The flow node opening at `text[at]`, and the index past it (§ 7.4).

    A list comes back as `(line, entry)` pairs and a mapping as `{key: (line,
    value)}`, as their block forms do. A collection its line does not close
    raises `Undecidable` (`PL-R417`): read from its first line, `on: [push,`
    over `pull_request]` named no pull-request event.
    """
    carried = (
        f"{what} holds a flow collection carried past its line, which this reader does not "
        "join - write it on one line, or as a block collection"
    )
    at = _blank(text, at)
    if at == len(text):
        raise Undecidable(carried, line)
    opener = text[at]
    if opener not in "[{":
        return _flow_scalar(text, at, line, what)
    closer = "]" if opener == "[" else "}"
    entries: list[tuple[int, object]] = []
    keyed: dict[str, tuple[int, object]] = {}
    at += 1
    while True:
        at = _blank(text, at)
        if at == len(text):
            raise Undecidable(carried, line)
        if text[at] == closer:
            break
        if opener == "[":
            entry, at = _flow(text, at, line, what)
            if text[_blank(text, at) : _blank(text, at) + 1] == ":":
                raise Undecidable(
                    f"{what} holds a mapping inside a flow list, which this reader does not read",
                    line,
                )
            entries.append((line, entry))
        else:
            key, at = _flow_scalar(text, at, line, what)
            if not isinstance(key, str):
                raise Undecidable(
                    f"{what} holds an empty key, which this reader does not read", line
                )
            value: object = None
            at = _blank(text, at)
            if text[at : at + 1] == ":":
                at = _blank(text, at + 1)
                if text[at : at + 1] not in ("", ",", "}"):
                    value, at = _flow(text, at, line, f"`{key}:`")
            if key in keyed:
                raise Undecidable(
                    f"`{key}:` appears twice in {what}, which YAML does not allow", line
                )
            keyed[key] = (line, value)
        at = _blank(text, at)
        if at == len(text):
            raise Undecidable(carried, line)
        if text[at] == ",":
            at += 1
        elif text[at] != closer:
            raise Undecidable(
                f"{what} holds `{text[at]}` where its flow collection expects `,` or `{closer}`",
                line,
            )
    return (entries if opener == "[" else keyed), at + 1


def _inline(text: str, line: int, what: str) -> object:
    """The node `text` holds whole on `line`: a flow collection, or a quoted or plain scalar."""
    if text[:1] in "[{":
        value, end = _flow(text, 0, line, what)
        if text[end:].strip():
            raise Undecidable(
                f"{what} holds `{text[end:].strip()}` after its flow collection", line
            )
        return value
    if text[:1] in "'\"":
        end = _closing_quote(text)
        if end < 0:
            raise Undecidable(
                f"{what} holds a quoted scalar carried past its line, which this reader does "
                "not join - write it on one line",
                line,
            )
        if text[end + 1 :].strip():
            raise Undecidable(f"{what} holds `{text[end + 1 :].strip()}` after its quote", line)
        return _quoted(text[: end + 1], line, what)
    _refuse_opener(text, line, what)
    if _key(text, line) is not None:
        raise Undecidable(
            f"{what} opens a mapping on its key's line, which YAML does not allow", line
        )
    return None if text in NULLS else text


def _not_continued(lines: Sequence[str], index: int, indent: int, what: str) -> None:
    """Raise `Undecidable` where a line from `index` is indented past `indent`.

    Under a value already read whole, such a line is YAML carrying a scalar on
    (§ 7.3.3) - `on: pull_request` over an indented `push` is the one event
    `pull_request push` - or no YAML at all.
    """
    after = _next(lines, index)
    if after is not None and after.indent > indent:
        raise Undecidable(
            f"{what} continues onto a line indented under it, which this reader does not join "
            "- write the value on one line",
            after.index + 1,
        )


def _sequence(lines: Sequence[str], first: _Line, what: str) -> tuple[object, int]:
    """The block list whose first entry is `first`, and the index past it (§ 8.2.1)."""
    entries: list[tuple[int, object]] = []
    entry: _Line | None = first
    while entry is not None and entry.indent == first.indent and _item(entry.text):
        line = entry.index + 1
        rest = entry.text[1:].strip()
        if not rest:
            raise Undecidable(
                f"{what} holds a list entry whose value opens on the line after its `-`, which "
                "this reader does not read",
                line,
            )
        if rest[:1] not in "[{" and _key(rest, line) is not None:
            raise Undecidable(f"{what} holds a mapping in a list entry, where names belong", line)
        entries.append((line, _inline(rest, line, what)))
        _not_continued(lines, entry.index + 1, entry.indent, what)
        entry = _next(lines, entry.index + 1)
    return entries, len(lines) if entry is None else entry.index


def _passed_over(lines: Sequence[str], index: int, indent: int, inline: str) -> int:
    """The index past the value of a key at `indent`, found by indentation alone.

    Every line of a block value is indented past its key, and a list may sit at
    the key's own indentation (§ 6.1, § 8.2.1), so where the value ends needs
    nothing in it read - a block scalar, a `cron:` or an input's description.
    """
    for at in range(index, len(lines)):
        body = lines[at].lstrip(" ")
        text = _uncommented(body).strip()
        if not text:
            continue
        depth = len(lines[at]) - len(body)
        if depth < indent or (depth == indent and (inline or not _item(text))):
            return at
    return len(lines)


def _entry_key(entry: _Line, seen: Iterable[str], what: str) -> tuple[str, str]:
    """The key the block mapping entry `entry` opens, and what follows its `:`.

    Raises `Undecidable` where `entry` opens no key, or one `seen` already
    holds, since YAML allows a key once in a mapping (§ 3.2.1.1).
    """
    line = entry.index + 1
    opened = None if entry.text[:1] in "[{" or _item(entry.text) else _key(entry.text, line)
    if opened is None:
        raise Undecidable(f"{what} holds `{entry.text}` among its keys, and it is no key", line)
    if opened[0] in seen:
        raise Undecidable(
            f"`{opened[0]}:` appears twice in {what}, which YAML does not allow", line
        )
    return opened


def _mapping(
    lines: Sequence[str], first: _Line, what: str, unread: Callable[[str], bool] | None
) -> tuple[object, int]:
    """The block mapping whose first key opens `first`, and the index past it (§ 8.2.2).

    A key `unread` answers yes for is passed over by its indentation, its value
    `UNREAD`, so nothing in it is read or refused.
    """
    keyed: dict[str, tuple[int, object]] = {}
    entry: _Line | None = first
    while entry is not None and entry.indent == first.indent:
        line = entry.index + 1
        key, inline = _entry_key(entry, keyed, what)
        if unread is not None and unread(key):
            keyed[key] = (line, UNREAD)
            end = _passed_over(lines, entry.index + 1, entry.indent, inline)
        else:
            _, value, end = _block(lines, entry.index + 1, entry.indent, inline, line, f"`{key}:`")
            keyed[key] = (line, value)
        entry = _next(lines, end)
        if entry is not None and entry.indent > first.indent:
            raise Undecidable(
                f"a line indented between `{key}:` and the value under it, which YAML does not "
                "allow",
                entry.index + 1,
            )
    return keyed, len(lines) if entry is None else entry.index


def _block(
    lines: Sequence[str],
    index: int,
    indent: int,
    inline: str,
    line: int,
    what: str,
    unread: Callable[[str], bool] | None = None,
) -> tuple[int, object, int]:
    """The value of the key at `indent` on `line`, which `what` names.

    `inline` is what follows the key's `:` on its line, and `index` the line
    after. The value may sit there whole or open on the next line holding more
    than a comment, as a list, a mapping, a flow collection or a scalar (§ 8.2).
    Returns the line it opens on, the value, and the index past it.
    """
    if inline[:1] == "&":
        # An anchor names the value it opens and changes nothing in it (§ 6.9.2).
        inline = (inline.split(None, 1) + [""])[1].strip()
    if inline:
        value = _inline(inline, line, what)
        _not_continued(lines, index, indent, what)
        return line, value, index
    first = _next(lines, index)
    if first is None or first.indent < indent or (first.indent == indent and not _item(first.text)):
        return line, None, index
    if _item(first.text):
        entries, end = _sequence(lines, first, what)
        return first.index + 1, entries, end
    if first.text[:1] not in "[{" and _key(first.text, first.index + 1) is not None:
        keyed, end = _mapping(lines, first, what, unread)
        return first.index + 1, keyed, end
    value = _inline(first.text, first.index + 1, what)
    _not_continued(lines, first.index + 1, indent, what)
    return first.index + 1, value, first.index + 1


def _top_level(lines: Sequence[str], name: str) -> tuple[int, str] | None:
    """The index of the line opening the top-level `name:` key, and what follows its `:`.

    `None` where no top-level key has that name. Two raise `Undecidable`, since
    YAML allows a key once in a mapping (§ 3.2.1.1) and which one a reader of a
    malformed file keeps is not this parser's to guess.
    """
    found: tuple[int, str] | None = None
    for index, raw in enumerate(lines):
        if raw[:1] in ("", " ", "\t", "#"):
            continue
        text = _uncommented(raw).strip()
        if not text or text[:1] in "[{" or _item(text):
            continue
        opened = _key(text, index + 1)
        if opened is not None and opened[0] == name:
            if found is not None:
                raise Undecidable(
                    f"`{name}:` appears twice at the top level, which YAML does not allow",
                    index + 1,
                )
            found = (index, opened[1])
    return found


def _filters(event: str, held: object, line: int) -> dict[str, tuple[str, ...]]:
    """What narrows a pull-request event, by key, and nothing where it holds nothing.

    GitHub's schema gives a pull-request event nothing or a mapping of
    `PULL_REQUEST_FILTERS`, each one name or a list of them; anything else
    raises `Undecidable`, naming it, as does the pair of filters GitHub refuses
    on one event.
    """
    if held is None:
        return {}
    if not isinstance(held, dict):
        form = "a list" if isinstance(held, list) else "a scalar"
        raise Undecidable(
            f"`{event}:` holds {form}, where GitHub's workflow schema takes its filters or nothing",
            line,
        )
    filters: dict[str, tuple[str, ...]] = {}
    for key, (key_line, value) in held.items():
        if key not in PULL_REQUEST_FILTERS:
            raise Undecidable(
                f"`{event}` carries `{key}:`, which GitHub's workflow schema does not allow there",
                key_line,
            )
        if isinstance(value, str):
            listed: list[object] = [value]
        elif isinstance(value, list):
            listed = [name for _, name in value]
        else:
            listed = []
        if not listed or not all(isinstance(name, str) and name for name in listed):
            raise Undecidable(
                f"`{event}`'s `{key}:` holds no name or list of names, which GitHub's workflow "
                "schema requires",
                key_line,
            )
        filters[key] = tuple(name for name in listed if isinstance(name, str))
    for one, other in (("branches", "branches-ignore"), ("paths", "paths-ignore")):
        if one in filters and other in filters:
            raise Undecidable(
                f"`{event}` carries both `{one}:` and `{other}:`, which GitHub refuses on one "
                "event",
                line,
            )
    return filters


def triggers(lines: Sequence[str]) -> dict[str, Trigger]:
    """The events a workflow's `on:` names, each with the line naming it.

    GitHub's workflow schema gives `on:` three forms - an event name, a list of
    them, or a mapping keyed by them - and YAML writes each as a block or a
    flow node, on the key's line or the next (§ 7, § 8). Each is read here
    (`PL-848V`, `PL-4T49`), at any indentation (`PL-GWQ7`), and a comment is no
    part of a name (`PL-PZP7`). A pull-request event's value is read whole,
    since its filters decide which pull requests run it; any other event's is
    passed over by its indentation, unread.

    Raises `Undecidable`, with the line, for YAML this does not read: a block
    scalar, an alias, a tag, an explicit key, and a scalar or flow collection
    carried past its line (`PL-R417`). So too a pull-request event holding what
    GitHub's schema does not allow there, an `on:` naming no event, and a
    workflow with no top-level `on:` or two.
    """
    found = _top_level(lines, "on")
    if found is None:
        raise Undecidable("no `on:` key at the top level", 1)
    index, inline = found
    line, value, end = _block(
        lines, index + 1, 0, inline, index + 1, "`on:`", lambda key: key not in PULL_REQUEST_EVENTS
    )
    after = _next(lines, end)
    if after is not None and after.indent > 0:
        raise Undecidable(
            "a line indented between `on:` and the value under it, which YAML does not allow",
            after.index + 1,
        )
    named: list[tuple[int, str, object]] = []
    if isinstance(value, dict):
        named = [(key_line, event, held) for event, (key_line, held) in value.items()]
    elif isinstance(value, list):
        for entry_line, entry in value:
            if not isinstance(entry, str):
                raise Undecidable("`on:` lists an entry that is no event name", entry_line)
            named.append((entry_line, entry, None))
    elif isinstance(value, str):
        named = [(line, value, None)]
    else:
        raise Undecidable("`on:` names no event", line)
    events: dict[str, Trigger] = {}
    for event_line, event, held in named:
        filters = _filters(event, held, event_line) if event in PULL_REQUEST_EVENTS else None
        events.setdefault(event, Trigger(event, event_line, filters))
    return events


def _branch_pattern(pattern: str, unread: Undecidable) -> re.Pattern[str]:
    """The expression a branch filter's pattern stands for, or `unread` raised.

    As *Workflow syntax for GitHub Actions* § "Filter pattern cheat sheet"
    documents them (docs.github.com, read 2026-10-05): `*` matches a run of
    anything but `/`, `**` a run of anything, `?` and `+` zero or one and one or
    more of the character before, `[]` one of the letters, digits and `a-z`,
    `A-Z` or `0-9` ranges it lists, and `\\` makes the next character plain. A
    construct the cheat sheet does not document is refused rather than guessed.
    """
    parts: list[str] = []
    quantifiable = False
    at = 0
    while at < len(pattern):
        char = pattern[at]
        if char == "*":
            double = pattern[at : at + 2] == "**"
            parts.append(".*" if double else "[^/]*")
            quantifiable = False
            at += 2 if double else 1
            continue
        if char in "?+":
            if not quantifiable:
                raise unread
            parts.append(char)
            quantifiable = False
        elif char == "[":
            close = pattern.find("]", at)
            listed = pattern[at + 1 : close] if close > at else ""
            if not re.fullmatch(r"(?:[a-z]-[a-z]|[A-Z]-[A-Z]|[0-9]-[0-9]|[a-zA-Z0-9])+", listed):
                raise unread
            parts.append(f"[{listed}]")
            quantifiable = True
            at = close
        elif char == "\\":
            if at + 1 == len(pattern):
                raise unread
            at += 1
            parts.append(re.escape(pattern[at]))
            quantifiable = True
        elif char == "]":
            raise unread
        else:
            parts.append(re.escape(char))
            quantifiable = True
        at += 1
    try:
        return re.compile("".join(parts))
    except re.error:
        raise unread from None


def _admits(trigger: Trigger, key: str, branch: str) -> bool:
    """Whether `trigger`'s `key:` filter lets a pull request onto `branch` run it.

    The patterns are read in order, so a `!` pattern after a match excludes the
    branch and a plain one after that includes it again, as the same page
    documents; `branches-ignore:` admits the branches its patterns do not match.
    A `!` pattern under `branches-ignore:`, whose meaning the page leaves
    unsaid, and a `branches:` list of `!` patterns alone, which it says GitHub
    refuses, raise `Undecidable`.
    """
    patterns = (trigger.filters or {})[key]
    unread = f"`{trigger.event}`'s `{key}:` pattern"
    if key == "branches-ignore" and any(pattern.startswith("!") for pattern in patterns):
        raise Undecidable(
            f"{unread} opens with `!`, whose meaning under `branches-ignore:` GitHub does not "
            "document",
            trigger.line,
        )
    if all(pattern.startswith("!") for pattern in patterns):
        raise Undecidable(
            f"`{trigger.event}`'s `branches:` lists only `!` patterns, and GitHub requires one "
            "without",
            trigger.line,
        )
    matched = False
    for pattern in patterns:
        negated = pattern.startswith("!")
        written = pattern[1:] if negated else pattern
        refused = Undecidable(
            f"{unread} `{pattern}` uses what GitHub's filter pattern cheat sheet does not document",
            trigger.line,
        )
        if written.startswith("refs/"):
            raise refused
        if _branch_pattern(written, refused).fullmatch(branch):
            matched = not negated
    return matched if key == "branches" else not matched


def _runs_on_every(trigger: Trigger, branch: str | None) -> bool:
    """Whether `trigger` runs on every pull request onto `branch`.

    False where its branch filter leaves `branch` out. A path filter, a `types:`
    list leaving a default out, and a branch filter with no branch named to
    match it against raise `Undecidable` (module docstring).
    """
    filters = trigger.filters or {}
    for key in ("branches", "branches-ignore"):
        if key not in filters:
            continue
        if branch is None:
            raise Undecidable(
                f"`{trigger.event}` carries a `{key}:` filter, and no branch was named to match "
                "it against",
                trigger.line,
            )
        if not _admits(trigger, key, branch):
            return False
    for key in ("paths", "paths-ignore"):
        if key in filters:
            raise Undecidable(
                f"`{trigger.event}` carries a `{key}:` filter, so GitHub runs it only for the "
                "pull requests that filter admits and leaves its checks pending on the rest",
                trigger.line,
            )
    left_out = sorted(DEFAULT_TYPES - set(filters.get("types", DEFAULT_TYPES)))
    if left_out:
        named = " or ".join(f"`{activity}`" for activity in left_out)
        raise Undecidable(
            f"`{trigger.event}` lists `types:` without {named}, so a commit that activity brings "
            "is never checked",
            trigger.line,
        )
    return True


def reports_on(found: Mapping[str, Trigger], events: Iterable[str], branch: str | None) -> bool:
    """Whether every pull request onto `branch` runs the workflow, by one of `events`.

    `found` is what `triggers` read, and `events` the pull-request events the
    caller counts: both here for `required_checks_check`, `pull_request` alone
    for `doc_check`'s merge gate. The first event that runs on every pull
    request decides yes, since its check runs report on each; one whose branch
    filter leaves `branch` out runs on none there. `branch` is what a branch
    filter is matched against, and `None` where no branch was named.

    Raises `Undecidable` where no event decides yes and one could not be read,
    since the workflow may then run on some pull requests and not others.
    """
    asked = set(events)
    if not asked <= PULL_REQUEST_EVENTS:
        raise ValueError(f"filters are read for {sorted(PULL_REQUEST_EVENTS)} alone")
    declined: Undecidable | None = None
    for event in sorted(asked & found.keys()):
        try:
            if _runs_on_every(found[event], branch):
                return True
        except Undecidable as error:
            declined = declined or error
    if declined is not None:
        raise declined
    return False


def _job_name(job: str, inline: str, below: Sequence[str]) -> str | None:
    """The check name a job's `name:` key gives, as YAML reads it.

    `inline` is what follows the key's `:` on its line, its comment gone, and
    `below` the lines of its value after that one holding more than a comment:
    the lines `_keys` passes over by indentation (`PL-GWQ7`, `PL-CK3F`).

    Two forms are read, the ones a workflow writes: a plain scalar on the key's
    line, which a comment ends (YAML 1.2.2 § 6.6), and a quoted scalar that
    closes on that line and holds no escape, read as what lies between its
    quotes. `None` where the key holds no value, so the job id names the check.

    Every other form raises `Undecidable`, naming it (`PL-TMX9`). Read from the
    key's line alone, `name: >` was the check name `>`, and `name: Long` over
    an indented `title` was `Long` where YAML hands GitHub `Long title`
    (§ 7.3.3, § 8.1). So a block scalar is refused, as is a plain scalar
    carried onto the lines after the key or opening on the line after it, a
    quoted scalar carried past the key's line or holding an escape, and an
    anchor, alias, tag or flow collection. A comment line is no continuation.
    No workflow here writes any of these, so each is refused rather than
    folded, as `doc_check._run_script` refuses them in a `run:` value
    (`PL-R417`).
    """
    form = None
    if inline[:1] in ("|", ">"):
        form = f"a block scalar (`{inline[0]}`)"
    elif inline[:1] in ('"', "'"):
        end = inline.find(inline[0], 1)
        if end < 0 or below:
            form = "a quoted scalar carried past the key's line"
        elif inline[end + 1 : end + 2] == "'" or (inline[0] == '"' and "\\" in inline[1:end]):
            form = "a quoted scalar holding an escape"
        else:
            return inline[1:end]
    elif inline[:1] in NODE_INDICATORS:
        form = f"a YAML node opening `{inline[0]}`"
    elif below:
        form = f"a plain scalar {'carried onto' if inline else 'opening on'} the line after it"
    if form is not None:
        raise Undecidable(
            f"job `{job}` writes its `name:` as {form}, which YAML resolves into the check "
            "name GitHub reports and this parser does not - write the name on the key's line"
        )
    return inline or None


def _not_required(lines: Sequence[str], job: _Line) -> str | None:
    """The reason a `# not-required:` comment gives the job whose key opens `job`, or `None`.

    Read from the comment lines directly above the key, at its indentation; a
    comment at another passes through, and a blank line or a line holding more
    than a comment ends them, since adjacency is the whole claim to being this
    job's exemption. Where two give one, the nearer the key holds.
    """
    for index in range(job.index - 1, -1, -1):
        body = lines[index].lstrip()
        if not body.startswith("#"):
            return None
        if len(lines[index]) - len(lines[index].lstrip(" ")) == job.indent:
            if found := NOT_REQUIRED.search(body.rstrip()):
                return found.group("reason")
    return None


def _first_job(lines: Sequence[str]) -> tuple[int, _Line | None] | None:
    """The index of the line opening the top-level `jobs:`, and the line its first job opens.

    `None` where no top-level key is `jobs`, and no first job where it holds
    none. `jobs:` written as a flow mapping, on its key's line or the next,
    raises `Undecidable` naming the form (`PL-4T49`).
    """
    found = _top_level(lines, "jobs")
    if found is None:
        return None
    start, inline = found
    if inline:
        raise Undecidable(
            "`jobs:` holds its value on the key's line, which this parser does not read - "
            "write the jobs as a block mapping under it",
            start + 1,
        )
    first = _next(lines, start + 1)
    if first is None or first.indent == 0:
        return start, None
    if first.text[:1] in "[{" or _item(first.text):
        raise Undecidable(
            "`jobs:` holds a flow collection or a list on the line after it, which this parser "
            "does not read - write the jobs as a block mapping",
            first.index + 1,
        )
    return start, first


def _jobs(lines: list[str], workflow: str) -> list[ReportingJob]:
    """Return every job in the workflow, with the check name it would report.

    The jobs are the keys of the block mapping under `jobs:`, and each job's
    keys those of the mapping under it, read through `_keys`, which passes each
    value over by its indentation, as `steps` reads them (`PL-CK3F`). So a line
    of a value - a `run: |` body, a quoted scalar carried across lines - is
    never read as a key, and only a structural line meets the tab guard: read a
    physical line at a time, a here-document's tab-led line was refused as a
    tab indenting it. YAML allows any indentation (§ 6.1, § 8.2.2), so a
    workflow indented four spaces reads as its two-space twin (`PL-GWQ7`).
    `jobs:` written as a flow mapping, on its key's line or the next, a job
    written on its own key's line or holding a list, and a line indented
    between a mapping's key and its keys, raise `Undecidable` naming the form
    (`PL-4T49`): read a line at a time, `{lint:` was a job, and a carried
    `runs-on:` another.
    """
    opened = _first_job(lines)
    if opened is None:
        raise Undecidable("no `jobs:` block at the top level")
    _, first = opened
    if first is None:
        return []

    jobs: list[ReportingJob] = []
    after = first.index
    for job, inline, at, end in _keys(lines, first, "`jobs:`"):
        after = end
        if inline:
            raise Undecidable(
                f"job `{job}` is written on its key's line, which this parser does not read "
                "- write its keys as a block mapping under it",
                at.index + 1,
            )
        display_name: str | None = None
        body = _next(lines, at.index + 1)
        if body is not None and body.index < end:
            if body.text[:1] in "[{" or _item(body.text):
                raise Undecidable(
                    f"job `{job}` holds a flow collection or a list, which this parser does not "
                    "read - write its keys as a block mapping",
                    body.index + 1,
                )
            inner = body.index
            for key, held, key_line, value_end in _keys(lines, body, f"job `{job}`"):
                inner = value_end
                if key == "name":
                    below = [
                        line
                        for line in lines[key_line.index + 1 : value_end]
                        if _uncommented(line.lstrip(" ")).strip()
                    ]
                    display_name = _job_name(job, held, below)
                elif key == "strategy":
                    raise Undecidable(
                        f"job `{job}` declares `strategy:` - a matrix expands into one check "
                        "per combination, and this parser will not guess those names"
                    )
                elif key == "uses":
                    raise Undecidable(
                        f"job `{job}` calls a reusable workflow - its checks report as "
                        "`<caller> / <called>`, which this parser will not guess"
                    )
            stray = _next(lines, inner)
            if stray is not None and stray.index < end:
                raise Undecidable(
                    f"a line indented between job `{job}` and its keys, which YAML does not allow",
                    stray.index + 1,
                )
        jobs.append(
            ReportingJob(
                workflow=workflow,
                job_id=job,
                check_name=display_name or job,
                not_required=_not_required(lines, at),
            )
        )
    stray = _next(lines, after)
    if stray is not None and stray.indent > 0:
        raise Undecidable(
            "a line indented between `jobs:` and the jobs under it, which YAML does not allow",
            stray.index + 1,
        )
    return jobs


@dataclass(frozen=True)
class Step:
    """One entry of a job's `steps:` list, at the line its `-` opens on, counted from 1.

    `keys` maps each key the step carries to the index of the line it opens on
    and its column, which is where its value is read from. Where the step, or
    the job holding it, is in a form `steps` does not read, `refused` names it
    and `keys` is empty.
    """

    line: int
    keys: dict[str, tuple[int, int]] = field(default_factory=dict)
    refused: Undecidable | None = None


def _keys(lines: Sequence[str], first: _Line, what: str) -> Iterator[tuple[str, str, _Line, int]]:
    """Each key of the block mapping whose first key opens `first`, its value passed over unread.

    Yields the key, what follows its `:` on its line, the line it opens and the
    index past its value, which ends where indentation alone says it does
    (`_passed_over`), so no line of a value - another key's block scalar, a
    mapping nested under it - is read as a key. `first` may hold the text after
    a list entry's `-`, at the column it opens. A line among the keys that
    opens none raises `Undecidable`, as does a key written twice (§ 8.2.2).
    """
    seen: set[str] = set()
    entry: _Line | None = first
    while entry is not None and entry.indent == first.indent:
        key, inline = _entry_key(entry, seen, what)
        seen.add(key)
        end = _passed_over(lines, entry.index + 1, entry.indent, inline)
        yield key, inline, entry, end
        entry = _next(lines, end)


def _step_keys(lines: Sequence[str], entry: _Line) -> dict[str, tuple[int, int]]:
    """Each key the step whose `-` opens `entry` carries: the index of its line, and its column.

    The step is a block mapping, opening after the `-` or on the line below it.
    Any other node raises `Undecidable` naming it: a flow mapping, which read a
    line at a time kept its closing brace in the command (`PL-S3XS`), an alias,
    an anchor, a tag or a scalar.
    """
    rest = entry.text[1:].lstrip(" \t")
    if rest:
        first = _Line(entry.index, entry.indent + len(entry.text) - len(rest), rest)
    else:
        below = _next(lines, entry.index + 1)
        if below is None or below.indent <= entry.indent:
            raise Undecidable("this step holds nothing", entry.index + 1)
        first = below
    if first.text[:1] in "[{":
        raise Undecidable(
            f"this step is written as a flow collection (`{first.text[0]}`), which this reader "
            "does not read - write it as a block mapping",
            first.index + 1,
        )
    if _key(first.text, first.index + 1) is None:
        raise Undecidable(
            f"this step opens no block mapping, but `{first.text}`, which this reader does not "
            "read - write it as a block mapping",
            first.index + 1,
        )
    return {
        key: (opened.index, opened.indent) for key, _, opened, _ in _keys(lines, first, "this step")
    }


def _job_steps(
    lines: Sequence[str], job: str, inline: str, opened: _Line, end: int
) -> Iterator[Step]:
    """The steps of job `job`, its key `opened` holding `inline` and its value ending at `end`.

    A step in a form this does not read comes back refused, and the steps after
    it are read on. A job, or a `steps:`, in a form this does not read raises
    `Undecidable`, naming it, after the steps read before it.
    """
    if inline:
        raise Undecidable(
            f"job `{job}` is written on its key's line, which this reader does not read - "
            "write its keys as a block mapping under it",
            opened.index + 1,
        )
    body = _next(lines, opened.index + 1)
    if body is None or body.index >= end:
        return
    if body.text[:1] in "[{" or _item(body.text):
        raise Undecidable(
            f"job `{job}` holds a flow collection or a list, which this reader does not read - "
            "write its keys as a block mapping",
            body.index + 1,
        )
    for key, held, key_line, value_end in _keys(lines, body, f"job `{job}`"):
        if key != "steps":
            continue
        if held:
            raise Undecidable(
                f"job `{job}` holds its `steps:` on the key's line, which this reader does not "
                "read - write them as a block list under it",
                key_line.index + 1,
            )
        entry = _next(lines, key_line.index + 1)
        column = None if entry is None else entry.indent
        while entry is not None and entry.index < value_end:
            if entry.indent != column or not _item(entry.text):
                raise Undecidable(
                    f"job `{job}`'s `steps:` holds `{entry.text}` where a list entry belongs, "
                    "which this reader does not read",
                    entry.index + 1,
                )
            step_end = _passed_over(lines, entry.index + 1, entry.indent, "-")
            try:
                keys = _step_keys(lines, entry)
            except Undecidable as unread:
                yield Step(entry.index + 1, refused=unread)
            else:
                yield Step(entry.index + 1, keys)
            entry = _next(lines, step_end)


def steps(lines: Sequence[str]) -> list[Step]:
    """Every step a workflow's jobs carry, in the order written (`PL-S3XS`).

    A step is an entry of the block list a job's `steps:` holds, and a job a key
    of the block mapping under the top-level `jobs:`, where GitHub's workflow
    schema puts them. Each value is passed over by its indentation alone, so a
    key nested deeper is no step's: a line of another key's block scalar, an
    action's `with:` input, or the `run:` of a `defaults:` block, which sets
    the shell steps run in and runs nothing. Read a line at a time, each was a
    `run:` step to `doc_check`.

    A step or job in a form this does not read comes back as a `Step` that
    names it in `refused`, at its line, and the rest are read on: a job written
    on its key's line, a `steps:` held there or holding no block list, and a
    step that is no block mapping (`PL-R417`). A `jobs:` it does not read raises
    `Undecidable`, as `_jobs` does.
    """
    opened = _first_job(lines)
    first = None if opened is None else opened[1]
    if first is None:
        return []
    read: list[Step] = []
    for job, held, at, end in _keys(lines, first, "`jobs:`"):
        try:
            for step in _job_steps(lines, job, held, at, end):
                read.append(step)
        except Undecidable as unread:
            read.append(Step(unread.line or at.index + 1, refused=unread))
    return read


def reporting_jobs(workflow_dir: Path, branch: str | None = None) -> list[ReportingJob]:
    """Return every job in the tree that reports a status check onto a pull request.

    `branch` is the protected branch, which a `branches:` or `branches-ignore:`
    filter is matched against (`PL-C72H`). With none named, a workflow carrying
    one raises `Undecidable` rather than being guessed in or out.
    """
    found: list[ReportingJob] = []
    for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        lines = split_lines(path.read_text(encoding="utf-8"))
        try:
            if not reports_on(triggers(lines), PULL_REQUEST_EVENTS, branch):
                continue
            found.extend(_jobs(lines, path.name))
        except Undecidable as exc:
            where = f"{path}:{exc.line}" if exc.line else f"{path}"
            raise Undecidable(f"{where}: {exc}", exc.line) from exc
    return found


def _get(url: str, token: str | None, attempts: int = 3) -> object:
    """GET a JSON document, retrying a transient failure before giving up.

    The token is optional and buys only rate limit: every endpoint read here
    answers unauthenticated on a public repository. In Actions it is the
    automatic `GITHUB_TOKEN`, which lifts the limit from 60 requests an hour per
    runner IP - shared across every runner - to 1,000 per hour for this
    repository, and that is the whole of what it is for.
    """
    # The URL is always this module's literal API root plus a repo slug.
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", API_VERSION)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"could not read {url}: {last}")


def required_contexts(repo: str, branch: str, token: str | None) -> tuple[set[str], list[str]]:
    """Return the required status check names on `branch`, and which surfaces held them.

    Both surfaces are read. Classic branch protection is where this repository
    keeps them today; rulesets are where GitHub's UI now steers, and a migration
    would empty one while filling the other with nothing to announce it.
    """
    contexts: set[str] = set()
    sources: list[str] = []

    branch_doc = _get(f"{API_ROOT}/repos/{repo}/branches/{branch}", token)
    protection: dict[str, object] = {}
    if isinstance(branch_doc, dict):
        protection = branch_doc.get("protection") or {}
    status_checks = protection.get("required_status_checks")
    classic = status_checks.get("contexts") or [] if isinstance(status_checks, dict) else []
    if classic:
        contexts.update(classic)
        sources.append("classic branch protection")

    rules = _get(f"{API_ROOT}/repos/{repo}/rules/branches/{branch}", token)
    from_rulesets: set[str] = set()
    if isinstance(rules, list):
        for rule in rules:
            if not isinstance(rule, dict) or rule.get("type") != "required_status_checks":
                continue
            parameters = rule.get("parameters") or {}
            for check in parameters.get("required_status_checks") or []:
                if isinstance(check, dict) and check.get("context"):
                    from_rulesets.add(check["context"])
    if from_rulesets:
        contexts.update(from_rulesets)
        sources.append("a ruleset")

    return contexts, sources


def reconcile(reporting: dict[str, ReportingJob], required: set[str]) -> list[tuple[str, str]]:
    """Compare the two sets and return `(headline, what it means)` for each disagreement.

    Pure, and deliberately separate from both the parse and the API read: this
    is the decidable half, so it is the half that can be tested without a tree
    or a network.
    """
    problems: list[tuple[str, str]] = []
    exempt = {name for name, job in reporting.items() if job.not_required}

    if not required:
        problems.append(
            (
                "no required status check is set on this branch, by either classic branch "
                "protection or a ruleset",
                "Every job above can go red without blocking a merge. Either the requirement "
                "was removed, or it moved to a surface this check does not read.",
            )
        )
        return problems

    orphaned = sorted(required - set(reporting))
    if orphaned:
        problems.append(
            (
                f"required but reported by no job: {', '.join(orphaned)}",
                "Nothing will ever report these, so every pull request waits on them forever - "
                "pending rather than failing. Rename the job back, or drop the requirement in "
                "settings.",
            )
        )

    ungated = sorted(set(reporting) - required - exempt)
    if ungated:
        problems.append(
            (
                f"reports on a pull request but is not required: {', '.join(ungated)}",
                "These can go red without blocking a merge. Add each to the required list in "
                "settings, or declare a `# not-required: <reason>` above the job key.",
            )
        )

    stale = sorted(exempt & required)
    if stale:
        problems.append(
            (
                f"declared `not-required` but required in settings: {', '.join(stale)}",
                "The comment and the setting disagree. Delete the comment, or drop the "
                "requirement.",
            )
        )

    return problems


def _repo_from_git(root: Path) -> str:
    """Return `owner/name` from the origin remote."""
    try:
        url = record_text(
            subprocess.run(
                ["git", "-C", str(root), "remote", "get-url", REMOTE],
                capture_output=True,
                check=True,
            ).stdout
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"no --repo given and no {REMOTE} remote to read one from") from exc
    slug = github_slug(url)
    if slug is None:
        raise RuntimeError(f"cannot read owner/name out of the {REMOTE} remote: {url}")
    return slug


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/name; defaults to $GITHUB_REPOSITORY, then to the origin remote",
    )
    parser.add_argument(
        "--branch",
        # On a `pull_request` run this is the branch the pull request targets,
        # which is exactly the branch whose protection is about to gate it. Off
        # a pull request there is no such branch, and the default branch is the
        # one every trigger and the release process name - read from
        # `vcs.default_branch` rather than spelt here (`PL-9KLN`).
        default=os.environ.get("GITHUB_BASE_REF") or default_branch(root),
        help="the protected branch to read; defaults to $GITHUB_BASE_REF, then the default branch",
    )
    args = parser.parse_args(argv)

    repo = args.repo or _repo_from_git(root)
    token = github_token()

    try:
        jobs = reporting_jobs(root / ".github" / "workflows", args.branch)
    except Undecidable as exc:
        print(f"required-checks: cannot decide what this tree reports - {exc}")
        print(
            "required-checks: reconcile the required list by hand, or teach this parser the shape."
        )
        return 1

    reporting = {job.check_name: job for job in jobs}

    try:
        required, sources = required_contexts(repo, args.branch, token)
    except RuntimeError as exc:
        print(f"required-checks: {exc}")
        print(
            "required-checks: the settings side could not be read, so nothing was compared. "
            "This is not a clean result - re-run it."
        )
        return 1

    print(f"required-checks: {repo} @ {args.branch}")
    for name, job in sorted(reporting.items()):
        mark = f"  (exempt: {job.not_required})" if job.not_required else ""
        print(f"  reports on a pull request: {name}  [{job.workflow}]{mark}")
    held = " and ".join(sources) if sources else "nothing"
    print(f"  required by {held}: {', '.join(sorted(required)) or '(none)'}")

    problems = reconcile(reporting, required)
    for headline, meaning in problems:
        print(f"required-checks: FAIL - {headline}")
        print(f"  {meaning}")
    if problems:
        return 1

    print("required-checks: OK - the two lists agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
