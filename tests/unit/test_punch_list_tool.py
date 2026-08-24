"""Tests for `tools/punch_list.py`, the punch-list checker.

The tool's value is entirely in the failures it catches, so every check has a
test that constructs the broken input and asserts the tool notices. A checker
that has only ever been run against a clean file proves nothing.

Fixtures are built by `_document()` from minimal valid entries, so a test
names only the one thing it breaks.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import punch_list

TODAY = date(2026, 8, 23)

BANDS = {
    "P0": "## P0 — Now",
    "P1": "## P1 — Next",
    "P2": "## P2 — Queued",
    "P3": "## P3 — Icebox",
}


def _entry(
    identifier: str = "PL-001",
    *,
    priority: str = "P1",
    effort: str = "M",
    status: str = "ready",
    classes: tuple[str, ...] = ("perf",),
    added: str = "2026-08-01",
    title: str = "Do the thing",
    fields: dict[str, str] | None = None,
    filler: int = 0,
) -> str:
    """Build one syntactically valid entry, minus whatever a test removes."""
    brief = {
        "Problem": "Something is wrong.",
        "Why it matters": "It has a consequence.",
        "Where": "`core/thing.py`.",
        "Done when": "It is no longer wrong.",
    }
    if fields is not None:
        brief = fields
    rendered = " ".join(f"`{name}`" for name in classes)
    lines = [
        f"### {identifier} {title}",
        f"`{priority}` · `{effort}` · {rendered} · {status} · added {added}",
        "",
        *[f"**{name}.** {value}" for name, value in brief.items()],
        *[f"Filler line {n}." for n in range(filler)],
        "",
    ]
    return "\n".join(lines)


def _document(
    *entries: str,
    completed: tuple[str, ...] = (),
    archived: tuple[str, ...] = (),
) -> str:
    """Assemble entries into a punch list, each under its declared band."""
    body = ["# Punch list", ""]
    for priority, heading in BANDS.items():
        body.append(heading)
        body.append("")
        for entry in entries:
            if f"`{priority}`" in entry.splitlines()[1]:
                body.append(entry)
    body.append("## Recently completed")
    body.append("")
    body.extend(f"- {identifier} Some finished thing — `abc1234`" for identifier in completed)
    body.append("## Archive")
    body.append("")
    body.extend(
        f"- {identifier} Some old thing — closed 2026-08-24, superseded" for identifier in archived
    )
    return "\n".join(body) + "\n"


def _analyze(text: str, **kwargs: object) -> punch_list.Report:
    related = kwargs.pop("related", None)
    assert not kwargs
    return punch_list.analyze(text, TODAY, related)  # type: ignore[arg-type]


def _messages(items: list[str], needle: str) -> bool:
    return any(needle in message for message in items)


# --- parsing ---------------------------------------------------------------


def test_parses_a_valid_entry() -> None:
    report = _analyze(_document(_entry()))

    assert report.errors == []
    (entry,) = report.entries
    assert entry.identifier == "PL-001"
    assert entry.title == "Do the thing"
    assert entry.priority == "P1"
    assert entry.effort == "M"
    assert entry.status == "ready"
    assert entry.classes == ("perf",)
    assert entry.added == date(2026, 8, 1)


def test_metadata_is_read_by_token_not_position() -> None:
    """Reordering the metadata line must not change what is parsed."""
    reordered = _entry().replace(
        "`P1` · `M` · `perf` · ready · added 2026-08-01",
        "added 2026-08-01 · ready · `perf` · `M` · `P1`",
    )
    (entry,) = _analyze(_document(reordered)).entries

    assert (entry.priority, entry.effort, entry.status) == ("P1", "M", "ready")


def test_fenced_template_is_not_parsed_as_an_entry() -> None:
    """The format example in the file's own header is not a real item."""
    text = _document(_entry()).replace(
        "# Punch list",
        "# Punch list\n\n```text\n### PL-999 Template title\n`P1` · `M` · `x` · ready\n```",
    )
    report = _analyze(text)

    assert [entry.identifier for entry in report.entries] == ["PL-001"]


def test_real_punch_list_is_clean() -> None:
    """The punch list shipped in this repository must pass its own checks."""
    root = Path(__file__).resolve().parents[2]
    related = {
        path: path.read_text(encoding="utf-8")
        for path in (root / "docs" / "WORKING_NOTES.md", root / "ROADMAP.md")
    }
    report = punch_list.analyze(
        (root / "docs" / "PUNCH_LIST.md").read_text(encoding="utf-8"), TODAY, related
    )

    assert report.errors == []


