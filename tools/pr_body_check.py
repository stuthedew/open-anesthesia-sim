"""Report where a squash commit lost its pull request's body, and recover it into the tree.

`main` is squash-merged, `allow_merge_commit` is false, and the repository is
configured `squash_merge_commit_title: PR_TITLE` / `squash_merge_commit_message:
PR_BODY`, so each squash commit carries a copy of its pull request's body. The
body is the densest record this project produces: what was refused, what was
measured, what was filed, and why. **The squash commit's body on `main` is the
record of it, and `docs/pr-bodies/<N>.md` holds only a body a merge dropped**,
recovered in one batch at each release (project owner, 2026-09-26, ratified,
over keeping `PL-979D`'s per-pull-request record behind `pr-title`'s required
check, and over recording every body in one batch at each release; `PL-3PH2`).
Accepted as properties of that record rather than defects: a hard-wrapped table
(`PL-BZHX`), a body edited after auto-merge was armed landing as armed
(`PL-M7W1`), and a merge that sends a different non-empty message (`#744`),
which nothing detects offline and `--compare` measures by hand.

**`PL-979D`'s record stood from 2026-09-25 to 2026-09-26, and measurement
retired it.** `--record` wrote each open pull request's body into the tree and
`--check`, a step of `pr-title.yml`'s required job, held the merge until the
head held it, so the squash body was only a copy. It was built against the
27.4% loss below, which came from one merge client, the GitHub iPhone app. The
owner stopped merging there on 2026-09-22; of the 149 squash commits merged
after `#918` up to `#1068`, 2 lost a body (`#1015` and `#1044`, both
recovered), and none of the 39 after it. In its first day the record produced
four items of its own (`PL-F6MM`, `PL-K9XQ`, `PL-7VWK`, `PL-X2XP`). The files
it wrote stay, with their `recorded:` header.

**What `--recover` writes** (`PL-PNJF`, `PL-73G8`): `pr:`, then `recovered:`,
the date it was fetched, because the API serves the body as it stands that day
rather than as it stood at the merge; then `commit:`, `merged:`, `items:`,
`subject:`, and `squash: empty`, the one shape it recovers. No HTML comment
sits above the body: this repository's bodies open with the harness's own
`<!-- ccr-projects-attribution ... -->` marker, and a reader could not tell a
tool's comment from the body's. The 201 files recovered before `PL-979D` keep
their older header and comment, forward only; the commit that added each one
dates its fetch.

**`--anchors` checks that every recovered file's `commit:` is a first-parent
commit of the default branch** (`PL-73G8`). It is the one field tying a
recovered body to the tree, and the 2026-09-06 signing rewrite remapped every
hash once already. It runs in `make check`, fails naming each file and the
squash commit its number resolves to now, and on a shallow clone or with no
default branch says it checked nothing.

**What follows is the history behind that record.** The squash copy did not
always arrive. Measured 2026-09-20 over all 805 first-parent commits on `main`:
**187 of the 683 squash commits, 27.4%, carry a zero-length body**, and every
one of those 187 pull requests *had* a body on GitHub - 763,224 characters of
reasoning that exist only outside the repository. The loss is silent from every direction
anyone looks: the pull request still reads correctly on GitHub, and `git log`
shows a subject line that looks deliberate. `PL-843V`.

**The mechanism is known; the client sending it is not, and this check depends
on neither.** The merge request is submitted with an *explicitly empty*
`commit_message` string rather than with the field absent. GitHub honours `""`
literally, skips the repository default, and suppresses the `Co-authored-by`
trailer with it - which is why these bodies are zero-length rather than the 46
characters a trailer alone leaves behind. Direct evidence: of the merged pull
requests whose `auto_merge` object survived the merge, **9 of 9 in the affected
group carry `auto_merge.commit_message == ""` against 0 of 73 in the
unaffected** - a perfect separator, though it accounts for only 9 of the 187.

**What sends it is a per-sitting property, which is the signature of a merge
client rather than of anything about the pull request.** Merges less than 60
seconds apart agree on affected-or-not 98.3% of the time against 60.2% by
chance; 15-minute sittings of three or more merges are label-pure 80.9% of the
time against 25.0% expected. Owner-local hour separates at permutation
p = 5e-5 even shuffling within each day - 05h is 15/15 affected and 17h 27/38,
while 00h, 14h, 22h and 23h hold 97 merges and zero - and the band replicates
blind on a held-out second half, 45.9% against 11.8%. Affected merges also land
a median 483 seconds after CI goes green against 70 seconds, which reads as
away-from-desk against at-desk. GitHub records no client identity either way
(`performed_via_github_app` is null and `committer.login` is `web-flow` on all
683), so the client stays an inference however strong the timing is.

**Ruled out by measurement over the full population**, not a sample: pull
request body content (30 structural features; largest gap 8.0 points, rank AUC
0.472 on length), the merge actor (`merged_by` is this account on all 683), a
body written after the merge (2 of 187, max 364 s), and a later history
rewrite - `main` was rewritten once when commit signing was switched on
2026-09-06, and of the original GitHub-created merge commits that still exist
the body is empty in 74/74 of the affected and non-empty in 116/116 of the
rest, so the loss originates at merge time in GitHub's own commit object.

So prevention needed a change of merge client, which cannot be enforced from
the tree; the owner made it by hand on 2026-09-22. For a merge that drops a
body all the same, detection plus repair is what this tool can do.

**The default mode reads git and the filesystem, never the network.** The rule
is exact: a first-parent commit on the default branch whose subject ends in
`(#N)`, whose message body is empty, and for which `docs/pr-bodies/<N>.md` does
not exist. That predicate was checked against the whole history - the 20
body-less commits it must *not* fire on are the 2026-08 bootstrap commits and
the old `Merge pull request #N from ...` merges, and neither shape ends in
`(#N)`. `allow_merge_commit` is now false, so no new commit of that second
shape can appear.

**Repair is a separate mode, because it needs the network and detection must
not.** `--recover` fetches each missing body from the public API - no token,
like `tools/main_ci_status.py`, since the repository is public - and writes it
under `docs/pr-bodies/`. One file per pull request, which is the shape
`docs/items/` already uses for 1,378 records and for the reason recorded in
`docs/dead-ends.md`: a single shared document serializes every writer, and this
project runs many concurrent branches.

**A body can also arrive and say something else, and `--compare` reports that
one** (`PL-Y1W0`). An empty body is decidable offline; a body that differs from
the pull request's is not, because only GitHub holds the other copy - so it is
a third mode, and it reads the network. Measured 2026-09-24 over all 681 squash
commits whose body held more than GitHub's trailer: **27 say something other
than their pull request**. Six are exactly `auto_merge.commit_message`, the
body as it stood when auto-merge was armed, with the pull request edited after
it - the body version of `PL-M7W1`'s frozen subject. The other 21 carry no
surviving `auto_merge` object: some bodies were edited after the merge (`#466`
and `#522` add a note saying so), and some merges were sent a shorter message
of their own (`#744` landed a 464-character message where the pull request's
body is 3,507).
Nothing offline could have seen any of them, and `PL-WFFX` was closed on this
tool's reading, which could not either. A squash body that differs is
accepted as a property of the record (`PL-3PH2`), so `--compare` is a hand-run
measurement and nothing runs it as a check.

**A plain equality test would report 679 of the 681, so both sides are
normalised the same way first, and each step is here because a measurement
needed it.** GitHub appends a `Co-authored-by` trailer to 670 of the 681, 470
of them after a `---------` line and the rest directly. The squash message
arrives hard-wrapped: 651 of the 654 that match differ in whitespace, and 653
of 654 still match with whitespace collapsed only inside paragraphs, their
breaks kept, so all whitespace is compared as a single space. The 2026-09-06 signing rewrite
remapped the abbreviated commit hashes quoted in messages, while the pull
request still quotes the old ones: 22 bodies differ in nothing else, and
`main`'s copy is the one whose hashes resolve, so a token of 7 to 40 hex
characters that contains both a digit and a letter compares equal to any
other. The claude.ai
attribution footer appears on one side only in `#969`, and is attribution
rather than reasoning. What these steps cannot see is a difference made only
of whitespace, or only of one commit hash replaced by another.

The bodies come from the closed-pull-request listing, 100 to a request, so the
whole history is about ten requests: inside the 60 an hour GitHub allows
without a token, which this tool does not read. A listing that fails partway
is reported with the number of commits left uncompared, not treated as a
clean result.

**Advisory, never a hard failure, and that is a considered refusal rather than
timidity.** The condition is created by a *merge*, so the branch running a
check is never the branch that caused it; failing that branch would block
unrelated work for a defect it did not introduce and could not have prevented.
It would also be unsatisfiable offline, since the remedy needs the API. What
the advisory buys is that the loss becomes visible while the body is still
retrievable - the pull request could be edited, or the repository migrated, and
then it is gone for good.

**It runs at each release rather than at session start or in `make check`,
and the reason is about when a session may act rather than about cost.** The
remedy is a network fetch and a commit of files outside the current item's
declared `touches`, which `CLAUDE.md`'s fix-now rule forbids inline and its
housekeeping rule says must be filed first. In `make check` this advisory would
fire at the one moment a session may do nothing about it, and at session start,
where it ran until `PL-3PH2`, it fired in every session between a drop and its
recovery with nothing that session should do. Either way it trains a reader to
skim the region a real one appears in, which is the defect `CLAUDE.md` names.
A release is already a commit across the tree, so the recovered files ride its
pull request (`.claude/skills/docket/modes/release.md`). This reads the default
branch's ref and fetches nothing, so the release fetches first.

**The modes run by hand always print a verdict, because a release step reads
silence as a clean history.** A checkout with no readable default branch says
it checked nothing, and the default mode on a shallow one says only the
commits it holds were read. Even so, the verdict covers the refs in this
checkout: it surfaces a loss, and never certifies that none occurred.

**Deliberately not decided here: whether a recovered body is any good.** This
tool asks whether the reasoning is present in the checkout, never whether it
was worth keeping. A body is recorded verbatim, attribution footers and all,
because it is a historical record and editing it would make it a worse one.

Standard library only, parsing at the 3.11 floor `tools/ruff.toml` sets, so a
bare checkout with no virtualenv can run it.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.store import ID_PATTERN  # noqa: E402
from docket.vcs import default_base, github_slug, resolved, subject_pull_request  # noqa: E402

#: Relative, as a message names a file; `RECOVERY_DIR` is where they are read.
RECORD_PATH = "docs/pr-bodies"
RECOVERY_DIR = ROOT / RECORD_PATH
API = "https://api.github.com"
TIMEOUT_S = 15

#: Separates the two records inside one recovery file. `---` on its own line is
#: YAML frontmatter, which is what `docs/items/` uses, so a reader meeting one
#: of these files already knows the convention.
FRONT_MATTER = "---"

#: What GitHub appends to a squash body: `Co-authored-by` trailers, after a
#: `---------` line or directly after a blank one - both shapes are on `main`.
#: Anchored to the end and to the start of each line, so a trailer quoted
#: inside the body, or named mid-sentence on its last line, is compared.
APPENDED_TRAILER_RE = re.compile(
    r"(?:^-{9}\n)?(?:^[ \t]*\n)*(?:^Co-authored-by: [^\n]*(?:\n|\Z))+\s*\Z",
    re.IGNORECASE | re.MULTILINE,
)

#: The attribution footer the claude.ai server appends to a pull request body,
#: matched after whitespace is collapsed, since the squash copy is wrapped
#: inside it (`[Claude` / `Code]`).
FOOTER_RE = re.compile(r"(?:\s*---)?\s*_Generated by \[Claude Code\]\([^)]*\)_\s*\Z")

#: An abbreviated commit hash, as the 2026-09-06 rewrite remapped them. A digit
#: *and* a letter are both required, so a plain number and a hex-spelled word
#: are never masked, and neither is a token straight after a dot: the
#: `000000e` in `1.000000e+00` and the `c100011` in a DOI's `cphy.c100011`
#: both occur in bodies here and are figures, not hashes. A hash after a dot,
#: as in `a1b2c3d..e4f5a6b`, then shows up as a difference, which a reader can
#: dismiss, rather than a figure that changed passing as the same.
ABBREVIATED_HASH_RE = re.compile(r"(?<!\.)\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")

#: The closed-pull-request listing gives 100 bodies to a request. A listing that
#: never returns an empty page must still end, and this repository is an order
#: of magnitude short of the bound.
PER_PAGE = 100
MAX_PAGES = 100

#: Written in place of a body where the pull request genuinely has none. The
#: file has to exist so the advisory can clear - without it the check would
#: report a loss that no run could ever repair - and it has to say that it is
#: a tombstone rather than a recovery, so a reader does not take the silence
#: for a recovered record.
TOMBSTONE = (
    "This pull request has no body on GitHub, so the squash commit lost "
    "nothing.\nThere is nothing to recover; this file records that the "
    "question was asked\nand answered, so the advisory does not report it "
    "again."
)


def _git(*args: str) -> str:
    """Run git in the repository root, returning stdout, or "" on any failure."""
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=TIMEOUT_S, check=True, cwd=ROOT
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def default_branch_ref() -> str | None:
    """Name a ref for the default branch: `docket`'s own answer, `vcs.default_base`.

    It prefers the remote's copy and knows a default named `master`, which the
    `origin/main`-then-`main` list spelled here before did not (`PL-GNCB`). A
    bare or offline checkout may have only a local branch; a shallow CI
    checkout may have none deep enough to read, and `default_base` then answers
    with a ref nothing established, which is None here because every caller
    treats that as "say nothing".
    """
    base = default_base(ROOT, runner=lambda args, _root: _git(*args))
    return str(base) if resolved(base) else None


def squash_commits(ref: str) -> list[tuple[str, int, str, str]]:
    """Every first-parent squash commit on `ref`, as (sha, pr, subject, body)."""
    #: `%x00` between fields and `%x01` between records, because a subject may
    #: contain anything and a body certainly contains newlines.
    out = _git("log", ref, "--first-parent", "--format=%H%x00%s%x00%b%x01")
    rows: list[tuple[str, int, str, str]] = []
    for record in out.split("\x01"):
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split("\x00")
        if len(parts) != 3:
            continue
        sha, subject, body = parts
        # The squash shape alone: `Merge pull request #101 from ...`, the
        # pre-2026-08-31 merge shape, legitimately carries no body.
        named = subject_pull_request(subject)
        if named is None or not named.squash:
            continue
        rows.append((sha, named.number, subject, body))
    return rows


def recovered() -> set[int]:
    """Pull request numbers already recorded under `docs/pr-bodies/`."""
    if not RECOVERY_DIR.is_dir():
        return set()
    found: set[int] = set()
    for path in RECOVERY_DIR.glob("*.md"):
        if path.stem.isdigit():
            found.add(int(path.stem))
    return found


def missing(ref: str) -> list[tuple[str, int, str]]:
    """Squash commits with an empty body and no recovery file, newest first."""
    have = recovered()
    return [
        (sha, pr, subject)
        for sha, pr, subject, body in squash_commits(ref)
        if not body.strip() and pr not in have
    ]


def repo_slug() -> str | None:
    """`owner/repo` from origin's URL, or None if it is not a GitHub remote (`vcs.github_slug`)."""
    return github_slug(_git("remote", "get-url", "origin"))


