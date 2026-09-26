"""Releases: what has shipped since the last version, and what to call the next.

**A milestone records what went out, it does not plan what will.** That
direction matters more than it looks. The obvious design is the other one -
assign items to `v0.3.0`, then ship when they are all closed - and it fails
in practice, because it makes shipping depend on somebody having done the
bookkeeping in advance. Anyone who forgets is told their release is empty
while a fortnight of finished work sits outside it.

So an item that is `done` with no `milestone` is simply unreleased, which is
the state finished work is naturally in - all of it but the item a release is
cut under, which ships in none (`unreleased` says why). Cutting a release
stamps that work with the version it went out in. Nothing has to be decided up
front, nothing is forgotten, and the question "is it worth cutting one?"
becomes answerable by reading the store rather than by remembering what was
promised.

Planning ahead is what `feature` is for. A feature says what a group of items
is *for*; a milestone says which release it left in.
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from .model import RELEASE_TRAIN, Item
from .store import ID_PATTERN

if TYPE_CHECKING:  # `roadmap` reads this module's version grammar, so the
    from .roadmap import Wave  # runtime import would close the cycle.

VERSION_RE = re.compile(r'^(version\s*=\s*")([^"]+)(")', re.M)
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

#: What `SEMVER_RE` accepts, in the words a refusal of anything else uses, so
#: the grammar a reader is told and the one enforced sit on adjacent lines.
SEMVER_GRAMMAR = (
    "three whole numbers joined by dots, MAJOR.MINOR.PATCH, with an optional "
    "leading v, such as 0.5.12 or v0.5.12"
)

#: Where the generated notes are written, and therefore where a release
#: already cut can be read back from. A constant rather than a setting: it is
#: one directory, written in one place and read in one, and the value of
#: having it here is that the write and the duplicate-cut check below cannot
#: drift into two spellings of the same path.
NOTES_DIR = "docs/releases"


@dataclass(frozen=True)
class Milestone:
    """One release: the items in it, and whether they are finished."""

    name: str
    items: list[Item]

    @property
    def done(self) -> list[Item]:
        return [item for item in self.items if item.status == "done"]

    @property
    def outstanding(self) -> list[Item]:
        return [item for item in self.items if item.is_open]

    @property
    def is_complete(self) -> bool:
        return bool(self.items) and not self.outstanding

    @property
    def version(self) -> str:
        """The version string this milestone ships, without its leading `v`."""
        return self.name.lstrip("v")


def unreleased(items: list[Item], resuming: str = "") -> list[Item]:
    """Finished work that has not gone out in any version yet.

    This is the default state of a closed item, not a state anyone has to put
    it into, which is the whole point: no one has to predict at capture time
    which release something will land in.

    `resuming` names a release whose cut was interrupted, and folds the work
    that cut already stamped back in. Without it a re-run sees only what the
    first run had not reached, and ships a short release under the full one's
    name: `PL-1MKQ` is 26 items of 33 stamped, a re-run reporting "7 finished
    item(s)" and exiting 0, and notes that would have been the permanent
    record of a 33-item release naming 7 of them. Reclaiming makes the cut of
    a named version idempotent, which is the property that holds however far
    the interrupted run got - and it is the stamp loop, not the bump, that is
    the likely place to be interrupted, since it writes a file per item.

    The item a release was cut under is never among it (`PL-KRS6`). It closes
    in the cut's own pull request, after the notes are written, so it carries
    no `milestone:` - and read as unreleased it was the next release's whole
    content, offered to every session from the moment a cut merged until real
    work closed. Its `resource: release-train`, which every cut requires
    (`PL-331V`), is what marks it, so it counts toward no release and no notes
    name it.
    """
    return sorted(
        (
            i
            for i in items
            if i.status == "done"
            and i.resource != RELEASE_TRAIN
            and (not i.milestone or (bool(resuming) and i.milestone.strip() == resuming))
        ),
        key=lambda i: (i.closed or date.min, i.identifier),
    )


def milestones(items: list[Item]) -> dict[str, Milestone]:
    """Group items by the release they belong to, newest name last."""
    grouped: dict[str, list[Item]] = {}
    for item in items:
        if item.milestone:
            grouped.setdefault(item.milestone, []).append(item)
    return {
        name: Milestone(name, sorted(grouped[name], key=lambda i: i.sort_key()))
        for name in sorted(grouped, key=version_key)
    }


def version_key(name: str) -> tuple[int, ...]:
    """Sort versions numerically, so v0.10.0 follows v0.9.0 rather than v0.1.0."""
    match = SEMVER_RE.match(name.strip())
    if match is None:
        return (0, 0, 0)
    return tuple(int(part) for part in match.groups())


def suggest_version(current: str, items: list[Item], minor_classes: tuple[str, ...]) -> str:
    """The version a set of finished work should ship as.

    New functionality is a minor bump and everything else is a patch, which is
    the semantic-versioning rule stated in terms the items already carry. A
    major bump is deliberately not inferred: breaking a published interface is
    a decision somebody makes, not a fact derivable from a class label.
    """
    match = SEMVER_RE.match(current.strip())
    if match is None:
        return current
    major, minor, patch = (int(part) for part in match.groups())
    if any(cls in minor_classes for item in items for cls in item.classes):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def is_untagged(version: str, existing: frozenset[str]) -> bool:
    """Whether an already-shipped version has no tag, in a project that tags.

    A release cut without a tag leaves a permanent gap: `git describe
    --contains` resolves nothing for any commit in its span, so the question
    "which release did this change go out in" stops having an answer, and it
    cannot be repaired later with any confidence once the history has moved
    on. Refusing the *next* release is what turns that from a thing somebody
    remembers into a thing that cannot silently lapse.

    A project with no tags at all is not held to this. Its emptiness says the
    project does not tag releases, and adopting the practice is its decision,
    not this tool's.
    """
    if not version or not existing:
        return False
    name = version.lstrip("v")
    return f"v{name}" not in existing and name not in existing


def notes_name(version: str) -> str:
    """The notes file a version's release is written to, with no leading path."""
    return f"v{version.strip().lstrip('v')}.md"


