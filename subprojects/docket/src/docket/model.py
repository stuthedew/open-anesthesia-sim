"""The item: what a unit of work is, and how it is written down.

One item, one file. That single decision is what the rest of this package
exists to exploit. A queue kept in one shared document has to serialize
every writer, because two people adding work touch the same lines and two
people allocating an id read the same counter; a queue kept as one file per
item has nothing to serialize, because adding work means adding a file and
nobody else's file moves.

The format is markdown with a small front-matter block. Front matter is what
a tool reads; the body below it is what a person reads. Keeping them in one
file - rather than a database plus a description somewhere else - means the
machine-readable state and the human-readable brief can never drift apart,
and both arrive in a `git diff` for review.

Standard library only, so a session-start hook can run in a bare checkout
with no virtualenv.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

# Front matter is a `---` fenced block of `key: value` lines at the top of the
# file. Deliberately not YAML: a real YAML parser is a dependency, and the
# subset that is actually wanted here - scalars and comma-separated lists - is
# a dozen lines of parsing that cannot surprise anyone.
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
FIELD_RE = re.compile(r"^([a-z][a-z0-9-]*):[ \t]*(.*)$")

PRIORITIES = ("P0", "P1", "P2", "P3")
EFFORTS = ("S", "M", "L")

# `untriaged` is the capture state: an idea recorded before anyone has decided
# what it is worth. It exists so that writing something down costs nothing at
# the moment it occurs - no priority to guess, no band to choose, no other
# file to touch. Triage is the act of filling in the rest.
#
# `done` and `dropped` are terminal. Neither deletes the file: an item that
# leaves the queue leaves a record of why, because a finding dropped without a
# recorded reason gets raised again by the next person who notices it.
OPEN_STATUSES = ("untriaged", "ready", "needs-decision", "blocked")
CLOSED_STATUSES = ("done", "dropped")
STATUSES = OPEN_STATUSES + CLOSED_STATUSES

# Classes whose subject matter is safety-critical, and so may not sit in the
# lower priority bands however small the task looks.
SAFETY_CLASSES = ("safety", "science")

# Work on the development process rather than on the product it builds. An
# item counts as process work only when every one of its classes is in this
# set, so a `science`-and-`infra` item is still science.
PROCESS_CLASSES = ("session-cost", "docs", "infra")

LIST_FIELDS = ("classes", "touches", "blocked-by")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Split a document into its front-matter fields and its body.

    A file with no front matter yields no fields rather than an error; the
    caller decides whether that is a malformed item or simply not one.
    """
    match = FRONT_MATTER_RE.match(text)
    if match is None:
        return {}, text

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        field_match = FIELD_RE.match(line)
        if field_match is not None:
            fields[field_match.group(1)] = field_match.group(2).strip()
    return fields, match.group(2)


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@dataclass(frozen=True)
class Item:
    """One unit of work, as stored in one file.

    Every field a tool branches on lives in the front matter, and every field
    a person needs to start the work cold lives in the body. The split is the
    point: `touches` is there so the conflict graph can be computed without a
    model reading prose, and the brief is there so the work can be picked up
    by someone who was not present when it was written down.
    """

    identifier: str
    title: str
    priority: str
    effort: str
    status: str
    classes: tuple[str, ...]
    touches: tuple[str, ...]
    blocked_by: tuple[str, ...]
    feature: str
    milestone: str
    added: date | None
    closed: date | None
    commit: str
    reason: str
    body: str
    path: str = ""
    unknown_fields: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_open(self) -> bool:
        return self.status in OPEN_STATUSES

    @property
    def is_untriaged(self) -> bool:
        return self.status == "untriaged"

    @property
    def is_process_work(self) -> bool:
        """Whether this improves how the project is developed, not the product."""
        return bool(self.classes) and all(c in PROCESS_CLASSES for c in self.classes)

    @property
    def safety_classes(self) -> tuple[str, ...]:
        return tuple(c for c in self.classes if c in SAFETY_CLASSES)

    @property
    def model_guidance(self) -> str | None:
        """Whether this item is reasoning-heavy enough to warrant the strongest model.

        Safety- or science-classed work, and any item whose next step is an
        unresolved design decision, is not routine execution. Encoded here
        rather than left to each session to remember, so the recommendation
        does not depend on someone re-deriving the rule.
        """
        if self.safety_classes:
            return f"{'/'.join(self.safety_classes)}-tagged"
        if self.status == "needs-decision":
            return "open design decision"
        return None

    def sort_key(self) -> tuple[int, int, str]:
        """Order for display: priority band, then effort, then id.

        Untriaged items sort after everything triaged, because they are not
        yet candidates for work - they are candidates for a decision.
        """
        band = PRIORITIES.index(self.priority) if self.priority in PRIORITIES else len(PRIORITIES)
        if self.is_untriaged:
            band = len(PRIORITIES) + 1
        effort = EFFORTS.index(self.effort) if self.effort in EFFORTS else len(EFFORTS)
        return (band, effort, self.identifier)


def parse_item(text: str, path: str = "") -> Item:
    """Read one item file.

    Missing fields come back empty rather than defaulted. Nothing here
    substitutes a plausible value for an absent one: an item with no priority
    is an item with no priority, and `checks.py` decides whether that is
    allowed for its status. Guessing would turn a validation failure into a
    silently wrong queue position.
    """
    fields, body = parse_front_matter(text)
    known = {
        "id",
        "title",
        "priority",
        "effort",
        "status",
        "classes",
        "touches",
        "blocked-by",
        "feature",
        "milestone",
        "added",
        "closed",
        "commit",
        "reason",
    }
    return Item(
        identifier=fields.get("id", ""),
        title=fields.get("title", ""),
        priority=fields.get("priority", ""),
        effort=fields.get("effort", ""),
        status=fields.get("status", ""),
        classes=_split_list(fields.get("classes", "")),
        touches=_split_list(fields.get("touches", "")),
        blocked_by=_split_list(fields.get("blocked-by", "")),
        feature=fields.get("feature", ""),
        milestone=fields.get("milestone", ""),
        added=_parse_date(fields.get("added", "")),
        closed=_parse_date(fields.get("closed", "")),
        commit=fields.get("commit", ""),
        reason=fields.get("reason", ""),
        body=body,
        path=path,
        unknown_fields=tuple(sorted(set(fields) - known)),
    )


def render_item(item: Item) -> str:
    """Write one item file.

    Fields are emitted in a fixed order and empty ones are omitted, so that
    rewriting a file the tool has already written is a no-op. A round trip
    that reorders keys would put noise in every diff and make review harder,
    which is the opposite of why the state is kept in git at all.
    """
    lines = [f"id: {item.identifier}", f"title: {item.title}"]
    for name, value in (
        ("priority", item.priority),
        ("effort", item.effort),
        ("status", item.status),
        ("classes", ", ".join(item.classes)),
        ("feature", item.feature),
        ("milestone", item.milestone),
        ("touches", ", ".join(item.touches)),
        ("blocked-by", ", ".join(item.blocked_by)),
        ("added", item.added.isoformat() if item.added else ""),
        ("closed", item.closed.isoformat() if item.closed else ""),
        ("commit", item.commit),
        ("reason", item.reason),
    ):
        if value:
            lines.append(f"{name}: {value}")
    body = item.body if item.body.endswith("\n") else item.body + "\n"
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body.lstrip("\n")