# --- errors ----------------------------------------------------------------


def test_duplicate_id_is_an_error() -> None:
    report = _analyze(_document(_entry("PL-001"), _entry("PL-001", title="Other")))

    assert _messages(report.errors, "id already used")


def test_priority_disagreeing_with_its_section_is_an_error() -> None:
    """Catches an item moved between bands without its metadata updated."""
    misfiled = _entry(priority="P2").replace("`P2`", "`P1`", 1)
    text = _document().replace("## P2 — Queued\n", f"## P2 — Queued\n\n{misfiled}")
    report = _analyze(text)

    assert _messages(report.errors, "filed under the P2 section but marked P1")


def test_missing_brief_field_is_an_error() -> None:
    report = _analyze(
        _document(_entry(fields={"Problem": "x", "Why it matters": "y", "Where": "z"}))
    )

    assert _messages(report.errors, "**Done when.**")


def test_blocked_entry_omits_done_when() -> None:
    """A blocked item cannot always state its finish condition yet."""
    report = _analyze(
        _document(
            _entry(
                priority="P3",
                status="blocked",
                fields={
                    "Problem": "x",
                    "Why it matters": "y",
                    "Where": "z",
                    "Blocked by": "PL-002.",
                },
            )
        )
    )

    assert report.errors == []


def test_blocked_entry_must_name_its_blocker() -> None:
    report = _analyze(
        _document(
            _entry(
                priority="P3",
                status="blocked",
                fields={
                    "Problem": "x",
                    "Why it matters": "y",
                    "Where": "z",
                    "Blocked by": "something unwritten.",
                },
            )
        )
    )

    assert _messages(report.errors, "names no blocking PL- item")


def test_needs_decision_entry_must_state_the_decision() -> None:
    report = _analyze(_document(_entry(status="needs-decision")))

    assert _messages(report.errors, "states no decision to make")


def test_safety_class_may_not_sit_below_p1() -> None:
    """CLAUDE.md's standard, enforced rather than remembered."""
    report = _analyze(_document(_entry(priority="P2", classes=("ux", "safety"))))

    assert _messages(report.errors, "safety-critical work starts at P0 or P1")


def test_missing_effort_is_an_error() -> None:
    text = _document(_entry()).replace(" · `M` · ", " · ")
    report = _analyze(text)

    assert _messages(report.errors, "no effort estimate")


def test_missing_added_date_is_an_error() -> None:
    text = _document(_entry()).replace(" · added 2026-08-01", "")
    report = _analyze(text)

    assert _messages(report.errors, "no 'added YYYY-MM-DD' date")


def test_item_both_open_and_completed_is_an_error() -> None:
    report = _analyze(_document(_entry("PL-001"), completed=("PL-001",)))

    assert _messages(report.errors, "listed as completed but still open")


def test_item_both_open_and_archived_is_an_error() -> None:
    report = _analyze(_document(_entry("PL-001"), archived=("PL-001",)))

    assert _messages(report.errors, "listed as archived but still open")


def test_item_recorded_in_both_resolved_sections_is_an_error() -> None:
    """One disposal per item; two records mean one of them is a lie."""
    report = _analyze(_document(_entry("PL-001"), completed=("PL-002",), archived=("PL-002",)))

    assert _messages(report.errors, "recorded under both")


def test_archived_id_resolves_a_cross_reference() -> None:
    """Archiving an item must never turn a live pointer into a build error.

    `ROADMAP.md` cites completed ids permanently, so a reference has to keep
    resolving after the item ages out of "Recently completed".
    """
    report = _analyze(
        _document(_entry("PL-001", effort="S"), archived=("PL-404",)),
        related={Path("ROADMAP.md"): "Closed by PL-404."},
    )

    assert report.errors == []


def test_working_notes_thread_for_an_archived_item_is_flagged() -> None:
    report = _analyze(
        _document(_entry("PL-001", effort="S"), archived=("PL-002",)),
        related={Path("docs/WORKING_NOTES.md"): "## Open thread: something - PL-002"},
    )

    assert report.errors == []
    assert _messages(report.advisories, "delete it rather than leaving it stale")