def notes_path(version: str) -> str:
    """The notes file a version's release is written to, from the repository root."""
    return f"{NOTES_DIR}/{notes_name(version)}"


#: What a release's *cut* is, stated once for every reader of it: the commit
#: that added its notes file, compared with its first parent. That commit's
#: tree is the first to carry the release's notes and its version bump, so it
#: is the commit the release shipped from and the one its tag goes on - not
#: whatever `origin/main` names when somebody gets round to tagging, which is
#: the next merge as often as this one (`PL-VYK1`). `--first-parent` keeps a
#: merge that brought the file in from counting as its add, and
#: `--diff-filter=A` keeps a later edit to the notes from moving the cut.
#:
#: **Never ask it of a branch's `HEAD`.** A branch that merged the default
#: branch in after a release has its own merge commit on its first-parent line,
#: and that merge added the notes file compared with *its* first parent:
#: measured 2026-09-26, a scratch branch that merged the v0.5.11 cut `fe2046f7`
#: named its own merge `4308874b` instead. So the printed commands ask
#: `origin/main`, and `tools/doc_check.py` asks each tag's own commit
#: (`PL-QHCW`).
CUT_FLAGS = ("--first-parent", "--diff-filter=A")


def cut_query(version: str, ref: str) -> list[str]:
    """The `git` arguments that name the commit which cut `version`, read from `ref`.

    One commit where the notes were added once; none where `ref` never carried
    them; more than one where they were added, deleted and added again, which
    no reader may settle by picking one.
    """
    return ["log", *CUT_FLAGS, "--format=%H", ref, "--", notes_path(version)]


def tag_commands(
    version: str, remote: str = "origin", branch: str = "main"
) -> tuple[str, str, str]:
    """The three shell lines that tag `version` on its cut, filled in.

    The tag line finds the cut *when it runs*, from `remote/branch`, instead
    of naming a commit here. Printed by the cut, there is no commit on the
    default branch to name yet; printed later, a named commit is only as good
    as the moment it was read. Run before the release has merged, the lookup
    prints nothing and `git tag` refuses the empty name; run late, it still
    finds the cut, however many merges have landed since (`PL-VYK1`).
    """
    name = f"v{version.strip().lstrip('v')}"
    lookup = shlex.join(["git", *cut_query(version, f"{remote}/{branch}")])
    return (
        f"git fetch {remote} {branch}",
        f'git tag -a {name} "$({lookup})" -m "{name}"',
        f"git push {remote} {name}",
    )


#: Where a notes file stops claiming work and starts pointing at it. Bullets
#: below this heading name a closing pull request inside this tag's span that
#: the *cut* did not stamp, and the release another cut did stamp it in -
#: `ROADMAP.md` § "Tags" for why the two records differ, and
#: `doc_check.check_tag_span_covers_its_notes` for what holds them to it.
SPAN_HEADING = "### also inside this tag's span"


