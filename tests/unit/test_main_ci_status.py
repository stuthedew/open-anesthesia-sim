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

import email.message
import http.client
import json
import pathlib
import subprocess
import urllib.error

import main_ci_status
import pytest


def _workflow() -> str:
    return (
        pathlib.Path(__file__).resolve().parents[2] / ".github/workflows/quality.yml"
    ).read_text()


def _workflow_step_names() -> list[str]:
    names = [
        line.split("- name:", 1)[1].strip()
        for line in _workflow().splitlines()
        if line.strip().startswith("- name:")
    ]
    assert names, "the workflow should name at least one step"
    return names


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


# Every failure either request can raise. `IncompleteRead` is the one that was
# missing: GitHub cutting a response body short raises an `http.client`
# exception, which is neither an `OSError` nor a `ValueError`, so it escaped
# both call sites and the red-`main` line was lost with it (`PL-T83R`).
_NETWORK_FAILURES = [
    urllib.error.URLError("offline"),
    urllib.error.HTTPError("u", 503, "busy", email.message.Message(), None),
    OSError("connection reset"),
    ConnectionResetError("reset"),
    TimeoutError("slow"),
    ValueError("not json"),
    json.JSONDecodeError("bad", "", 0),
    http.client.IncompleteRead(b"half"),
    http.client.HTTPException("protocol error"),
]


def _job(steps: list[tuple[str, str]]) -> dict:
    """One job whose steps are (name, conclusion) in the order CI ran them."""
    return {
        "name": "checks",
        "steps": [
            {"number": i, "name": name, "conclusion": conclusion}
            for i, (name, conclusion) in enumerate(steps, 1)
        ],
    }


