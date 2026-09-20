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
763,222 characters of reasoning that exist only outside the repository. The
loss is silent from every direction anyone looks: the pull request still reads
correctly on GitHub, and `git log` shows a subject line that looks deliberate.
`PL-843V`.

**The cause is not recorded anywhere GitHub exposes, and this check does not
depend on knowing it.** Tested and ruled out across a 60/60 stratified sample:
the merge actor (`merged_by` is the same account in both groups), auto-merge
(zero `auto_merge_enabled` events among the affected, and *more* among the
unaffected), a body written after the merge (`updated_at - merged_at` has the
same 2-second median in both), an empty body at creation (none of the 187), the
single-commit squash special case (the commit-count distributions overlap), an
overriding `commit_title` (the subject equals the pull request title in
186/187), draft state, branch namespace and committer timezone. What is left
are merge-*client* properties GitHub does not record. So the remedy cannot be
"stop doing the thing that causes it" - nobody can see the thing - and has to
be detection plus repair instead.

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
timidity.** The condition is created by a *merge*, so the branch running `make
check` is never the branch that caused it; failing that branch would block
unrelated work for a defect it did not introduce and could not have prevented.
It would also be unsatisfiable offline, since the remedy needs the API. What
the advisory buys is that the loss becomes visible while the body is still
retrievable - the pull request could be edited, or the repository migrated, and
then it is gone for good.

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


def fetch_body(slug: str, pr: int) -> str | None:
    """The pull request's body from the public API, or None if unreadable.

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
    return body if isinstance(body, str) and body.strip() else None


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

    shown = gaps[:5]
    print(
        f"pr-body: {len(gaps)} squash commit(s) on {ref} carry no message body, and the "
        f"reasoning is not in this checkout.",
        file=sys.stderr,
    )
    for sha, pr, subject in shown:
        print(f"    {sha[:8]}  #{pr}  {subject[:72]}", file=sys.stderr)
    if len(gaps) > len(shown):
        print(f"    ... and {len(gaps) - len(shown)} more", file=sys.stderr)
    print(
        "  The pull request body is this repository's squash commit message "
        "(`squash_merge_commit_message: PR_BODY`), so what is missing is the design\n"
        "  reasoning itself, not a review artifact. It is still on GitHub and still "
        "retrievable; it stops being retrievable if the body is edited or the\n"
        "  repository is migrated. To record it in the checkout:\n"
        "    python3 tools/pr_body_check.py --recover\n"
        "  Advisory only - the merge created this, not your branch. `PL-843V`.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