def test_blocked_by_an_archived_item_is_flagged_for_promotion() -> None:
    """A blocker that was dropped unblocks its dependant just as landing does."""
    report = _analyze(
        _document(
            _entry(
                "PL-003",
                priority="P3",
                status="blocked",
                fields={
                    "Problem": "x",
                    "Why it matters": "y",
                    "Where": "z",
                    "Blocked by": "PL-002.",
                },
            ),
            archived=("PL-002",),
        )
    )

    assert _messages(report.advisories, "promote it to ready")


def test_dangling_cross_reference_is_an_error() -> None:
    """A pointer to an item that never existed loses the reader."""
    report = _analyze(
        _document(_entry("PL-001")),
        related={Path("docs/WORKING_NOTES.md"): "See PL-404 for context."},
    )

    assert _messages(report.errors, "PL-404")


# --- grooming advisories ---------------------------------------------------


def test_overlong_entry_is_an_advisory_not_an_error() -> None:
    report = _analyze(_document(_entry(filler=punch_list.MAX_ENTRY_LINES + 5)))

    assert report.errors == []
    assert _messages(report.advisories, "move the narrative")


def test_entry_at_the_length_limit_is_not_flagged() -> None:
    report = _analyze(_document(_entry(filler=0)))

    assert not _messages(report.advisories, "move the narrative")


def test_blocked_by_a_landed_item_is_flagged_for_promotion() -> None:
    report = _analyze(
        _document(
            _entry(
                "PL-003",
                priority="P3",
                status="blocked",
                fields={
                    "Problem": "x",
                    "Why it matters": "y",
                    "Where": "z",
                    "Blocked by": "PL-002.",
                },
            ),
            completed=("PL-002",),
        )
    )

    assert _messages(report.advisories, "promote it to ready")


def test_stale_item_is_flagged() -> None:
    report = _analyze(_document(_entry(added="2025-01-01")))

    assert _messages(report.advisories, "do it, demote it, or drop it")


def test_large_item_outside_the_icebox_is_flagged() -> None:
    report = _analyze(_document(_entry(priority="P1", effort="L")))

    assert _messages(report.advisories, "scope it into a ROADMAP.md milestone")


def test_no_short_ready_item_is_flagged() -> None:
    """The queue must always hold something a leftover-time session can take."""
    report = _analyze(_document(_entry(effort="M")))

    assert _messages(report.advisories, "nothing is both ready and sized S")


def test_short_ready_item_satisfies_the_check() -> None:
    report = _analyze(_document(_entry(effort="S")))

    assert not _messages(report.advisories, "nothing is both ready and sized S")


def test_working_notes_thread_for_a_completed_item_is_flagged() -> None:
    report = _analyze(
        _document(_entry("PL-001", effort="S"), completed=("PL-002",)),
        related={Path("docs/WORKING_NOTES.md"): "## Open thread: something - PL-002"},
    )

    assert report.errors == []
    assert _messages(report.advisories, "delete it rather than leaving it stale")


def test_oversized_queue_is_flagged() -> None:
    entries = [
        _entry(f"PL-{n:03d}", priority="P3", effort="S", title=f"Item {n}")
        for n in range(1, punch_list.MAX_OPEN_ITEMS + 3)
    ]
    report = _analyze(_document(*entries))

    assert _messages(report.advisories, "become a backlog")


def test_a_long_but_well_shaped_queue_is_not_flagged() -> None:
    """Length alone is not a defect. A queue whose top band is short, mostly
    ready, and mostly product work answers "what is next?" however many items
    sit behind it in the icebox, and must not draw an advisory that trains its
    reader to dismiss the ones that matter."""
    top = [
        _entry(f"PL-{n:03d}", priority="P1", effort="S", classes=("defect",), title=f"Top {n}")
        for n in range(1, punch_list.MAX_BAND_ITEMS + 1)
    ]
    icebox = [
        _entry(f"PL-1{n:02d}", priority="P3", effort="S", title=f"Later {n}")
        for n in range(1, punch_list.MAX_OPEN_ITEMS - punch_list.MAX_BAND_ITEMS + 1)
    ]
    report = _analyze(_document(*top, *icebox))

    assert report.errors == []
    assert report.advisories == []


# --- grooming: the shape of the top band ------------------------------------


def test_wide_top_band_is_flagged() -> None:
    entries = [
        _entry(f"PL-{n:03d}", priority="P1", effort="S", classes=("defect",), title=f"Item {n}")
        for n in range(1, punch_list.MAX_BAND_ITEMS + 2)
    ]
    report = _analyze(_document(*entries))

    assert _messages(report.advisories, '"what is next?" has no answer')