#: `fetch_body` answers in three states, and the difference decides whether a
#: file is written. A body is recorded; `NO_BODY` means the pull request was
#: read and genuinely has none, which is permanent and gets a tombstone; `None`
#: means the read itself failed - rate limit, outage, no network - which is
#: transient and must leave the advisory standing. Collapsing the last two
#: would either nag forever about a body that cannot exist, or silence the
#: check on a body that does.
NO_BODY = object()


def _get_json(url: str) -> object | None:
    """GET one GitHub API URL and parse it, or None if the read failed.

    Unauthenticated, for the reason `tools/main_ci_status.py` gives: the
    repository is public, so no token is needed, which keeps this runnable from
    a bare checkout and keeps a credential out of it.
    """
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "pr-body-check"}
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload: object = json.load(response)
    except (OSError, urllib.error.URLError, ValueError, TimeoutError):
        return None
    return payload


def fetch_body(slug: str, pr: int) -> str | object | None:
    """The pull request's body, `NO_BODY` if it has none, or None if unreadable."""
    payload = _get_json(f"{API}/repos/{slug}/pulls/{pr}")
    if not isinstance(payload, dict):
        return None
    body = payload.get("body")
    if isinstance(body, str) and body.strip():
        return body
    #: The pull request was read and has no body. `#325` is the live example:
    #: `body` is null on GitHub, and its squash commit escaped this check only
    #: because GitHub left the 46-character `Co-authored-by` trailer behind.
    return NO_BODY


