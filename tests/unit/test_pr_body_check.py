"""Tests for `tools/pr_body_check.py`, the lost-squash-body guard.

The check exists because this repository's squash commit message *is* the pull
request body (`squash_merge_commit_message: PR_BODY`), and 187 of 683 squash
commits on `main` landed without one - 763,222 characters of design reasoning
that survive only on GitHub (`PL-843V`).

Three failure modes are worth more than the happy path.

A guard that stays quiet on a lost body is the defect itself, so the incident
shape asserts that it fires. A guard that fires on correct work gets worked
around, so the two shapes that legitimately carry no body each assert silence -
and those are the interesting ones, because they are exactly what a crude "does
this commit have a body" check gets wrong: the pre-2026-08-31 `Merge pull
request #101 from ...` merges, which carry the number but not in the trailing
`(#N)` form, and the 2026-08 bootstrap commits, which are nobody's pull
request. Both are real commits on `main` today, so a regression here would fire
on 20 commits that can never be recovered because there is nothing to recover.

The third is that a recovered body has to be recorded *verbatim*. It is a
historical record; a recovery that reflows, strips or re-wraps it produces a
document that reads like the original and is not, which is the failure this
whole item is about arriving a second time by another route.

`--compare` has the same two ways to fail and a third of its own (`PL-Y1W0`).
A body that landed saying something else has to be reported, which is the test
the item's `verify:` names. What GitHub, the 2026-09-06 rewrite and the
claude.ai footer do to every body must not be, or 654 bodies that match would
bury the 27 that do not. And a listing that could not be read has to say so,
because a comparison never made reads exactly like one that found nothing.

The record written before the merge (`PL-979D`) adds the case that matters
most: what `--record` writes has to be exactly what `--check` accepts, and a
body edited after it was recorded has to be refused.

`_git`, `fetch_body`, `fetch_pull` and `_get_json` are substituted rather than a repository
built and the network called, because what is under test is the reading of
subjects and bodies, not git and not GitHub.
"""

from __future__ import annotations

import pr_body_check
import pytest

#: A record as `squash_commits` asks git for it: sha, subject, body.
NUL = "\x00"
RS = "\x01"


def _install(monkeypatch: pytest.MonkeyPatch, records: list[tuple[str, str, str]]) -> None:
    """A `_git` serving one history, and a resolvable default branch."""
    log = RS.join(f"{sha}{NUL}{subject}{NUL}{body}" for sha, subject, body in records) + RS

    def fake(*args: str) -> str:
        if args[0] == "rev-parse":
            return "origin/main\n" if "origin/main" in args else ""
        if args[0] == "log" and "--first-parent" in args:
            return log
        if args[0] == "log":
            return "2026-09-20\n"
        if args[0] == "remote":
            return "https://github.com/stuthedew/open-anesthesia-sim.git\n"
        return ""

    monkeypatch.setattr(pr_body_check, "_git", fake)


def test_fires_on_a_squash_commit_whose_body_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The incident shape: a `(#N)` subject with nothing under it."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: give the flow envelope a name (#768)", "")])

    assert pr_body_check.missing("origin/main") == [
        ("abc1234", 768, "PL-8PS6: give the flow envelope a name (#768)")
    ]


def test_silent_on_a_squash_commit_that_kept_its_body(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The mechanism works most of the time; firing on those is the way it dies."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: give the flow envelope a name (#768)", "Why.")])

    assert pr_body_check.missing("origin/main") == []