def notes_claims(text: str) -> tuple[str, str]:
    """One notes file split into what its release claims and what it only points at.

    Every reader and writer of a bullet below takes the first half, and the
    writer puts the second back byte for byte. The pointer section is bullets
    of the same shape naming items *another* release stamped, so a reader given
    the whole file reports each one as the notes and the store disagreeing -
    which is the thing the pointer exists to say - and `restate_references`
    would append a second reference to a line that already carries one.

    The second half keeps its heading, so `head + tail` is the file.
    """
    head, separator, tail = text.partition(SPAN_HEADING)
    return head, separator + tail


#: An item id at the head of a notes bullet, which is the only place a release's
#: notes *claim* an item. Anchored deliberately: the rest of the line is the
#: item's title, and titles quote other ids - "PL-2GQW PL-L9JS's not-delegable
#: reason rests on the recursion claim PL-20CQ disproved" names three. Reading
#: every id in the file made 20 of this project's 37 healthy releases look
#: inconsistent; reading the bullet's leader makes 36 of the 37 agree exactly,
#: and the 37th predates the notes directory.
NOTES_ENTRY_RE = re.compile(rf"^- ({ID_PATTERN})", re.M)


def notes_by_version(root: Path, notes_dir: str = NOTES_DIR) -> dict[str, frozenset[str]]:
    """Which items each cut release's notes file says it shipped.

    The notes rather than the store, because the notes are the half that is
    permanent: a `milestone:` stamp can be edited afterwards, while a released
    `docs/releases/vX.Y.Z.md` is what a reader has. Comparing the two is
    `checks._check_release_notes`; this reports only what is written.

    A directory that does not exist is a project that does not write notes,
    and comes back empty rather than raising.
    """
    directory = root / notes_dir
    if not directory.is_dir():
        return {}
    return {
        path.stem: frozenset(
            NOTES_ENTRY_RE.findall(notes_claims(path.read_text(encoding="utf-8"))[0])
        )
        for path in sorted(directory.glob("v*.md"))
        if SEMVER_RE.match(path.stem)
    }


def unrecorded_milestones(
    items: list[Item], notes: dict[str, frozenset[str]], current_version: str = ""
) -> list[str]:
    """Releases the store says it shipped that no notes file records.

    This is the state an interrupted cut leaves. `cmd_release` writes the
    `milestone:` stamps one file at a time and the notes after them, so a run
    that dies inside that loop leaves work stamped with a release that has no
    record - and a plain re-run reads those items as already shipped, cuts the
    remainder under the same name and exits 0 (`PL-1MKQ`: 26 items of 33
    stamped, notes covering the other 7).

    One rule, read by both halves of the repair: `cmd_release` resumes what
    this names and `checks` reports it, so the command and the check cannot
    disagree about what an interrupted cut is.

    Releases cut before the project wrote notes at all are not judged. The
    floor is the oldest version that does have a notes file, supplied by the
    directory itself rather than configured so that it cannot go stale: this
    project's v0.2.2 shipped eleven items before `docs/releases/` existed and
    no file will ever be written for it.

    The current version is a floor too, and it is the one that covers a
    project's *first* release. There the interrupted cut has written no notes
    file at all, so the directory offers no floor and every historical stamp
    would otherwise be judged against a practice the project has not adopted.
    Taking the lower of the two keeps the directory's answer wherever it has
    one - it is always at or below the current version - and falls back to
    "only the release being cut right now" where it has none.

    With neither, there is nothing to measure against and nothing is judged.
    """
    floors = [version_key(name) for name in notes]
    if SEMVER_RE.match(current_version.strip()):
        floors.append(version_key(current_version))
    if not floors:
        return []
    floor = min(floors)
    stamped = {
        item.milestone.strip()
        for item in items
        if item.milestone and SEMVER_RE.match(item.milestone.strip())
    }
    return sorted(
        (name for name in stamped if name not in notes and version_key(name) >= floor),
        key=version_key,
    )


def version_in(text: str) -> str:
    """The version a project file declares, or empty where it declares none.

    Separated from `read_version` because the same grammar has to answer for a
    file on disk and for the same file read out of another ref, and two
    spellings of one question are two answers waiting to disagree.
    """
    match = VERSION_RE.search(text)
    return match.group(2) if match else ""