def test_top_band_of_open_decisions_is_flagged() -> None:
    """A band nothing can be started from needs decisions scheduled, not tasks."""
    report = _analyze(
        _document(
            _entry("PL-001", priority="P1", effort="S", status="needs-decision"),
            _entry("PL-002", priority="P1", effort="S", status="needs-decision"),
            _entry("PL-003", priority="P1", effort="S", status="ready"),
        )
    )

    assert _messages(report.advisories, "schedule the decisions, they are the work")


def test_top_band_of_mostly_ready_items_is_not_flagged() -> None:
    report = _analyze(
        _document(
            _entry("PL-001", priority="P1", effort="S", status="needs-decision"),
            _entry("PL-002", priority="P1", effort="S", status="ready"),
            _entry("PL-003", priority="P1", effort="S", status="ready"),
        )
    )

    assert not _messages(report.advisories, "schedule the decisions")


def test_top_band_crowded_by_process_work_is_flagged() -> None:
    """The capture rule promotes `session-cost` work to P1 and sets no ceiling,
    so process items accumulate at the top ahead of the simulator's own
    correctness. This is the check that notices."""
    report = _analyze(
        _document(
            _entry("PL-001", priority="P1", effort="S", classes=("session-cost", "infra")),
            _entry("PL-002", priority="P1", effort="S", classes=("docs", "session-cost")),
            _entry("PL-003", priority="P1", effort="S", classes=("science",)),
        )
    )

    assert _messages(report.advisories, "2 of 3 items are process work")
    assert _messages(report.advisories, "PL-001, PL-002")


def test_a_mixed_class_item_is_not_counted_as_process_work() -> None:
    """`science` and `infra` together is science work that happens to touch
    tooling, not process overhead."""
    report = _analyze(
        _document(
            _entry("PL-001", priority="P1", effort="S", classes=("science", "infra")),
            _entry("PL-002", priority="P1", effort="S", classes=("docs", "session-cost")),
        )
    )

    assert not _messages(report.advisories, "process work")


def test_band_checks_apply_to_p0_when_a_hotfix_is_open() -> None:
    """P0 is the band a session reads when anything sits in it."""
    entries = [
        _entry(f"PL-{n:03d}", priority="P0", effort="S", classes=("safety",), title=f"Item {n}")
        for n in range(1, punch_list.MAX_BAND_ITEMS + 2)
    ]
    report = _analyze(_document(*entries))

    assert _messages(report.advisories, "P0: 6 items in the top band")


def test_a_wide_icebox_does_not_trip_the_band_checks() -> None:
    """The icebox is allowed to be wide; that is what it is for."""
    entries = [
        _entry(f"PL-{n:03d}", priority="P3", effort="S", title=f"Item {n}")
        for n in range(1, punch_list.MAX_BAND_ITEMS + 3)
    ]
    report = _analyze(_document(*entries, _entry("PL-900", priority="P1", effort="S")))

    assert not _messages(report.advisories, "in the top band")


# --- model guidance ---------------------------------------------------------


def test_safety_classed_entry_warrants_a_strong_model() -> None:
    """Mirrors CLAUDE.md's model-matching rule: safety-critical work is
    reasoning-heavy regardless of size or how routine the fix looks."""
    (entry,) = _analyze(_document(_entry(classes=("perf", "safety")))).entries

    assert entry.model_guidance == "safety-tagged"


def test_science_classed_entry_warrants_a_strong_model() -> None:
    (entry,) = _analyze(_document(_entry(classes=("science",)))).entries

    assert entry.model_guidance == "science-tagged"


def test_needs_decision_entry_warrants_a_strong_model() -> None:
    """An unresolved design question is the 'ambiguous problem or genuine
    trade-off' CLAUDE.md names, even outside the safety/science classes."""
    (entry,) = _analyze(_document(_entry(status="needs-decision", classes=("refactor",)))).entries

    assert entry.model_guidance == "open design decision"


def test_routine_entry_has_no_model_guidance() -> None:
    (entry,) = _analyze(_document(_entry(classes=("docs",), status="ready"))).entries

    assert entry.model_guidance is None


def test_digest_flags_model_guidance_on_the_p0_line() -> None:
    report = _analyze(_document(_entry("PL-001", priority="P0", effort="S", classes=("safety",))))
    digest = punch_list.format_digest(report)

    assert "safety-tagged" in digest
    assert "opusplan" in digest


