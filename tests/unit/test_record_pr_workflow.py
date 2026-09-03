"""Tests for `.github/workflows/record-pr.yml`, the merge-time `pr:` write.

The workflow is the one job in this repository that pushes to the default
branch, and the two ways it could go wrong quietly are both decidable from the
file, so they are checked here rather than left to review.

The first is its commit subject. `vcs.PR_SUBJECT_RE` reads a trailing `(#N)`,
or a leading `Merge pull request #N`, as "this commit is the merge of pull
request N", and `_merges_naming` takes the newest such subject naming an item
id as that item's provenance. A subject shaped like one here would therefore
make the recording commit, rather than the merge it is recording, the answer to
where those items closed - and it would be wrong in the safe-looking direction,
because the number in it is right.

The second is the checkout depth. `closed_by` compares a merge commit's tree
against its parent's and declines outright where the parent is missing, which
is what `fetch-depth: 1` would produce on every run.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "record-pr.yml"

sys.path.insert(0, str(REPO / "subprojects" / "docket" / "src"))

from docket.vcs import PR_SUBJECT_RE  # noqa: E402

#: Every `git commit -m "..."` the workflow makes.
SUBJECT_RE = re.compile(r"""git commit -m ["']([^"']+)["']""")


def _subjects() -> list[str]:
    return SUBJECT_RE.findall(WORKFLOW.read_text(encoding="utf-8"))


def test_the_workflow_commits_something() -> None:
    """Guards the two tests below from passing on a file that stopped committing."""
    assert _subjects()


def test_no_commit_subject_reads_as_a_merge() -> None:
    """A `(#N)` here would out-rank the merge it is recording."""
    for subject in _subjects():
        rendered = subject.replace("${PR_NUMBER}", "257")
        assert PR_SUBJECT_RE.search(rendered) is None, rendered


def test_the_checkout_is_deep_enough_to_read_a_parent() -> None:
    """`closed_by` declines at depth 1, so every run would record nothing."""
    assert "fetch-depth: 0" in WORKFLOW.read_text(encoding="utf-8")


def test_the_write_is_validated_before_it_is_pushed() -> None:
    """A push made with GITHUB_TOKEN starts no workflow, so this is the only gate."""
    body = WORKFLOW.read_text(encoding="utf-8")
    assert body.index("bin/docket check") < body.index("git push")