class Listed(NamedTuple):
    """One pull request as the closed-pull-request listing reports it."""

    body: str | None
    #: `auto_merge.commit_message`: the message auto-merge was armed with, which
    #: survives the merge on some pull requests and not on others.
    armed_message: str | None


def normalise(body: str | None) -> str:
    """A body as `--compare` reads it, with what GitHub and the rewrite changed taken out.

    Applied to both sides alike, so a step can hide a difference but never make
    one. The module docstring gives the measurement behind each step.
    """
    text = APPENDED_TRAILER_RE.sub("", (body or "").replace("\r\n", "\n"))
    text = FOOTER_RE.sub("", " ".join(text.split()))
    return ABBREVIATED_HASH_RE.sub("<hash>", text)


def comparable(ref: str) -> list[tuple[str, int, str]]:
    """Squash commits `--compare` reads, newest first, as (sha, pr, body).

    Those with a body on `ref` and no recovery file. An empty body is the
    default mode's to report, and a recovery file already puts the pull
    request's own body in the checkout.
    """
    have = recovered()
    return [
        (sha, pr, body)
        for sha, pr, _, body in squash_commits(ref)
        if body.strip() and pr not in have
    ]


def listed_bodies(slug: str, wanted: set[int]) -> tuple[dict[int, Listed], str | None]:
    """The listing's entry for each wanted pull request, and why reading stopped short.

    The reason is None when the listing was read until every wanted pull request
    was found or the listing ran out; otherwise it says where reading stopped,
    so a caller reports what went uncompared rather than passing it as equal.
    """
    found: dict[int, Listed] = {}
    for page in range(1, MAX_PAGES + 1):
        if wanted <= found.keys():
            return found, None
        payload = _get_json(
            f"{API}/repos/{slug}/pulls?state=closed&sort=created&direction=desc"
            f"&per_page={PER_PAGE}&page={page}"
        )
        if not isinstance(payload, list):
            return found, f"the pull request listing could not be read at page {page}"
        if not payload:
            return found, None
        for entry in payload:
            number = entry.get("number") if isinstance(entry, dict) else None
            if number not in wanted:
                continue
            auto = entry.get("auto_merge")
            armed = auto.get("commit_message") if isinstance(auto, dict) else None
            found[number] = Listed(entry.get("body"), armed if isinstance(armed, str) else None)
    return found, f"the pull request listing ran past {MAX_PAGES} pages"


