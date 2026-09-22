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
    #:
    #: `housekeeping` is one of them, and is also the class `checks.py` reads
    #: to excuse an item from the two brief sections that argue for the work
    #: (see `checks.HOUSEKEEPING`). It is listed here rather than only in a
    #: project's `known_classes` for two reasons: the derived `vocabulary()`
    #: below is the union of these lists, so a project that declares nothing
    #: still gets the class; and the top-band rule counts an item as process
    #: work only when *every* class it carries is in this list, which a
    #: housekeeping-only item must satisfy.
    process_classes: tuple[str, ...] = ("session-cost", "docs", "infra", "housekeeping")
    #: Classes that make an open item recorded debt. Work already recognized
    #: as owed, as against work not yet begun: a project clearing debt before
    #: starting a milestone needs to know which is which, and the class labels
    #: are where it is written down.
    debt_classes: tuple[str, ...] = ("defect", "safety", "science", "refactor", "perf")
    #: Classes that make an open item new work - what a project is building,
    #: as against something it marked as wanting doing and set aside. `docket
    #: next --oldest` leaves these out and treats every other startable item as
    #: owed, which reaches the `docs`, `infra` and `test` work `debt_classes`
    #: never counts. A debt class or `needs-decision` overrides it
    #: (`plan.is_new_work`), so the two lists cannot disagree about one item.
    new_work_classes: tuple[str, ...] = ("feature", "planning")
    #: Past this, the top band is too large to choose from at a glance.
    top_band_limit: int = 5
    #: Past this, an untriaged capture has become a second queue nobody reads.
    untriaged_stale_days: int = 14
    #: Past this, a dated assertion in the instruction set is due for
    #: re-checking - not wrong, and not judged here, only old enough that
    #: nobody has confirmed it lately.
    #:
    #: **90 rather than 180, and the number is the load-bearing decision**
    #: (project owner, 2026-09-21, ratified, over 180). The threshold decides
    #: whether the advisory is ever tested before it matters. The oldest dated
    #: assertion in this repository's instruction set was 21 days old when
    #: this was set, so at 180 days the advisory names nothing for about 159
    #: days and then fires for the first time, untested, against assertions
    #: nobody remembers writing, in a session with no idea what it is for -
    #: the shape of a mechanism discovered to be broken at exactly the moment
    #: it was built to help. At 90 it first fires in about 69 days, while the
    #: assertions are recent enough to be judged quickly, and that first
    #: firing is the validation run. Raise it once the advisory has been seen
    #: to name the right things.
    instruction_stale_days: int = 90
    #: The instruction files whose dated assertions the advisory above audits:
    #: a markdown file, or a directory every `.md` beneath it is read from.
    #:
    #: Empty by default, which leaves the audit off. Not fail-closed in the
    #: sense `protected_paths` and `workflow_paths` are - there is nothing
    #: here to permit - but the same refusal to guess: which files instruct a
    #: session is a fact about a project's conventions, and a package that
    #: went looking for them would be encoding one repository's layout, which
    #: is what `notes_file` and `open_pull_requests_command` are also empty to
    #: avoid.
    instruction_paths: tuple[str, ...] = ()
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
    #: The date from which a `verify:` command may no longer stand a pytest
    #: run beside a separate discriminating clause. The field records the
    #: discriminator and nothing else, so a pytest clause with a *different*
    #: clause beside it proves the tree twice - once here, once in
    #: `check_command`, which every consumer already runs. Anchored to the
    #: capture date, so the commands already recorded are a closed set that
    #: drains as each item is started rather than in one pass. `None` leaves
    #: it off, and so does an empty `collected_test_paths`, which is what
    #: says which pytest targets `check_command` already covers.
    verify_prerequisite_refused_from: date | None = None
    #: The test trees `check_command` already runs, as the project spells
    #: them for its own runner. Only a pytest target inside one of these is
    #: provably redundant with `check_command`; one outside it is running
    #: something no other consumer does, and is left alone. Empty means "this
    #: project has not said", which leaves the rule above off rather than
    #: guessing.
    collected_test_paths: tuple[str, ...] = ()
    #: The date from which a `verify:` command may no longer narrow a pytest
    #: run with `-k`. Over a tree `collected_test_paths` names, such a run
    #: either selects tests `check_command` already proves or selects none
    #: and exits 5, so it can never be the ordinary failure the field owes -
    #: and a substring is satisfied by whatever test later comes to carry it.
    #: A date of its own rather than the prerequisite rule's, because the two
    #: close different sets. `None` leaves it off, and so does an empty
    #: `collected_test_paths`.
    verify_k_selector_refused_from: date | None = None
    #: The date the `payoff:` requirement started applying: an item reaching
    #: `ready` must carry one plain-language line of what closing it buys.
    #: Dated for the reason `verify_required_from` is - a store written before
    #: the rule holds items that predate it, and turning every one of them
    #: into an error at once makes the checker useless from its first run
    #: rather than making the queue better. Items captured before it raise a
    #: grooming advisory only as each is about to be offered, which is also
    #: where the sentence is cheapest: the session about to work an item
    #: already has its brief open.
    #:
    #: There is deliberately no close-time counterpart to
    #: `verify_required_at_close_from`. That one exists because closing an
    #: item is the first moment its command can be *run*, and a consequence
    #: needs no run - it is answerable in full the moment the item becomes a
    #: commitment, so the requirement has nowhere later to reach. `None`
    #: leaves it off.
    payoff_required_from: date | None = None
    #: The date from which an item at `needs-decision` must *mark* a
    #: recommendation in its brief - give one, or say in so many words that
    #: none is being made and why.
    #:
    #: The question survives in the item; the recommendation that would let it
    #: be answered in one read survives only in the reply that posed it, and a
    #: reply dies with its session. So the longer an item waits, the likelier
    #: the recommendation is gone when the answer arrives - backwards, because
    #: waiting is what the status is for. Measured over the 45 open
    #: `needs-decision` items on 2026-09-20: 8 marked one, 37 did not.
    #:
    #: An advisory and never an error, because a brief may honestly decline to
    #: recommend - `PL-PFK1` declines and says the deciding number cannot be
    #: measured retroactively. Marking the declination satisfies it, which is
    #: what keeps one pattern serving both endings.
    #:
    #: Anchored to the capture date, and paired in `checks.py` with the set
    #: `bin/docket next` is about to offer, because the two reach different
    #: sessions: the date reaches the session *writing* the item, while it
    #: still holds the reasoning, and the offered set reaches the session
    #: about to act on a question the store already holds. `None` leaves the
    #: requirement off.
    recommendation_required_from: date | None = None
    #: Classes that make a release a minor version bump rather than a patch.
    minor_classes: tuple[str, ...] = ("feature",)
    #: Every class an item may carry. Empty means "derive it", and the derived
    #: value is the union of the five lists above - every class this tool
    #: actually branches on. That default is the useful one: a class outside
    #: it changes no decision the tool makes, so a project that has declared
    #: nothing still gets the check that matters, which is that a class the
    #: tool reads is spelled the way the tool reads it.
    #:
    #: The check exists because these fields fail *open*. `classes: safey` is
    #: not in `safety_classes`, so the pin refusing to seat safety-critical
    #: work below the top band does not fire and nothing says so - a typo is
    #: enough to leave such an item in the bottom band (`PL-MVC2`). A project
    #: using descriptive classes beyond the five lists declares the whole
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
    #: A command printing, one branch name per line, every branch the project's
    #: forge has an open pull request for - each optionally followed by
    #: whitespace and that pull request's number. `docket flight` runs it to
    #: tell a branch waiting on review from one nobody opened, which is the
    #: second half of knowing that finished work has stalled, and to say on
    #: every row whether a pull request is open, since a branch outlives its
    #: session and an age alone cannot say so in the first hour (`PL-7TVT`).
    #:
    #: A command rather than an API call, because this package answers from a
    #: bare checkout with no network and knows nothing about GitHub or any
    #: other forge - nor should it, since which forge a project uses is not a
    #: fact about its queue. The project supplies the knowledge; this supplies
    #: the question.
    #:
    #: Empty by default, which turns the second half off: `flight` then reports
    #: a finished branch as finished-and-unasked rather than claiming nothing
    #: is open on it. The contract the command owes is the same refusal - exit
    #: non-zero, printing nothing, when it could not look, so that "looked,
    #: none open" and "could not look" never arrive as the same empty answer.
    open_pull_requests_command: str = ""
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
    #: Paths holding the machinery that identifies and ranks *generators* -
    #: the `root-cause-of:` field, the predicate that decides a claim is
    #: sound, the rank term that lifts one above every band but `P0`, and
    #: whatever surfaces the claim to a reader. An item declaring
    #: `impairs-generators:` claims to be a defect in that machinery, which
    #: puts it on the generator tier; this list is what refutes the claim
    #: when its `touches` reaches none of it.
    #:
    #: It can only refute, never decide. Measured against this project's store
    #: on 2026-09-19, 36 of 322 open items touch one of these files for
    #: reasons having nothing to do with generators, so promoting on the path
    #: alone would mean what promoting on citation density would mean -
    #: nothing (`tools/generator_check.py` makes the same argument about 33).
    #: The machinery is a few functions inside shared files, so the judgment
    #: stays the declaring session's and this is the cheap falsifier.
    #:
    #: Empty by default, and fail-closed like `protected_paths` and
    #: `workflow_paths`: with no machinery declared, every claim is unsound
    #: and `docket check` says so, rather than every claim being free.
    generator_paths: tuple[str, ...] = ()
    #: Paths holding the product's own source and its tests, as against the
    #: prose written about it. `docket trend` splits product work on this, so
    #: that a period spent rewriting the roadmap is not read as a period spent
    #: building the thing - two very different answers to "what was the work".
    #: Unlike `workflow_paths` this fails *open*: with nothing declared, every
    #: product path is prose, which understates code and never invents it.
    code_paths: tuple[str, ...] = ("src", "tests")
    #: A running cross-session notes file whose `##` sections are threads, if
    #: the project keeps one. `docket show` names the threads concerning the
    #: item being shown, which is the only thing that makes such a file
    #: reachable: the instruction it usually carries - read it if your task
    #: touches an open thread - cannot be followed without reading it first.
    #: Empty by default and hardcoded nowhere, so a project without one is
    #: unaffected and this package keeps no notion of any particular
    #: repository's layout.
    notes_file: str = ""
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
            + self.new_work_classes
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
        new_work_classes=_tuple(section.get("new_work_classes"), defaults.new_work_classes),
        top_band_limit=int(section.get("top_band_limit", defaults.top_band_limit)),
        untriaged_stale_days=int(
            section.get("untriaged_stale_days", defaults.untriaged_stale_days)
        ),
        instruction_stale_days=int(
            section.get("instruction_stale_days", defaults.instruction_stale_days)
        ),
        instruction_paths=_tuple(section.get("instruction_paths"), defaults.instruction_paths),
        verify_required_from=_date(
            section.get("verify_required_from"), defaults.verify_required_from
        ),
        verify_required_at_close_from=_date(
            section.get("verify_required_at_close_from"),
            defaults.verify_required_at_close_from,
            "verify_required_at_close_from",
        ),
        verify_prerequisite_refused_from=_date(
            section.get("verify_prerequisite_refused_from"),
            defaults.verify_prerequisite_refused_from,
            "verify_prerequisite_refused_from",
        ),
        collected_test_paths=_tuple(
            section.get("collected_test_paths"), defaults.collected_test_paths
        ),
        verify_k_selector_refused_from=_date(
            section.get("verify_k_selector_refused_from"),
            defaults.verify_k_selector_refused_from,
            "verify_k_selector_refused_from",
        ),
        payoff_required_from=_date(
            section.get("payoff_required_from"),
            defaults.payoff_required_from,
            "payoff_required_from",
        ),
        recommendation_required_from=_date(
            section.get("recommendation_required_from"),
            defaults.recommendation_required_from,
            "recommendation_required_from",
        ),
        minor_classes=_tuple(section.get("minor_classes"), defaults.minor_classes),
        known_classes=_tuple(section.get("known_classes"), defaults.known_classes),
        protected_paths=_tuple(section.get("protected_paths"), defaults.protected_paths),
        workflow_paths=_tuple(section.get("workflow_paths"), defaults.workflow_paths),
        generator_paths=_tuple(section.get("generator_paths"), defaults.generator_paths),
        gate_paths=_tuple(section.get("gate_paths"), defaults.gate_paths),
        check_command=str(section.get("check_command", defaults.check_command)),
        open_pull_requests_command=str(
            section.get("open_pull_requests_command", defaults.open_pull_requests_command)
        ),
        code_paths=_tuple(section.get("code_paths"), defaults.code_paths),
        notes_file=str(section.get("notes_file", defaults.notes_file)),
        version_file=str(section.get("version_file", defaults.version_file)),
        roadmap_file=str(section.get("roadmap_file", defaults.roadmap_file)),
        version_policy=str(section.get("version_policy", defaults.version_policy)),
    )