def read_version(pyproject: Path) -> str:
    """The project's current version, or empty when there is none to read.

    A missing or version-less file is a legitimate state - a store consulted
    on its own, or a project that does not version - so it reports nothing
    rather than raising. Bumping is the operation that requires a version to
    exist, and that one still fails loudly.
    """
    if not pyproject.is_file():
        return ""
    return version_in(pyproject.read_text(encoding="utf-8"))


def already_released(
    version: str, notes: frozenset[str], base_version: str, version_file: str
) -> list[str]:
    """What on the default branch says this version has already gone out.

    **A cut is the one change whose own commits no in-flight guard can see.**
    Every one this package has matches a `PL-` id, and a cut still carries
    none - so the change that rewrites the version file, the lock file, the
    roadmap and a new notes file, which is the most collision-prone in the
    repository, was the only one nothing watched. Two sessions cut v0.3.7
    within an hour that way, and the second one's whole release was discarded
    at the merge (`PL-66FP`). The release item's claim on the release train is
    the id the guard reads now (`PL-331V`).

    This is the half of that which is *certain*. A notes file or a version
    field on the default branch is a fact about a merge that has already
    happened, not an inference from a ref that may have moved since it was
    fetched - so it can be refused on rather than merely reported, which is
    what separates it from every other parallel-session read here.

    Both facts are checked rather than either alone. The notes file is the
    direct evidence and the one a maintainer can see; the version field
    catches a project that writes its notes somewhere else, or a release
    landed by hand. Each is returned as a statement about the state of the
    default branch, so a reader can check it against what they are looking at
    rather than being told what to conclude.

    Empty means the number is free, and says nothing about whether another
    session is cutting it right now: that claim needs refs this cannot see.
    """
    name = version.strip().lstrip("v")
    if not name:
        return []
    found: list[str] = []
    if notes_name(name) in notes:
        found.append(f"{NOTES_DIR}/{notes_name(name)} is on it")
    if base_version.strip().lstrip("v") == name:
        found.append(f"its {version_file} already reads {name}")
    return found


def below_current(version: str, current: str, version_file: str) -> str:
    """Why cutting `version` would move the version field backwards, or empty.

    `already_released` asks whether this number has gone out; this asks what it
    leaves open, which is whether the number is below the one the tree
    declares. `version_policy = "manual"` is what makes that reachable: the
    number is typed by a person, and a dry run of 0.2.0 over 0.4.28 printed
    `0.4.28 -> 0.2.0` and exited 0, so the cut itself would have bumped the
    version field backwards, written its notes under the lower number and
    stamped every item with it - stamps no re-run takes back (`PL-3DN1`).

    Equal is decided here rather than left to fall out of the comparison, and
    it is not this refusal's. The current number is asked for by the resume of
    a cut interrupted after its bump, whose version field already carries the
    release being finished, and that run has to get through; and by a re-cut
    of a release already out, which `already_released` refuses naming the
    evidence a reader can check, letting a dry run preview it. A resume whose
    number is below the current one is refused like any other.

    Only numbers that parse are compared, so an empty or unversioned field
    stays `prepare_bump`'s to refuse.
    """
    requested = version.strip().lstrip("v")
    declared = current.strip().lstrip("v")
    if not SEMVER_RE.match(requested) or not SEMVER_RE.match(declared):
        return ""
    if version_key(requested) == version_key(declared):
        return ""
    if version_key(requested) > version_key(declared):
        return ""
    return f"{requested} is below {declared}, the version {version_file} declares"


@dataclass(frozen=True)
class PreparedBump:
    """A version bump proved possible, holding the bytes it has yet to write.

    Cutting a release writes two things - the `milestone:` stamp on every
    item going out, and the version - and neither order is safe while the
    bump can still fail on the file it is about to rewrite. Stamping first
    left the store recording a release that never happened, with nothing
    saying which stamps to unpick; bumping first would leave a version
    claiming items it had not stamped.

    Separating the proof from the write removes the choice. Everything the
    bump can reject - an absent file, a file carrying no version field - is
    settled here, before the first stamp is written, and what survives is a
    path and the text to put at it.
    """

    path: Path
    previous: str
    text: str

    def write(self) -> str:
        """Put the prepared text in place, returning the version it replaced."""
        self.path.write_text(self.text, encoding="utf-8")
        return self.previous


