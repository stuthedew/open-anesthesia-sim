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

`fetch_jobs` is the one exception and substitutes `urlopen` instead, a level
lower. Every other test replaces `fetch_jobs` wholesale, so a typo in its
endpoint path or in the response key it reads would leave this suite green
while the attribution never fired once - and its caller swallows the failure by
design, so nothing in production would report it either (`PL-T83R`).

The pytest line compares the step's median time with a recorded baseline
(`PL-YY32`). Its tests choose times whose median differs from their mean and
from the newest time, so a line built from either of those fails them.
"""

from __future__ import annotations

import email.message
import http.client
import io
import json
import pathlib
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import main_ci_status
import pytest


@pytest.fixture(autouse=True)
def _no_drift_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test reads no `drift.yml` runs unless it supplies some (`PL-JTWV`).

    `main` asks for them after the quality lines, so without this a test of
    those lines would reach the network.
    """
    monkeypatch.setattr(main_ci_status, "fetch_drift_runs", lambda slug: [])


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
    """One run as the API returns it.

    `id` and `run_number` are deliberately different values, and far apart. They
    are two of the three numbers this module handles and only one of them
    addresses the jobs endpoint - a fixture that let them coincide would pass a
    build that fetched `/actions/runs/1550/jobs` and got a 404 forever, with the
    attribution silently never firing and nothing here noticing.
    """
    return {
        "id": 99000000 + number,
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
        """A cancelled run never stands in for a verdict.

        Reading `cancelled` as an answer would report nothing about a red
        `main`, which is exactly the blindness the script exists to remove.
        The cancelled run gets a line of its own instead (`PL-JTHW`).
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


class TestPickUnjudged:
    """The cancelled run that earns a line: the newest one above every verdict (`PL-JTHW`)."""

    def test_takes_a_cancelled_run_newer_than_every_verdict(self) -> None:
        runs = [_run("cancelled", 1555), _run("success", 1553)]
        assert main_ci_status.pick_unjudged(runs)["run_number"] == 1555

    def test_takes_the_newest_of_several(self) -> None:
        """Re-running the newest checks the whole store again, so it answers for the rest."""
        runs = [_run("cancelled", 1556), _run("cancelled", 1555), _run("failure", 1553)]
        assert main_ci_status.pick_unjudged(runs)["run_number"] == 1556

    def test_passes_over_a_cancelled_run_a_later_verdict_covers(self) -> None:
        """Run 1556 checked the whole store on a tree containing 1555's commit."""
        runs = [_run("success", 1556), _run("cancelled", 1555), _run("success", 1553)]
        assert main_ci_status.pick_unjudged(runs) is None

    def test_looks_past_a_run_that_is_neither_a_verdict_nor_cancelled(self) -> None:
        runs = [_run("skipped", 1556), _run("cancelled", 1555), _run("success", 1553)]
        assert main_ci_status.pick_unjudged(runs)["run_number"] == 1555

    def test_takes_a_cancelled_run_when_none_reached_a_verdict(self) -> None:
        runs = [_run("cancelled", 1555), _run("cancelled", 1554)]
        assert main_ci_status.pick_unjudged(runs)["run_number"] == 1555

    def test_returns_none_without_a_cancelled_run_above_the_verdict(self) -> None:
        assert main_ci_status.pick_unjudged([]) is None
        assert main_ci_status.pick_unjudged([_run("success"), _run("cancelled")]) is None
        assert main_ci_status.pick_unjudged(["not a dict", 7]) is None

    def test_skips_a_malformed_entry_above_it(self) -> None:
        runs = ["not a dict", _run("cancelled", 1555)]
        assert main_ci_status.pick_unjudged(runs)["run_number"] == 1555


class TestUnjudgedAdvisory:
    def test_action_required_is_no_verdict_rather_than_main_red(self) -> None:
        """`PL-351H`: the conclusion `update_armed.py` reads as not failed is read so here too.

        It sat in `VERDICTS`, so a run GitHub held for an action printed "main
        is red" while the same conclusion on a check run did not hold a pull
        request back. Now neither reads it as a failure, and this says the
        commit has no verdict, as it does for a cancelled run.
        """
        runs = [_run("action_required", 1555, "c0ffee9900"), _run("success", 1553, "abcdef1234")]

        assert main_ci_status.pick_run(runs)["run_number"] == 1553
        unjudged = main_ci_status.pick_unjudged(runs)
        assert unjudged is not None and unjudged["run_number"] == 1555
        line = main_ci_status.unjudged_advisory(unjudged, main_ci_status.pick_run(runs))
        assert "#1555 on c0ffee99 concluded action_required" in line
        assert "no whole-store verdict" in line and "main is red" not in line

    def test_failed_is_the_one_set_update_armed_reads(self) -> None:
        import update_armed

        assert update_armed.FAILED is main_ci_status.FAILED
        assert "action_required" not in main_ci_status.FAILED | main_ci_status.VERDICTS

    def test_names_the_cancelled_run_and_the_older_verdict(self) -> None:
        """Which commit each answer is about is the reader's whole question.

        This reads completed runs only, so a newer merge's run still going is
        invisible to it; the line says so rather than send a reader to re-run
        a commit that run is already checking again.
        """
        line = main_ci_status.unjudged_advisory(
            _run("cancelled", 1555, "c0ffee9900"), _run("success", 1553, "abcdef1234")
        )
        assert "#1555 on c0ffee99 was cancelled" in line
        assert "no whole-store verdict" in line
        assert "#1553 on abcdef12" in line
        assert "Re-run it, unless a newer merge's run is still going" in line
        assert line.endswith("https://github.com/o/r/actions/runs/1555")


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
# ruff, mypy and the suite pass above it. The replay is the job's last step, so
# only GitHub's two cleanup rows follow it.
_REPLAY_STEPS = [
    ("Set up job", "success"),
    (main_ci_status.BARE_CHECK_STEP, "success"),
    ("Run uv run ruff check .", "success"),
    ("Run uv run mypy", "success"),
    ("Run uv run pytest", "success"),
    ("verify replay, scoped to what this branch changed", "skipped"),
    (main_ci_status.REPLAY_STEP, "failure"),
    # GitHub's own cleanup rows, one per `uses:` action. Every real job carries
    # them and every recorded replay failure carries exactly two.
    ("Post Run astral-sh/setup-uv@v9.0.0", "skipped"),
    ("Post Run actions/checkout@v7.0.1", "success"),
]


# The shape of a red `main` as it actually occurs: the whole-store replay is the
# only failing step, and every check that reads the tree passed above it.
_REPLAY_ONLY = _job(_REPLAY_STEPS)


def _github_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitute `git remote get-url` with this repository's GitHub remote."""
    monkeypatch.setattr(
        main_ci_status.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            a[0], 0, stdout=b"https://github.com/stuthedew/open-anesthesia-sim.git\n", stderr=b""
        ),
    )