def _pairs(steps: list[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    """The same steps as `advisory` receives them."""
    return main_ci_status.step_conclusions([_job(steps)])


# `quality.yml`'s real shape on a replay failure: the bare `bin/docket check`,
# ruff, mypy and the suite pass above it, and six to eleven checks below it -
# among them the four that read `src/` and `app/` - never run at all.
_REPLAY_STEPS = [
    ("Set up job", "success"),
    (main_ci_status.BARE_CHECK_STEP, "success"),
    ("Run uv run ruff check .", "success"),
    ("Run uv run mypy", "success"),
    ("Run uv run pytest", "success"),
    ("verify replay, scoped to what this branch changed", "skipped"),
    (main_ci_status.REPLAY_STEP, "failure"),
    ("Run uv run python tools/import_boundary_check.py", "skipped"),
    ("Run uv run python tools/glyph_check.py", "skipped"),
]


# The shape of a red `main` as it actually occurs: the whole-store replay is the
# only failing step, and every check that reads the tree passed above it.
_REPLAY_ONLY = _job(_REPLAY_STEPS)


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

    @pytest.mark.parametrize("boom", _NETWORK_FAILURES)
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

    def test_attributes_a_red_main_to_the_step_that_failed(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("failure", 1553)])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", lambda slug, run_id: [_REPLAY_ONLY])
        assert main_ci_status.main() == 0
        out = capsys.readouterr().out
        assert main_ci_status.REPLAY_STEP in out
        assert "bin/docket check --verify" in out

    def test_asks_for_the_jobs_only_once_the_verdict_is_a_failure(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The second request is the whole cost of this, and a green `main` must not pay it.

        Every session start but a few reads a green `main`, so a request made
        unconditionally would be paid on all of them for an answer nobody prints.
        """
        asked: list[object] = []

        def _jobs(slug: str, run_id: object) -> list[object]:
            asked.append(run_id)
            return [_REPLAY_ONLY]

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("success", 1553)])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""
        assert asked == [], "a green main must cost one request, not two"

    @pytest.mark.parametrize("boom", _NETWORK_FAILURES)
    def test_still_reports_a_red_main_when_the_attribution_cannot_be_read(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], boom: Exception
    ) -> None:
        """The enrichment is allowed to fail; the fact it enriches is not lost with it.

        By this point `main` is known to be red, which is the whole reason the
        script exists. Swallowing that because a second request timed out would
        turn a partial answer into the silence `PL-0ZGK` was filed on.
        """

        def _raise(slug: str, run_id: object) -> list[object]:
            raise boom

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("failure", 1553)])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _raise)
        assert main_ci_status.main() == 0
        out = capsys.readouterr().out
        assert "concluded failure" in out
        assert "main is red and no pull request will show it" in out


class TestStepConclusions:
    """Which steps ran and how they ended, read from the run's jobs.

    Measured over every completed `main` push run from 2026-08-22 to 2026-09-20
    (`PL-T83R`): 93 of the 109 failures were the replay step alone, with the
    bare `bin/docket check`, `ruff`, `mypy` and the full suite passing above it
    in the same job. The old line named no step, so a reader could not tell
    those 93 from the 16 that were something else without opening the run.
    """

    def test_reads_every_step_in_run_order(self) -> None:
        got = _pairs([("a", "success"), ("b", "failure"), ("c", "skipped")])
        assert got == (("a", "success"), ("b", "failure"), ("c", "skipped"))

    def test_names_the_step_that_failed(self) -> None:
        assert main_ci_status.failing_steps(_pairs(_REPLAY_STEPS)) == (main_ci_status.REPLAY_STEP,)

    def test_reports_every_failing_step_in_run_order(self) -> None:
        pairs = _pairs([("a", "failure"), ("b", "success"), ("c", "failure")])
        assert main_ci_status.failing_steps(pairs) == ("a", "c")

    def test_a_skipped_or_cancelled_step_is_not_a_failure(self) -> None:
        """Steps after the failure are `skipped`; reporting them would bury the cause."""
        pairs = _pairs([("a", "failure"), ("b", "skipped"), ("c", "cancelled")])
        assert main_ci_status.failing_steps(pairs) == ("a",)

    def test_a_failing_step_with_no_readable_name_still_takes_a_row(self) -> None:
        """Dropping it would turn two failures into the one that licenses the strong line."""
        jobs = [{"steps": [{"name": 7, "conclusion": "failure"}, {"conclusion": "failure"}]}]
        assert main_ci_status.failing_steps(main_ci_status.step_conclusions(jobs)) == (
            main_ci_status.UNNAMED_STEP,
            main_ci_status.UNNAMED_STEP,
        )

    @pytest.mark.parametrize(
        "jobs", [[], ["not a dict"], [{"steps": "not a list"}], [{}], [{"steps": ["x", 3]}]]
    )
    def test_returns_nothing_from_a_malformed_or_empty_payload(self, jobs: list) -> None:
        """Parsed JSON the API has promised nothing about; the caller degrades."""
        assert main_ci_status.step_conclusions(jobs) == ()

    def test_counts_the_steps_a_failure_left_unrun(self) -> None:
        assert main_ci_status.unrun_after(_pairs(_REPLAY_STEPS), main_ci_status.REPLAY_STEP) == 2

    def test_counts_nothing_for_a_step_that_is_not_there(self) -> None:
        assert main_ci_status.unrun_after(_pairs(_REPLAY_STEPS), "no such step") == 0


class TestAdvisoryNamesTheCause:
    def test_says_the_failure_is_the_queue_when_the_replay_failed_alone(self) -> None:
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(_REPLAY_STEPS))
        assert main_ci_status.REPLAY_STEP in line
        assert "the only step that failed" in line
        assert "bin/docket check --verify" in line, "the reader needs the command, not the cause"

    def test_never_calls_the_tree_clean_on_steps_the_failure_skipped(self) -> None:
        """The blocking half. `quality.yml` runs six to eleven checks *below* the
        replay - `import_boundary_check`, `core_vocabulary_check`, `glyph_check`
        and `contrast_check` among them, all reading `src/` and `app/` - and a
        failing step skips every one. A line calling the tree clean would be
        handing the reader a guarantee nobody checked.
        """
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(_REPLAY_STEPS))
        assert "unrun rather than green" in line
        assert "2 step(s) below it were skipped" in line

    def test_does_not_claim_the_queue_when_another_step_failed_too(self) -> None:
        """The whole claim rests on the replay being the only failure."""
        steps = [*_REPLAY_STEPS[:4], ("Run uv run mypy", "failure"), *_REPLAY_STEPS[5:]]
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(steps))
        assert "bin/docket check --verify" not in line
        assert "Run uv run mypy" in line

    def test_does_not_claim_the_queue_when_the_bare_check_never_passed(self) -> None:
        """The dangerous direction, and the one nothing else here would catch.

        Without the bare run's verdict the replay's failure is not narrowed to
        the `--verify` report at all: every store error the bare run rules out
        is back in scope. A missing step is not a passing one.
        """
        without = [s for s in _REPLAY_STEPS if s[0] != main_ci_status.BARE_CHECK_STEP]
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(without))
        assert "bin/docket check --verify" not in line
        skipped = [
            (main_ci_status.BARE_CHECK_STEP, "skipped")
            if s[0] == main_ci_status.BARE_CHECK_STEP
            else s
            for s in _REPLAY_STEPS
        ]
        assert "bin/docket check --verify" not in main_ci_status.advisory(
            _run("failure", 1553), _pairs(skipped)
        )

    def test_does_not_claim_the_queue_when_the_replay_was_killed_by_the_timeout(self) -> None:
        """A hung command says nothing about what it would have found.

        `quality.yml` sets `timeout-minutes: 15` precisely because one item's
        `verify:` command can hang. Reading that kill as "already passing" would
        invert it.
        """
        killed = [
            (main_ci_status.REPLAY_STEP, "timed_out") if s[0] == main_ci_status.REPLAY_STEP else s
            for s in _REPLAY_STEPS
        ]
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(killed))
        assert "bin/docket check --verify" not in line
        assert main_ci_status.REPLAY_STEP in line

    def test_does_not_claim_the_queue_when_the_run_itself_did_not_conclude_failure(self) -> None:
        line = main_ci_status.advisory(_run("timed_out", 1553), _pairs(_REPLAY_STEPS))
        assert "bin/docket check --verify" not in line

    def test_cuts_a_long_unnamed_step_and_says_that_it_cut_it(self) -> None:
        """`quality.yml`'s pytest step has no `name:`, so GitHub names it after 180
        characters of shell. Printed whole it buries the run number and the URL.
        """
        long_step = (
            "Run uv run pytest -n $(python3 -c 'import os; print(os.cpu_count() * 2)') "
            "--dist worksteal --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100"
        )
        line = main_ci_status.advisory(_run("failure", 1553), _pairs([(long_step, "failure")]))
        assert "Run uv run pytest" in line
        assert "(cut)" in line, "a command cut to look complete is worse than one that says so"
        assert long_step not in line
        assert line.endswith("https://github.com/o/r/actions/runs/1553")

    def test_leaves_every_named_step_in_the_workflow_whole(self) -> None:
        for step in _workflow_step_names():
            assert len(step) <= main_ci_status.STEP_WIDTH, step
            line = main_ci_status.advisory(_run("failure"), _pairs([(step, "failure")]))
            assert "(cut)" not in line

    def test_names_an_ordinary_failing_step_without_interpreting_it(self) -> None:
        line = main_ci_status.advisory(
            _run("failure", 1553), _pairs([("Run uv run mypy", "failure")])
        )
        assert "Run uv run mypy" in line
        assert "main is red and no pull request will show it" in line

    def test_falls_back_to_the_unattributed_line_when_no_step_could_be_read(self) -> None:
        """The enrichment may fail; the fact that `main` is red must still print."""
        line = main_ci_status.advisory(_run("failure", 1553), ())
        assert "concluded failure" in line
        assert "main is red and no pull request will show it" in line
        assert "1553" in line

    def test_still_says_nothing_when_main_is_green(self) -> None:
        assert main_ci_status.advisory(_run("success"), _pairs(_REPLAY_STEPS)) is None


class TestStepNamesMatchTheWorkflow:
    """The constants are strings GitHub derives from `quality.yml`; hold them to it.

    A renamed step would silently drop the attribution back to the generic line
    - the check would go on passing while the guarantee it stands for was void,
    which is what `CLAUDE.md` calls a defect in the check. `PL-T83R`.
    """

    def test_the_replay_step_is_named_in_quality_yml(self) -> None:
        assert f"name: {main_ci_status.REPLAY_STEP}" in _workflow()

    def test_the_bare_check_step_is_the_run_line_github_names_it_after(self) -> None:
        """It has no `name:`, so GitHub calls it `Run ` plus the `run:` line verbatim."""
        command = main_ci_status.BARE_CHECK_STEP.removeprefix("Run ")
        assert f"- run: {command}\n" in _workflow()
