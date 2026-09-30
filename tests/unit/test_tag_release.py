"""Tests for `tools/tag_release.py`, which tags a release on its cut once the cut is on `main`.

Every case runs real git against a bare `origin`, because what is pinned is
what git does with the lookup and the push: which commit the tag lands on,
what `origin` ends up holding, and that a run which cannot be sure changes
nothing. These carry over the four tests that ran the pasted tag lines
(`PL-VYK1`, `PL-PNW6`) before this workflow replaced them (`PL-2FY6`).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from tag_release import run


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return done.stdout.strip()


def _commit(root: Path, message: str, files: dict[str, str | None]) -> str:
    """Commit `files`, where `None` deletes one, and return the new commit's hash."""
    for name, text in files.items():
        path = root / name
        if text is None:
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)
    return _git(root, "rev-parse", "HEAD")


def _cut(root: Path, version: str) -> str:
    """Commit a cut of `version` as `make release` writes one: its notes and its bump."""
    return _commit(
        root,
        f"PL-TR4N: cut v{version}",
        {
            f"docs/releases/v{version}.md": f"## v{version}\n",
            "pyproject.toml": f'[project]\nversion = "{version}"\n',
        },
    )


@pytest.fixture
def published(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """A bare `origin` and a clone of it, `main` holding one commit and no notes."""
    for name, value in (("NAME", "T"), ("EMAIL", "t@example.com")):
        monkeypatch.setenv(f"GIT_AUTHOR_{name}", value)
        monkeypatch.setenv(f"GIT_COMMITTER_{name}", value)
    origin = tmp_path / "origin.git"
    _git(tmp_path, "-c", "init.defaultBranch=main", "init", "-q", "--bare", str(origin))
    work = tmp_path / "work"
    _git(tmp_path, "-c", "init.defaultBranch=main", "clone", "-q", str(origin), str(work))
    _commit(work, "base", {"pyproject.toml": '[project]\nversion = "0.2.9"\n'})
    _git(work, "push", "-q", "origin", "HEAD:main")
    return origin, work


def test_the_tag_lands_on_the_cut_however_late_it_runs(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    """`PL-VYK1`: after another merge `origin/main` is that merge; the cut is still the cut.

    An edit to the notes after the cut does not move it either, which is what
    `--diff-filter=A` is for.
    """
    origin, work = published
    cut = _cut(work, "0.3.0")
    _commit(work, "PL-D1D1: the next merge", {"README.md": "later\n"})
    _commit(work, "PL-D1D2: an edit to the notes", {"docs/releases/v0.3.0.md": "## v0.3.0\n\n+\n"})
    _git(work, "push", "-q", "origin", "HEAD:main")
    tagger = tmp_path / "tagger"
    _git(tmp_path, "clone", "-q", str(origin), str(tagger))

    assert run(tagger, apply=True) == 0

    assert _git(origin, "rev-parse", "v0.3.0^{commit}") == cut
    assert _git(origin, "cat-file", "-t", "v0.3.0") == "tag", "not an annotated tag"
    assert run(tagger, apply=True) == 0, "a second run is not a failure"


def test_a_push_that_is_not_a_cut_tags_nothing(
    published: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    """The version's notes are not on `origin/main` yet, so there is no cut to tag."""
    origin, work = published

    assert run(work, apply=True) == 0

    assert "has no commit adding docs/releases/v0.2.9.md" in capsys.readouterr().out
    assert _git(origin, "tag", "--list") == ""


def test_a_listing_pushes_nothing(
    published: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    origin, work = published
    cut = _cut(work, "0.3.0")
    _git(work, "push", "-q", "origin", "HEAD:main")

    assert run(work, apply=False) == 0

    assert f"v0.3.0 goes on its cut, {cut[:7]}" in capsys.readouterr().out
    assert _git(origin, "tag", "--list") == ""
    assert _git(work, "tag", "--list") == ""


def test_a_withdrawn_tag_held_here_is_replaced_on_the_cut(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    """`PL-PNW6`: a re-used number, tagged from a checkout still holding the withdrawn tag.

    `git fetch` never removes a tag, so the warm clone keeps it. Left in place,
    `git tag` refuses the name; pushed, it would put the withdrawn tag back on
    `origin`.
    """
    origin, work = published
    withdrawn = _git(work, "rev-parse", "HEAD")
    _git(work, "tag", "-a", "v0.3.0", "-m", "v0.3.0")
    _git(work, "push", "-q", "origin", "v0.3.0")
    warm = tmp_path / "warm"
    _git(tmp_path, "clone", "-q", str(origin), str(warm))
    _git(origin, "tag", "-d", "v0.3.0")
    _git(work, "tag", "-d", "v0.3.0")
    cut = _cut(work, "0.3.0")
    _git(work, "push", "-q", "origin", "HEAD:main")
    assert _git(warm, "rev-parse", "v0.3.0^{commit}") == withdrawn

    assert run(warm, apply=True) == 0

    assert _git(warm, "rev-parse", "v0.3.0^{commit}") == cut
    assert _git(origin, "rev-parse", "v0.3.0^{commit}") == cut, "origin took the withdrawn tag"


def test_nothing_is_deleted_when_origin_cannot_answer(
    published: tuple[Path, Path], tmp_path: Path
) -> None:
    """Only `ls-remote`'s exit 2 says `origin` lacks the tag; unreachable, a held one stays."""
    _, work = published
    _cut(work, "0.3.0")
    _git(work, "push", "-q", "origin", "HEAD:main")
    assert run(work, apply=True) == 0
    held = _git(work, "rev-parse", "v0.3.0")
    _git(work, "remote", "set-url", "origin", str(tmp_path / "gone.git"))

    assert run(work, apply=True) == 1

    assert _git(work, "rev-parse", "v0.3.0") == held


def test_a_tag_on_another_commit_is_left_for_a_person(
    published: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-YKSD`'s shape: a tag pushed onto the commit before its release's own."""
    origin, work = published
    early = _git(work, "rev-parse", "HEAD")
    _git(work, "tag", "-a", "v0.3.0", "-m", "v0.3.0")
    _git(work, "push", "-q", "origin", "v0.3.0")
    _cut(work, "0.3.0")
    _git(work, "push", "-q", "origin", "HEAD:main")

    assert run(work, apply=True) == 1

    assert f"holds v0.3.0 on {early[:9]}, not on its cut" in capsys.readouterr().out
    assert _git(origin, "rev-parse", "v0.3.0^{commit}") == early


def test_notes_added_twice_name_no_cut(
    published: tuple[Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    """Added, deleted and added again, there are two candidates and neither is picked."""
    origin, work = published
    _cut(work, "0.3.0")
    _commit(work, "drop the notes", {"docs/releases/v0.3.0.md": None})
    _commit(work, "cut v0.3.0 again", {"docs/releases/v0.3.0.md": "## v0.3.0\n"})
    _git(work, "push", "-q", "origin", "HEAD:main")

    assert run(work, apply=True) == 1

    assert "in 2 commits" in capsys.readouterr().out
    assert _git(origin, "tag", "--list") == ""


def test_a_shallow_clone_is_declined(
    published: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Its oldest commit reads as adding every file, so it could name that commit as the cut."""
    origin, work = published
    _cut(work, "0.3.0")
    _commit(work, "PL-D1D1: the next merge", {"README.md": "later\n"})
    _git(work, "push", "-q", "origin", "HEAD:main")
    shallow = tmp_path / "shallow"
    _git(tmp_path, "clone", "-q", "--depth", "1", f"file://{origin}", str(shallow))

    assert run(shallow, apply=True) == 1

    assert "shallow" in capsys.readouterr().out
    assert _git(origin, "tag", "--list") == ""
