"""Which sessions worked a closed item, joined from the session ledger through its pull request.

The facts about a session - the model that served it, its effort level, its
cost - belong to the session, not to an item. One session often closes
several items, and it keeps spending after the commit that closes one. So
`docs/session-ledger.tsv` stores each session once, and the model review
writes it from the harness's own record (`PL-92ZN`). This module joins an
item to its rows at read time, so `docket show` can print one item whole
without a second copy of the facts (`PL-70M6`).

The join runs from the item's `pr:` to the squash commit on the default
branch whose subject ends `(#N)`, then to every `claude.ai/code/session_...`
URL in that commit's message. A `Claude-Session:` trailer holds such a URL,
and so does a pull request body, where the URL usually stands on a line of
its own. Where the commit names no session, the body record that
`tools/pr_body_check.py` wrote under `docs/pr-bodies/` is read instead. Each
session id found is then looked up in the ledger.

`item_sessions` is the one implementation of the join. The model review
calls it rather than writing its own (`PL-63CB`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .model import Item, pr_number
from .vcs import RECORDS, Runner, squash_message

#: The ledger, relative to the project root. The model review is its only
#: writer, and `docs/maintainer.md` § "The session ledger records what model
#: and effort worked each item" says how it is refreshed.
LEDGER_NAME = "docs/session-ledger.tsv"

#: A session's link, as a commit trailer or a pull request body writes it.
#: The id is read from the link and not from a bare `session_` word, which
#: prose about sessions also contains.
SESSION_URL_RE = re.compile(r"claude\.ai/code/(session_[A-Za-z0-9]+)")

#: A cost as the ledger writes it: dollars, in plain decimal digits.
COST_RE = re.compile(r"[0-9]+(\.[0-9]+)?")

#: The ledger columns this module reads. A ledger missing one is refused.
LEDGER_COLUMNS = ("session_id", "configured_model", "last_served_model", "effort_level", "cost_usd")


@dataclass(frozen=True)
class LedgerRow:
    """One session's row in the ledger: what served it, at what effort, and what it cost."""

    session_id: str
    configured_model: str
    last_served_model: str
    effort_level: str
    cost_usd: str


@dataclass(frozen=True)
class Ledger:
    """Every row of the ledger by session id, or why the ledger could not be read."""

    rows: dict[str, LedgerRow]
    declined: str = ""


def read_ledger(root: Path) -> Ledger:
    """The ledger at `root / LEDGER_NAME`, or a declined `Ledger` saying why it was not read.

    The file is split on tabs and newlines alone. Titles hold double quotes
    that no writer escaped, so a CSV reader's quoting would misread them.
    """
    path = root / LEDGER_NAME
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return Ledger({}, declined=f"{LEDGER_NAME} does not exist in this checkout")
    except (OSError, UnicodeDecodeError) as error:
        return Ledger({}, declined=f"{LEDGER_NAME} could not be read ({error})")
    lines = text.split("\n")
    header = lines[0].split("\t")
    missing = [name for name in LEDGER_COLUMNS if name not in header]
    if missing:
        return Ledger({}, declined=f"{LEDGER_NAME} has no {', '.join(missing)} column")
    at = {name: header.index(name) for name in LEDGER_COLUMNS}
    rows: dict[str, LedgerRow] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        values = {name: cells[i].strip() if i < len(cells) else "" for name, i in at.items()}
        rows[values["session_id"]] = LedgerRow(**values)
    return Ledger(rows)


def session_ids(text: str) -> tuple[str, ...]:
    """Every session a message links to, in the order first named, each once."""
    return tuple(dict.fromkeys(SESSION_URL_RE.findall(text)))


@dataclass(frozen=True)
class JoinedSession:
    """One session that worked the item, and its ledger row, or None where the ledger has none."""

    session_id: str
    row: LedgerRow | None


@dataclass(frozen=True)
class ItemSessions:
    """The sessions joined to one item, or the plain reason the join found none.

    `sessions` is empty exactly when `unjoined` says why, so no reader can take
    an empty tuple for an item that no session worked. `source` names where the
    session ids were read. `ledger_declined` is set when the ids were found but
    the ledger could not be read, so every row is None for that reason rather
    than because the ledger lacks the session.
    """

    pr: int | None
    sessions: tuple[JoinedSession, ...] = ()
    source: str = ""
    unjoined: str = ""
    ledger_declined: str = ""


