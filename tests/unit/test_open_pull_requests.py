"""Tests for `tools/open_pull_requests.py`, the forge half of `docket flight`.

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


def test_the_command_prints_one_branch_per_line_and_exits_zero(
    _served, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _served(_payload(_entry(841, "claude/one"), _entry(842, "claude/two")))
    monkeypatch.setattr(open_pull_requests, "repo_slug", lambda: "owner/repo")
    assert open_pull_requests.main() == 0
    assert capsys.readouterr().out == "claude/one\nclaude/two\n"


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
