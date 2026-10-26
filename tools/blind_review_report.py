"""Report, pass by pass, what blind review found on the simulator pull requests merged since one.

Close-out step 9 runs one or two blind generalist review passes on every
simulator pull request, and records each finding in a `Blind-review` trailer
with its pass, its severity, its outcome and whether an earlier pass named it
(`PL-0BRY`). The monthly model review runs this report to check that each pass
still finds faults the session accepts, and the second pass in particular,
which `PL-TBQS` kept on 3 defects its replay found (`PL-TDV9`).

**Where the records are read from.** The squash commit on the default branch
carries the pull request's body, not the branch's commits, so the trailer is
read from each pull request's frozen head, `refs/pull/<n>/head`, which GitHub
keeps after the branch is deleted. One `git ls-remote` lists every head, and
the heads this clone lacks are fetched by hash, which writes no ref. The
record is the newest `Blind-review` trailer in `<head> ^<merge>^`, read by
`docket.arming.newest_blind_record`, the reading `bin/docket arm` takes.

**How many passes a pull request owed** is worked out from its merge commit's
own diff by `tools/blind_review.py`'s `passes_between`, so by today's rule
(`docket.arming.blind_passes`) rather than the rule in force when it merged. A
pull request that owed none is counted and otherwise left out.

**What the table counts.** One row per pass, from the records that list their
findings by pass. `new` is a finding that was fixed or filed and that no
earlier pass named. Fixed, filed and rejected are the authoring session's
judgment of each finding, not a blind check's. Records in the older totals form
cannot be split by pass, so their totals are printed below the table, by the
number of passes they record. Every pull request that owed passes and could not
be counted in full is listed by number with the reason.

Exits 0 when it reported, gaps included, and 1 when it could not report at
all: a shallow clone, an unknown default branch, a `--since` that names no
merge on it, or a remote that would not list its heads. It runs under
`uv run python`, because `passes_between` parses each changed test under
`tests/`, and those may use grammar newer than the bare interpreter reads.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.arming import (  # noqa: E402
    BLIND_REVIEW,
    BLIND_SEVERITIES,
    BlindRecord,
    newest_blind_record,
)
from docket.lines import split_lines  # noqa: E402
from docket.model import pr_number  # noqa: E402
from docket.vcs import (  # noqa: E402
    REMOTE,
    GitCall,
    GitUnanswered,
    call_git,
    default_base,
    is_shallow,
    read_git,
    resolved,
    subject_pull_request,
    unresolved_base_cause,
)

from blind_review import passes_between  # noqa: E402

#: The pull request after which `bin/docket arm` held a simulator branch for a
#: `Blind-review` record (`PL-HDRN`), so the first one a record is owed on.
DEFAULT_SINCE = 1767

#: Seconds for a call that reaches the remote, longer than `vcs.GIT_TIMEOUT`.
NETWORK_TIMEOUT = 60.0

#: How many heads one `git fetch` asks for.
FETCH_BATCH = 100

#: The severities that count as a real fault rather than a polish point: every
#: one but `optional`, which `BLIND_SEVERITIES` lists last.
SERIOUS = BLIND_SEVERITIES[:-1]

#: How the report asks git a question that reaches the network: the argv after
#: `git`, and the timeout. A test serves its own.
NetworkGit = Callable[[Sequence[str]], GitCall]


class Declined(Exception):
    """The report could not be made at all, and why."""


@dataclass(frozen=True)
class Merge:
    """One pull request merged into the default branch, and the commit that merged it."""

    number: int
    commit: str


@dataclass
class PassRow:
    """What one pass found across the pull requests whose record lists it."""

    pull_requests: int = 0
    findings: int = 0
    fixed_or_filed: int = 0
    new: int = 0
    new_serious: int = 0
    rejected: int = 0
    with_new: int = 0


@dataclass
class TotalsRow:
    """The older records' totals, for the records of one pass count."""

    pull_requests: int = 0
    findings: int = 0
    fixed: int = 0
    filed: int = 0
    rejected: int = 0


@dataclass
class Report:
    """The tables and every gap, as `render` prints them."""

    since: int
    base: str
    merged: int = 0
    owed_nothing: int = 0
    owed: int = 0
    by_pass: dict[int, PassRow] = field(default_factory=dict)
    older: dict[int, TotalsRow] = field(default_factory=dict)
    second_owed: int = 0
    second_new_serious: int = 0
    gaps: list[tuple[int, str]] = field(default_factory=list)