def verdict(squash_body: str, listed: Listed) -> str | None:
    """Why a squash body is not its pull request's body, or None where it is."""
    ours = normalise(squash_body)
    theirs = normalise(listed.body)
    if ours == theirs:
        return None
    if not ours:
        #: `missing()` asks for an empty body, and GitHub's trailer alone is not
        #: empty: `#325` escaped it that way, though its pull request had no body.
        return "carries only GitHub's trailer"
    if listed.armed_message is not None and normalise(listed.armed_message) == ours:
        return "is the body auto-merge was armed with, and the pull request was edited after"
    return "differs"


def compare(ref: str) -> list[str]:
    """The `--compare` report, as the lines to print."""
    slug = repo_slug()
    if slug is None:
        return ["pr-body: origin is not a GitHub remote; nothing to compare against."]
    commits = comparable(ref)
    listed, short = listed_bodies(slug, {pr for _, pr, _ in commits})
    report: list[str] = []
    unread = 0
    for sha, pr, body in commits:
        entry = listed.get(pr)
        if entry is None:
            unread += 1
            continue
        reason = verdict(body, entry)
        if reason is not None:
            report.append(
                f"  #{pr} ({sha[:8]}) {reason}: {len(normalise(body)):,} characters compared "
                f"on {ref}, {len(normalise(entry.body)):,} on the pull request"
            )
    compared = len(commits) - unread
    if report:
        head = (
            f"pr-body: {len(report)} of {compared} squash commit(s) on {ref} say something "
            f"other than their pull request's body:"
        )
    else:
        head = (
            f"pr-body: compared {compared} squash commit(s) on {ref}; "
            f"none differs from its pull request's body."
        )
    tail = []
    if unread:
        why = short or "the pull request listing did not include them"
        tail.append(f"pr-body: {unread} squash commit(s) not compared: {why}.")
    return [head, *report, *tail]