def item_sessions(
    item: Item,
    root: Path,
    runner: Runner | None = None,
    *,
    ask_git: bool = True,
    ledger: Ledger | None = None,
) -> ItemSessions:
    """Join `item` to the sessions that worked it, through its pull request.

    `runner` defaults to `docket.vcs`'s own, as every read there does.
    `ask_git=False` asks git nothing, as `--no-git` does, so the body record
    alone is read. Pass `ledger` to read the file once across many items; it
    is read here when omitted.
    """
    pr = pr_number(item.pr)
    if pr is None:
        if item.pr:
            return ItemSessions(None, unjoined=f"its `pr:` value `{item.pr}` is not a number")
        return ItemSessions(None, unjoined="it has no `pr:`, so there is no pull request to join")
    ids: tuple[str, ...] = ()
    source = ""
    commit_miss = ""
    if not ask_git:
        commit_miss = "`--no-git` asks git nothing, so the squash commit was not read"
    else:
        squash = squash_message(root, pr, runner=runner)
        if squash.declined:
            commit_miss = f"the squash commit for #{pr} was not read: {squash.declined}"
        elif not squash.found:
            commit_miss = f"no squash commit on the default branch has a subject ending (#{pr})"
        else:
            ids = session_ids(squash.message)
            source = f"squash commit {squash.commit[:12]}"
            if not ids:
                commit_miss = f"squash commit {squash.commit[:12]} names no session"
    if not ids:
        record = root / RECORDS / f"{pr}.md"
        try:
            ids = session_ids(record.read_text(encoding="utf-8"))
        except FileNotFoundError:
            record_miss = f"there is no {RECORDS}{pr}.md"
        except (OSError, UnicodeDecodeError) as error:
            record_miss = f"{RECORDS}{pr}.md could not be read ({error})"
        else:
            record_miss = f"{RECORDS}{pr}.md names no session"
            source = f"{RECORDS}{pr}.md"
        if not ids:
            return ItemSessions(pr, unjoined=f"{commit_miss}, and {record_miss}")
    if ledger is None:
        ledger = read_ledger(root)
    joined = tuple(JoinedSession(i, ledger.rows.get(i)) for i in ids)
    return ItemSessions(pr, joined, source=source, ledger_declined=ledger.declined)


#: The section's heading, which says what its lines are. A placeholder name
#: (`PL-70M6`, 2026-10-19).
SECTION_HEADING = "Sessions that worked it"


def _cost(value: str) -> str:
    """A ledger cost as dollars to the cent, or the reason there is none.

    Only plain decimal digits are read, so `nan`, `inf` and an exponent that
    `float` would accept are reported rather than printed as a cost.
    """
    if COST_RE.fullmatch(value):
        return f"${float(value):.2f}"
    return f"cost `{value}` is not a number" if value else "cost not recorded"


def _describe(row: LedgerRow) -> str:
    served = row.last_served_model or "served model not recorded"
    if row.configured_model and row.configured_model != row.last_served_model:
        served += f" (configured {row.configured_model})"
    effort = f"effort {row.effort_level}" if row.effort_level else "effort not recorded"
    return f"{served} · {effort} · {_cost(row.cost_usd)}"


def format_item_sessions(joined: ItemSessions) -> str:
    """The section `docket show` prints for a closed item: a heading, then one line per session.

    Where no session joined, the heading is followed by the reason, never by
    an empty list.
    """
    if not joined.sessions:
        return f"{SECTION_HEADING}: none joined, because {joined.unjoined}."
    lines = [
        f"{SECTION_HEADING} (#{joined.pr}, read from {joined.source}; rows from {LEDGER_NAME}):"
    ]
    for session in joined.sessions:
        if session.row is not None:
            lines.append(f"  {session.session_id} · {_describe(session.row)}")
        elif joined.ledger_declined:
            lines.append(f"  {session.session_id} · ledger not read: {joined.ledger_declined}")
        else:
            lines.append(f"  {session.session_id} · no row in {LEDGER_NAME}")
    return "\n".join(lines)
