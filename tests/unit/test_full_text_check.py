"""`tools/full_text_check.py` must refuse a tracked document file no licence covers.

The direction that matters most is the false green: a publisher's PDF tracked
in this public repository while the gate passes. Two sat in the tree until
2026-09-06 under the rule in prose alone (`PL-SHG5`, `PL-KQBM`).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from full_text_check import LICENSED_BEGIN, LICENSED_END, main, problems

README = "docs/references/README.md"


def _readme(*entries: str) -> str:
    return "# References\n\n## Redistribution\n\n" + "\n".join(
        [LICENSED_BEGIN, *entries, LICENSED_END, ""]
    )


def _tree(root: Path, files: dict[str, str | bytes]) -> Path:
    for path, content in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            (root / path).write_bytes(content)
        else:
            (root / path).write_text(content, encoding="utf-8")
    return root


def test_the_repository_tracks_no_unlicensed_full_text(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "full texts: 0 errors" in capsys.readouterr().out


def test_a_tracked_pdf_is_refused(tmp_path: Path) -> None:
    root = _tree(tmp_path, {README: _readme(), "docs/references/paper.pdf": b"%PDF-1.7\n"})
    (found,) = problems(root)
    assert found.startswith("docs/references/paper.pdf: a tracked document file")


def test_the_extension_is_compared_in_any_letter_case(tmp_path: Path) -> None:
    root = _tree(tmp_path, {README: _readme(), "book.EPUB": b"PK"})
    (found,) = problems(root)
    assert found.startswith("book.EPUB:")


def test_a_listed_file_passes(tmp_path: Path) -> None:
    root = _tree(
        tmp_path,
        {
            README: _readme("- `docs/references/open.pdf`: CC BY 4.0"),
            "docs/references/open.pdf": b"%PDF-1.7\n",
        },
    )
    assert problems(root) == []


def test_an_untracked_file_is_ignored(tmp_path: Path) -> None:
    """A file git does not track is not redistributed, so only a tracked one counts."""
    root = _tree(tmp_path, {README: _readme(), "scratch/paper.pdf": b"%PDF-1.7\n"})
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", README], check=True, capture_output=True)
    assert problems(root) == []
    subprocess.run(
        ["git", "-C", str(root), "add", "scratch/paper.pdf"], check=True, capture_output=True
    )
    (found,) = problems(root)
    assert found.startswith("scratch/paper.pdf:")


def test_a_list_line_of_the_wrong_shape_fails(tmp_path: Path) -> None:
    """A list the check cannot read is one it cannot vouch for, so it fails rather than passes."""
    root = _tree(tmp_path, {README: _readme("- docs/references/open.pdf, CC BY")})
    (found,) = problems(root)
    assert "write each licensed file as" in found


def test_a_readme_without_the_markers_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path, {README: "# References\n"})
    (found,) = problems(root)
    assert "needs exactly one" in found