def queue_backlinks() -> dict[int, set[str]]:
    """Map each pull request number to the items whose `pr:` field names it.

    Built once and reused, rather than per pull request: the queue is 1,378
    files, and asking it 187 times is 257,000 reads for an answer that does not
    change between them.
    """
    links: dict[int, set[str]] = {}
    items_dir = ROOT / "docs" / "items"
    if not items_dir.is_dir():
        return links
    for path in items_dir.glob("*.md"):
        head = path.read_text(encoding="utf-8")[:2000]
        pr_match = re.search(r"^pr:\s*(\d+)\s*$", head, re.M)
        id_match = re.search(r"^id:\s*(\S+)", head, re.M)
        if pr_match and id_match:
            links.setdefault(int(pr_match.group(1)), set()).add(id_match.group(1))
    return links


def item_ids(subject: str, pr: int, backlinks: dict[int, set[str]]) -> list[str]:
    """Item ids for a pull request, from its subject and from the queue's own `pr:`.

    Both sources, because neither is complete: a release commit names no item
    at all, and an item closed by a rider may never lead the subject. Measured
    over the 187: the subject alone leaves 50 without an id, the `pr:` field
    alone leaves 4 - the four release commits - and together they leave the
    same 4.
    """
    found = set(re.findall(ID_PATTERN, subject))
    found.update(backlinks.get(pr, set()))
    return sorted(found)


