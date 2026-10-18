"""Reading and writing the item directory, and allocating ids.

The store is a directory of markdown files and nothing else - no index, no
database, no manifest. Anything an index would hold can be recomputed by
reading the files, and an index is one more thing two branches can conflict
over. Recomputing costs milliseconds at this scale and buys the property the
whole design turns on: adding work is adding a file.
"""

from __future__ import annotations

import random
import re
import unicodedata
from pathlib import Path

from .model import Item, parse_item, render_item, with_front_matter_field, with_front_matter_value

# Which files the store reads, and not whose they are. The store takes an
# item's id from its front matter, and reads every markdown file so that
# `docket check` sees each one; a reader that has only a name - a tree listing,
# a diff, a glob - takes the id from it by `vcs.ITEM_FILE_RE`, which is the
# grammar `filename_for` writes. A file named otherwise is still read here, and
# `checks._check_filenames` names it, as it names any drifted slug (`PL-5QG4`).
ITEM_GLOB = "*.md"

# Ids are random, not sequential, and that is the point. A sequential id has
# to be allocated by reading every existing id and adding one, which is a
# read-modify-write on shared state: two branches that allocate at the same
# time both pick the same number and neither finds out until they merge. A
# random id needs no coordination at all.
#
# Crockford base32 minus the vowels that turn into words, four characters:
# about a million values, which for a backlog measured in hundreds means a
# collision is not going to happen. `checks.py` still tests for one, because
# "not going to happen" is not the same as "cannot".
ID_ALPHABET = "0123456789BCDFGHJKLMNPQRSTVWXYZ"
ID_LENGTH = 4
ID_PREFIX = "PL-"

# Historical ids are sequential (`PL-001`); new ones are random (`PL-K7QX`).
# Both are accepted forever: the old ones are cited from `ROADMAP.md`, from
# commit messages, and from each other, and renumbering them to tidy the
# scheme would break every one of those references to no benefit.
#
# The pattern is exported unanchored as well, because an id has to be
# recognised inside prose too - `roadmap.py` reads them out of the debt list
# a milestone records - and two spellings of the same grammar would drift.
ID_PATTERN = rf"{ID_PREFIX}(?:[{ID_ALPHABET}]{{{ID_LENGTH}}}|\d{{3}})(?![{ID_ALPHABET}])"
ID_RE = re.compile(rf"^{ID_PATTERN}$")
SLUG_RE = re.compile(r"[^a-z0-9]+")
_CITED_ID_RE = re.compile(ID_PATTERN)


def cited_ids(text: str, own: str) -> frozenset[str]:
    """The ids an item's file names other than its own, anywhere in the file.

    The one reading of which items an item cites, for
    `tools/generator_check.py`'s citation signal and `tools/item_reads.py`'s
    traversal count (`PL-86H3`). The front matter counts: an id named only in
    `root-cause-of:` or `blocked-by:` is the strongest citation an item makes,
    and the body-only reading in `item_reads` missed it.
    """
    return frozenset(_CITED_ID_RE.findall(text)) - {own}


# An item file's whole name, as `filename_for` writes one: the id, then a
# slug, then the suffix. This is what tells a `touches` entry that names *an
# item* from one that names the store directory itself - 48 of this store's 95
# entries under `docs/items/` on 2026-09-19 are the bare directory, written by
# release cuts that rewrite many briefs at once, and those claim nothing about
# any one item.
#
# Named apart from `vcs.ITEM_FILE_RE`, which is the same id capture without the
# suffix anchor: that one pulls an id out of a path git already reported, so it
# must match a prefix, and this one judges a string a person typed, so it must
# refuse everything that is not a whole filename. One name over two rules is
# how a reader imports the wrong one.
DECLARED_ITEM_RE = re.compile(rf"^({ID_PATTERN})-.+\.md$")


def new_id(taken: set[str], rng: random.Random | None = None) -> str:
    """Allocate an id that no existing item uses.

    Takes the ids already in use only to rule out the astronomically unlikely
    duplicate, never to derive the next value from them. Nothing about the
    result depends on what else is in the store, which is what makes it safe
    to do this on two branches at once.
    """
    source = rng or random.SystemRandom()
    while True:
        candidate = ID_PREFIX + "".join(source.choice(ID_ALPHABET) for _ in range(ID_LENGTH))
        if candidate not in taken:
            return candidate


def slugify(title: str, limit: int = 48) -> str:
    """Reduce a title to the filename half of an item's path."""
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = SLUG_RE.sub("-", normalized.lower()).strip("-")
    if len(slug) <= limit:
        return slug or "item"
    return slug[:limit].rsplit("-", 1)[0] or slug[:limit]


def filename_for(item: Item) -> str:
    """The file an item belongs in: its id, then a human-readable slug.

    The id leads so that a file can be found from a commit subject or a branch
    name without knowing the title, and the slug follows so that a directory
    listing is readable without opening anything.
    """
    return f"{item.identifier}-{slugify(item.title)}.md"


def declared_item_file(entry: str, items_dir: str) -> tuple[str, str] | None:
    """The (id, filename) a `touches` entry names inside the store, or `None`.

    `None` for every entry that is not a claim about one item's file: a path
    outside the store, the store directory itself, a subdirectory, anything
    inside it that no id leads. Decided from the name rather than by asking
    the filesystem, which keeps `analyze` pure - and the id is also the more
    useful half, since it is what lets `docket check` say where the item
    actually lives instead of only that the path is wrong.

    Here rather than in `checks`, its first reader, because the near-duplicate
    search asks it too: whether two declarations name one item, or only the
    directory every capturing branch changes (`PL-0HLS`).
    """
    prefix = items_dir.strip().strip("/")
    candidate = entry.strip().strip("/")
    if not candidate.startswith(f"{prefix}/"):
        return None
    name = candidate[len(prefix) + 1 :]
    match = DECLARED_ITEM_RE.match(name)
    return None if match is None else (match.group(1), name)