def prepare_bump(pyproject: Path, version: str) -> PreparedBump:
    """Read and validate the single source of the project version.

    One string in one file. A project that resolves its displayed version
    from package metadata has nothing else to update; a second hard-coded
    copy somewhere else is a second thing to forget.

    Raises on a file that is absent or carries no version field. `read_version`
    tolerates both, because a store may be consulted away from any project;
    bumping is the operation that requires a version to exist.
    """
    text = pyproject.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None:
        raise ValueError(f"{pyproject}: no version field to bump")
    return PreparedBump(
        path=pyproject,
        previous=match.group(2),
        text=VERSION_RE.sub(rf"\g<1>{version}\g<3>", text, count=1),
    )


def release_notes(milestone: Milestone, today: date) -> str:
    """Write the release notes from the items themselves.

    Generated rather than composed, so the notes cannot claim something the
    items do not, and so nothing shipped goes unmentioned because whoever
    wrote the notes forgot it.
    """
    lines = [f"## {milestone.name} - {today.isoformat()}", ""]
    by_class: dict[str, list[Item]] = {}
    for item in milestone.done:
        key = item.classes[0] if item.classes else "other"
        by_class.setdefault(key, []).append(item)
    for name in sorted(by_class):
        lines.append(f"### {name}")
        lines.append("")
        for item in by_class[name]:
            lines.append(f"- {item.identifier} {markdown_title(item.title)}{reference(item)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


#: A code span, as CommonMark delimits one: a run of backticks and the next run
#: of exactly as many, neither part of a longer run.
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)", re.S)

#: An opening angle bracket no backslash already escapes.
UNESCAPED_LT_RE = re.compile(r"(?<!\\)<")


def markdown_title(title: str) -> str:
    """A title as markdown that renders it as filed (`PL-PRSF`).

    A title is prose, so a placeholder in it - `refs/pull/<n>/head` - reaches
    a notes bullet or a capture's Problem line outside a code span, where
    GitHub reads `<n>` as an HTML tag and its sanitizer drops it: the page
    prints `refs/pull//head`, a wrong command rather than a missing word.
    CommonMark lets any ASCII punctuation be backslash-escaped, and `<` is the
    character every tag, comment and autolink opens with, so escaping it alone
    keeps the whole placeholder; a lone `>` mid-line is already literal. A code
    span is copied as it stands, since a placeholder inside one survives and a
    backslash there would print, and so is a `<` a backslash already escapes.
    """
    kept: list[str] = []
    start = 0
    for span in CODE_SPAN_RE.finditer(title):
        kept.append(UNESCAPED_LT_RE.sub(r"\\<", title[start : span.start()]))
        kept.append(span.group())
        start = span.end()
    kept.append(UNESCAPED_LT_RE.sub(r"\\<", title[start:]))
    return "".join(kept)


def reference(item: Item) -> str:
    """Where a reader goes to see the change one notes bullet is about.

    The pull request in preference to the commit: it is what a reader can
    still follow after a squash-merge discards the branch, and a bare `#48`
    renders as a link where these notes are read. Empty where the item records
    neither, which is the state every closure is in until the number its merge
    event carried is written back.

    Its own function because two callers have to agree on it exactly. The cut
    writes it, and `restate_references` puts it on a bullet that shipped
    before the number existed - so a second spelling of the rule would let a
    repaired line and a generated one differ inside the same file.
    """
    if item.pr:
        return f" — #{item.pr}"
    if item.commit:
        return f" — `{item.commit}`"
    return ""


#: A notes bullet that already says where its change landed. Anchored to the
#: end of the line because that is the only place `reference` writes one, and
#: matched on shape rather than against the item's current title: a bullet
#: records the title *as it shipped*, so an item retitled afterwards would fail
#: an equality test while its missing number stayed exactly as recoverable.
#: Measured 2026-09-21 over this project's 1,412 items, no title ends in a tail
#: this could mistake for a reference.
REFERENCED_RE = re.compile(r" — (#\d+|`[0-9a-f]{7,40}`)$")

#: A notes bullet split into the id it claims and everything after it, which is
#: the title plus whatever reference the bullet carries. Same anchoring as
#: `NOTES_ENTRY_RE` and for the same reason: titles quote other ids, so only
#: the leader says which item a bullet is about.
NOTES_BULLET_RE = re.compile(rf"^- ({ID_PATTERN})(.*)$", re.M)


def unreferenced(text: str) -> tuple[str, ...]:
    """The ids one notes file names with no route back to the change that made them."""
    return tuple(
        identifier
        for identifier, tail in NOTES_BULLET_RE.findall(text)
        if not REFERENCED_RE.search(tail)
    )