def test_silent_on_the_old_merge_commit_shape(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """`Merge pull request #101 from ...` carries a number but never a `(#N)`.

    Seven such commits are on `main` and legitimately carry no body. They are
    what a check keyed on "mentions a pull request number" would wrongly claim.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(
        monkeypatch,
        [("abc1234", "Merge pull request #101 from stuthedew/claude/roadmap-write", "")],
    )

    assert pr_body_check.missing("origin/main") == []


def test_silent_on_a_direct_commit_that_was_never_a_pull_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The 2026-08 bootstrap commits owe no body to anyone."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "Initial Commit", "")])

    assert pr_body_check.missing("origin/main") == []


def test_a_whitespace_only_body_counts_as_lost(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """A body of blank lines carries no reasoning, whatever its length."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "  \n\n  \n")])

    assert [pr for _, pr, _ in pr_body_check.missing("origin/main")] == [768]


def test_a_recovered_body_stops_the_advisory(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Once the reasoning is in the checkout the check has nothing left to say."""
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "768.md").write_text("recovered", encoding="utf-8")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])

    assert pr_body_check.missing("origin/main") == []


def test_recover_records_the_body_verbatim(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """The record is historical, so every character of it survives the round trip."""
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    body = "| Claim | What it says |\n| --- | --- |\n\n*emphasis*, `code`, <angle>.\n"
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])
    monkeypatch.setattr(pr_body_check, "fetch_body", lambda slug, pr: body)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)

    assert pr_body_check.recover("origin/main") == 1
    written = (recovery / "768.md").read_text(encoding="utf-8")
    assert written.endswith(body.rstrip() + "\n")
    assert "pr: 768" in written
    assert "commit: abc1234" in written


def test_a_body_unreadable_from_the_api_is_left_for_a_later_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """A rate limit or an outage must not write a file that then silences the check.

    Writing an empty recovery file would satisfy `recovered()` forever, and the
    loss would become permanent at the moment the tool meant to repair it ran.
    """
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])
    monkeypatch.setattr(pr_body_check, "fetch_body", lambda slug, pr: None)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)

    assert pr_body_check.recover("origin/main") == 0
    assert not (recovery / "768.md").exists()
    assert [pr for _, pr, _ in pr_body_check.missing("origin/main")] == [768]


def test_default_branch_ref_follows_docket_on_a_master_only_clone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A clone whose default is `master` gets `origin/master`, as every docket command does.

    The `origin/main`-then-`main` list spelled here gave None, so the advisory
    stayed silent on a history it could have read (`PL-GNCB`). It now asks
    `vcs.default_base`, through this module's own `_git`.
    """

    def fake(*args: str) -> str:
        return "0" * 40 + "\n" if args[:1] == ("rev-parse",) and "origin/master" in args else ""

    monkeypatch.setattr(pr_body_check, "_git", fake)
    assert pr_body_check.default_branch_ref() == "origin/master"


def test_says_nothing_when_the_default_branch_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bare or shallow checkout has no history to judge, and must not claim one.

    At session start that means silence. Asked to `--compare`, it means saying
    nothing was compared, since a run that prints nothing there reads as clean.
    """
    monkeypatch.setattr(pr_body_check, "_git", lambda *args: "")

    assert pr_body_check.default_branch_ref() is None
    assert pr_body_check.main([]) == 0
    assert capsys.readouterr().out == ""
    assert pr_body_check.main(["--compare"]) == 0
    assert "nothing compared" in capsys.readouterr().out


def test_a_pull_request_with_no_body_is_tombstoned_rather_than_reported_forever(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """A body that cannot exist must stop being reported, without being called recovered.

    `#325` is the live case: `body` is null on GitHub, and its squash commit
    escaped this check only because GitHub left the 46-character
    `Co-authored-by` trailer behind. Without a tombstone the advisory would
    report a loss that no run could ever repair, which is the shape of an
    advisory nobody can act on.
    """
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "")])
    monkeypatch.setattr(pr_body_check, "fetch_body", lambda slug, pr: pr_body_check.NO_BODY)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)

    assert pr_body_check.recover("origin/main") == 1
    written = (recovery / "768.md").read_text(encoding="utf-8")
    assert "nothing to recover" in written
    assert pr_body_check.missing("origin/main") == []


def test_the_advisory_is_one_line(monkeypatch: pytest.MonkeyPatch, tmp_path, capsys) -> None:
    """Session-start output is resent on every turn, so the budget is a line.

    `tools/dead_ends.py` caps its emitted half for the same reason. A
    multi-line advisory here is paid by every turn of every session for as long
    as one loss stays unrecovered, which at the measured recurrence is always.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [(f"abc123{n}", f"PL-8PS6: a title (#{760 + n})", "") for n in range(9)])

    assert pr_body_check.main([]) == 0
    printed = capsys.readouterr().out.strip()
    assert printed.count("\n") == 0
    assert "--recover" in printed


def test_item_ids_judges_a_subject_by_the_stores_own_grammar() -> None:
    """A recovered body is filed under the ids in its subject, so those have to be ids.

    `PL-[0-9A-Z]{3,4}` stood here: it read any three characters as one of the
    store's historical ids, where only three *digits* is one, and admitted the
    vowels the alphabet excludes. A recovery filed under a token no item
    carries is provenance attached to nothing (`PL-KYW3`).
    """
    assert pr_body_check.item_ids("PL-001: the early work (#12)", 12, {}) == ["PL-001"]
    assert pr_body_check.item_ids("Rework the PL-CAP fixture (#13)", 13, {}) == []  # not-an-id


def _serve(
    monkeypatch: pytest.MonkeyPatch, pages: list[list[dict] | None], calls: list[str] | None = None
) -> None:
    """A `_get_json` serving the closed-pull-request listing a page at a time.

    `None` as a page is a failed read. Past the last page the listing is empty,
    which is how GitHub ends one.
    """

    def fake(url: str) -> object | None:
        if calls is not None:
            calls.append(url)
        page = int(url.rsplit("page=", 1)[1])
        return pages[page - 1] if page <= len(pages) else []

    monkeypatch.setattr(pr_body_check, "_get_json", fake)


def _pull(number: int, body: str | None, armed: str | None = None) -> dict:
    """One listing entry, in the shape the API returns it."""
    return {
        "number": number,
        "body": body,
        "auto_merge": None if armed is None else {"commit_message": armed},
    }


def _differing(lines: list[str]) -> list[int]:
    """The pull request numbers a `compare` report names."""
    return [int(line.split("#")[1].split()[0]) for line in lines if line.startswith("  #")]


def test_fires_on_a_squash_body_that_differs_from_its_pull_request_body(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The incident shape: `#844` landed a 1,969-character message where the body is 5,392.

    Nothing offline can see it, because only GitHub holds the other copy, and the
    default mode passes it as intact since the body is not empty.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "Why, in brief.")])
    _serve(monkeypatch, [[_pull(768, "Why, in brief.\n\n## What was refused\n\nThe other route.")]])

    lines = pr_body_check.compare("origin/main")

    assert _differing(lines) == [768]
    assert "differs" in lines[1]
    assert lines[0].startswith("pr-body: 1 of 1 squash commit(s)")
    assert pr_body_check.missing("origin/main") == []