def read_items(directory: Path) -> list[Item]:
    """Read every item in the store, in filename order."""
    if not directory.is_dir():
        return []
    return [
        parse_item(path.read_text(encoding="utf-8"), path.name)
        for path in sorted(directory.glob(ITEM_GLOB))
        if path.name != "README.md"
    ]


def write_item(directory: Path, item: Item) -> Path:
    """Write a new item under the name its title gives it.

    This is the writer for creating an item, and it removes nothing: written
    over an item whose file has another name, it leaves two files claiming one
    id, which `checks.py` reports as a duplicate. A command writing a field
    reaches for `rewrite_item` instead, whatever it finds the name to be: see
    there for why a rename arriving as a side effect is worse than a stale slug.

    A rename is a pass of its own, made with `git mv` (`PL-YTDN`), which is the
    route `docket check`'s stale-slug advisory names. This function used to take
    a `replace=` path and delete it, a rename branch with no caller left that
    the next field writer could have reached for without anything failing to
    say so (`PL-9KSY`).
    """
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename_for(item)
    target.write_text(render_item(item), encoding="utf-8")
    return target


def rewrite_item(directory: Path, item: Item) -> Path:
    """Write an item back to the file it was read from, whatever its title now says.

    `write_item` names the file from the title, which is right for a new item
    and wrong for a write to an existing one: a rename arriving as a side
    effect lands in a diff about something else, where nobody is looking for
    it, and conflicts against a branch holding the file instead of merging with
    it (`PL-LBR6`). So a field write keeps the name, and bringing a drifted name
    back into line stays a pass of its own, made with `git mv` (`PL-YTDN`).

    The front matter is still rendered in canonical order, which is right for
    a command that was asked to change a field and wrong for one that was
    asked to *add* one: on a file the tool did not write, re-rendering moves
    keys and reflows multi-line values, and those are removals in a diff about
    something else. `insert_field` is the writer for that case.
    """
    if not item.path:
        raise ValueError(f"{item.identifier or 'the item'} was not read from a file")
    target = directory / item.path
    target.write_text(render_item(item), encoding="utf-8")
    return target


def insert_field(
    directory: Path, item: Item, name: str, value: str, *, append: bool = False
) -> Path:
    """Add one front-matter field to an item, leaving every other byte as it was.

    The third writer here, and the three differ by what they leave alone:
    `write_item` re-derives the filename and re-renders the file,
    `rewrite_item` keeps the name and re-renders, and this keeps the name and
    the existing text both.

    That last one is what `bin/docket record` needs and what `PL-LBR6` and
    `PL-7K8Y` are the two halves of. The `docket` skill grants `record` a
    standing exemption from the in-flight guard on the grounds that two
    sessions running it write the same line and git merges them, and
    `verify.sanctioned_queue_edit` exempts its write from the close-out audit
    on the grounds that the item reads as it did with one field added, every
    other in its place. A rename defeated the first and a reorder defeated the
    second; both were the same cause, a field write re-rendering a file it was
    not asked to rewrite.

    Reads the file rather than rendering `item`, so the value written is the
    only thing about the block that comes from the caller.

    `append` extends a list field that already exists instead of refusing,
    which is what `bin/docket new` needs for the second and later filings it
    matches to one item. Byte-faithfulness is the reason it lands here rather
    than in a re-render: see `with_front_matter_field`.
    """
    if not item.path:
        raise ValueError(f"{item.identifier or 'the item'} was not read from a file")
    target = directory / item.path
    text = target.read_text(encoding="utf-8")
    target.write_text(with_front_matter_field(text, name, value, append=append), encoding="utf-8")
    return target


def replace_field(directory: Path, item: Item, name: str, value: str) -> Path:
    """Rewrite one front-matter field's value, leaving every other byte as it was.

    `insert_field`'s counterpart, and the writer for a field that changes
    rather than grows: `bin/docket withdraw` annotating a `recurrences:` entry
    it is disowning. Byte-faithfulness matters here for the reason it matters
    there - a re-render normalises key order and reflows multi-line values, and
    both are removals in a diff about something else (`PL-LBR6`, `PL-7K8Y`).

    Reads the file rather than rendering `item`, so the value written is the
    only thing about the block that comes from the caller.
    """
    if not item.path:
        raise ValueError(f"{item.identifier or 'the item'} was not read from a file")
    target = directory / item.path
    text = target.read_text(encoding="utf-8")
    target.write_text(with_front_matter_value(text, name, value), encoding="utf-8")
    return target


def find_item(items: list[Item], reference: str) -> Item | None:
    """Resolve a user-typed reference to one item.

    Case-insensitive, and tolerant of a bare id without its prefix, because
    the id is typed by hand into commit subjects and command lines far more
    often than it is copied.
    """
    wanted = as_identifier(reference)
    return next((item for item in items if item.identifier.upper() == wanted), None)


def as_identifier(reference: str) -> str:
    """A typed reference as the store spells an id: upper case, with its prefix supplied.

    `k7qx`, `pl-k7qx` and `PL-K7QX` are one id. `find_item` resolves an item
    through this, and `claim`, `yield` and `show` read a typed id through it
    too, so a reference one of them takes is one the others take (`PL-4DK2`).
    The result is not checked against the id grammar; a caller that needs an
    id holds it to `ID_RE`.
    """
    wanted = reference.strip().upper()
    return wanted if wanted.startswith(ID_PREFIX) else ID_PREFIX + wanted