def unreferenced_by_version(root: Path, notes_dir: str = NOTES_DIR) -> dict[str, tuple[str, ...]]:
    """Which items each cut release's notes name without saying where they landed.

    The companion to `notes_by_version`, reading the same files for the other
    half of what a bullet records. That one answers *which* items a release
    claims, which is what `_check_release_notes` holds against the stamps;
    this answers which of those claims a reader cannot follow.

    Releases whose bullets all carry a reference are absent rather than empty,
    so a healthy project reports `{}` and the caller has nothing to filter.
    """
    directory = root / notes_dir
    if not directory.is_dir():
        return {}
    found: dict[str, tuple[str, ...]] = {}
    for path in sorted(directory.glob("v*.md")):
        if not SEMVER_RE.match(path.stem):
            continue
        claims, _ = notes_claims(path.read_text(encoding="utf-8"))
        if missing := unreferenced(claims):
            found[path.stem] = missing
    return found


def restate_references(text: str, by_id: Mapping[str, Item]) -> tuple[str, tuple[str, ...]]:
    """Append the reference the store can now supply to every bullet missing one.

    An append, and nothing else. The id and the title are left exactly as they
    shipped, so this cannot change what a release *claims* - which is the
    hazard `PL-1MKQ` names for re-cutting one, and which adding the route back
    to a change the bullet already names does not engage. Every other byte of
    the file, including the headings and the class grouping, is untouched for
    the same reason `_write_pr` inserts a field rather than re-rendering the
    item: a repair that rewrites what it did not have to is a repair nobody can
    review.

    A bullet whose item the store no longer holds, or holds with neither a
    number nor a commit, is left alone. This supplies a fact or it does
    nothing; there is no third thing it could honestly write.

    Returns the new text and the ids it repaired, so a caller can report the
    repair rather than a diff.
    """
    repaired: list[str] = []

    def restate(match: re.Match[str]) -> str:
        identifier, tail = match.group(1), match.group(2)
        item = by_id.get(identifier)
        if item is None or REFERENCED_RE.search(tail):
            return match.group(0)
        if not (suffix := reference(item)):
            return match.group(0)
        repaired.append(identifier)
        return f"- {identifier}{tail}{suffix}"

    claims, pointer = notes_claims(text)
    return NOTES_BULLET_RE.sub(restate, claims) + pointer, tuple(repaired)


@dataclass(frozen=True)
class Readiness:
    """Whether there is enough finished work to be worth cutting a release.

    Deliberately advisory. It reports what is shippable and what the version
    would be; it does not decide that a release should happen, because that
    depends on things no store knows - whether a demo is on Friday, whether
    the next item is nearly done, whether anyone wants to review it.
    """

    shippable: list[Item]
    completed_features: list[str]
    partial_features: list[str]
    current_version: str
    suggested_version: str

    @property
    def is_worth_cutting(self) -> bool:
        """Whether to raise it unprompted.

        A finished feature is worth mentioning on its own, however few items
        it took. Otherwise it takes a few closed items before the suggestion
        is more useful than it is noise.
        """
        return bool(self.completed_features) or len(self.shippable) >= 3


def readiness(
    items: list[Item], current_version: str, minor_classes: tuple[str, ...], resuming: str = ""
) -> Readiness:
    """What could ship right now, and what it would be called.

    `resuming` is passed through to `unreleased`, and only `cmd_release`
    supplies it: every other caller is asking what is shippable *now*, and an
    interrupted cut's stamps are not that question.
    """
    from .plan import features as group_features

    shippable = unreleased(items, resuming)
    shipped_ids = {item.identifier for item in shippable}

    completed: list[str] = []
    partial: list[str] = []
    for name, feature in group_features(items).items():
        if not any(i.identifier in shipped_ids for i in feature.items):
            continue
        (completed if feature.is_complete else partial).append(name)

    return Readiness(
        shippable=shippable,
        completed_features=sorted(completed),
        partial_features=sorted(partial),
        current_version=current_version,
        suggested_version=suggest_version(current_version, shippable, minor_classes),
    )


# What the plan says about the version a bump has arrived at, as three answers.
# Two of them are the interesting ones, and they are opposite failures: the
# number is spoken for, or the number is free but is not the one the plan is
# waiting to cut.
STANDS = "stands"
PLANNED = "planned"
RESERVED = "reserved"