def test_digest_flags_model_guidance_on_the_top_p1_line() -> None:
    report = _analyze(_document(_entry(priority="P1", status="needs-decision")))
    digest = punch_list.format_digest(report)

    assert "open design decision" in digest
    assert "opusplan" in digest


def test_digest_omits_model_guidance_for_routine_items() -> None:
    report = _analyze(_document(_entry(priority="P1", classes=("docs",))))
    digest = punch_list.format_digest(report)

    assert "opusplan" not in digest


# --- output ----------------------------------------------------------------


def test_digest_leads_with_p0_and_stays_short() -> None:
    report = _analyze(
        _document(
            _entry("PL-001", priority="P0", effort="S", classes=("safety",), title="Bad number"),
            _entry("PL-002", priority="P1", title="Next thing"),
        )
    )
    digest = punch_list.format_digest(report)

    assert "P0 (hotfix, before feature work): PL-001 Bad number" in digest
    assert "Top P1: PL-002 Next thing" in digest
    assert len(digest.splitlines()) <= 8


def test_digest_reminds_about_grooming_only_when_due() -> None:
    clean = punch_list.format_digest(_analyze(_document(_entry(effort="S"))))
    stale = punch_list.format_digest(_analyze(_document(_entry(effort="S", added="2025-01-01"))))

    assert "Grooming due" not in clean
    assert "Grooming due: 1 advisory" in stale


def test_digest_is_empty_for_an_empty_queue() -> None:
    assert punch_list.format_digest(_analyze(_document())) == ""


def test_list_carries_every_field_a_recommendation_branches_on() -> None:
    report = _analyze(
        _document(
            _entry("PL-001", priority="P1", effort="S", status="ready", title="Fix the thing"),
            _entry("PL-002", priority="P2", effort="M", status="blocked", title="Wait on it"),
        )
    )
    listing = punch_list.format_list(report)

    assert "P1 PL-001 Fix the thing (S, ready)" in listing
    assert "P2 PL-002 Wait on it (M, blocked)" in listing


def test_list_carries_model_guidance() -> None:
    """So that choosing from the listing does not need the file to apply
    CLAUDE.md's model-matching rule."""
    report = _analyze(_document(_entry("PL-001", effort="S", classes=("safety",))))

    assert "safety-tagged, strongest model" in punch_list.format_list(report)


def test_list_says_it_is_not_enough_to_work_from() -> None:
    """The brief is what makes an item startable cold; a one-line title looks
    actionable and is not."""
    report = _analyze(_document(_entry(effort="S")))

    assert "Read an entry's brief before starting it" in punch_list.format_list(report)


def test_list_is_one_line_per_item_plus_a_header_and_a_footer() -> None:
    entries = [_entry(f"PL-{n:03d}", effort="S", title=f"Item {n}") for n in range(1, 8)]
    listing = punch_list.format_list(_analyze(_document(*entries)))

    assert len(listing.splitlines()) == len(entries) + 2


def test_list_is_far_cheaper_than_the_file_it_summarizes() -> None:
    """The whole point of the mode. Briefs are the bulk of the file and are
    not needed to choose between items."""
    entries = [_entry(f"PL-{n:03d}", effort="S", title=f"Item {n}") for n in range(1, 20)]
    document = _document(*entries)
    listing = punch_list.format_list(_analyze(document))

    assert len(listing) < len(document) / 4


def test_list_is_empty_for_an_empty_queue() -> None:
    assert punch_list.format_list(_analyze(_document())) == ""


def test_check_exits_nonzero_on_errors(tmp_path: Path) -> None:
    broken = tmp_path / "PUNCH_LIST.md"
    broken.write_text(_document(_entry("PL-001"), _entry("PL-001")), encoding="utf-8")

    assert punch_list.main(["check", "--file", str(broken), "--today", "2026-08-23"]) == 1


def test_check_exits_zero_on_a_clean_file(tmp_path: Path) -> None:
    clean = tmp_path / "PUNCH_LIST.md"
    clean.write_text(_document(_entry(effort="S")), encoding="utf-8")

    assert punch_list.main(["check", "--file", str(clean), "--today", "2026-08-23"]) == 0


def test_missing_file_is_silent(tmp_path: Path) -> None:
    """A checkout without a punch list must not make session start noisy."""
    assert punch_list.main(["digest", "--file", str(tmp_path / "absent.md")]) == 0
