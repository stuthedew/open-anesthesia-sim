"""`tools/fact_home_check.py` must refuse a second reader of a fact and say where its home is.

The direction that matters most is the false green: a reader the walk misses,
a home that covers more of a file than it names, or a baseline that grows
without failing, leaves the principle asserted and not held. The other
direction costs a session: a listing of one directory, a `shlex.quote`, a
docstring that names the API's host or an alias of another module's constant
is not a second reader, and a check that said it was would be routed around.
"""

from __future__ import annotations

from pathlib import Path

from fact_home_check import analyze, format_report, main

REPO_ROOT = Path(__file__).resolve().parents[2]

TREES = {"tools": "tools", "docket": "subprojects/docket/src/docket", "hooks": ".claude/hooks"}

GIT_RUNNER = 'import subprocess\n\ndef _git(args):\n    return subprocess.run(["git", *args])\n'


def _tree(root: Path, **modules: str) -> None:
    """Write a synthetic apparatus; a keyword is `tree__name` with `tree` one of `TREES`."""
    for key, source in modules.items():
        tree, _, name = key.partition("__")
        path = root / TREES[tree] / f"{name}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")


def _report(root: Path, baseline: dict[str, dict[tuple[str, str], int]] | None = None) -> str:
    return format_report(analyze(root, baseline=baseline or {}))


def test_a_git_call_outside_vcs_fails_naming_file_line_scope_and_home(tmp_path: Path) -> None:
    _tree(tmp_path, tools__branch=GIT_RUNNER)

    report = analyze(tmp_path, baseline={})
    printed = format_report(report)

    assert report.errors == 1
    assert 'tools/branch.py:4: subprocess.run(["git", ...]) in _git' in printed
    assert (
        "Home: subprojects/docket/src/docket/vcs.py, `_git` in .claude/hooks/stop_hook_patch.py"
        in printed
    )


def test_the_git_homes_pass_and_so_does_a_command_that_is_not_git(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        docket__vcs=GIT_RUNNER,
        hooks__stop_hook_patch=GIT_RUNNER,
        tools__gate='import subprocess\n\ndef tests():\n    return subprocess.run(["uv", "run"])\n',
    )

    assert analyze(tmp_path, baseline={}).errors == 0


def test_a_home_named_by_scope_covers_that_function_and_not_the_rest_of_its_file(
    tmp_path: Path,
) -> None:
    _tree(
        tmp_path,
        hooks__stop_hook_patch=GIT_RUNNER
        + '\ndef _branch():\n    return subprocess.run(["git", "branch"])\n',
    )

    printed = _report(tmp_path)

    assert ".claude/hooks/stop_hook_patch.py:4:" not in printed
    assert '.claude/hooks/stop_hook_patch.py:7: subprocess.run(["git", ...]) in _branch' in printed


def test_a_git_argv_as_a_string_or_through_an_imported_run_is_still_git(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        tools__shelled=(
            "import subprocess\n\ndef status():\n"
            '    return subprocess.check_output("git status --short", shell=True)\n'
        ),
        tools__imported=(
            'from subprocess import run\n\ndef log():\n    return run(args=["git", "log"])\n'
        ),
    )

    printed = _report(tmp_path)

    assert 'tools/shelled.py:4: subprocess.check_output(["git", ...]) in status' in printed
    assert 'tools/imported.py:4: subprocess.run(["git", ...]) in log' in printed


def test_a_recursive_walk_outside_tracked_files_fails_and_a_directory_listing_passes(
    tmp_path: Path,
) -> None:
    _tree(
        tmp_path,
        tools__walker=(
            "import glob\nimport os\n\n"
            "def every(root):\n"
            "    deep = sorted(root.rglob('*.py'))\n"
            "    flat = sorted(root.glob('*.md'))\n"
            "    starred = sorted(root.glob('**/*.md'))\n"
            "    listed = list(root.iterdir())\n"
            "    for _ in os.walk(root):\n"
            "        pass\n"
            "    return deep, flat, starred, listed, "
            "glob.glob('x/**', recursive=True), glob.glob('x/*')\n"
        ),
        docket__vcs=(
            "def tracked_files(root):\n    return sorted(root.rglob('*'))\n\n"
            "def ruff_configs(root):\n    return sorted(root.rglob('ruff.toml'))\n"
        ),
        docket__grep="import os\n\ndef _walk(directory):\n    return list(os.walk(directory))\n",
    )

    printed = _report(tmp_path)

    assert "tools/walker.py:5: rglob in every" in printed
    assert "tools/walker.py:6:" not in printed
    assert 'tools/walker.py:7: glob("**") in every' in printed
    assert "tools/walker.py:8:" not in printed
    assert "tools/walker.py:9: os.walk in every" in printed
    assert printed.count("tools/walker.py:11:") == 1
    assert "tools/walker.py:11: glob.glob in every" in printed
    assert "subprojects/docket/src/docket/vcs.py:2:" not in printed
    assert "subprojects/docket/src/docket/vcs.py:5: rglob in ruff_configs" in printed
    # `grep._walk` models `grep -r`, which reads the disk: a home of its own (`PL-J4YY`).
    assert "subprojects/docket/src/docket/grep.py:4:" not in printed
    assert "Home: `tracked_files` in subprojects/docket/src/docket/vcs.py" in printed


