"""Tests for the release cut's reading of where simulator defects land.

The rules under test are the ones a wrong answer would hide: which items and
files are counted, which weeks, and when a design review covers a file.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from docket.config import Config
from docket.hotspots import HOTSPOT_FILES, REVIEW_FEATURE, read
from docket.model import Item
from docket.render import format_hotspots

CONFIG = Config(
    items_dir="docs/items",
    workflow_paths=("tools",),
    product_paths=("src", "docs/MODEL.md"),
    safety_classes=("safety", "science"),
)
TODAY = date(2026, 11, 24)
#: The first day the reading counts: eight weeks before `TODAY`.
FIRST = TODAY - timedelta(days=56)


def _item(
    identifier: str,
    added: date,
    touches: tuple[str, ...],
    *,
    classes: tuple[str, ...] = ("defect",),
    feature: str = "",
    status: str = "ready",
    closed: date | None = None,
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority="P2",
        effort="S",
        status=status,
        classes=classes,
        touches=touches,
        blocked_by=(),
        feature=feature,
        milestone="",
        added=added,
        closed=closed,
        commit="",
        reason="",
        body="",
    )


def _review(
    identifier: str, touches: tuple[str, ...], *, status: str = "ready", closed: date | None = None
) -> Item:
    """A design review, which is planning work rather than a defect."""
    return _item(
        identifier,
        FIRST,
        touches,
        classes=("planning",),
        feature=REVIEW_FEATURE,
        status=status,
        closed=closed,
    )


def _tree(root: Path, *paths: str, lines: int = 3) -> Path:
    for path in paths:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text("x = 1\n" * lines, encoding="utf-8")
    return root


def _defects(count: int, path: str, first: int, *, also: tuple[str, ...] = ()) -> list[Item]:
    return [
        _item(f"PL-{first + n:04d}", FIRST + timedelta(days=n), (path, *also)) for n in range(count)
    ]


def test_only_defects_in_simulator_source_files_in_the_window_are_counted(tmp_path: Path) -> None:
    """A feature, a document, an apparatus file, a removed file and an old filing count nothing."""
    root = _tree(tmp_path, "src/a.py", "src/b.py", "tools/t.py", "docs/MODEL.md")
    items = [
        _item("PL-0001", FIRST, ("src/a.py",)),
        _item("PL-0002", FIRST, ("src/a.py",), classes=("safety",)),
        _item("PL-0003", FIRST, ("src/a.py", "src/a.py"), classes=("science", "ux")),
        _item("PL-0004", FIRST, ("src/a.py",), classes=("feature",)),
        _item("PL-0005", FIRST - timedelta(days=1), ("src/a.py",)),
        _item("PL-0006", TODAY, ("src/a.py",)),
        _item("PL-0007", FIRST, ("docs/MODEL.md", "tools/t.py", "src/gone.py", "src/b.py")),
    ]

    report = read(items, CONFIG, root, TODAY)

    assert (report.start, report.end) == (FIRST, TODAY - timedelta(days=1))
    assert [(hotspot.path, hotspot.defects) for hotspot in report.files] == [
        ("src/a.py", 3),
        ("src/b.py", 1),
    ]
    assert report.files[0].lines == 3


def test_the_reading_keeps_the_files_with_the_most_defects_and_their_usual_partner(
    tmp_path: Path,
) -> None:
    paths = [f"src/f{n}.py" for n in range(HOTSPOT_FILES + 2)]
    root = _tree(tmp_path, *paths)
    items = [
        item
        for rank, path in enumerate(paths)
        for item in _defects(len(paths) - rank, path, 1000 * (rank + 1))
    ]
    items += _defects(2, "src/f0.py", 9000, also=("src/f6.py",))

    report = read(items, CONFIG, root, TODAY)

    assert [hotspot.path for hotspot in report.files] == paths[:HOTSPOT_FILES]
    top = report.files[0]
    assert (top.defects, top.partner, top.together) == (9, "src/f6.py", 2)
    assert report.files[1].partner is None


def test_an_open_review_covers_its_files_and_a_dropped_one_covers_nothing(tmp_path: Path) -> None:
    root = _tree(tmp_path, "src/a.py", "src/b.py")
    items = [*_defects(4, "src/a.py", 1000), *_defects(4, "src/b.py", 2000)]
    reviewing = _review("PL-RV01", ("src",))
    dropped = _review("PL-RV02", ("src/b.py",), status="dropped", closed=FIRST + timedelta(days=30))

    report = read([*items, reviewing], CONFIG, root, TODAY)
    assert report.owed == ()
    assert format_hotspots(report) == ""

    report = read([*items, dropped], CONFIG, root, TODAY)
    assert [hotspot.path for hotspot in report.owed] == ["src/a.py", "src/b.py"]


def test_a_finished_review_covers_its_file_until_three_more_defects_land(tmp_path: Path) -> None:
    """Triage's rule for a fix that did not hold: three filings after it closed."""
    root = _tree(tmp_path, "src/a.py")
    closed = FIRST + timedelta(days=1)
    review = _review("PL-RV01", ("src/a.py",), status="done", closed=closed)
    before_and_after = _defects(4, "src/a.py", 1000)  # filed on days 0 to 3

    (held,) = read([*before_and_after, review], CONFIG, root, TODAY).files
    assert (held.since_review, held.owed, held.last_review) == (2, False, review)

    later = _item("PL-2000", FIRST + timedelta(days=10), ("src/a.py",))
    (broken,) = read([*before_and_after, later, review], CONFIG, root, TODAY).files
    assert (broken.since_review, broken.owed) == (3, True)


def test_the_cut_names_each_file_owed_a_review_and_how_to_file_one(tmp_path: Path) -> None:
    root = _tree(tmp_path, "src/a.py", "src/b.py", lines=1200)
    items = [*_defects(4, "src/a.py", 1000, also=("src/b.py",))]
    review = _review("PL-RV01", ("src/b.py",), status="done", closed=FIRST - timedelta(days=1))

    shown = format_hotspots(read([*items, review], CONFIG, root, TODAY))

    assert "filed 2026-09-29 to 2026-11-23" in shown
    assert "  src/a.py\n      4 defect items, 1,200 lines. Most often with src/b.py, in 4." in shown
    assert "4 filed since PL-RV01, the last design review, closed 2026-09-28." in shown
    assert f'`bin/docket new --feature {REVIEW_FEATURE} "..."`' in shown