@pytest.mark.parametrize(
    "appended",
    [
        "\n\n---------\n\nCo-authored-by: Claude <noreply@anthropic.com>\n",
        "\n\nCo-authored-by: Claude <noreply@anthropic.com>\n",
    ],
    ids=["after-separator", "directly"],
)
def test_silent_on_a_body_github_rewrapped_and_signed(
    monkeypatch: pytest.MonkeyPatch, tmp_path, appended: str
) -> None:
    """`#993`'s shape: the same body, hard-wrapped, with GitHub's trailer below it.

    Both trailer shapes are on `main`, and 651 of the 654 bodies that match
    differ in whitespace, so a check that fired on either would fire on
    nearly every merge there is.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    pull_body = (
        "- `bin/docket arm` on this branch says `hold`: seven paths lie outside "
        "`docs/items`, so it is left unarmed for review.\r\n\r\n"
        "---\n_Generated by [Claude Code](https://claude.ai/code/session_01Qp)_"
    )
    squash_body = (
        "- `bin/docket arm` on this branch says `hold`: seven paths lie outside\n"
        "`docs/items`, so it is left unarmed for review.\n\n"
        "---\n_Generated by [Claude\nCode](https://claude.ai/code/session_01Qp)_" + appended
    )
    _install(monkeypatch, [("abc1234", "PL-DDYD: a title (#993)", squash_body)])
    _serve(monkeypatch, [[_pull(993, pull_body)]])

    assert _differing(pr_body_check.compare("origin/main")) == []


def test_silent_on_a_commit_hash_the_rewrite_remapped(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """`#375`'s shape: `main` quotes the rewritten hash, the pull request the one it replaced.

    22 bodies differ in nothing else, and `main`'s copy is the one that resolves.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#381)", "Landed in `954546a` (#375).")])
    _serve(monkeypatch, [[_pull(381, "Landed in `a575f8d` (#375).")]])

    assert _differing(pr_body_check.compare("origin/main")) == []


