"""Tests for `tools/open_pull_requests.py`, the forge half of `docket flight`.

And, through `--newest`, of `docket branch` and `docket arm` (`PL-8BR0`): the
same request asking what became of one branch's newest pull request, under the
same contract - exit 1 with nothing printed where it could not ask, exit 0 with
nothing printed where the forge answered that none was ever opened.

One property carries this file, and it is the reason the script exists rather
than the request living inside `docket`: **"could not look" and "looked, and
nothing is open" must never arrive as the same answer.** `docket flight` says
"every item closed, and no pull request is open" on the second and "every item
closed" alone on the first, so a script that exited 0 with an empty stdout when
the token was missing would have `flight` announce that finished work has
stalled on every branch waiting on review. The exit status is the whole
contract, so most of what is below asserts it.

`urlopen` is substituted rather than a server run, one level below the JSON, so
that the URL the script builds is itself under test - `per_page`, the `head`
filter and the `state` are what decide whether the answer is about the right
branches.
"""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.request

import open_pull_requests
import pytest

TOKEN = "gh-token-for-the-test"


def _payload(*entries: dict) -> str:
    return json.dumps(list(entries))


def _entry(number: int, head: str, title: str = "PL-K7QX: a thing") -> dict:
    return {"number": number, "title": title, "head": {"ref": head}}


@pytest.fixture
def _served(monkeypatch: pytest.MonkeyPatch):
    """Serve one body, and collect the URLs the script asked for."""
    urls: list[str] = []

    def serve(body: str | Exception):
        class _Response:
            def __enter__(self) -> io.BytesIO:
                assert isinstance(body, str)
                return io.BytesIO(body.encode())

            def __exit__(self, *exc: object) -> None:
                return None

        def _open(request: urllib.request.Request, timeout: float = 0) -> _Response:
            urls.append(request.full_url)
            if isinstance(body, Exception):
                raise body
            return _Response()

        monkeypatch.setenv("GH_TOKEN", TOKEN)
        monkeypatch.setattr(open_pull_requests.urllib.request, "urlopen", _open)
        return urls

    return serve


def test_the_branches_of_the_open_pull_requests_are_returned(_served) -> None:
    _served(_payload(_entry(841, "claude/one"), _entry(842, "claude/two")))
    found = open_pull_requests.open_pull_requests("owner/repo")
    assert found is not None
    assert [entry.head for entry in found] == ["claude/one", "claude/two"]
    assert [entry.number for entry in found] == [841, 842]


def test_a_repository_with_nothing_open_answers_an_empty_listing(_served) -> None:
    """Empty is an answer here, and the caller acts on it; only None is a refusal."""
    _served(_payload())
    assert open_pull_requests.open_pull_requests("owner/repo") == ()


def test_the_listing_asks_for_open_pull_requests_a_page_at_a_time(_served) -> None:
    urls = _served(_payload())
    open_pull_requests.open_pull_requests("owner/repo")
    assert urls == ["https://api.github.com/repos/owner/repo/pulls?state=open&per_page=100"]


def test_a_head_narrows_the_listing_to_one_branch(_served) -> None:
    urls = _served(_payload(_entry(841, "claude/one")))
    open_pull_requests.open_pull_requests("owner/repo", head="claude/one")
    assert urls == [
        "https://api.github.com/repos/owner/repo/pulls"
        "?state=open&per_page=1&head=owner%3Aclaude%2Fone"
    ]


def test_a_full_page_declines_rather_than_reporting_what_it_saw(_served) -> None:
    """A truncated listing cannot say a particular branch is absent.

    The caller's question is whether *this* branch has something open, and a
    listing that stopped at the page limit looks exactly like a complete one
    while being unable to answer it. Declining is the reading that is never
    wrong.
    """
    _served(_payload(*(_entry(index, f"claude/{index}") for index in range(100))))
    assert open_pull_requests.open_pull_requests("owner/repo") is None


def test_no_token_is_a_refusal_rather_than_an_empty_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert open_pull_requests.open_pull_requests("owner/repo") is None


@pytest.mark.parametrize(
    "failure",
    [
        urllib.error.URLError("no network"),
        urllib.error.HTTPError("u", 403, "forbidden", {}, None),  # type: ignore[arg-type]
        OSError("a proxy hung up"),
    ],
)
def test_a_forge_that_did_not_answer_is_a_refusal(_served, failure: Exception) -> None:
    _served(failure)
    assert open_pull_requests.open_pull_requests("owner/repo") is None


@pytest.mark.parametrize(
    "body",
    [
        "{}",
        "not json at all",
        json.dumps([{"number": 841, "title": "t"}]),
        json.dumps([{"number": 841, "title": "t", "head": "claude/one"}]),
        json.dumps([{"number": "841", "title": "t", "head": {"ref": "claude/one"}}]),
    ],
)
def test_a_body_the_api_has_promised_nothing_about_is_a_refusal(_served, body: str) -> None:
    """A shape this cannot read is a shape it must not summarize."""
    _served(body)
    assert open_pull_requests.open_pull_requests("owner/repo") is None