def today() -> str:
    """The UTC date a record or recovery is written on, as its header states it."""
    return datetime.now(UTC).date().isoformat()


def as_recorded(body: str) -> str:
    """A body as a recovered file holds it: line endings and the end cut, nothing inside.

    The file is a historical record, and the whitespace collapse `normalise()`
    makes for a comparison would make it a worse one.
    """
    return body.replace("\r\n", "\n").rstrip()


def _write(pr: int, header: list[str], body: str) -> Path:
    """Write `docs/pr-bodies/<pr>.md`: front matter, one blank line, the body."""
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    path = RECOVERY_DIR / f"{pr}.md"
    lines = [FRONT_MATTER, *header, FRONT_MATTER, "", ""]
    path.write_text("\n".join(lines) + as_recorded(body) + "\n", encoding="utf-8")
    return path


def write_recovery(
    sha: str,
    pr: int,
    subject: str,
    body: str,
    merged: str,
    backlinks: dict[int, set[str]],
    squash: str,
    recovered_on: str,
) -> Path:
    """A merged pull request's body, fetched on `recovered_on`, anchored to its squash commit."""
    ids = item_ids(subject, pr, backlinks)
    header = [
        f"pr: {pr}",
        f"recovered: {recovered_on}",
        f"commit: {sha}",
        f"merged: {merged}",
        f"items: {', '.join(ids) if ids else '(none)'}",
        f"subject: {subject}",
        f"squash: {squash}",
    ]
    return _write(pr, header, body)


def parse_record(text: str) -> tuple[dict[str, str], str] | None:
    """A record's front matter and body, or None where it opens with no front matter."""
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0] != FRONT_MATTER or FRONT_MATTER not in lines[1:]:
        return None
    end = lines.index(FRONT_MATTER, 1)
    header: dict[str, str] = {}
    for line in lines[1:end]:
        key, colon, value = line.partition(":")
        if colon:
            header[key.strip()] = value.strip()
    rest = lines[end + 1 :]
    #: The one blank line `_write` puts after the front matter, and no more, so
    #: a body that itself opens with a blank line survives the round trip.
    return header, "\n".join(rest[1:] if rest[:1] == [""] else rest)


