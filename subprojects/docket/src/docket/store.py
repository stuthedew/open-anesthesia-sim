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

from .model import Item, parse_item, render_item

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


def read_items(directory: Path) -> list[Item]:
    """Read every item in the store, in filename order."""
    if not directory.is_dir():
        return []
    return [
        parse_item(path.read_text(encoding="utf-8"), path.name)
        for path in sorted(directory.glob(ITEM_GLOB))
        if path.name != "README.md"
    ]


def write_item(directory: Path, item: Item, *, replace: Path | None = None) -> Path:
    """Write an item, removing the file it used to live in if it was renamed.

    A title edit changes the slug and so changes the filename. Writing the new
    name without removing the old one would leave two files claiming the same
    id, which `checks.py` reports as a duplicate - correctly, but confusingly,
    since the cause is a rename rather than a collision.
    """
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename_for(item)
    target.write_text(render_item(item), encoding="utf-8")
    if replace is not None and replace.resolve() != target.resolve() and replace.exists():
        replace.unlink()
    return target


def find_item(items: list[Item], reference: str) -> Item | None:
    """Resolve a user-typed reference to one item.

    Case-insensitive, and tolerant of a bare id without its prefix, because
    the id is typed by hand into commit subjects and command lines far more
    often than it is copied.
    """
    wanted = reference.strip().upper()
    if not wanted.startswith(ID_PREFIX):
        wanted = ID_PREFIX + wanted
    return next((item for item in items if item.identifier.upper() == wanted), None)