def test_the_command_prints_each_branch_and_its_number_and_exits_zero(
    _served, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _served(_payload(_entry(841, "claude/one"), _entry(842, "claude/two")))
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.main() == 0
    assert capsys.readouterr().out == "claude/one 841\nclaude/two 842\n"


def test_the_command_exits_non_zero_and_prints_nothing_when_it_could_not_look(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The contract `docket flight` reads: silence on exit 1 means unasked."""
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    monkeypatch.setattr(open_pull_requests, "open_pull_requests", lambda *a, **k: None)
    assert open_pull_requests.main() == 1
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("url", ["https://gitlab.com/o/r.git\n", "/srv/mirrors/bare.git\n", "\n"])
def test_a_remote_that_is_not_github_s_is_not_guessed_at(
    monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    """Not an error: a checkout with another remote, or none, has nothing to look up."""
    monkeypatch.setattr(open_pull_requests, "_git", lambda args, url=url: url)
    assert open_pull_requests.repo_slug() is None


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/owner/repo.git\n",
        "https://github.com/owner/repo\n",
        "git@github.com:owner/repo.git\n",
        "ssh://git@github.com/owner/repo.git\n",
    ],
)
def test_the_slug_is_read_from_every_spelling_of_the_remote(
    monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    """All four reach this in practice: a `.gitconfig` rewriting ssh to https
    means which one arrives depends on when the remote is read."""
    monkeypatch.setattr(open_pull_requests, "_git", lambda args: url)
    assert open_pull_requests.repo_slug() == "owner/repo"


@pytest.mark.parametrize(
    "url",
    [
        "https://x-access-token:abc@github.com/owner/repo.git\n",
        "https://github.com/owner/repo.git/\n",
        "ssh://git@github.com:22/owner/repo.git\n",
    ],
)
def test_repo_slug_reads_a_token_bearing_url(monkeypatch: pytest.MonkeyPatch, url: str) -> None:
    """The three shapes the four parsers disagreed on read alike, through `vcs.github_slug`.

    The token-bearing URL was None here and `owner/repo` to the other three,
    which `left_behind_check` and `pr_title_check` inherit (`PL-2TV9`).
    """
    monkeypatch.setattr(open_pull_requests, "_git", lambda args: url)
    assert open_pull_requests.repo_slug() == "owner/repo"


# --- `--newest`: what became of a branch's newest pull request (PL-8BR0) -----

#: The head a merged pull request's listing names, as GitHub froze it.
HEAD_SHA = "46620e20" + "7" * 32


def _newest(number: int, state: str, merged_at: str | None, sha: str = HEAD_SHA) -> dict:
    return {
        "number": number,
        "state": state,
        "merged_at": merged_at,
        "head": {"ref": "claude/one", "sha": sha},
    }


def test_the_newest_asks_every_state_for_that_branch_into_that_base_newest_first(_served) -> None:
    """The listing `left_behind_check.github_lookup` makes: one result, the newest created."""
    urls = _served(_payload())
    open_pull_requests.newest_pull_request("owner/repo", "claude/one", "main")
    assert urls == [
        "https://api.github.com/repos/owner/repo/pulls?state=all&head=owner%3Aclaude%2Fone"
        "&base=main&sort=created&direction=desc&per_page=1"
    ]


@pytest.mark.parametrize(
    ("state", "merged_at", "said"),
    [
        ("closed", "2026-09-25T10:00:00Z", "merged"),
        ("closed", None, "closed"),
        ("open", None, "open"),
    ],
)
def test_the_newest_reads_a_merge_from_merged_at_and_otherwise_the_state(
    _served, state: str, merged_at: str | None, said: str
) -> None:
    """GitHub closes a merged pull request, so `state` alone cannot tell a merge from a refusal."""
    _served(_payload(_newest(841, state, merged_at)))
    assert open_pull_requests.newest_pull_request("owner/repo", "claude/one", "main") == (
        open_pull_requests.NewestPullRequest(number=841, state=said, head=HEAD_SHA),
    )


def test_the_newest_prints_its_number_state_and_head_and_exits_zero(
    _served, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _served(_payload(_newest(841, "closed", "2026-09-25T10:00:00Z")))
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.main(["--newest", "claude/one", "main"]) == 0
    assert capsys.readouterr().out == f"841 merged {HEAD_SHA}\n"


def test_a_branch_nothing_was_opened_from_answers_with_nothing_and_exits_zero(
    _served, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The forge answered, so this is a fact the caller acts on, not a refusal."""
    _served(_payload())
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.newest_pull_request("owner/repo", "claude/one", "main") == ()
    assert open_pull_requests.main(["--newest", "claude/one", "main"]) == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "failure",
    [
        urllib.error.URLError("no network"),
        urllib.error.HTTPError("u", 403, "forbidden", {}, None),  # type: ignore[arg-type]
        "{}",
    ],
    ids=["no-network", "refused", "not-a-listing"],
)
def test_the_newest_exits_non_zero_and_prints_nothing_when_it_could_not_ask(
    _served,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    failure: str | Exception,
) -> None:
    """Printed nothing with exit 0 would read as "never opened", and `branch` would believe it."""
    _served(failure)
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.main(["--newest", "claude/one", "main"]) == 1
    assert capsys.readouterr().out == ""


def test_the_newest_without_a_token_exits_non_zero(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.main(["--newest", "claude/one", "main"]) == 1
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "entry",
    [
        "not an object",
        {**_newest(841, "open", None), "number": "841"},
        {**_newest(841, "open", None), "state": "merged"},
        {key: value for key, value in _newest(841, "closed", None).items() if key != "merged_at"},
        {**_newest(841, "closed", None), "merged_at": 1},
        {**_newest(841, "open", None), "head": "claude/one"},
        _newest(841, "open", None, sha=""),
        {**_newest(841, "open", None), "head": {"ref": "claude/one"}},
    ],
    ids=["entry", "number", "state", "no-merged-at", "merged-at", "head", "empty-sha", "no-sha"],
)
def test_a_newest_entry_the_api_has_promised_nothing_about_is_a_refusal(
    _served, entry: object
) -> None:
    """A missing `merged_at` most of all: read as "not merged", it is the answer being fixed."""
    _served(json.dumps([entry]))
    assert open_pull_requests.newest_pull_request("owner/repo", "claude/one", "main") is None
