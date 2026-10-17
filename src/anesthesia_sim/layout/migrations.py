"""The version this build writes its documents at, and how an older Workspace set is read.

`PL-SSQW` Q5 (project owner, 2026-09-27, ratified, over inheriting
`core/parameters.py`'s one-version window): the file a reader saves outlives
the build that wrote it, so a document's `schema_version` is answered in three
cases by name, and this module is the first of them. **Older than this build
writes: migrated in memory, one step per version.** Each `Migration` takes a
set document's body written at one version and returns it as the next version
writes it; `migrate` applies them in order from the version found up to
`LAYOUT_SCHEMA_VERSION`. The migrated set is written back only at the reader's
next "Save as default", when `layout/store.py` keeps the pre-migration file
once as `workspaces.v<N>.json`, and the reader is told only where a step says
it is lossy.

**Newer than this build writes** is `UnsupportedSchemaVersion`, raised before
any rule of this build's touches the body, and **invalid at a supported
version** is `LayoutFormatError`; both are raised in `layout/serialization.py`,
and what the store does with each is `layout/store.py`'s.

**At version 1 the table is empty and the hook exists**, so the first bump has
somewhere to go. The change that raises `LAYOUT_SCHEMA_VERSION` adds the step
that reads the version before it in the same commit, and `oldest_readable`
checks the chain when this module loads - the steps read consecutive versions
ending one below the current - so a version raised without its step fails at
import rather than at a reader's launch. The steps migrate the **set
document** `workspace_set_to_json` writes, the one document a reader's machine
keeps across builds; every other document in the tree ships with the build
and is at this version by construction.

**One number for every form the package writes.** The layout body, the
Workspace body and the set document change together, so the one
`schema_version` at the top of a document covers all of it (`PL-SSQW` Q2), and
a body carries no version of its own. It is defined here rather than in
`layout/serialization.py` because the version and the steps that bridge the
versions before it are one record.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    UnsupportedSchemaVersion,
)

__all__ = [
    "LAYOUT_SCHEMA_VERSION",
    "MIGRATIONS",
    "OLDEST_READABLE_VERSION",
    "Migrated",
    "Migration",
    "migrate",
    "oldest_readable",
]

# The version of the serialized form this build writes, and the newest it
# reads. Raised by the change that alters the shape, together with the
# `Migration` that reads the version before it.
LAYOUT_SCHEMA_VERSION: Final = 1


@dataclass(frozen=True, slots=True)
class Migration:
    """One step: a set document body written at `reads`, returned as `reads + 1` writes it.

    `lossy` is `None` for a step that keeps everything, and otherwise the
    sentence the reader is shown saying what the step could not carry over.

    Raises:
        TypeError: a field is not of its declared type.
        InvalidLayout: `reads` is below 1, or `lossy` is an empty sentence.
    """

    reads: int
    apply: Callable[[dict[str, object]], dict[str, object]]
    lossy: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.reads, bool) or not isinstance(self.reads, int):
            raise TypeError(
                f"a migration reads a version given as an int, not {type(self.reads).__name__}"
            )

        if not callable(self.apply):
            raise TypeError(f"a migration's apply is callable, not {type(self.apply).__name__}")

        if self.lossy is not None and not isinstance(self.lossy, str):
            raise TypeError(
                f"a migration's lossy is a str or None, not {type(self.lossy).__name__}"
            )

        if self.reads < 1:
            raise InvalidLayout(f"a schema version counts from 1, not {shown(self.reads)}")

        if self.lossy is not None and not self.lossy:
            raise InvalidLayout("a lossy migration says what it loses; an empty sentence does not")


@dataclass(frozen=True, slots=True)
class Migrated:
    """A body brought to the current version, and what the reader is told about the way."""

    body: dict[str, object]
    lossy: tuple[str, ...]


def oldest_readable(steps: tuple[Migration, ...], current: int) -> int:
    """The oldest version `steps` read up to `current`, checking the chain has no gap.

    Raises:
        InvalidLayout: a step reads a version out of sequence, so some version
            between the oldest and `current` has no step, or two have one.
    """

    oldest = current - len(steps)

    for index, step in enumerate(steps):
        expected = oldest + index

        if step.reads != expected:
            raise InvalidLayout(
                f"the migration at position {index} reads version {step.reads}, and the chain "
                f"up to version {current} needs the step reading version {expected} there"
            )

    return oldest


# The steps this build applies, in order, each reading the version the one
# before it writes. Empty at version 1, the only version there has been.
MIGRATIONS: Final[tuple[Migration, ...]] = ()

# The oldest version this build reads: the current one, less a step for each
# version before it that has one.
OLDEST_READABLE_VERSION: Final = oldest_readable(MIGRATIONS, LAYOUT_SCHEMA_VERSION)


def migrate(
    body: dict[str, object],
    written_at: int,
    steps: tuple[Migration, ...] = MIGRATIONS,
    current: int = LAYOUT_SCHEMA_VERSION,
) -> Migrated:
    """`body`, written at `written_at`, as version `current` writes it.

    `steps` and `current` are this build's unless a test passes its own chain.

    Raises:
        UnsupportedSchemaVersion: `written_at` is above `current`.
        LayoutFormatError: `written_at` is below the oldest version `steps`
            read, so no chain of steps reaches it.
        InvalidLayout: `steps` has a gap, as `oldest_readable` says, or a step
            returned something other than a dict.
    """

    oldest = oldest_readable(steps, current)

    if written_at > current:
        raise UnsupportedSchemaVersion(written_at, current)

    if written_at < oldest:
        raise LayoutFormatError(
            f"schema_version: this build reads versions from {oldest} to {current}, and "
            f"{shown(written_at)} is older than any it has a step for"
        )

    lossy: list[str] = []

    for step in steps[written_at - oldest :]:
        body = step.apply(body)

        if not isinstance(body, dict):
            raise InvalidLayout(
                f"the migration reading version {step.reads} returned {type(body).__name__}, "
                "and a step returns the body as a dict"
            )

        if step.lossy is not None:
            lossy.append(step.lossy)

    return Migrated(body, tuple(lossy))
