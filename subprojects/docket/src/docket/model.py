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

# Efforts a delegated item may carry. An `L` item is a milestone in disguise;
# nothing that large has a brief precise enough to be worked without judgment.
DELEGABLE_EFFORTS = ("S", "M")


def _front_matter_pairs(text: str) -> tuple[list[tuple[str, str]], str] | None:
    """Every `key: value` line of the front matter, in file order, with the body.

    Pairs rather than a dict, because a dict is exactly where a repeated key
    stops being visible. `parse_front_matter` collapses them for callers that
    want the fields; `repeated_front_matter_keys` reads the same list to find
    the ones a collapse would have hidden. `None` when there is no front
    matter at all, which the two callers report differently.
    """
    match = FRONT_MATTER_RE.match(text)
    if match is None:
        return None

    pairs: list[tuple[str, str]] = []
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        field_match = FIELD_RE.match(line)
        if field_match is not None:
            pairs.append((field_match.group(1), field_match.group(2).strip()))
    return pairs, match.group(2)


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Split a document into its front-matter fields and its body.

    A file with no front matter yields no fields rather than an error; the
    caller decides whether that is a malformed item or simply not one.

    A repeated key collapses to its last occurrence here, which is what a dict
    can express. That is a lossy answer rather than a wrong one, and
    `parse_item` pairs it with `repeated_front_matter_keys` so the loss is
    reported instead of taken. Do not "fix" this by keeping the first instead:
    either choice picks a winner, and picking one silently is the defect
    (`PL-BR4G`).
    """
    parsed = _front_matter_pairs(text)
    if parsed is None:
        return {}, text
    pairs, body = parsed
    return dict(pairs), body


def repeated_front_matter_keys(text: str) -> tuple[str, ...]:
    """Front-matter keys the file spells more than once, sorted.

    The store is one file per item precisely so that two branches adding work
    cannot conflict, and that property has a sharp edge: two branches editing
    the *same* item, inserting the same field at different line positions,
    also do not conflict. Git merges both lines, the dict keeps whichever came
    last, and every check downstream reads a value nobody chose. Observed on
    `main` 2026-09-02 with two `pr:` lines that happened to agree.
    """
    parsed = _front_matter_pairs(text)
    if parsed is None:
        return ()
    pairs, _ = parsed
    seen: set[str] = set()
    repeated: set[str] = set()
    for key, _value in pairs:
        if key in seen:
            repeated.add(key)
        seen.add(key)
    return tuple(sorted(repeated))


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
    #: The pull request that carried the work, as a bare number. Recorded
    #: beside `commit` rather than instead of it, because the two answer
    #: different questions: `commit` names the branch commit, which a
    #: squash-merge discards, while the number is known before the merge and
    #: outlives it. Defaulted empty like the fields below, so an item written
    #: before the field existed still parses.
    pr: str = ""
    #: The command that proves this item done. Defaulted empty rather than
    #: required, so an item written before the field existed - or captured
    #: without one - is simply not delegable, which is the safe reading.
    verify: str = ""
    #: The reason a qualifying item is withheld from delegation. Presence is
    #: the switch; there is deliberately no field that grants delegability.
    not_delegable: str = ""
    path: str = ""
    unknown_fields: tuple[str, ...] = field(default_factory=tuple)
    duplicate_fields: tuple[str, ...] = field(default_factory=tuple)

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

    def delegability(self, protected_paths: tuple[str, ...]) -> str | None:
        """Why this item may *not* be handed to a cheaper model, or None if it may.

        Derived, never stored, and that asymmetry is the whole safeguard. There
        is no `delegable: yes` to set, so no session - least of all a worker
        tidying front matter on its way past - can mark its own work eligible.
        The only writable control is `not-delegable`, which withholds an item
        that would otherwise qualify. Delegability can be taken away by hand
        and never granted by hand.

        A returned string is the reason, phrased to be printed. `None` means
        every condition below is met:

        - the work is startable at all (`ready`, so not blocked and not
          awaiting a decision);
        - `model_guidance` is silent, which excludes safety- and
          science-classed work and open design decisions by the rule that
          already existed rather than by a second one written here;
        - a `verify:` command exists, because without one "done" is a
          judgment and there is nothing for a reviewer to trust instead;
        - `touches` is declared and wholly outside the protected paths, so the
          diff's blast radius is known before the work starts;
        - the effort is one a precise brief can actually cover.
        """
        if self.not_delegable:
            return f"withheld: {self.not_delegable}"
        if not protected_paths:
            return "no protected paths configured"
        if self.status != "ready":
            return f"status is {self.status or 'unset'}, not ready"
        guidance = self.model_guidance
        if guidance is not None:
            return guidance
        if not self.verify:
            return "no `verify:` command"
        if not self.touches:
            return "declares no `touches`"
        protected = [path for path in self.touches if _is_protected(path, protected_paths)]
        if protected:
            return f"touches protected path(s) {', '.join(protected)}"
        if self.effort not in DELEGABLE_EFFORTS:
            return f"effort {self.effort or 'unset'} is not {' or '.join(DELEGABLE_EFFORTS)}"
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


def _is_protected(path: str, protected_paths: tuple[str, ...]) -> bool:
    """Whether one declared path falls inside the protected set.

    Compared as `/`-separated path prefixes rather than as strings, so that
    `core/` protects `core/blood.py` while `docs/MODEL.md` does not also
    protect a hypothetical `docs/MODEL.md.bak`. Matching by bare string prefix
    would silently protect the wrong things and, worse, silently fail to
    protect the right ones.
    """
    candidate = path.strip().strip("/")
    for protected in protected_paths:
        target = protected.strip().strip("/")
        if not target:
            continue
        if candidate == target or candidate.startswith(target + "/"):
            return True
    return False


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
        "pr",
        "reason",
        "verify",
        "not-delegable",
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
        pr=fields.get("pr", ""),
        reason=fields.get("reason", ""),
        verify=fields.get("verify", ""),
        not_delegable=fields.get("not-delegable", ""),
        body=body,
        path=path,
        unknown_fields=tuple(sorted(set(fields) - known)),
        duplicate_fields=repeated_front_matter_keys(text),
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
        ("pr", item.pr),
        ("reason", item.reason),
        ("verify", item.verify),
        ("not-delegable", item.not_delegable),
    ):
        if value:
            lines.append(f"{name}: {value}")
    body = item.body if item.body.endswith("\n") else item.body + "\n"
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body.lstrip("\n")