def network_git(root: Path) -> NetworkGit:
    """Ask git in `root` a question that reaches the remote, never prompting for credentials."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    def run(args: Sequence[str]) -> GitCall:
        return call_git(args, root, timeout=NETWORK_TIMEOUT, env=env)

    return run


def merges_since(root: Path, base: str, since: int) -> list[Merge]:
    """The pull requests merged on `base`'s first-parent line after `since`'s, oldest first."""
    log = read_git(["log", "--first-parent", "--format=%H%x1f%s", base], root)
    found: list[Merge] = []
    for line in split_lines(log):
        commit, _, subject = line.partition("\x1f")
        named = subject_pull_request(subject)
        if named is None:
            continue
        if named.number == since:
            return found[::-1]
        found.append(Merge(named.number, commit))
    raise Declined(f"no commit on {base} names #{since}, so nothing is known to follow it")


def pull_heads(git: NetworkGit) -> dict[int, str]:
    """Every `refs/pull/<n>/head` the remote holds, by pull request number."""
    done = git(["ls-remote", REMOTE, "refs/pull/*/head"])
    if done.code != 0:
        raise Declined(f"`git ls-remote {REMOTE}` did not list the pull heads: {done.reason}")
    heads: dict[int, str] = {}
    for line in split_lines(done.stdout.decode("utf-8", "replace")):
        sha, _, ref = line.partition("\t")
        number = pr_number(ref.removeprefix("refs/pull/").removesuffix("/head"))
        if number is not None and ref.endswith("/head"):
            heads[number] = sha.strip()
    return heads


def _present(root: Path, sha: str) -> bool:
    """Whether this clone holds the commit `sha`."""
    return bool(read_git(["rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"], root).strip())


def fetch_heads(root: Path, git: NetworkGit, shas: Iterable[str]) -> set[str]:
    """Fetch by hash each of `shas` this clone lacks, writing no ref, and return any still missing.

    The heads go in batches of `FETCH_BATCH`. One head that cannot be fetched
    fails its whole batch, so a failed batch is asked again one head at a time,
    to name the heads that are really missing.
    """
    missing = sorted({sha for sha in shas if not _present(root, sha)})
    fetch = ["fetch", "--quiet", "--no-tags", "--no-write-fetch-head", REMOTE]
    for start in range(0, len(missing), FETCH_BATCH):
        batch = missing[start : start + FETCH_BATCH]
        if git([*fetch, *batch]).code != 0:
            for sha in batch:
                git([*fetch, sha])
    return {sha for sha in missing if not _present(root, sha)}


def count(report: Report, owed: int, record: BlindRecord) -> None:
    """Add one pull request's record to the tables."""
    if record.totals is not None:
        older = report.older.setdefault(record.passes, TotalsRow())
        older.pull_requests += 1
        older.findings += record.totals.findings
        older.fixed += record.totals.fixed
        older.filed += record.totals.filed
        older.rejected += record.totals.rejected
        return
    for number, findings in enumerate(record.split, start=1):
        row = report.by_pass.setdefault(number, PassRow())
        row.pull_requests += 1
        row.findings += len(findings)
        accepted = [finding for finding in findings if finding.outcome != "rejected"]
        new = [finding for finding in accepted if not finding.repeat]
        row.fixed_or_filed += len(accepted)
        row.new += len(new)
        row.new_serious += sum(finding.severity in SERIOUS for finding in new)
        row.rejected += len(findings) - len(accepted)
        row.with_new += bool(new)
    if owed >= 2 and len(record.split) >= 2:
        report.second_owed += 1
        report.second_new_serious += sum(
            finding.severity in SERIOUS and finding.outcome != "rejected" and not finding.repeat
            for finding in record.split[1]
        )


