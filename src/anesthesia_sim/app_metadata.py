"""App identity/version constants, read from installed package metadata."""

import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

DISTRIBUTION_NAME = "anesthesia-sim"
APP_DISPLAY_NAME = "Open Anesthesia Simulator"
APP_AUTHOR = "Open Anesthesia Simulator contributors"

#: The value of `APP_VERSION` when installed-package metadata is absent. It is a
#: named sentinel rather than a literal repeated at each site, because the
#: interface must be able to *ask* whether the running build is identified. If
#: "unknown" were rendered verbatim into a provenance line, it would look like a
#: version string. A reader would take it as a version rather than as the
#: absence of one (`PL-KCWD`).
UNKNOWN_VERSION = "unknown"

try:
    # Sourced from pyproject.toml; do not hardcode here.
    APP_VERSION = version(DISTRIBUTION_NAME)
except PackageNotFoundError:
    # A frozen or bundled build (see ROADMAP.md item 24) may not keep the
    # installed-package metadata. Fail visibly rather than crash on launch.
    APP_VERSION = UNKNOWN_VERSION

#: Whether the running build could be identified at all. This module keeps the
#: fact, next to the metadata it is read from. The words a reader sees on screen
#: come from `app/formatting.py`. So the one on-screen statement of provenance
#: is composed in the module that owns presentation, rather than built from a
#: sentinel that leaked into that module.
APP_VERSION_IS_KNOWN = APP_VERSION != UNKNOWN_VERSION

# `APP_VERSION` changes only when a release is cut. So every build between two
# releases displays the same string, including a build from before a fix and a
# build from after it. `PL-QC38` records what that cost. The item `PL-61WW`,
# about the agent name losing contrast in the disabled selector, was merged. The
# symptom was then reported as still present, and nothing on screen could say
# which build had drawn it. The session spent its context re-deriving a
# correctness argument for code that was already correct. The same problem
# applies to every item whose fix can only be confirmed by eye, which is most of
# the `presentation-safety` feature. The problem also has a worse direction: a
# fix that did not work can be confirmed as working because the screen looks new.
#
# So a build that is not a release says so, in the one place where the
# interface already states its provenance (`app/formatting.py`'s
# `format_subtitle`).

#: How long, in seconds, to wait for git before giving up on its output. A
#: build identifier is a convenience, and a launch must not hang waiting for one.
_GIT_TIMEOUT_S = 2.0

#: The pattern that matches only this project's release tags. With `--match`,
#: a stray tag in someone's clone is not treated as a release.
_RELEASE_TAG_GLOB = "v[0-9]*"


def _git(*arguments: str) -> str | None:
    """Run one git command in the directory that this module was loaded from.

    The working directory is the module's own directory, never the process's.
    Otherwise, launching the app from another directory would describe whatever
    repository happened to be there. The result would be a build identifier
    that names code other than the running code, which is worse than no
    identifier at all.

    The argument list is fixed and no shell is involved, so nothing a caller
    passes can become a command.

    Args:
        arguments: The git subcommand and its arguments.

    Returns:
        The trimmed standard output, or None when git is absent, the directory
        is not a repository, the call times out, or the command fails.
    """

    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    # This except clause without parentheses is PEP 758 syntax (Python 3.14).
    # It is the one construct in this file that a bare `python3` cannot parse.
    # `pyproject.toml` requires 3.14, but `tools/` and `.claude/hooks/` run on
    # the minimum version 3.11, which `tools/ruff.toml` pins. So
    # `python3 -m compileall src/` reports `SyntaxError: multiple exception
    # types must be parenthesized` on this line, although the code is correct.
    # That error is expected and is not a defect. Use `uv run python` instead.
    # `.claude/hooks/floor-interpreter-guard.sh` refuses the bare invocation,
    # and `PL-JQJQ` records why the error kept being re-investigated.
    except OSError, subprocess.SubprocessError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def build_identifier(
    described: str | None, revision: str | None, release_version: str
) -> str | None:
    """Decide what a build should append to its version, given git's output.

    This function is pure, and it is kept separate from `_git` for that reason.
    What to display is the part worth testing. Testing it against this
    checkout's own state would assert whatever happens to be true today, rather
    than the rule.

    Args:
        described: `git describe --tags --always --dirty` output, or None.
        revision: Short commit hash, or None.
        release_version: The installed distribution's version.

    Returns:
        None when the running code is the released tag, or when either git call
        returned None. Otherwise, the local-version segment to append.
    """

    if described is None or revision is None:
        return None
    if described == f"v{release_version}":
        return None
    return f"g{revision}.dirty" if described.endswith("-dirty") else f"g{revision}"


APP_BUILD = build_identifier(
    _git("describe", "--tags", "--always", "--dirty", "--match", _RELEASE_TAG_GLOB),
    _git("rev-parse", "--short=8", "HEAD"),
    APP_VERSION,
)

#: The version string that the interface shows. A release build shows the bare
#: version, and any other build shows the version plus the commit. The string
#: uses PEP 440 local-version syntax (`0.4.10+g8d46af8`), so a reader takes it
#: as a version rather than as debug output.
#:
#: **A bare version means "the release, or a build that cannot be identified",
#: not just "the release".** No git, no repository, a timeout and a failed call
#: all give the bare version, the same as a clean checkout of the tag. Telling
#: these cases apart would mean printing "unknown build" on every installed
#: copy. That would be noise on the shipped product to serve a development
#: need, and an installed wheel genuinely has nothing better to say. This
#: comment states the ambiguity so that a reader does not take a bare version
#: as proof of a release build.
APP_BUILD_VERSION = APP_VERSION if APP_BUILD is None else f"{APP_VERSION}+{APP_BUILD}"

APP_BUNDLE_ID = "org.openanesthesia.simulator"

#: The organization name that `main()` gives Qt. Qt files the reader's data
#: under this name and under `APP_DISPLAY_NAME`. On Linux the saved Workspaces
#: are in `~/.local/share/OpenAnesthesia/Open Anesthesia Simulator/`. It is the
#: organization part of `APP_BUNDLE_ID`. Changing either name moves that
#: directory, so a reader's saved Workspaces would no longer be found
#: (`PL-DWHG`).
APP_ORGANIZATION_NAME = "OpenAnesthesia"
