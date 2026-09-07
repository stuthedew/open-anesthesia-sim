"""Per-project settings, so the package is usable outside the repository it grew in.

Everything here has a working default. A project that does not care about the
distinction between safety-critical and ordinary work, or that calls its
process work something else, should not have to write a config file to use
this - but a project that does care should not have to edit the source.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

CONFIG_NAME = "docket.toml"

#: Classes `checks.py` branches on that no setting above names. `anticipated`
#: claims the safety-band exemption for a concern whose feature does not exist
#: yet, so it has to be spellable; a project redeclaring `known_classes` and
#: leaving it out turns that exemption off, which fails closed and is correct.
BRANCHED_ON: tuple[str, ...] = ("anticipated",)


@dataclass(frozen=True)
class Config:
    """The knobs a project is likely to want to turn."""

    items_dir: str = "docs/items"
    #: Classes whose subject matter may not sit in the lower priority bands.
    safety_classes: tuple[str, ...] = ("safety", "science")
    #: Classes describing work on the process rather than on the product.
    process_classes: tuple[str, ...] = ("session-cost", "docs", "infra")
    #: Classes that make an open item recorded debt. Work already recognized
    #: as owed, as against work not yet begun: a project clearing debt before
    #: starting a milestone needs to know which is which, and the class labels
    #: are where it is written down.
    debt_classes: tuple[str, ...] = ("defect", "safety", "science", "refactor", "perf")
    #: Past this, the top band is too large to choose from at a glance.
    top_band_limit: int = 5
    #: Past this, an untriaged capture has become a second queue nobody reads.
    untriaged_stale_days: int = 14
    #: The date the `verify:` requirement started applying. An item that
    #: reaches `ready` must name the command that proves it done, but a store
    #: written before the rule existed holds items that predate it, and
    #: turning every one of them into an error at once makes the checker
    #: useless from its first run rather than making the queue better. So the
    #: requirement is anchored to a date a project records here: items
    #: captured on or after it are held to the rule, and the ones before it
    #: raise a grooming advisory only as each is about to be offered, which is
    #: also the first moment its command could be run before being written.
    #: `None` leaves the
    #: requirement off entirely, which is the right default for a project that
    #: does not delegate work and therefore has nothing riding on the field.
    verify_required_from: date | None = None
    #: The same requirement at the other end of an item's life: an item
    #: *closed* on or after this date must name a command or a
    #: `not-delegable` reason, as an error rather than an advisory. Anchored
    #: to the closure date rather than the capture date on purpose, since
    #: that is what lets it reach the set `verify_required_from` grandfathers
    #: - exempt at `ready`, and closing one is the first moment its command
    #: could be run before being written. `None` leaves it off.
    verify_required_at_close_from: date | None = None
    #: Classes that make a release a minor version bump rather than a patch.
    minor_classes: tuple[str, ...] = ("feature",)
    #: Every class an item may carry. Empty means "derive it", and the derived
    #: value is the union of the four lists above - every class this tool
    #: actually branches on. That default is the useful one: a class outside
    #: it changes no decision the tool makes, so a project that has declared
    #: nothing still gets the check that matters, which is that a class the
    #: tool reads is spelled the way the tool reads it.
    #:
    #: The check exists because these fields fail *open*. `classes: safey` is
    #: not in `safety_classes`, so the pin refusing to seat safety-critical
    #: work below the top band does not fire and nothing says so - a typo is
    #: enough to leave such an item in the bottom band (`PL-MVC2`). A project
    #: using descriptive classes beyond the four lists declares the whole
    #: vocabulary here; declaring some does not extend the derived set.
    known_classes: tuple[str, ...] = ()
    #: Paths holding the checks themselves. A delegated diff that edits one
    #: has changed the thing measuring it, so the measurement means nothing.
    gate_paths: tuple[str, ...] = (
        "Makefile",
        "pyproject.toml",
        ".github",
        ".claude",
        "docket.toml",
    )
    #: The project's own full check, run by `docket verify` alongside the
    #: item's command. Shelled out, so it may be whatever the project uses.
    check_command: str = "make check"
    #: Paths a delegated item may never modify, whatever its check proves.
    #: Empty by default, and that default is fail-closed rather than
    #: permissive: with nothing declared protected, no item is delegable at
    #: all. A project that has not said which of its files produce
    #: consequential output has not earned an unguarded delegation lane, and
    #: defaulting the other way would hand one to every project that never
    #: read this setting.
    protected_paths: tuple[str, ...] = ()
    #: Paths holding the apparatus the project is built *with*, as against the
    #: product it builds. `docket next workflow` and `docket next product`
    #: split the queue on this so two sessions can run at once without racing
    #: for the same item, reading each item's `touches` against it.
    #:
    #: Empty by default, and fail-closed like `protected_paths`: with no
    #: boundary declared, every item is unplaceable and the lane arguments are
    #: refused rather than quietly answering from the whole queue. A lane that
    #: silently degrades to "everything" is worse than no lane at all - it is
    #: the failure the split exists to prevent, wearing the flag that was
    #: supposed to prevent it.
    workflow_paths: tuple[str, ...] = ()
    #: Paths holding the product's own source and its tests, as against the
    #: prose written about it. `docket trend` splits product work on this, so
    #: that a period spent rewriting the roadmap is not read as a period spent
    #: building the thing - two very different answers to "what was the work".
    #: Unlike `workflow_paths` this fails *open*: with nothing declared, every
    #: product path is prose, which understates code and never invents it.
    code_paths: tuple[str, ...] = ("src", "tests")
    version_file: str = "pyproject.toml"
    #: The plan `docket wave` reads: the release train, the milestone
    #: sections, and the debt list each one records when it is scoped.
    roadmap_file: str = "ROADMAP.md"
    #: How the next version is chosen. "infer" derives it from the classes of
    #: what shipped, which suits a project where a patch is a patch. "manual"
    #: requires it to be named, for a project whose version marks the
    #: capability boundary a release crosses rather than counting changes -
    #: a distinction no class label can carry, and one this tool must not
    #: guess at, because a plausible wrong version is a provenance error.
    version_policy: str = "infer"
    extra: dict[str, object] = field(default_factory=dict)

    def vocabulary(self) -> frozenset[str]:
        """Every class an item may carry, declared or derived.

        Derived from the lists the tool branches on when nothing is declared,
        so the check is never comparing against an empty set and silently
        passing everything - which would be this check having the same defect
        it exists to catch.
        """
        if self.known_classes:
            return frozenset(self.known_classes)
        return frozenset(
            self.safety_classes
            + self.process_classes
            + self.debt_classes
            + self.minor_classes
            + BRANCHED_ON
        )


def _date(value: object, fallback: date | None, name: str = "verify_required_from") -> date | None:
    """Read a date written either as a TOML date literal or as a quoted string.

    Both spellings are accepted because both are natural to write and the
    difference between them is invisible in the file. A value that is neither
    is rejected by failing to parse rather than by falling back to the
    default: a cutover date silently ignored would leave the requirement off
    in a project that believed it had turned it on.
    """
    if value is None:
        return fallback
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError(f"{name}: {value!r} is not a date")


def _tuple(value: object, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return tuple(str(v) for v in value)
    return fallback


def load(root: Path) -> Config:
    """Read `docket.toml` from the project root, falling back to the defaults.

    A malformed config is reported by failing to parse rather than by being
    silently ignored: a setting that looks applied but is not is worse than
    one that was never written.
    """
    path = root / CONFIG_NAME
    if not path.is_file():
        return Config()
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", data)
    defaults = Config()
    return Config(
        items_dir=str(section.get("items_dir", defaults.items_dir)),
        safety_classes=_tuple(section.get("safety_classes"), defaults.safety_classes),
        process_classes=_tuple(section.get("process_classes"), defaults.process_classes),
        debt_classes=_tuple(section.get("debt_classes"), defaults.debt_classes),
        top_band_limit=int(section.get("top_band_limit", defaults.top_band_limit)),
        untriaged_stale_days=int(
            section.get("untriaged_stale_days", defaults.untriaged_stale_days)
        ),
        verify_required_from=_date(
            section.get("verify_required_from"), defaults.verify_required_from
        ),
        verify_required_at_close_from=_date(
            section.get("verify_required_at_close_from"),
            defaults.verify_required_at_close_from,
            "verify_required_at_close_from",
        ),
        minor_classes=_tuple(section.get("minor_classes"), defaults.minor_classes),
        known_classes=_tuple(section.get("known_classes"), defaults.known_classes),
        protected_paths=_tuple(section.get("protected_paths"), defaults.protected_paths),
        workflow_paths=_tuple(section.get("workflow_paths"), defaults.workflow_paths),
        gate_paths=_tuple(section.get("gate_paths"), defaults.gate_paths),
        check_command=str(section.get("check_command", defaults.check_command)),
        code_paths=_tuple(section.get("code_paths"), defaults.code_paths),
        version_file=str(section.get("version_file", defaults.version_file)),
        roadmap_file=str(section.get("roadmap_file", defaults.roadmap_file)),
        version_policy=str(section.get("version_policy", defaults.version_policy)),
    )
