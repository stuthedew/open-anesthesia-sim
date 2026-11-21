"""What a closing item records to show its work, read once on the branch that closes it."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from docket import done
from docket.model import RELEASE_TRAIN, Item, parse_item
from docket.vcs import ForkTexts

TEST_FILE = "tests/test_thing.py"
BEFORE = "def test_old():\n    assert thing() == 1\n"
NODE = f"{TEST_FILE}::test_new"


def _fork(**texts: str) -> ForkTexts:
    return ForkTexts(fork="0" * 40, texts=texts)


def _reader(**texts: str) -> Callable[[str], str | None]:
    return lambda path: texts.get(path)


def _faults(entries: list[str], here: str, there: str | None = BEFORE) -> list[str]:
    fork = ForkTexts(fork="0" * 40, texts={} if there is None else {TEST_FILE: there})
    faults, unread = done.test_faults(entries, lambda path: {TEST_FILE: here}.get(path), fork)
    assert unread == []
    return faults


# --- the entries of `tests:` -------------------------------------------------


@pytest.mark.parametrize(
    ("entry", "path", "name"),
    [
        ("tests/unit/test_x.py::test_it", "tests/unit/test_x.py", "test_it"),
        ("a/test_x.py::TestThing::test_it", "a/test_x.py", "TestThing::test_it"),
    ],
)
def test_a_node_id_names_a_file_and_a_test(entry: str, path: str, name: str) -> None:
    assert done.read_node(entry) == done.Node(path=path, name=name)


@pytest.mark.parametrize(
    "entry", ["tests/unit/test_x.py", "test_it", "tests/unit/test_x.py::", "docs/x.md::test_it"]
)
def test_an_entry_that_is_no_node_id_is_refused(entry: str) -> None:
    assert done.read_node(entry) is None
    assert "not a pytest node id" in done.node_refusal(entry)


def test_a_parameter_set_is_refused_by_name() -> None:
    assert "one parameter set" in done.node_refusal("tests/test_x.py::test_it[fast]")


# --- whether a named test shows the work -------------------------------------


def test_a_test_the_branch_added_shows_the_work() -> None:
    here = BEFORE + "\n\ndef test_new():\n    assert thing() == 2\n"

    assert _faults([NODE], here) == []


def test_a_test_in_a_file_the_branch_created_shows_the_work() -> None:
    assert _faults([NODE], "def test_new():\n    assert thing() == 2\n", there=None) == []


def test_a_test_the_branch_changed_shows_the_work() -> None:
    assert _faults([f"{TEST_FILE}::test_old"], "def test_old():\n    assert thing() == 2\n") == []


def test_a_test_the_tree_does_not_define_is_a_fault() -> None:
    (fault,) = _faults([NODE], BEFORE)

    assert "does not define" in fault


def test_a_file_the_tree_does_not_hold_is_a_fault() -> None:
    faults, _ = done.test_faults(["tests/test_gone.py::test_new"], lambda path: None, _fork())

    assert "names a file the tree does not hold" in faults[0]


def test_a_test_the_branch_left_alone_is_a_fault() -> None:
    """A test that was there before the work passed before it, and shows nothing about it."""
    here = BEFORE + "\n\ndef test_new():\n    assert thing() == 2\n"

    (fault,) = _faults([f"{TEST_FILE}::test_old"], here)

    assert "neither added nor changed" in fault


def test_a_changed_comment_or_a_rewrap_is_no_change() -> None:
    here = "def test_old():\n    # reworded\n    assert thing(\n    ) == 1\n"

    (fault,) = _faults([f"{TEST_FILE}::test_old"], here)

    assert "neither added nor changed" in fault


def test_a_changed_decorator_is_a_change() -> None:
    here = "@pytest.mark.slow\n" + BEFORE

    assert _faults([f"{TEST_FILE}::test_old"], here) == []


def test_a_method_is_found_under_its_class_and_not_under_another() -> None:
    here = (
        "class TestA:\n    def test_it(self):\n        assert 1\n\n"
        "class TestB:\n    def test_other(self):\n        assert 1\n"
    )

    assert _faults([f"{TEST_FILE}::TestA::test_it"], here, there=None) == []
    assert "does not define" in _faults([f"{TEST_FILE}::TestB::test_it"], here, there=None)[0]


def test_a_file_the_tokenizer_refuses_is_unread_and_not_a_pass() -> None:
    faults, unread = done.test_faults([NODE], _reader(**{TEST_FILE: "def test_new(:\n  '''"}), _fork())

    assert faults == []
    assert unread and TEST_FILE in unread[0]


# --- the one search for fixed text -------------------------------------------


def test_a_search_reads_its_words_and_its_files() -> None:
    assert done.read_text_search("grep -qF 'two words' docs/a.md docs/b.md") == done.TextSearch(
        absent=False, words="two words", paths=("docs/a.md", "docs/b.md")
    )
    assert done.read_text_search("! grep -qF -- '-x' docs/a.md") == done.TextSearch(
        absent=True, words="-x", paths=("docs/a.md",)
    )


@pytest.mark.parametrize(
    ("command", "said"),
    [
        ("grep -q 'def test_x' tests/unit/test_x.py", "runs `grep -q`"),
        ("grep -qF 'a' docs/a.md && grep -qF 'b' docs/b.md", "not one command"),
        ("uv run pytest tests/unit/test_x.py", "runs `uv run`"),
        ("grep -qF 'words'", "names no file"),
        ("grep -qF ' ' docs/a.md", "searches for no words"),
        ("grep -qF 'a' ../other/a.md", "not a file under the repository's root"),
        ("grep -qF 'def test_x' tests/unit/test_x.py", "named in `tests:`"),
    ],
)
def test_any_other_command_is_refused_by_name(command: str, said: str) -> None:
    refusal = done.read_text_search(command)

    assert isinstance(refusal, str) and said in refusal


def test_words_the_work_removed_may_be_searched_for_in_python() -> None:
    assert isinstance(done.read_text_search("! grep -qF 'old_name' src/a.py"), done.TextSearch)


def test_words_a_document_holds_are_found(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("The work adds these words.\n")

    assert done.search_faults("grep -qF 'adds these words' a.md", tmp_path) == []


def test_words_a_document_wraps_over_two_lines_are_found(tmp_path: Path) -> None:
    """`grep` reads one line at a time and found such a phrase on neither (`PL-RR1N`)."""
    (tmp_path / "a.md").write_text("The work adds these\nwords.\n")

    assert done.search_faults("grep -qF 'adds these words' a.md", tmp_path) == []
    assert "still holds them" in done.search_faults("! grep -qF 'adds these words' a.md", tmp_path)[0]


def test_words_no_file_holds_are_a_fault(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("Nothing here.\n")

    assert "does not hold them" in done.search_faults("grep -qF 'these words' a.md", tmp_path)[0]
    assert done.search_faults("! grep -qF 'these words' a.md", tmp_path) == []


def test_a_file_the_tree_does_not_hold_cannot_show_words_are_gone(tmp_path: Path) -> None:
    """`grep` exits 2 on a missing file, which `!` turned into a pass."""
    assert "does not hold" in done.search_faults("! grep -qF 'these words' gone.md", tmp_path)[0]


def test_a_path_may_name_an_item_file_by_its_id(tmp_path: Path) -> None:
    (tmp_path / "PL-K7QX-a-title.md").write_text("Answered here.\n")

    assert done.search_faults("grep -qF 'Answered here' PL-K7QX-*.md", tmp_path) == []


# --- a result recorded in the brief ------------------------------------------


@pytest.mark.parametrize(
    "paragraph",
    [
        "**Answered 2026-11-20.** The owner chose the first.",
        "**Counted 2026-11-21**, on `main`.",
        "**Checked 2026-10-17:** it still reproduces.",
        "**Answered 2026-09-19 under PL-4Q9B** in full.",
    ],
)
def test_a_dated_bold_label_is_a_record(paragraph: str) -> None:
    assert done.dated_record(f"**Problem.** A question.\n\n{paragraph}\n")


@pytest.mark.parametrize(
    "body",
    [
        "**Problem.** A question.\n\n**Done when.** It is answered.\n",
        "**Problem.** Filed 2026-11-20 after the freeze.\n",
        "Text first, then **Answered 2026-11-20.** in the middle of a line.\n",
        "```\n**Answered 2026-11-20.**\n```\n",
    ],
)
def test_a_brief_with_no_dated_label_holds_no_record(body: str) -> None:
    assert not done.dated_record(body)


# --- one closing item, read on its branch ------------------------------------


def _item(**fields: str) -> Item:
    front = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return parse_item(f"---\nid: PL-K7QX\ntitle: t\nstatus: done\n{front}---\nBody\n")


def test_a_release_item_keeps_the_command_it_has(tmp_path: Path) -> None:
    item = _item(verify="grep -q '^version' pyproject.toml", resource=RELEASE_TRAIN)

    assert done.closing_faults(item, tmp_path, _fork()) == ([], [])


def test_an_item_that_says_why_no_search_can_show_it_is_not_read(tmp_path: Path) -> None:
    item = _item(verify="make check", **{"not-delegable": "proving it means cutting a release"})

    assert done.closing_faults(item, tmp_path, _fork()) == ([], [])


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)


@pytest.fixture
def branch(tmp_path: Path) -> Path:
    """A repository whose branch added one test to a file the default branch holds."""
    _git(tmp_path, "init", "--quiet", "--initial-branch", "main")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "tests").mkdir()
    (tmp_path / TEST_FILE).write_text(BEFORE)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "--quiet", "-m", "base")
    _git(tmp_path, "checkout", "--quiet", "-b", "work")
    (tmp_path / TEST_FILE).write_text(BEFORE + "\n\ndef test_new():\n    assert thing() == 2\n")
    _git(tmp_path, "commit", "--quiet", "-am", "work")
    return tmp_path


def test_names_a_test_the_branch_added(branch: Path) -> None:
    report = done.read_closing(branch, [_item(tests=NODE)])

    assert report == done.ClosingReport()


def test_refuses_a_test_the_branch_did_not_change(branch: Path) -> None:
    report = done.read_closing(branch, [_item(tests=f"{TEST_FILE}::test_old")])

    assert "neither added nor changed" in report.faults["PL-K7QX"][0]
    assert not report.declined


def test_a_change_not_yet_committed_counts_as_the_branch_s(branch: Path) -> None:
    (branch / TEST_FILE).write_text((branch / TEST_FILE).read_text().replace("== 1", "== 3"))

    assert done.read_closing(branch, [_item(tests=f"{TEST_FILE}::test_old")]).faults == {}


def test_a_checkout_with_no_default_branch_declines(tmp_path: Path) -> None:
    _git(tmp_path, "init", "--quiet", "--initial-branch", "elsewhere")

    report = done.read_closing(tmp_path, [_item(tests=NODE)])

    assert report.declined and report.faults == {}


def test_no_closing_item_asks_git_nothing(tmp_path: Path) -> None:
    assert done.read_closing(tmp_path, []) == done.ClosingReport()