def _shown(path: Path) -> Path:
    """`path` relative to the repository where it is inside it, as a message names it.

    `relative_to` raises where the recovery directory is not under the root,
    which is only ever a test's temporary directory, and a progress line is not
    worth an exception either way.
    """
    return path.relative_to(ROOT) if path.is_relative_to(ROOT) else path


def recover(ref: str) -> int:
    """Fetch and record every missing body. Returns the number written."""
    slug = repo_slug()
    if slug is None:
        print("pr-body: origin is not a GitHub remote; nothing to recover from.", file=sys.stderr)
        return 0
    backlinks = queue_backlinks()
    written = 0
    for sha, pr, subject in missing(ref):
        body = fetch_body(slug, pr)
        if body is None:
            print(f"pr-body: #{pr} unreadable from the API; left for a later run.", file=sys.stderr)
            continue
        merged = _git("log", "-1", "--format=%cs", sha).strip() or "unknown"
        if body is NO_BODY:
            write_recovery(sha, pr, subject, TOMBSTONE, merged, backlinks, "empty", today())
            print(f"  #{pr} has no body on GitHub either; recorded as nothing to recover")
            written += 1
            continue
        assert isinstance(body, str)
        path = write_recovery(sha, pr, subject, body, merged, backlinks, "empty", today())
        print(f"  recovered #{pr} -> {_shown(path)} ({len(body):,} chars)")
        written += 1
    return written


def anchors(ref: str | None) -> int:
    """`--anchors`: every recovered file's `commit:` must be on `ref`'s first-parent line."""
    shallow = _git("rev-parse", "--is-shallow-repository").strip()
    line = (
        set(_git("rev-list", "--first-parent", ref).split())
        if ref and shallow == "false"
        else set()
    )
    if not line:
        print("pr-body: recovery anchors not checked: no full default branch is readable here.")
        return 0
    stray: list[tuple[str, str, str]] = []
    for path in sorted(RECOVERY_DIR.glob("*.md")) if RECOVERY_DIR.is_dir() else []:
        parsed = parse_record(path.read_text(encoding="utf-8"))
        sha = parsed[0].get("commit", "") if parsed else ""
        if sha and sha not in line:
            stray.append((path.name, parsed[0].get("pr", path.stem) if parsed else path.stem, sha))
    if not stray:
        return 0
    now = {str(pr): sha for sha, pr, _, _ in squash_commits(ref or "")}
    print(
        f"pr-body: {len(stray)} recovered file(s) name a `commit:` that is not on {ref}'s "
        f"first-parent line, so nothing anchors the body to the tree:",
        file=sys.stderr,
    )
    for name, pr, sha in stray:
        fix = f"its squash commit there is {now[pr]}" if pr in now else "no squash commit names it"
        print(f"  {RECORD_PATH}/{name}: commit {sha[:12]}; {fix}", file=sys.stderr)
    print("  Replace each `commit:` with the squash commit named, and commit.", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    """Run the mode `argv` names.

    The default mode, `--recover` and `--compare` report and always exit 0,
    since a merge made what they find rather than the branch that runs them.
    `--anchors` exits 1 where it fails, because `make check` rests on it.
    """
    ref = default_branch_ref()
    if "--anchors" in argv:
        return anchors(ref)
    if ref is None:
        print("pr-body: no default branch is readable here; nothing checked.")
        return 0

    if "--recover" in argv:
        written = recover(ref)
        print(f"pr-body: recovered {written} body/bodies.")
        return 0

    if "--compare" in argv:
        print("\n".join(compare(ref)))
        return 0

    gaps = missing(ref)
    if not gaps:
        shallow = _git("rev-parse", "--is-shallow-repository").strip() == "true"
        read = "; this clone is shallow, so only the commits it holds were read" if shallow else ""
        print(f"pr-body: no squash commit on {ref} lost its body without a recovered file{read}.")
        return 0

    newest_sha, newest_pr, _ = gaps[0]
    print(
        f"pr-body: {len(gaps)} squash commit(s) on {ref} lost their body, newest "
        f"#{newest_pr} ({newest_sha[:8]}); the reasoning is on GitHub, not in this "
        f"checkout. Recover with: python3 tools/pr_body_check.py --recover"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