@dataclass(frozen=True)
class ReleaseOffer:
    """Whether a release may be recommended, and under which version.

    `Readiness` reads the store and only the store. That is what makes it
    honest about what is finished and blind to what a version *means*: the
    number it suggests is arithmetic on the last one, and a project that plans
    in versions has usually spent that number already. Where it has, cutting
    the suggestion is not a smaller release than the plan's - it is the plan's
    milestone going out under its own name with most of it missing, which a
    tag makes permanent and a reader has no way to see through afterwards.

    So this is the readiness answer with the plan folded in, as three
    outcomes: the number is free (`STANDS`), the plan names a different one to
    cut (`PLANNED`), or the plan has already given the number to something it
    has not finished (`RESERVED`, and there is nothing to offer).

    The reservation is read from the plan rather than from where the project
    stands in it. `wave` carries every version `ROADMAP.md` names ahead of the
    current one - the release train's milestone rows and the milestone
    sections both - and the suggestion is checked against all of them. So a
    milestone reserves its number from the moment it is *placed*, months
    before anyone scopes it, and goes on reserving it however many rows the
    plan later puts between it and the project.

    This used to read two objects `wave` binds, the step and the beat's
    milestone, and the limit was a *distance* rather than a state: both reach
    one row, and nothing reached two. Every version ahead is reserved, the
    beat's own included: an `implement` beat counts an open scope or is not
    returned at all, so there is no version the guard stands down on
    (`PL-J45M`).
    """

    kind: str
    #: The version to cut. Under `RESERVED` it is the version *not* to cut:
    #: the one the bump arrived at and the plan has spoken for.
    version: str
    #: The roadmap's own name for the step or milestone the answer turns on -
    #: "the workflow works", not "v0.2.8". Empty under `STANDS`, where neither
    #: is involved.
    milestone: str


def release_offer(ready: Readiness, plan: Wave | None) -> ReleaseOffer:
    """Reconcile the version a bump arrived at with the one the plan has planned.

    The plan is allowed to be absent or unreadable - `wave` declines rather
    than guesses, and a project with no roadmap is a legitimate state - and
    the offer then stands, because there is no plan for it to contradict.
    """
    from .roadmap import RELEASE

    suggested = ready.suggested_version.lstrip("v")
    if plan is None:
        return ReleaseOffer(STANDS, suggested, "")

    if plan.beat == RELEASE and plan.release_version is not None:
        # The plan is itself asking for a release, so the only thing left to
        # disagree about is the number - and there the plan wins: it named the
        # version when the milestone was scoped, the bump inferred one from a
        # class label.
        #
        # Read from the beat rather than from `plan.step`, which names the
        # version in two of the three release arrangements and not in the
        # third: a milestone whose gate is clear and whose `Required scope` has
        # closed is released while the project still stands on the patch-track
        # row beneath it, and that row carries `(0, 4, -1)` - a track marker
        # rather than a number anything can be cut at, which matches no
        # suggestion and falls through to the bump's own arithmetic. Left on
        # `step`, the digest offered `0.4.21` directly above a beat reading
        # `release v0.5.0` (`PL-KD98`).
        planned = "{}.{}.{}".format(*plan.release_version)
        if planned == suggested:
            return ReleaseOffer(STANDS, suggested, "")
        return ReleaseOffer(PLANNED, planned, plan.release_name)

    # Ask the plan which numbers it has spent, rather than asking the two
    # objects that happen to be bound here. `plan.reserved` is every version
    # `ROADMAP.md` names ahead of the current one, with the roadmap's own name
    # for what holds it.
    #
    # The reason is the history rather than the tidiness. This compared the
    # suggestion against one binding, then two, each added after the
    # arrangement it reads had already produced a wrong offer: `PL-KD98` moved
    # the release beat off `step`; `PL-6T4L` added the milestone the beat is
    # about, after the digest printed `Offer 0.5.0 before taking new work`
    # directly above `Beat: implement v0.5.0 - the case you can branch ... 8
    # still open`, which would have stamped `milestone: 0.5.0` onto four items
    # and tagged a branching release with no branching in it; `PL-188T` found a
    # patch cut mid-port offered the port's own number as free; `PL-VFD8` found
    # a milestone with a timeline row and no section binding neither. A third
    # binding would have answered the fifth arrangement and no more. The plan
    # can be rearranged - a row moved between the project and its milestone is
    # an ordinary editorial act - faster than the bindings can be enumerated,
    # so the enumeration had to stop rather than grow, and reading the file's
    # own statement of what is spent is what stops it.
    #
    # Nothing cuttable is suppressed. Every version here is one the roadmap
    # places *ahead* of the current one, so it is unreleased by construction,
    # and a `release` beat has already returned above - `wave` sets
    # `release_version` whenever it sets that beat - so the version a release
    # is actually due at is still offered.
    #
    # No exemption for the milestone the beat is about. There was one, for an
    # `implement` beat counting nothing: `implement` was also `wave`'s
    # fall-through when `_release_due` matched no arrangement, and one shape it
    # fell through on was a *finished* gate-only milestone reached from a row
    # that was not its own - so `RESERVED`'s "which is unfinished" would have
    # been printed against a milestone that was done. `_release_due` now
    # releases that shape from whichever row the project stands on, and
    # `implement` is returned only where an `own_scope` counts open work, so
    # the word has something behind it wherever it is printed (`PL-J45M`).
    for reserved in plan.reserved:
        if "{}.{}.{}".format(*reserved.version) == suggested:
            return ReleaseOffer(RESERVED, suggested, reserved.name)
    return ReleaseOffer(STANDS, suggested, "")


