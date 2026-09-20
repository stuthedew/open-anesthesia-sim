"""Report a squash commit on the default branch that landed with no body.

`main` is squash-merged, `allow_merge_commit` is false, and the repository is
configured `squash_merge_commit_title: PR_TITLE` / `squash_merge_commit_message:
PR_BODY`. So the pull request body is not a review artifact thrown away on
merge - it *is* the permanent commit message a reader of `main` meets, and it
is the densest record this project produces: what was refused, what was
measured, what was filed, and why.

It does not always arrive. Measured 2026-09-20 over all 805 first-parent
commits on `main`: **187 of the 683 squash commits, 27.4%, carry a zero-length
body**, and every one of those 187 pull requests *had* a body on GitHub -
763,224 characters of reasoning that exist only outside the repository. The
loss is silent from every direction anyone looks: the pull request still reads
correctly on GitHub, and `git log` shows a subject line that looks deliberate.
`PL-843V`.

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

So prevention needs a change of merge client, which is the project owner's to
make and cannot be enforced from the tree. Detection plus repair is what this
tool can do, and it holds whether or not the client is ever named.

**Detection reads git and the filesystem, never the network.** The rule is
exact: a first-parent commit on the default branch whose subject ends in
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

**Advisory, never a hard failure, and that is a considered refusal rather than
timidity.** The condition is created by a *merge*, so the branch running a
check is never the branch that caused it; failing that branch would block
unrelated work for a defect it did not introduce and could not have prevented.
It would also be unsatisfiable offline, since the remedy needs the API. What
the advisory buys is that the loss becomes visible while the body is still
retrievable - the pull request could be edited, or the repository migrated, and
then it is gone for good.

**It runs from the session-start hook rather than from `make check`, and the
reason is about when a session may act rather than about cost.** The remedy is
a network fetch and a commit of files outside the current item's declared
`touches`, which `CLAUDE.md`'s fix-now rule forbids inline and its housekeeping
rule says must be filed first and worked under its own id. In `make check` this
advisory would therefore fire at the one moment a session is not allowed to do
anything about it - and an advisory nobody can act on trains a reader to skim
the region a real one appears in, which is the defect `CLAUDE.md` names. Session
start is before an item is picked, which is when filing or starting one is the
right move. It is also the only place the answer is fresh: this reads
`origin/main` and does no fetch of its own, and the digest has just done one.
So the output is one line, because session-start output is resent on every
turn, and the reasoning lives here instead.

**Silence is not a clean history.** It means no unrecovered loss was readable
from the refs in this checkout, which is also what a shallow or unfetched one
returns - `default_branch_ref` finds nothing and this says nothing. It surfaces
a loss; it never certifies that none occurred.

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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECOVERY_DIR = ROOT / "docs" / "pr-bodies"
API = "https://api.github.com"
TIMEOUT_S = 15

#: A squash subject as GitHub writes it under `squash_merge_commit_title:
#: PR_TITLE`: the pull request title with its number appended. Anchored to the
#: end so that `Merge pull request #101 from ...` - the pre-2026-08-31 merge
#: shape, which legitimately carries no body - cannot match.
SQUASH_SUBJECT_RE = re.compile(r"\(#(\d+)\)\s*$")

#: Separates the two records inside one recovery file. `---` on its own line is
#: YAML frontmatter, which is what `docs/items/` uses, so a reader meeting one
#: of these files already knows the convention.
FRONT_MATTER = "---"

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
    """Name a ref for the default branch, preferring the remote's copy.

    `origin/main` is what a session's checkout has after a fetch and is the
    branch the squash lands on. A bare or offline checkout may have only the
    local `main`; a shallow CI checkout may have neither deep enough to read,
    which is why every caller treats "" as "say nothing".
    """
    for ref in ("origin/main", "main"):
        if _git("rev-parse", "--verify", "--quiet", ref).strip():
            return ref
    return None


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
        match = SQUASH_SUBJECT_RE.search(subject)
        if match is None:
            continue
        rows.append((sha, int(match.group(1)), subject, body))
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
    """`owner/repo` from origin's URL, or None if it is not a GitHub remote."""
    match = re.search(
        r"github\.com[:/]+([^/]+/[^/]+?)(?:\.git)?\s*$", _git("remote", "get-url", "origin")
    )
    return match.group(1) if match else None