def test_silent_on_the_attribution_footer_alone(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """`#969`'s shape: the claude.ai footer on the pull request and not on `main`.

    It is attribution rather than reasoning, so a body missing only that has
    not said anything else.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(
        monkeypatch, [("abc1234", "PL-8PS6: a title (#969)", "Why.\n\nCo-authored-by: C <c@x>\n")]
    )
    _serve(
        monkeypatch,
        [
            [
                _pull(
                    969,
                    "Why.\n\n---\n_Generated by [Claude Code](https://claude.ai/code/session_01Dr)_",
                )
            ]
        ],
    )

    assert _differing(pr_body_check.compare("origin/main")) == []


@pytest.mark.parametrize(
    ("ours", "theirs"),
    [
        ("4506 passed, 1234567 bytes", "4506 passed, 1234568 bytes"),
        ("was deadbeef", "was cafebabe"),
        ("unaccounted=1.000000e+00 L", "unaccounted=1.500000e+00 L"),
        ("[10.1002/cphy.c100011]", "[10.1002/cphy.c100012]"),
    ],
    ids=["digits-only", "letters-only", "exponent", "dotted-identifier"],
)
def test_a_number_or_a_hex_word_is_not_taken_for_a_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path, ours: str, theirs: str
) -> None:
    """A hash is masked only where it holds a digit and a letter both.

    A changed count is reasoning, and masking it would pass a body that says
    something else as the same; a hash spelled in one class alone is a false
    positive a reader can dismiss instead.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", ours)])
    _serve(monkeypatch, [[_pull(768, theirs)]])

    assert _differing(pr_body_check.compare("origin/main")) == [768]


def test_a_trailer_quoted_inside_the_body_is_compared() -> None:
    """Only whole trailer lines at the end are GitHub's; anything else is the author's text.

    This repository's bodies discuss the trailer (`#493`, `#800`), so one
    naming it mid-sentence on the last line is a real shape: stripped from the
    pull request's side alone, it reads as a body that differs.
    """
    quoted = "Co-authored-by: A <a@example.com>\nwas lost from the subject.\n"
    named = "GitHub adds the trailer.\n\nIt appends a `Co-authored-by: ` line"

    assert pr_body_check.normalise(quoted) == (
        "Co-authored-by: A <a@example.com> was lost from the subject."
    )
    assert pr_body_check.normalise(named) == (
        "GitHub adds the trailer. It appends a `Co-authored-by: ` line"
    )
    assert pr_body_check.normalise(
        named + "\n\n---------\n\nCo-authored-by: C <c@x>\n"
    ) == pr_body_check.normalise(named)
    assert pr_body_check.normalise("Why.\n\nCo-authored-by: A <a@example.com>\n") == "Why."


def test_names_a_body_frozen_when_auto_merge_was_armed(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """`#834`'s shape: the squash is `auto_merge.commit_message`, the body edited after.

    Saying which it is tells the reader the mechanism - `PL-M7W1`'s frozen
    subject, arriving in the body - without a lookup. The armed message is in
    the shape the listing really returns it: hard-wrapped, with the footer
    wrapped inside and GitHub's trailer below, as on all six real cases. So the
    label is only reached if that message is normalised like the other two.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    armed = (
        "The second of the two shared-column attribution items on the\n"
        "v0.5.0 debt gate.\n\n---\n_Generated by [Claude\n"
        "Code](https://claude.ai/code/session_01Ab)_\n\n---------\n\n"
        "Co-authored-by: Claude <noreply@anthropic.com>\n"
    )
    edited = (
        "The last of the three shared-column attribution items on the v0.5.0 debt gate."
        "\n\n---\n_Generated by [Claude Code](https://claude.ai/code/session_01Ab)_"
    )
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#834)", armed)])
    _serve(monkeypatch, [[_pull(834, edited, armed=armed)]])

    lines = pr_body_check.compare("origin/main")

    assert _differing(lines) == [834]
    assert "auto-merge was armed with" in lines[1]


def test_names_a_body_that_is_only_githubs_trailer(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """`#325`'s shape, with a body on the pull request this time.

    The default mode asks for an empty body and a lone trailer is not one, so
    this is the loss both modes would otherwise pass. `#325` itself is silent,
    correctly: its pull request has no body either.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    trailer = "Co-authored-by: Claude <noreply@anthropic.com>\n"
    _install(
        monkeypatch,
        [
            ("abc1234", "PL-8PS6: a title (#768)", trailer),
            ("abc1235", "PL-QTN6: a title (#325)", trailer),
        ],
    )
    _serve(monkeypatch, [[_pull(768, "Why, at length."), _pull(325, None)]])

    lines = pr_body_check.compare("origin/main")

    assert _differing(lines) == [768]
    assert "carries only GitHub's trailer" in lines[1]
    assert pr_body_check.missing("origin/main") == []


def test_compare_leaves_an_empty_body_and_a_recovered_one_alone(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """An empty body is the default mode's to report, and a recovery file settles it.

    Reporting either here would name one loss twice, or name one whose
    reasoning is already in the checkout.
    """
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "770.md").write_text("recovered", encoding="utf-8")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(
        monkeypatch,
        [
            ("abc1234", "PL-8PS6: lost (#769)", ""),
            ("abc1235", "PL-8PS6: recovered (#770)", "An old copy."),
        ],
    )
    calls: list[str] = []
    _serve(monkeypatch, [[_pull(769, "Why."), _pull(770, "Why.")]], calls)

    lines = pr_body_check.compare("origin/main")

    assert _differing(lines) == []
    assert lines == [
        "pr-body: compared 0 squash commit(s) on origin/main; "
        "none differs from its pull request's body."
    ]
    assert calls == []


def test_a_listing_that_cannot_be_read_is_reported_not_passed(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """A comparison never made must not read like one that found nothing."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "Why.")])
    _serve(monkeypatch, [None])

    lines = pr_body_check.compare("origin/main")

    assert lines[0].startswith("pr-body: compared 0 squash commit(s)")
    assert lines[-1] == (
        "pr-body: 1 squash commit(s) not compared: "
        "the pull request listing could not be read at page 1."
    )


def test_the_listing_is_read_until_every_wanted_body_is_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """Ten requests cover the history, inside the 60 an hour GitHub allows without a token.

    Reading on past the oldest wanted pull request would spend that allowance
    for nothing, and stopping before it would leave commits uncompared.
    """
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(
        monkeypatch,
        [
            ("abc1234", "PL-8PS6: newer (#768)", "Same."),
            ("abc1235", "PL-8PS6: older (#650)", "Ours."),
        ],
    )
    calls: list[str] = []
    _serve(
        monkeypatch,
        [[_pull(768, "Same."), _pull(700, "Unwanted.")], [_pull(650, "Theirs.")], [_pull(1, "x")]],
        calls,
    )

    lines = pr_body_check.compare("origin/main")

    assert _differing(lines) == [650]
    assert len(calls) == 2
    assert "per_page=100" in calls[0]


def test_compare_is_its_own_mode_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path, capsys
) -> None:
    """Advisory like the default mode, for the same reason: a merge made it, not the branch."""
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", tmp_path / "pr-bodies")
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", "Ours.")])
    _serve(monkeypatch, [[_pull(768, "Theirs.")]])

    assert pr_body_check.main(["--compare"]) == 0
    printed = capsys.readouterr().out
    assert "#768" in printed
    assert "--recover" not in printed


# The record, written before the merge (`PL-979D`). What `--record` writes has
# to be exactly what `--check` accepts, so the two are tested as one path; a
# body edited after it was recorded has to be refused, or the file is a
# snapshot rather than the record; and a header has to say truthfully which of
# its two provenances it is.


def _git_serving(
    monkeypatch: pytest.MonkeyPatch,
    records: list[tuple[str, str, str]],
    shown: dict[str, str] | None = None,
    shallow: str = "false",
) -> None:
    """`_install`'s history, plus the head tree `--check` reads and the line `--anchors` does."""
    _install(monkeypatch, records)
    served = pr_body_check._git

    def fake(*args: str) -> str:
        if args[0] == "show":
            return (shown or {}).get(args[1].split(":", 1)[1], "")
        if args[:2] == ("rev-parse", "--is-shallow-repository"):
            return f"{shallow}\n"
        if args[0] == "rev-list":
            return "".join(f"{sha}\n" for sha, _, _ in records)
        return served(*args)

    monkeypatch.setattr(pr_body_check, "_git", fake)


def test_a_recorded_body_is_what_the_check_holds_the_pull_request_to(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The writer's file is the checker's input, so a format drift between them fails here.

    The body arrives with Windows line endings and trailing blank lines, as one
    edited in the browser does, and opens with the harness's own HTML comment,
    which is why the record carries no comment of its own.
    """
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    monkeypatch.setattr(pr_body_check, "today", lambda: "2026-09-26")
    body = "<!-- ccr-projects-attribution: {} -->\r\n| a | b |\r\n| --- | --- |\r\n\r\nWhy.\r\n\r\n"
    _install(monkeypatch, [])
    monkeypatch.setattr(
        pr_body_check, "fetch_pull", lambda slug, pr: {"state": "open", "body": body}
    )

    assert pr_body_check.record(1059) == 0
    written = (recovery / "1059.md").read_text(encoding="utf-8")
    assert written == (
        "---\npr: 1059\nrecorded: 2026-09-26\n---\n\n"
        "<!-- ccr-projects-attribution: {} -->\n| a | b |\n| --- | --- |\n\nWhy.\n"
    )

    _git_serving(monkeypatch, [], shown={"docs/pr-bodies/1059.md": written})
    monkeypatch.setenv("PR_NUMBER", "1059")
    monkeypatch.setenv("PR_BODY", body)
    assert pr_body_check.check() == 0


def test_a_body_edited_after_it_was_recorded_holds_the_merge(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`edited` re-runs the check, and this is the answer it has to give.

    A record that still passes an older body is the snapshot the rule exists to
    refuse: the merge would carry reasoning the tree does not hold.
    """
    held = "---\npr: 1059\nrecorded: 2026-09-26\n---\n\nThe first draft.\n"
    _git_serving(monkeypatch, [], shown={"docs/pr-bodies/1059.md": held})
    monkeypatch.setenv("PR_NUMBER", "1059")
    monkeypatch.setenv("PR_BODY", "The first draft, with a paragraph added.")

    assert pr_body_check.check() == 1
    err = capsys.readouterr().err
    assert "edited after it was recorded" in err
    assert "--record 1059" in err


def test_a_body_with_no_record_is_refused_and_an_empty_one_owes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Red from opening until the first record; a pull request with no body never is."""
    _git_serving(monkeypatch, [])
    monkeypatch.setenv("PR_NUMBER", "1059")
    monkeypatch.setenv("PR_BODY", "Why this change.")
    assert pr_body_check.check() == 1
    assert "is not in the tree" in capsys.readouterr().err

    monkeypatch.setenv("PR_BODY", "  \n")
    assert pr_body_check.check() == 0


def test_a_body_missing_from_the_environment_is_not_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    """The step always sets `PR_BODY`, so an unset one is a broken step, never a pass."""
    _git_serving(monkeypatch, [])
    monkeypatch.setenv("PR_NUMBER", "1059")
    monkeypatch.delenv("PR_BODY", raising=False)

    assert pr_body_check.check() == 1


def test_recording_an_emptied_body_removes_the_stale_record(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """A file left from before the body was emptied would record text nobody can see."""
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "1059.md").write_text("---\npr: 1059\nrecorded: 2026-09-25\n---\n\nOld.\n")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _install(monkeypatch, [])
    monkeypatch.setattr(
        pr_body_check, "fetch_pull", lambda slug, pr: {"state": "open", "body": None}
    )

    assert pr_body_check.record(1059) == 0
    assert not (recovery / "1059.md").exists()


@pytest.mark.parametrize(
    ("squash_body", "armed", "shape"),
    [
        ("", None, "empty"),
        ("Co-authored-by: Someone <someone@example.com>\n", None, "trailer-only"),
        ("The body as armed.\n", "The body as armed.", "armed-message"),
        ("Something else entirely.\n", None, "differs"),
        ("The body as it stands.\n", None, "matches"),
    ],
)
def test_recording_a_merged_pull_request_names_how_its_squash_copy_compares(
    monkeypatch: pytest.MonkeyPatch, tmp_path, squash_body: str, armed: str | None, shape: str
) -> None:
    """`PL-PNJF`: one case per shape, each named truthfully in a header dated when it was fetched.

    The old header said every recovered commit "landed with an empty message
    body", which was true of the one shape `--recover` wrote and false of the
    27 `--compare` found; and it claimed the body verbatim from the merge,
    where what the API serves is the body as it stands on the day (`PL-73G8`).
    """
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    monkeypatch.setattr(pr_body_check, "today", lambda: "2026-09-26")
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)
    _install(monkeypatch, [("abc1234", "PL-8PS6: a title (#768)", squash_body)])
    pull = {
        "state": "closed",
        "merged_at": "2026-09-20T00:00:00Z",
        "body": "The body as it stands.",
        "auto_merge": None if armed is None else {"commit_message": armed},
    }
    monkeypatch.setattr(pr_body_check, "fetch_pull", lambda slug, pr: pull)

    assert pr_body_check.record(768) == 0
    parsed = pr_body_check.parse_record((recovery / "768.md").read_text(encoding="utf-8"))
    assert parsed is not None
    header, body = parsed
    assert (header["squash"], header["recovered"], header["commit"]) == (
        shape,
        "2026-09-26",
        "abc1234",
    )
    assert "recorded" not in header
    assert body == "The body as it stands.\n"


@pytest.mark.parametrize(
    ("pull", "records"),
    [
        ({"state": "closed", "merged_at": None, "body": "Closed unmerged."}, []),
        ({"state": "closed", "merged_at": "2026-09-20T00:00:00Z", "body": "Not fetched here."}, []),
        (None, []),
    ],
    ids=["closed-without-merging", "squash-commit-not-here", "unreadable"],
)
def test_record_refuses_what_it_cannot_anchor_rather_than_writing_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path, pull: dict | None, records: list
) -> None:
    """A file here is read as the record, so a wrong one is worse than none."""
    recovery = tmp_path / "pr-bodies"
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    monkeypatch.setattr(pr_body_check, "queue_backlinks", dict)
    _install(monkeypatch, records)
    monkeypatch.setattr(pr_body_check, "fetch_pull", lambda slug, pr: pull)

    assert pr_body_check.record(768) == 1
    assert not (recovery / "768.md").exists()


def test_a_recovery_file_whose_commit_sha_no_longer_resolves_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-73G8`: an anchor a history rewrite left naming nothing fails, and says what it is now.

    The 2026-09-06 signing rewrite remapped every hash on `main` once, and
    `PL-TDBT` counted 30 unresolvable shas across the corpus with nothing
    reporting one as it was written. A record made before the merge has no
    anchor to check.
    """
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "768.md").write_text(f"---\npr: 768\ncommit: {'0' * 40}\n---\n\nBody.\n")
    (recovery / "769.md").write_text(f"---\npr: 769\ncommit: {'b' * 40}\n---\n\nBody.\n")
    (recovery / "1059.md").write_text("---\npr: 1059\nrecorded: 2026-09-26\n---\n\nBody.\n")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _git_serving(
        monkeypatch,
        [("a" * 40, "PL-8PS6: a title (#768)", ""), ("b" * 40, "PL-8PS6: another (#769)", "")],
    )

    assert pr_body_check.anchors("origin/main") == 1
    err = capsys.readouterr().err
    assert "768.md: commit 000000000000; its squash commit there is " + "a" * 40 in err
    assert "769.md" not in err
    assert "1059.md" not in err


def test_anchors_on_a_shallow_clone_say_nothing_was_checked(
    monkeypatch: pytest.MonkeyPatch, tmp_path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A clone cut short cannot tell a dangling anchor from one past its graft, so it says so."""
    recovery = tmp_path / "pr-bodies"
    recovery.mkdir()
    (recovery / "768.md").write_text(f"---\npr: 768\ncommit: {'0' * 40}\n---\n\nBody.\n")
    monkeypatch.setattr(pr_body_check, "RECOVERY_DIR", recovery)
    _git_serving(monkeypatch, [("a" * 40, "PL-8PS6: a title (#768)", "")], shallow="true")

    assert pr_body_check.anchors("origin/main") == 0
    assert "not checked" in capsys.readouterr().out