def stamp(items: list[Item], version: str) -> list[Item]:
    """Record which release a batch of finished work went out in."""
    return [item.__class__(**{**item.__dict__, "milestone": version}) for item in items]


def outstanding_roadmap_edits(roadmap: str, version: str, plan: Wave | None = None) -> list[str]:
    """The roadmap statements a cut release has just made wrong.

    Reported, never written. The version table's milestone column and the
    baseline section say what a release was *for*, which is a judgment about
    the work rather than a fact about the store - a generated row would either
    be thin or would overwrite something considered. What a tool can do is say
    exactly which statements are now stale, so the hand-off names them instead
    of leaving the next command to discover them as a test failure.

    Each string is one wrong statement, phrased as the state of the file
    rather than as an instruction, so a reader can check it against what they
    are looking at. The milestone statements end by naming the edit owed,
    because there two readings of one fact owe different edits.

    `plan` is the plan as it stood before the cut's bump, and where one is
    given it settles the one statement the file cannot (`PL-YS9F`). A milestone
    number the cut has exactly reached is this release where that plan's
    `release` beat asked for this very version, and a number a patch has taken
    under any other beat; without a plan the statement names both edits and
    the reader decides, as it always did.
    """
    # Imported here rather than at module scope: `roadmap` reads this module's
    # version grammar, so a top-level import would close the cycle.
    from .roadmap import (
        BASELINE_MARK,
        RELEASE,
        VERSION_TABLE_HEADING,
        baseline_heading,
        parse_milestones,
        parse_timeline,
        parse_version_table,
        stale_milestones,
        version_tuple,
    )

    name = version.lstrip("v")
    rows = parse_version_table(roadmap)
    if not rows:
        return [f'there is no version table under "{VERSION_TABLE_HEADING}"']

    owed: list[str] = []
    row = next((candidate for candidate in rows if candidate.version == name), None)
    if row is None:
        owed.append(f"the version table has no row for v{name}")
    elif not row.is_baseline:
        owed.append(f'the v{name} row (line {row.line}) is not marked "{BASELINE_MARK}"')
    owed.extend(
        f'the v{other.version} row (line {other.line}) is still marked "{BASELINE_MARK}"'
        for other in rows
        if other.is_baseline and other.version != name
    )

    heading = baseline_heading(roadmap)
    if heading is None:
        owed.append('there is no "Current baseline: vX.Y.Z" heading')
    elif heading[1] != name:
        owed.append(f"the baseline heading (line {heading[0]}) still names v{heading[1]}")

    # A milestone number the cut has reached or passed is the fourth statement
    # a release can make wrong, and the one nothing named: a patch cut at or
    # past the Qt port's number would have stepped the plan past the port while
    # the hand-off said only that the table lacked a row (`PL-Y1L0`). The table
    # lacks *this* release's row too at this point, which is why the statement
    # for a number the cut has exactly reached cannot decide between the edit
    # each reading owes from the file alone - and why the plan decides it where
    # the caller has one.
    reached = version_tuple(name)
    releasing = (
        None
        if plan is None
        else plan.beat == RELEASE
        and plan.release_version is not None
        and plan.release_version == reached
    )
    steps, _ = parse_timeline(roadmap)
    owed.extend(stale_milestones(steps, parse_milestones(roadmap), rows, reached, releasing))
    return owed
