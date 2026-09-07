"""Tests for `tools/main_ci_status.py`, the default branch's quality verdict.

The script exists because the whole-store `verify:` replay runs only on push to
`main`, so its failures land on a run nobody watches - `main` was red across
three consecutive merges with every session believing the tree was clean
(`PL-0ZGK`).

Two properties are worth more than the happy path, and they pull in opposite
directions. **It has to fire on the incident**, or it is the defect it was
built to catch. And **it has to stay silent on everything else**, because it is
read at the top of every session: `CLAUDE.md` treats a check that fires without
changing a decision as a defect in the check, since a routine line trains a
reader to skim the region a real advisory appears in. So the silence cases
outnumber the speaking ones here deliberately.

`fetch_runs` and the `git` call are substituted rather than a server or a
repository built, matching `test_branch_id_check.py`: what is under test is the
reading of a response and the decision to speak, not urllib and not git.
Nothing here touches a network.
"""

from __future__ import annotations

import subprocess
import urllib.error

import main_ci_status
import pytest


def _run(conclusion: str | None, number: int = 1550, sha: str = "abcdef1234") -> dict:
    return {
        "conclusion": conclusion,
        "run_number": number,
        "head_sha": sha,
        "html_url": f"https://github.com/o/r/actions/runs/{number}",
    }


class TestRepoSlug:
    @pytest.mark.parametrize(
        "remote",
        [
            "https://github.com/stuthedew/open-anesthesia-sim.git",
            "https://github.com/stuthedew/open-anesthesia-sim",
            "git@github.com:stuthedew/open-anesthesia-sim.git",
            "  https://github.com/stuthedew/open-anesthesia-sim.git\n",
        ],
    )
    def test_reads_every_form_this_repository_is_cloned_with(self, remote: str) -> None:
        assert main_ci_status.repo_slug(remote) == "stuthedew/open-anesthesia-sim"

    @pytest.mark.parametrize("remote", ["https://gitlab.com/o/r.git", "/srv/local.git", ""])
    def test_declines_a_remote_that_is_not_github(self, remote: str) -> None:
        """None rather than a guess: the caller's contract is to stay silent."""
        assert main_ci_status.repo_slug(remote) is None


class TestPickRun:
    def test_passes_over_a_cancelled_run_to_the_newest_real_verdict(self) -> None:
        """The workflow cancels superseded runs, so this is the common case.

        Reading `cancelled` as an answer would report nothing about a red
        `main`, which is exactly the blindness the script exists to remove.
        """
        runs = [_run("cancelled", 1555), _run(None, 1554), _run("failure", 1553)]
        assert main_ci_status.pick_run(runs)["run_number"] == 1553

    def test_takes_the_newest_when_several_reached_a_verdict(self) -> None:
        runs = [_run("failure", 1553), _run("success", 1551)]
        assert main_ci_status.pick_run(runs)["run_number"] == 1553

    def test_returns_none_when_nothing_reached_a_verdict(self) -> None:
        assert main_ci_status.pick_run([_run("cancelled"), _run(None)]) is None

    def test_returns_none_on_an_empty_or_malformed_page(self) -> None:
        assert main_ci_status.pick_run([]) is None
        assert main_ci_status.pick_run(["not a dict", 7]) is None


class TestAdvisory:
    def test_says_nothing_when_main_is_green(self) -> None:
        """The silence rule, at its single most important point."""
        assert main_ci_status.advisory(_run("success")) is None

    @pytest.mark.parametrize("conclusion", ["failure", "timed_out", "startup_failure"])
    def test_speaks_for_every_verdict_that_is_not_success(self, conclusion: str) -> None:
        line = main_ci_status.advisory(_run(conclusion, 1553, "9c6ebd29aaaa"))
        assert conclusion in line
        assert "1553" in line
        assert "9c6ebd29" in line, "the sha answers whether the failure is still main's head"
        assert "https://github.com/o/r/actions/runs/1553" in line


class TestMain:
    """End to end, with the two boundaries substituted."""

    @pytest.fixture(autouse=True)
    def _origin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            main_ci_status.subprocess,
            "run",
            lambda *a, **k: subprocess.CompletedProcess(
                a[0], 0, stdout="https://github.com/stuthedew/open-anesthesia-sim.git\n", stderr=""
            ),
        )

    def test_reports_a_failing_main_run(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("failure", 1553)])
        assert main_ci_status.main() == 0
        assert "concluded failure" in capsys.readouterr().out

    def test_prints_nothing_when_main_is_green(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("success", 1553)])
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize(
        "boom",
        [
            urllib.error.URLError("offline"),
            OSError("connection reset"),
            TimeoutError("slow"),
            ValueError("not json"),
        ],
    )
    def test_stays_silent_and_exits_zero_when_the_fetch_fails(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], boom: Exception
    ) -> None:
        """An offline container must start exactly as cleanly as an online one.

        This is the property that lets the hook call it unconditionally.
        """

        def _raise(slug: str) -> list[dict]:
            raise boom

        monkeypatch.setattr(main_ci_status, "fetch_runs", _raise)
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_stays_silent_when_there_is_no_git_remote(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def _raise(*a: object, **k: object) -> None:
            raise subprocess.CalledProcessError(128, "git")

        monkeypatch.setattr(main_ci_status.subprocess, "run", _raise)
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_stays_silent_when_the_remote_is_not_github(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            main_ci_status.subprocess,
            "run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout="/srv/r.git\n", stderr=""),
        )
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""
