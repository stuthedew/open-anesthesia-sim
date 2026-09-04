"""SessionStart hook: correct the harness stop hook's unpushed-commit test.

A cloud container provisions `~/.claude/stop-hook-git-check.sh` at start and
wires it as a `Stop` hook. Its last test picks what to compare `HEAD` against
by whether `origin/<branch>` *resolves locally*:

    if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
      upstream="origin/$current_branch"
    ...
    unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0

A merged pull request deletes the head branch on the remote and leaves the
tracking ref behind, and the harness seeds such a ref for a session branch that
was never pushed, so the test passes against a ref naming a branch that no
longer exists and counts everything `main` has gained since as unpushed. The
hook then blocks the stop and demands a push that would recreate a dead branch
identical to `main`, with no content and no pull request. `PL-WW08` carries the
diagnosis; `PL-1Q3S` and `PL-PF8H` the two ways the stale ref arises.

`git rev-list HEAD --not --remotes` counts commits contained by *no* remote
ref, so a stale ref cannot be mistaken for a current one. It is more accurate
than the line it replaces rather than merely quieter - the `origin/HEAD`
fallback over-counts on a branch cut from another feature branch - it stays
offline, and it is the idiom the same hook already trusts a few lines above,
where the signing check scopes itself the same way.

**Why a hook, and not a patch handed to the project owner.** The file is not
theirs to change. `~/.claude/` is written by the environment manager at
container start, so an edit inside a container is erased by the next one, and
their own machine does not reach it either: user-level settings stay on that
machine and never reach a cloud session. An environment setup script is no
better - it runs *before* Claude Code launches and is skipped entirely once the
environment cache exists. A SessionStart hook runs after Claude Code launches,
on every session including resumed, which is the one moment the file exists and
no `Stop` has yet fired. Nor can a second `Stop` hook undo the first: one that
exits 2 blocks the stop whatever else runs.
(https://code.claude.com/docs/en/cloud-environments, read 2026-09-04.)

**Silent on the path it takes every session.** Standard output from a
SessionStart hook enters the session's context and is resent on every turn, so
a line announcing the ordinary success would cost tokens in every session
forever to report that nothing needs deciding - a defect in a check rather than
coverage. It speaks only when the correction is *not* in place, because then a
push demand may be false and the session needs to know how to disprove one.

Every path exits 0, including a missing file, an unreadable one and a failed
write: a session that will not start is a worse outcome than a spurious demand.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

#: The line as the harness ships it, and the line that replaces it. Matched
#: whole, indentation included, so a near-miss elsewhere in the script cannot
#: be rewritten and an upstream change to this line is a clean miss rather than
#: a partial edit.
VULNERABLE = '  unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0\n'
CORRECTED = "  unpushed=$(git rev-list HEAD --not --remotes --count 2>/dev/null) || unpushed=0\n"

#: Printed only when the correction is not in place. It carries the disproof
#: commands because this is the moment they are needed: `CLAUDE.md` no longer
#: spends resident lines on them.
UNPATCHED = """\
{path} still carries the unpushed-commit test `PL-WW08` corrects, and this
session could not correct it ({reason}). A demand to push at the end of this
session may be false. `git ls-remote --heads origin <branch>` says whether the
branch still exists; `git rev-list HEAD --not --remotes --count` says whether
anything is genuinely unpushed. Do not clear a stale ref with `git fetch
--prune`: it can be the only copy of an item captured on a branch nobody
merged, which `bin/docket stranded` recovers.
"""


def default_hook() -> Path:
    """Where the harness writes the stop hook."""
    return Path.home() / ".claude" / "stop-hook-git-check.sh"


def corrected(source: str) -> str | None:
    """`source` with the test corrected, or `None` if it cannot be.

    `None` is returned both when the line is absent and when it appears more
    than once: either means this is not the script this tool was written
    against, and a guess at which occurrence to rewrite is how a hook every
    session depends on gets silently broken.
    """
    if source.count(VULNERABLE) != 1:
        return None
    return source.replace(VULNERABLE, CORRECTED)


def _write_atomically(target: Path, text: str) -> None:
    """Replace `target`'s contents, keeping its mode and never truncating it.

    The file is executed by every `Stop` in the session, so a partial write
    would break the session it was meant to help. Writing a sibling and
    renaming it means the hook is either the old script or the new one.
    """
    mode = stat.S_IMODE(target.stat().st_mode)
    handle_fd, name = tempfile.mkstemp(dir=str(target.parent), prefix=target.name + ".")
    scratch = Path(name)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(scratch, mode)
        os.replace(scratch, target)
    except BaseException:
        scratch.unlink(missing_ok=True)
        raise


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else default_hook()
    try:
        source = target.read_text(encoding="utf-8")
    except OSError:
        # No such hook here: a local session, or a container that ships none.
        # Nothing to say - this is the ordinary case away from the harness.
        return 0
    if CORRECTED in source:
        return 0
    replacement = corrected(source)
    if replacement is None:
        print(UNPATCHED.format(path=target, reason="the line it rewrites is not there"))
        return 0
    try:
        _write_atomically(target, replacement)
    except OSError as error:
        print(UNPATCHED.format(path=target, reason=f"writing it failed: {error}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