class TestMain:
    """End to end, with the two boundaries substituted.

    These are the verdict lines' tests, so they leave the pytest line out.
    `TestMainWithThePytestLine` puts it back and checks how the two print together.
    """

    @pytest.fixture(autouse=True)
    def _origin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _github_origin(monkeypatch)
        monkeypatch.setattr(main_ci_status, "pytest_time_line", lambda slug, runs: None)

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

    def test_a_cancelled_main_run_is_reported(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """`main`'s newest run was cancelled, so its commit has no whole-store verdict.

        The green verdict below it is about an older commit, and printing
        nothing handed that answer to a reader as `main`'s - true of that
        commit and silent about the one that lost its run (`PL-JTHW`). The line
        asks for no step attribution: the verdict is green, so no step is asked about.
        """
        asked: list[object] = []

        def _jobs(slug: str, run_id: object) -> list[object]:
            asked.append(run_id)
            return [_REPLAY_ONLY]

        runs = [_run("cancelled", 1555, "c0ffee9900"), _run("success", 1553)]
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: runs)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        out = capsys.readouterr().out
        assert "#1555 on c0ffee99 was cancelled" in out
        assert "Re-run it" in out
        assert out.rstrip("\n").endswith("https://github.com/o/r/actions/runs/1555")
        assert asked == [], "a green verdict must ask for no step attribution"

    def test_a_cancelled_run_a_later_verdict_covers_prints_nothing(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The silence rule holds over an older cancellation.

        Run 1556 checked the whole store again on a tree containing 1555's
        commit, so there is nothing to re-run 1555 for, and `main` is green.
        """
        runs = [_run("success", 1556), _run("cancelled", 1555), _run("success", 1553)]
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: runs)
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_reports_a_cancelled_run_above_a_red_verdict_before_the_red_line(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Both lines, the newer commit first, and the red one still attributed."""
        runs = [_run("cancelled", 1555, "c0ffee9900"), _run("failure", 1553)]
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: runs)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", lambda slug, run_id: [_REPLAY_ONLY])
        assert main_ci_status.main() == 0
        lines = capsys.readouterr().out.splitlines()
        assert len(lines) == 2
        assert "#1555 on c0ffee99 was cancelled" in lines[0]
        assert "#1553 on abcdef12 concluded failure" in lines[1]
        assert main_ci_status.REPLAY_STEP in lines[1]

    def test_reports_a_cancelled_run_when_no_run_reached_a_verdict(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        runs = [_run("cancelled", 1555, "c0ffee9900"), _run("cancelled", 1554)]
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: runs)
        assert main_ci_status.main() == 0
        lines = capsys.readouterr().out.splitlines()
        assert len(lines) == 1, "one line, for the newest"
        assert "#1555 on c0ffee99 was cancelled" in lines[0]
        assert "no run readable here reached one" in lines[0]

    @pytest.mark.parametrize("boom", _NETWORK_FAILURES)
    def test_says_only_that_it_could_not_read_and_exits_zero_when_the_fetch_fails(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], boom: Exception
    ) -> None:
        """An offline container must start as cleanly as an online one.

        It exits 0 and prints no verdict line, which is the property that lets
        the hook call it unconditionally. It prints one line saying the pytest
        time was not compared, and no figure, so that line's silence still means
        "inside the band" (`PL-YY32`).
        """

        def _raise(slug: str) -> list[dict]:
            raise boom

        monkeypatch.setattr(main_ci_status, "fetch_runs", _raise)
        assert main_ci_status.main() == 0
        lines = capsys.readouterr().out.splitlines()
        assert lines == [
            main_ci_status.pytest_declined(f"the Actions API could not be read ({boom})")
        ]

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
            lambda *a, **k: subprocess.CompletedProcess(
                a[0], 0, stdout=b"/srv/r.git\n", stderr=b""
            ),
        )
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_addresses_the_jobs_endpoint_with_the_run_id_not_the_run_number(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The one number that wires the two requests together.

        `run_number` is what the line prints and `id` is what the endpoint takes.
        Sending the wrong one 404s forever, the failure is swallowed by design,
        and the attribution would simply never appear.
        """
        run = _run("failure", 1553)
        seen: list[object] = []

        def _jobs(slug: str, run_id: object) -> list[object]:
            seen.append(run_id)
            return [_REPLAY_ONLY]

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [run])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        assert seen == [run["id"]]
        assert seen != [run["run_number"]]

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
        """The attribution request is paid only on a failing verdict.

        Every session start but a few reads a green `main`, so asking for the
        verdict run's steps unconditionally would be paid on all of them for an
        answer nobody prints. The pytest line's own requests are a separate cost,
        which `TestMainWithThePytestLine` counts.
        """
        asked: list[object] = []

        def _jobs(slug: str, run_id: object) -> list[object]:
            asked.append(run_id)
            return [_REPLAY_ONLY]

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("success", 1553)])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""
        assert asked == [], "a green main must ask for no step attribution"

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
        """Names chosen against alphabetical order, so sorting anywhere would fail."""
        pairs = _pairs([("zulu", "failure"), ("mike", "success"), ("alfa", "failure")])
        assert main_ci_status.failing_steps(pairs) == ("zulu", "alfa")

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


class TestAdvisoryNamesTheCause:
    def test_says_the_failure_is_the_queue_when_the_replay_failed_alone(self) -> None:
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(_REPLAY_STEPS))
        assert main_ci_status.REPLAY_STEP in line
        assert "the only step that failed" in line
        assert "bin/docket check --verify" in line, "the reader needs the command, not the cause"

    def test_the_queue_line_still_carries_the_run_number_sha_and_url(self) -> None:
        """The longer sentence must not have pushed out what identifies the run."""
        line = main_ci_status.advisory(_run("failure", 1553, "9c6ebd29aaaa"), _pairs(_REPLAY_STEPS))
        assert "#1553" in line
        assert "9c6ebd29" in line
        assert line.endswith("https://github.com/o/r/actions/runs/1553")

    def test_reads_the_queue_through_the_checks_jobs_failed_parts_gate(self) -> None:
        """A part failing fails the `checks` job's gate step too, on every red run.

        Since `PL-T9X9` split the suite, the replay runs in `checks-part-1` and
        the `checks` job's first step fails because that part did. Counting it
        as a second failure meant the queue reading could never fire.
        """
        gate = {
            "name": "checks",
            "steps": [
                {"name": "Set up job", "conclusion": "success"},
                {"name": main_ci_status.PARTS_GATE_STEP, "conclusion": "failure"},
                {"name": "Run uv run coverage report", "conclusion": "skipped"},
            ],
        }
        steps = main_ci_status.step_conclusions([_REPLAY_ONLY, gate])
        line = main_ci_status.advisory(_run("failure", 1553), steps)
        assert "bin/docket check --verify" in line
        assert main_ci_status.PARTS_GATE_STEP not in line

    def test_names_the_parts_gate_when_it_is_the_only_failing_step(self) -> None:
        """A part that was cancelled leaves the gate as the run's one clue."""
        pairs = _pairs([("Set up job", "success"), (main_ci_status.PARTS_GATE_STEP, "failure")])
        assert main_ci_status.failing_steps(pairs) == (main_ci_status.PARTS_GATE_STEP,)

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
        """`quality.yml`'s pytest step has no `name:`, so GitHub names it after 150
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

    @pytest.mark.parametrize("length,cut", [(69, False), (70, False), (71, True)])
    def test_cuts_exactly_at_the_declared_width(self, length: int, cut: bool) -> None:
        """The boundary itself, rather than one workflow step happening to sit near it."""
        assert main_ci_status.STEP_WIDTH == 70
        line = main_ci_status.advisory(_run("failure"), _pairs([("s" * length, "failure")]))
        assert ("(cut)" in line) is cut

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


class TestFetchJobs:
    """The request itself: nothing else here would notice a wrong path or key.

    Every other test substitutes `fetch_jobs`, so a typo in the endpoint or in
    the response key would leave the whole suite green while the attribution
    never fired once - and the caller swallows the failure by design, so
    production would be silent about it too.
    """

    @pytest.fixture
    def _capture(self, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        urls: list[str] = []

        class _Response:
            def __enter__(self) -> io.BytesIO:
                return io.BytesIO(json.dumps({"jobs": [_REPLAY_ONLY], "total_count": 1}).encode())

            def __exit__(self, *exc: object) -> None:
                return None

        def _open(request: urllib.request.Request, timeout: float = 0) -> _Response:
            urls.append(request.full_url)
            return _Response()

        monkeypatch.setattr(main_ci_status.urllib.request, "urlopen", _open)
        return urls

    def test_asks_the_jobs_endpoint_for_that_run(self, _capture: list[str]) -> None:
        main_ci_status.fetch_jobs("o/r", 4242)
        assert _capture == ["https://api.github.com/repos/o/r/actions/runs/4242/jobs?per_page=50"]

    def test_reads_the_jobs_key(self, _capture: list[str]) -> None:
        assert main_ci_status.fetch_jobs("o/r", 4242) == [_REPLAY_ONLY]

    @pytest.mark.parametrize("payload", [{}, {"jobs": "not a list"}, {"workflow_runs": []}])
    def test_returns_an_empty_list_for_a_payload_without_jobs(
        self, monkeypatch: pytest.MonkeyPatch, payload: dict
    ) -> None:
        """A shape the API has promised nothing about degrades to no attribution."""

        class _Response:
            def __enter__(self) -> io.BytesIO:
                return io.BytesIO(json.dumps(payload).encode())

            def __exit__(self, *exc: object) -> None:
                return None

        monkeypatch.setattr(main_ci_status.urllib.request, "urlopen", lambda *a, **k: _Response())
        assert main_ci_status.fetch_jobs("o/r", 1) == []


# Run #4805's one job as the Actions API returned it on 2026-10-05: GitHub
# cancelled it 15 minutes after creating it, having given it no runner, so it
# has no steps, `runner_id` 0 and an empty `runner_name`.
_RUN_4805_JOB = {
    "id": 52700000000,
    "name": "checks",
    "status": "completed",
    "conclusion": "cancelled",
    "created_at": "2026-10-05T19:34:02Z",
    "started_at": "2026-10-05T19:34:02Z",
    "completed_at": "2026-10-05T19:49:04Z",
    "runner_id": 0,
    "runner_name": "",
    "steps": [],
}


def _gate_job(conclusion: str) -> dict:
    """The `checks` job, whose first step fails unless both parts succeeded."""
    job = _job([("Set up job", "success"), (main_ci_status.PARTS_GATE_STEP, conclusion)])
    job["runner_id"] = 1000011567
    return job


class TestIdleJobs:
    """A job no runner took is told apart from one that ran (`PL-7WNJ`).

    GitHub cancels such a job at the same 15 minutes `timeout-minutes` sets for
    a hung step, so without this a red `main` that ran nothing reads as code
    hanging.
    """

    def test_names_a_job_no_runner_took_as_nothing_ran(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _github_origin(monkeypatch)
        monkeypatch.setattr(main_ci_status, "pytest_time_line", lambda slug, runs: None)
        run = _run("failure", 4805, "b67dace8aaaa")
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [run])
        monkeypatch.setattr(main_ci_status, "fetch_jobs", lambda slug, run_id: [_RUN_4805_JOB])
        assert main_ci_status.main() == 0
        out = capsys.readouterr().out
        assert '#4805 on b67dace8 concluded failure because no runner took the job "checks"' in out
        assert "so nothing ran" in out
        assert "re-run it rather than fixing anything" in out
        assert out.rstrip("\n").endswith("https://github.com/o/r/actions/runs/4805")

    def test_reads_the_4805_shape(self) -> None:
        assert main_ci_status.idle_jobs([_RUN_4805_JOB]) == ("checks",)

    def test_a_job_that_ran_is_not_idle(self) -> None:
        ran = {**_REPLAY_ONLY, "runner_id": 1000011567}
        assert main_ci_status.idle_jobs([ran]) == ()

    def test_a_job_with_steps_is_not_idle_even_with_runner_id_zero(self) -> None:
        assert main_ci_status.idle_jobs([{**_REPLAY_ONLY, "runner_id": 0}]) == ()

    @pytest.mark.parametrize("runner", [None, False, "0", 0.0])
    def test_only_a_runner_id_of_integer_zero_reads_as_no_runner(self, runner: object) -> None:
        """A missing or odd field is not evidence that the tree went unjudged."""
        job = {**_RUN_4805_JOB, "runner_id": runner}
        if runner is None:
            del job["runner_id"]
        assert main_ci_status.idle_jobs([job]) == ()

    def test_a_job_whose_steps_are_absent_reads_as_idle(self) -> None:
        job = {key: value for key, value in _RUN_4805_JOB.items() if key != "steps"}
        assert main_ci_status.idle_jobs([job, "not a dict"]) == ("checks",)

    def test_a_job_that_ran_keeps_todays_line(self) -> None:
        line = main_ci_status.advisory(_run("failure", 1553), _pairs(_REPLAY_STEPS), ())
        assert "bin/docket check --verify" in line
        assert "no runner" not in line.lower()

    def test_one_idle_part_beside_passing_jobs_is_the_whole_failure(self) -> None:
        part_1 = {**_job([("Set up job", "success"), ("Run uv run pytest", "success")])}
        part_2 = {**_RUN_4805_JOB, "name": "checks-part-2"}
        jobs = [part_1, part_2, _gate_job("failure")]
        line = main_ci_status.advisory(
            _run("failure", 1553),
            main_ci_status.step_conclusions(jobs),
            main_ci_status.idle_jobs(jobs),
        )
        assert 'no runner took the job "checks-part-2", so that job ran no step' in line
        assert "Every step that ran passed" in line
        assert "main is red" not in line

    def test_an_idle_job_beside_a_real_failure_names_both(self) -> None:
        line = main_ci_status.advisory(
            _run("failure", 1553),
            _pairs([("Run uv run mypy", "failure")]),
            ("checks-part-2", "checks"),
        )
        assert "Run uv run mypy" in line
        assert "main is red" in line
        assert 'No runner took the jobs "checks-part-2", "checks", so they ran nothing.' in line

    def test_withholds_the_queue_reading_while_a_job_is_idle(self) -> None:
        """A part that never ran checked nothing, so the tree is not cleared."""
        line = main_ci_status.advisory(
            _run("failure", 1553), _pairs(_REPLAY_STEPS), ("checks-part-2",)
        )
        assert "bin/docket check --verify" not in line
        assert main_ci_status.REPLAY_STEP in line
        assert 'No runner took the job "checks-part-2", so it ran nothing.' in line


class TestStepNamesMatchTheWorkflow:
    """The constants are strings GitHub derives from `quality.yml`; hold them to it.

    A renamed step would silently drop the attribution back to the generic line
    - the check would go on passing while the guarantee it stands for was void,
    which is what `CLAUDE.md` calls a defect in the check. `PL-T83R`.
    """

    def test_the_replay_step_is_named_in_quality_yml(self) -> None:
        assert f"name: {main_ci_status.REPLAY_STEP}" in _workflow()

    def test_the_parts_gate_step_is_named_in_quality_yml(self) -> None:
        assert f"- name: {main_ci_status.PARTS_GATE_STEP}\n" in _workflow()

    def test_the_bare_check_step_is_the_run_line_github_names_it_after(self) -> None:
        """It has no `name:`, so GitHub calls it `Run ` plus the `run:` line verbatim."""
        command = main_ci_status.BARE_CHECK_STEP.removeprefix("Run ")
        assert f"- run: {command}\n" in _workflow()


class TestFetchRuns:
    """The branch the runs are asked for is docket's rather than a literal here (`PL-9KLN`)."""

    def test_asks_for_the_runs_on_the_branch_docket_names(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        urls: list[str] = []

        class _Response:
            def __enter__(self) -> io.BytesIO:
                return io.BytesIO(json.dumps({"workflow_runs": []}).encode())

            def __exit__(self, *exc: object) -> None:
                return None

        def _open(request: urllib.request.Request, timeout: float = 0) -> _Response:
            urls.append(request.full_url)
            return _Response()

        monkeypatch.setattr(main_ci_status, "default_branch", lambda root: "trunk")
        monkeypatch.setattr(main_ci_status.urllib.request, "urlopen", _open)

        assert main_ci_status.fetch_runs("o/r") == []
        assert urls == [
            "https://api.github.com/repos/o/r/actions/workflows/quality.yml/runs"
            "?branch=trunk&event=push&status=completed&per_page=10"
        ]


def _pytest_step_names() -> list[str]:
    """The names GitHub gives `quality.yml`'s pytest steps: `Run ` plus each `run:` line.

    A step with a `name:` of its own carries its `run:` on a line that does not
    open the step, so the assertion below refuses it. The item-only fast path's
    step is left out (`PL-DXD4`). It runs only the tests marked
    `reads_item_store`, and it is named so that `pytest_seconds` leaves it out
    of the suite's time: it is skipped on `main`, and a skipped pytest step
    stops that time being read.
    """
    lines = [line.strip() for line in _workflow().splitlines()]
    runs = [
        line for line in lines if "run: uv run pytest" in line and "-m reads_item_store" not in line
    ]
    assert runs, "quality.yml should run pytest"
    assert all(line.startswith("- run: ") for line in runs), f"a pytest step is named: {runs}"
    return ["Run " + line.removeprefix("- run: ") for line in runs]


def _stamp(instant: datetime) -> str:
    """A time as the Actions API writes it."""
    return instant.strftime("%Y-%m-%dT%H:%M:%SZ")


def _timed_job(seconds: float, conclusion: str = "success", name: str = "checks-part-2") -> dict:
    """A part's job whose pytest step took `seconds`, between two other steps."""
    start = datetime(2026, 10, 17, 16, 8, 21, tzinfo=UTC)
    end = start + timedelta(seconds=seconds)
    return {
        "name": name,
        "steps": [
            {
                "name": "Run uv run mypy",
                "conclusion": "success",
                "started_at": _stamp(start - timedelta(seconds=9)),
                "completed_at": _stamp(start),
            },
            {
                "name": _pytest_step_names()[0],
                "conclusion": conclusion,
                "started_at": _stamp(start),
                "completed_at": _stamp(end),
            },
            {
                "name": "Run uv run python tools/branch_id_check.py",
                "conclusion": "success",
                "started_at": _stamp(end),
                "completed_at": _stamp(end + timedelta(seconds=1)),
            },
        ],
    }


def _times_by_id(seconds: dict[int, float]) -> Callable[[str, object], list[object]]:
    """A `fetch_jobs` substitute that answers each run id with its pytest time."""

    def _jobs(slug: str, run_id: object) -> list[object]:
        assert isinstance(run_id, int)
        return [_timed_job(seconds[run_id])]

    return _jobs


def _green_page(count: int, first: int = 1560) -> list[dict]:
    """`count` successful runs, newest first, numbered down from `first`."""
    return [_run("success", first - index) for index in range(count)]


# Times whose median (790) differs from their mean (894) and from the newest
# time (800), so a line built from either of those reads a different figure.
# The median is 1.68 times the baseline, above the band.
_SLOW = [800.0, 100.0, 790.0, 2000.0, 780.0]

# The median here (205) is 0.44 times the baseline, below the band, while the
# mean (333, 0.71 times) sits inside it. A line built from the mean would stay
# silent on a baseline this far out of date.
_FAST = [200.0, 150.0, 210.0, 900.0, 205.0]


class TestPytestSeconds:
    """The pytest step's time, read from one run's jobs (`PL-YY32`)."""

    def test_reads_the_time_between_the_steps_start_and_end(self) -> None:
        assert main_ci_status.pytest_seconds([_timed_job(523)]) == 523.0

    def test_sums_the_pytest_steps_of_the_parts(self) -> None:
        """Each part's job runs one pytest step, so the suite's time is their sum (`PL-T9X9`)."""
        first = _timed_job(300, name="checks-part-1")
        assert main_ci_status.pytest_seconds([first, _timed_job(223)]) == 523.0

    def test_a_job_with_no_pytest_step_adds_nothing(self) -> None:
        gate = _timed_job(9999, name="checks")
        gate["steps"] = [gate["steps"][0]]
        assert main_ci_status.pytest_seconds([gate, _timed_job(523)]) == 523.0
        assert main_ci_status.pytest_seconds([gate]) is None

    @pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", None])
    def test_a_step_that_did_not_end_in_success_has_no_time(self, conclusion: str | None) -> None:
        """It stopped early, so its time would understate the suite."""
        job = _timed_job(523)
        job["steps"][1]["conclusion"] = conclusion
        assert main_ci_status.pytest_seconds([job]) is None

    @pytest.mark.parametrize("key", ["started_at", "completed_at"])
    @pytest.mark.parametrize("value", [None, "", "yesterday", 1760717301])
    def test_a_step_without_a_readable_time_has_none(self, key: str, value: object) -> None:
        job = _timed_job(523)
        job["steps"][1][key] = value
        assert main_ci_status.pytest_seconds([job]) is None

    def test_a_named_pytest_step_is_not_found(self) -> None:
        """Naming the step would change what GitHub calls it; the caller then declines."""
        job = _timed_job(523)
        job["steps"][1]["name"] = "pytest, with coverage"
        assert main_ci_status.pytest_seconds([job]) is None

    @pytest.mark.parametrize(
        "jobs",
        [[], ["not a dict"], [{"name": "checks", "steps": "not a list"}], [{"name": "checks"}]],
    )
    def test_returns_none_from_a_malformed_or_empty_payload(self, jobs: list) -> None:
        assert main_ci_status.pytest_seconds(jobs) is None

    def test_a_job_whose_steps_cannot_be_read_hides_nothing(self) -> None:
        """It may hold a part's pytest step, so the sum without it would understate the suite."""
        jobs = [_timed_job(523), {"name": "checks-part-1", "steps": "not a list"}]
        assert main_ci_status.pytest_seconds(jobs) is None


class TestPytestAdvisory:
    """The computation: the median against the baseline and its band (`PL-YY32`)."""

    @pytest.mark.parametrize("fraction", [main_ci_status.PYTEST_BAND[0], 1.0, 0.8, 1.2])
    def test_says_nothing_inside_the_band(self, fraction: float) -> None:
        seconds = [main_ci_status.PYTEST_BASELINE_S * fraction] * main_ci_status.PYTEST_RUNS
        assert main_ci_status.pytest_advisory(seconds, _green_page(5)) is None

    def test_says_nothing_on_the_upper_bound(self) -> None:
        upper = main_ci_status.PYTEST_BASELINE_S * main_ci_status.PYTEST_BAND[1]
        assert main_ci_status.pytest_advisory([upper] * 5, _green_page(5)) is None

    def test_reports_the_median_above_the_band(self) -> None:
        line = main_ci_status.pytest_advisory(_SLOW, _green_page(5))
        assert line is not None
        assert "is 790 s, which is 1.68 times the 470 s baseline" in line
        assert "Find what slowed it." in line

    def test_reports_the_median_below_the_band(self) -> None:
        line = main_ci_status.pytest_advisory(_FAST, _green_page(5))
        assert line is not None
        assert "is 205 s, which is 0.44 times the 470 s baseline" in line
        assert "or the band cannot catch the next slowdown" in line

    def test_names_the_runs_the_median_was_taken_over(self) -> None:
        line = main_ci_status.pytest_advisory(_SLOW, _green_page(5, first=1560))
        assert line is not None
        assert "main's last 5 successful runs (#1560 back to #1556)" in line
        assert line.endswith("https://github.com/o/r/actions/runs/1560")


class TestPytestTimeLine:
    """Which runs are read, and every way the read declines (`PL-YY32`)."""

    def test_reads_the_newest_successful_runs_and_passes_over_the_rest(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        runs = [
            _run("cancelled", 1570),
            _run("success", 1569),
            _run("failure", 1568),
            *_green_page(6, first=1567),
        ]
        asked: list[object] = []
        slow = dict(zip([1569, 1567, 1566, 1565, 1564], _SLOW, strict=True))

        def _jobs(slug: str, run_id: object) -> list[object]:
            asked.append(run_id)
            assert isinstance(run_id, int)
            return [_timed_job(slow[run_id - 99000000])]

        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        line = main_ci_status.pytest_time_line("o/r", runs)
        assert sorted(asked) == sorted(99000000 + number for number in slow)
        assert line is not None
        assert "(#1569 back to #1564) is 790 s" in line

    def test_says_nothing_while_the_median_is_inside_the_band(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        page = _green_page(5)
        times = {run["id"]: 470.0 + index for index, run in enumerate(page)}
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _times_by_id(times))
        assert main_ci_status.pytest_time_line("o/r", page) is None

    def test_declines_with_fewer_successful_runs_than_the_median_needs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A median of a smaller set would mean something else, so it is not taken."""
        asked: list[object] = []
        monkeypatch.setattr(
            main_ci_status, "fetch_jobs", lambda slug, run_id: asked.append(run_id) or []
        )
        runs = [*_green_page(4), _run("failure", 1500), _run("cancelled", 1499)]
        assert main_ci_status.pytest_time_line("o/r", runs) == main_ci_status.pytest_declined(
            "only 4 of main's last 6 completed runs succeeded, and the median needs 5"
        )
        assert asked == [], "a declined line asks for nothing"

    @pytest.mark.parametrize("boom", _NETWORK_FAILURES)
    def test_declines_in_words_when_a_read_fails(
        self, monkeypatch: pytest.MonkeyPatch, boom: Exception
    ) -> None:
        """One failed read declines the whole line rather than take the median of four."""
        page = _green_page(5)

        def _jobs(slug: str, run_id: object) -> list[object]:
            if run_id == page[2]["id"]:
                raise boom
            return [_timed_job(2000)]

        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.pytest_time_line("o/r", page) == main_ci_status.pytest_declined(
            f"the Actions API could not be read ({boom})"
        )

    def test_declines_when_a_run_has_no_finished_pytest_step(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        page = _green_page(5, first=1560)

        def _jobs(slug: str, run_id: object) -> list[object]:
            if run_id == page[3]["id"]:
                return [_timed_job(2000, conclusion="cancelled")]
            return [_timed_job(2000)]

        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.pytest_time_line("o/r", page) == main_ci_status.pytest_declined(
            "run #1557 has a pytest step that did not finish, or none that could be read"
        )

    def test_a_declined_line_gives_no_figure_but_the_baseline(self) -> None:
        line = main_ci_status.pytest_declined("the Actions API could not be read (offline)")
        assert line == (
            "CI's pytest step time was not compared with its 470 s baseline, because "
            "the Actions API could not be read (offline)."
        )


class TestMainWithThePytestLine:
    """How the pytest line prints beside the verdict lines, end to end (`PL-YY32`)."""

    @pytest.fixture(autouse=True)
    def _origin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _github_origin(monkeypatch)

    def test_a_green_main_inside_the_band_prints_nothing(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        page = _green_page(10)
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: page)
        monkeypatch.setattr(
            main_ci_status, "fetch_jobs", _times_by_id({run["id"]: 480.0 for run in page})
        )
        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_a_green_main_costs_one_request_per_run_the_median_reads(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The runs list, then one jobs request for each of the newest five green runs."""
        page = _green_page(10)
        asked: list[object] = []

        def _jobs(slug: str, run_id: object) -> list[object]:
            asked.append(run_id)
            return [_timed_job(480)]

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: page)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        assert sorted(asked) == sorted(run["id"] for run in page[: main_ci_status.PYTEST_RUNS])

    def test_a_drifted_green_main_prints_only_the_pytest_line(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        page = _green_page(5)
        times = dict(zip((run["id"] for run in page), _SLOW, strict=True))
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: page)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _times_by_id(times))
        assert main_ci_status.main() == 0
        lines = capsys.readouterr().out.splitlines()
        assert len(lines) == 1
        assert lines[0].startswith("CI's pytest step has drifted from its baseline.")

    def test_the_pytest_line_comes_after_a_red_verdict(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A red `main` matters more than a slow suite, so it is read first."""
        page = [_run("failure", 1561), *_green_page(5)]
        times = dict(zip((run["id"] for run in page[1:]), _SLOW, strict=True))

        def _jobs(slug: str, run_id: object) -> list[object]:
            if run_id == page[0]["id"]:
                return [_REPLAY_ONLY]
            return _times_by_id(times)(slug, run_id)

        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: page)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _jobs)
        assert main_ci_status.main() == 0
        lines = capsys.readouterr().out.splitlines()
        assert len(lines) == 2
        assert "#1561 on abcdef12 concluded failure" in lines[0]
        assert lines[1].startswith("CI's pytest step has drifted from its baseline.")


class TestThePytestStepMatchesTheWorkflow:
    """The pytest steps' names are strings GitHub derives from `quality.yml`; hold them to it.

    A pytest step given a `name:` would make every run read as having no pytest
    step, or as having one part's. The line would then decline at every session start, which
    is honest but stops the check, so a test fails first.
    """

    def test_every_pytest_step_is_unnamed_and_github_names_it_with_the_prefix(self) -> None:
        names = _pytest_step_names()
        assert all(name.startswith(main_ci_status.PYTEST_STEP_PREFIX) for name in names), names


def _offline(*a: object, **k: object) -> list[object]:
    """A read of the API that fails as an unreachable host does."""
    raise urllib.error.URLError("offline")


def _drift_run(conclusion: str, number: int, created: str = "2026-10-01T06:00:12Z") -> dict:
    """One `drift.yml` run, dated as the API dates it."""
    return {**_run(conclusion, number), "created_at": created}


class TestDriftLine:
    """A failed `drift.yml` run reaches the session-start digest (`PL-JTWV`).

    The run of 2026-10-01 failed and went unread for 17 days, because this
    script read only `quality.yml`. The line names the run, its date and the
    jobs that failed, and stays silent while the newest verdict passed.
    """

    @pytest.fixture(autouse=True)
    def _origin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _github_origin(monkeypatch)
        monkeypatch.setattr(main_ci_status, "fetch_runs", lambda slug: [_run("success", 1553)])
        monkeypatch.setattr(main_ci_status, "pytest_time_line", lambda slug, runs: None)

    def test_a_failed_drift_run_is_named(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        asked: list[object] = []
        jobs = [
            {"name": "dependencies", "conclusion": "success"},
            {"name": "interpreter", "conclusion": "failure"},
            {"name": "order", "conclusion": "skipped"},
        ]
        monkeypatch.setattr(
            main_ci_status, "fetch_drift_runs", lambda slug: [_drift_run("failure", 12)]
        )
        monkeypatch.setattr(
            main_ci_status, "fetch_jobs", lambda slug, run_id: asked.append(run_id) or jobs
        )

        assert main_ci_status.main() == 0
        out = capsys.readouterr().out

        assert asked == [99000012]
        assert (
            "drift.yml's newest run on main, #12 on 2026-10-01, concluded failure in the job "
            '"interpreter".'
        ) in out
        assert "https://github.com/o/r/actions/runs/12" in out
        assert out.count("\n") == 1

    def test_the_newest_verdict_passing_prints_nothing_and_asks_for_no_jobs(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        runs = [_drift_run("cancelled", 14), _drift_run("success", 13), _drift_run("failure", 12)]
        monkeypatch.setattr(main_ci_status, "fetch_drift_runs", lambda slug: runs)
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _offline)

        assert main_ci_status.main() == 0
        assert capsys.readouterr().out == ""

    def test_a_failed_run_whose_jobs_cannot_be_read_still_prints(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            main_ci_status, "fetch_drift_runs", lambda slug: [_drift_run("timed_out", 12)]
        )
        monkeypatch.setattr(main_ci_status, "fetch_jobs", _offline)

        assert main_ci_status.main() == 0
        assert (
            "#12 on 2026-10-01, concluded timed_out and which of its jobs failed could not be read"
            in capsys.readouterr().out
        )

    def test_an_unread_drift_listing_says_so(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(main_ci_status, "fetch_drift_runs", _offline)

        assert main_ci_status.main() == 0
        assert "a failed drift run would not show here" in capsys.readouterr().out

    def test_asks_for_drift_runs_of_any_event_on_the_branch_docket_names(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        urls: list[str] = []

        class _Response:
            def __enter__(self) -> io.BytesIO:
                return io.BytesIO(json.dumps({"workflow_runs": []}).encode())

            def __exit__(self, *exc: object) -> None:
                return None

        def _open(request: urllib.request.Request, timeout: float = 0) -> _Response:
            urls.append(request.full_url)
            return _Response()

        monkeypatch.undo()
        monkeypatch.setattr(main_ci_status, "default_branch", lambda root: "trunk")
        monkeypatch.setattr(main_ci_status.urllib.request, "urlopen", _open)

        assert main_ci_status.fetch_drift_runs("o/r") == []
        assert urls == [
            "https://api.github.com/repos/o/r/actions/workflows/drift.yml/runs"
            "?branch=trunk&status=completed&per_page=5"
        ]

    def test_names_the_workflow_file_that_exists(self) -> None:
        workflow = pathlib.Path(__file__).resolve().parents[2] / ".github/workflows"
        assert (workflow / main_ci_status.DRIFT_WORKFLOW).is_file()