def test_the_github_host_outside_the_client_fails_and_a_docstring_mention_does_not(
    tmp_path: Path,
) -> None:
    _tree(
        tmp_path,
        tools__open_pull_requests='GITHUB_API = "https://api.github.com"\n',
        tools__armed='"""Reads https://api.github.com/repos for the arm."""\n\nAPI = "https://api.github.com"\n',
    )

    report = analyze(tmp_path, baseline={})
    printed = format_report(report)

    assert report.errors == 1
    assert 'tools/armed.py:3: "api.github.com" in <module>' in printed
    assert "Home: tools/open_pull_requests.py" in printed


def test_a_default_branch_literal_outside_vcs_fails_and_a_module_guard_does_not(
    tmp_path: Path,
) -> None:
    _tree(
        tmp_path,
        docket__vcs='GUESSED_BASE = "origin/main"\n',
        tools__behind=(
            "def behind(run):\n"
            '    return run(["rev-list", "origin/main"])\n\n'
            'if __name__ == "__main__":\n'
            "    behind(print)\n"
        ),
    )

    report = analyze(tmp_path, baseline={})
    printed = format_report(report)

    assert report.errors == 1
    assert 'tools/behind.py:2: "origin/main" in behind' in printed


def test_shlex_split_outside_the_lexers_fails_and_shlex_quote_does_not(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        hooks__shell_split=(
            "import shlex\n\ndef words(command):\n"
            "    return list(shlex.shlex(command, punctuation_chars=True))\n"
        ),
        tools__runner=(
            "import shlex\n\ndef argv(command):\n    return shlex.split(command)\n\n"
            "def shown(value):\n    return shlex.quote(value)\n"
        ),
    )

    report = analyze(tmp_path, baseline={})
    printed = format_report(report)

    assert report.errors == 1
    assert "tools/runner.py:4: shlex.split in argv" in printed
    assert "Home: subprojects/docket/src/docket/shell.py, .claude/hooks/shell_split.py" in printed


def test_a_name_defined_in_two_modules_fails_and_an_import_or_alias_does_not(
    tmp_path: Path,
) -> None:
    _tree(
        tmp_path,
        docket__store='import re\n\nID_RE = re.compile("PL-")\nROOT = 1\n',
        tools__generator='import re\n\n_ID_RE = re.compile("PL-")\nROOT = 2\nlower = 3\n',
        tools__reads="from store import ID_RE\n\nALIAS_RE = ID_RE\n",
    )

    report = analyze(tmp_path, baseline={})
    printed = format_report(report)

    assert report.errors == 2
    assert (
        "ID_RE: subprojects/docket/src/docket/store.py:3 ID_RE, tools/generator.py:3 _ID_RE"
        in printed
    )
    assert "ROOT" not in printed
    assert "ALIAS_RE" not in printed

    drained = {
        "subprojects/docket/src/docket/store.py": {("definition", "ID_RE"): 1},
        "tools/generator.py": {("definition", "ID_RE"): 1},
    }
    assert analyze(tmp_path, baseline=drained).errors == 0


def test_the_baseline_covers_what_it_names_and_refuses_one_more(tmp_path: Path) -> None:
    path = "tools/branch.py"
    baseline = {path: {("git", "_git"): 1}}
    _tree(tmp_path, tools__branch=GIT_RUNNER)
    assert analyze(tmp_path, baseline=baseline).errors == 0

    (tmp_path / path).write_text(
        'import subprocess\n\ndef _git(args):\n    subprocess.run(["git", "fetch"])\n'
        '    return subprocess.run(["git", *args])\n'
    )
    printed = _report(tmp_path, baseline)

    assert f'{path}:4: subprocess.run(["git", ...]) in _git' in printed
    assert f'{path}:5: subprocess.run(["git", ...]) in _git' in printed
    assert "the baseline allows 1 of these in _git, and 2 are there" in printed


def test_an_entry_the_tree_no_longer_fills_is_stale(tmp_path: Path) -> None:
    path = "tools/branch.py"
    _tree(tmp_path, tools__branch=GIT_RUNNER)
    baseline = {
        path: {("git", "_git"): 2, ("walk", "_git"): 1},
        "tools/gone.py": {("git", "main"): 1},
    }

    report = analyze(tmp_path, baseline=baseline)
    printed = format_report(report)

    assert report.errors == 3
    assert f"{path}, git in _git: baseline 2, found 1 - set it to 1" in printed
    assert f"{path}, walk in _git: baseline 1, found 0 - delete it" in printed
    assert "the file no longer exists; delete its entries" in printed


def test_a_tree_with_no_python_files_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "README.md").write_text("tools\n", encoding="utf-8")

    report = analyze(tmp_path, baseline={})

    assert report.errors == 1
    assert "the check read nothing" in format_report(report)


def test_a_file_that_does_not_parse_fails_and_its_entries_are_not_called_stale(
    tmp_path: Path,
) -> None:
    path = "tools/broken.py"
    _tree(tmp_path, tools__broken="def build(:\n")

    report = analyze(tmp_path, baseline={path: {("git", "build"): 1}})
    printed = format_report(report)

    assert report.errors == 1
    assert "Not checked - these files do not parse" in printed
    assert "delete it" not in printed


def test_the_real_tree_passes() -> None:
    assert main(["--root", str(REPO_ROOT)]) == 0