def build(root: Path, since: int, git: NetworkGit) -> Report:
    """Read every merged pull request after `since`, and its record."""
    shallow = is_shallow(root)
    if shallow is True:
        raise Declined("this clone is shallow, so the merges it is missing cannot be counted")
    if shallow is None:
        raise Declined("git cannot say whether this clone is complete")
    base = default_base(root)
    if not resolved(base):
        raise Declined(unresolved_base_cause(base))
    try:
        merges = merges_since(root, base, since)
    except GitUnanswered as error:
        raise Declined(f"git did not answer a log of {base}: {error}") from error
    report = Report(since=since, base=base, merged=len(merges))
    owing: list[tuple[Merge, int]] = []
    for merge in merges:
        try:
            owed = passes_between(root, f"{merge.commit}^", merge.commit)
        except GitUnanswered as error:
            report.gaps.append((merge.number, f"the passes it owed could not be counted: {error}"))
            continue
        if owed:
            owing.append((merge, owed))
        else:
            report.owed_nothing += 1
    report.owed = len(owing)
    if not owing:
        return report
    heads = pull_heads(git)
    unfetched = fetch_heads(root, git, (heads[m.number] for m, _ in owing if m.number in heads))
    for merge, owed in owing:
        head = heads.get(merge.number)
        if head is None:
            report.gaps.append((merge.number, f"{REMOTE} holds no refs/pull/{merge.number}/head"))
            continue
        if head in unfetched:
            report.gaps.append((merge.number, f"its head {head[:12]} could not be fetched"))
            continue
        reading = newest_blind_record(root, [head, f"^{merge.commit}^"])
        if reading.declined:
            report.gaps.append((merge.number, reading.declined))
        elif reading.record is None and reading.commit:
            report.gaps.append(
                (merge.number, f"its {BLIND_REVIEW} record does not parse ({reading.misread})")
            )
        elif reading.record is None:
            noun = "pass" if owed == 1 else "passes"
            report.gaps.append(
                (merge.number, f"it owed {owed} {noun} and has no {BLIND_REVIEW} record")
            )
        else:
            if reading.record.passes < owed:
                report.gaps.append(
                    (
                        merge.number,
                        f"counted, but its record lists {reading.record.passes} of the "
                        f"{owed} passes it owed",
                    )
                )
            count(report, owed, reading.record)
    return report


def render(report: Report) -> list[str]:
    """The report as Markdown, ready to paste into `docs/model-review.md`."""
    lines = [
        f"Pull requests merged on {report.base} after #{report.since}: {report.merged}. "
        f"Owed no blind review pass, by today's rule: {report.owed_nothing}. "
        f"Owed one or more: {report.owed}.",
        "",
        "Fixed, filed and rejected are the authoring session's judgment of each finding, "
        "not a blind check's.",
        "",
        "Records that list each finding by pass:",
        "",
    ]
    if report.by_pass:
        lines += [
            "| Pass | Pull requests | Findings | Fixed or filed | New | New, blocking or "
            "should-fix | Rejected | Pull requests with a new finding |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for number in sorted(report.by_pass):
            row = report.by_pass[number]
            lines.append(
                f"| {number} | {row.pull_requests} | {row.findings} | {row.fixed_or_filed} | "
                f"{row.new} | {row.new_serious} | {row.rejected} | {row.with_new} |"
            )
        lines += [
            "",
            f"Pass 2 on the pull requests that owed two passes: {report.second_owed} pull "
            f"requests, {report.second_new_serious} new findings marked blocking or should-fix.",
        ]
    else:
        lines.append("None.")
    lines += ["", "Older records, which total every pass together:", ""]
    if report.older:
        lines += [
            "| Passes recorded | Pull requests | Findings | Fixed | Filed | Rejected |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for passes in sorted(report.older):
            older = report.older[passes]
            lines.append(
                f"| {passes} | {older.pull_requests} | {older.findings} | {older.fixed} | "
                f"{older.filed} | {older.rejected} |"
            )
    else:
        lines.append("None.")
    lines += ["", "Pull requests that owed passes and were not counted in full:", ""]
    if report.gaps:
        lines += [f"- #{number}: {reason}" for number, reason in sorted(report.gaps)]
    else:
        lines.append("None.")
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=split_lines(__doc__)[0])
    parser.add_argument(
        "--since",
        type=int,
        default=DEFAULT_SINCE,
        help=f"report the pull requests merged after this one (default: {DEFAULT_SINCE})",
    )
    args = parser.parse_args(argv)
    try:
        report = build(ROOT, args.since, network_git(ROOT))
    except Declined as error:
        print(f"No report: {error}.", file=sys.stderr)
        return 1
    print("\n".join(render(report)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