#: `fetch_body` answers in three states, and the difference decides whether a
#: file is written. A body is recorded; `NO_BODY` means the pull request was
#: read and genuinely has none, which is permanent and gets a tombstone; `None`
#: means the read itself failed - rate limit, outage, no network - which is
#: transient and must leave the advisory standing. Collapsing the last two
#: would either nag forever about a body that cannot exist, or silence the
#: check on a body that does.
NO_BODY = object()


def fetch_body(slug: str, pr: int) -> str | object | None:
    """The pull request's body, `NO_BODY` if it has none, or None if unreadable.

    Unauthenticated, for the reason `tools/main_ci_status.py` gives: the
    repository is public, so no token is needed and none is read, which keeps
    this runnable from a bare checkout and keeps a credential out of it.
    """
    request = urllib.request.Request(
        f"{API}/repos/{slug}/pulls/{pr}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "pr-body-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, ValueError, TimeoutError):
        return None
    body = payload.get("body")
    if isinstance(body, str) and body.strip():
        return body
    #: The pull request was read and has no body. `#325` is the live example:
    #: `body` is null on GitHub, and its squash commit escaped this check only
    #: because GitHub left the 46-character `Co-authored-by` trailer behind.
    return NO_BODY


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
    found = set(re.findall(r"\bPL-[0-9A-Z]{3,4}\b", subject))
    found.update(backlinks.get(pr, set()))
    return sorted(found)


def write_recovery(
    sha: str, pr: int, subject: str, body: str, merged: str, backlinks: dict[int, set[str]]
) -> Path:
    """Write one recovery file, body verbatim below a frontmatter block."""
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    ids = item_ids(subject, pr, backlinks)
    header = [
        FRONT_MATTER,
        f"pr: {pr}",
        f"commit: {sha}",
        f"merged: {merged}",
        f"items: {', '.join(ids) if ids else '(none)'}",
        f"subject: {subject}",
        FRONT_MATTER,
        "",
        f"<!-- Recovered by tools/pr_body_check.py. The squash commit {sha[:8]} landed with an",
        "empty message body; this is the pull request body it should have carried, verbatim.",
        "PL-843V. -->",
        "",
        "",
    ]
    path = RECOVERY_DIR / f"{pr}.md"
    path.write_text(
        "\n".join(header) + body.replace("\r\n", "\n").rstrip() + "\n", encoding="utf-8"
    )
    return path


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
            path = write_recovery(sha, pr, subject, TOMBSTONE, merged, backlinks)
            print(f"  #{pr} has no body on GitHub either; recorded as nothing to recover")
            written += 1
            continue
        assert isinstance(body, str)
        path = write_recovery(sha, pr, subject, body, merged, backlinks)
        #: `relative_to` raises where the recovery directory is not under the
        #: repository root, which is only ever a test's temporary directory -
        #: but a progress line is not worth an exception either way.
        shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        print(f"  recovered #{pr} -> {shown} ({len(body):,} chars)")
        written += 1
    return written


def main(argv: list[str]) -> int:
    """Print the advisory if there is one. Always exits 0; never blocks a branch."""
    ref = default_branch_ref()
    if ref is None:
        return 0

    if "--recover" in argv:
        written = recover(ref)
        print(f"pr-body: recovered {written} body/bodies.")
        return 0

    gaps = missing(ref)
    if not gaps:
        return 0

    #: One line, because this is read at session start where the output is
    #: resent on every turn. The reasoning lives in this module's docstring
    #: rather than in the advisory, on `tools/main_ci_status.py`'s model.
    newest_sha, newest_pr, _ = gaps[0]
    print(
        f"pr-body: {len(gaps)} squash commit(s) on {ref} lost their body, newest "
        f"#{newest_pr} ({newest_sha[:8]}); the reasoning is on GitHub, not in this "
        f"checkout. Recover with: python3 tools/pr_body_check.py --recover"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
