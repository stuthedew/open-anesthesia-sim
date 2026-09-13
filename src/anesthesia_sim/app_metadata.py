"""App identity/version constants, read from installed package metadata."""

import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

DISTRIBUTION_NAME = "anesthesia-sim"
APP_DISPLAY_NAME = "Open Anesthesia Simulator"
APP_AUTHOR = "Open Anesthesia Simulator contributors"

#: What `APP_VERSION` holds when installed-package metadata is absent. A
#: sentinel rather than a literal at each site, because the interface has to
#: be able to *ask* whether the running build is identified: rendered
#: verbatim into a provenance line, "unknown" is a version-shaped string and
#: reads as an answer rather than as the absence of one (`PL-KCWD`).
UNKNOWN_VERSION = "unknown"

try:
    # Sourced from pyproject.toml; do not hardcode here.
    APP_VERSION = version(DISTRIBUTION_NAME)
except PackageNotFoundError:
    # A frozen/bundled build (see ROADMAP.md item 24) may not preserve
    # installed-package metadata; fail visibly rather than crash on launch.
    APP_VERSION = UNKNOWN_VERSION

#: Whether the running build could be identified at all. The fact, kept here
#: with the metadata it is read from; the words a reader sees are
#: `app/formatting.py`'s, so the one on-screen statement of provenance is
#: composed in the module that owns presentation rather than assembled from a
#: sentinel that leaked into it.
APP_VERSION_IS_KNOWN = APP_VERSION != UNKNOWN_VERSION

# `APP_VERSION` moves only when a release is cut, so every build between two
# releases displays the same string - including a build from before a fix and a
# build from after it. `PL-QC38` is what that cost: `PL-61WW` (the agent name
# losing contrast in the disabled selector) merged, the symptom was reported
# still present, and nothing on screen could say which build had drawn it. The
# session spent its context re-deriving a correctness argument for code that
# was already correct. That generalises to every item whose fix can only be
# confirmed by eye, which is most of `presentation-safety` - and it fails in
# the worse direction too, a fix that did not work confirmed as working because
# the screen looked new.
#
# So a build that is not a release says so, in the one place the interface
# already states its provenance (`app/formatting.py`'s `format_subtitle`).

#: How long to wait for git before deciding the answer is not worth having.
#: A build identifier is a convenience; a launch that hangs on it is not.
_GIT_TIMEOUT_S = 2.0

#: Only this project's release tags. `--match` keeps a stray tag in someone's
#: clone from being read as a release.
_RELEASE_TAG_GLOB = "v[0-9]*"


def _git(*arguments: str) -> str | None:
    """One git command against the directory this module was loaded from.

    The working directory is the module's own, never the process's. Launching
    the app from another directory would otherwise describe whatever
    repository happened to be there - a build identifier naming code that is
    not the code running, which is worse than none at all.

    The argument list is fixed and no shell is involved, so nothing a caller
    passes can become a command.

    Args:
        arguments: The git subcommand and its arguments.

    Returns:
        Trimmed standard output, or None where git is absent, the directory is
        not a repository, the call times out, or the command fails.
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
    except OSError, subprocess.SubprocessError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def build_identifier(
    described: str | None, revision: str | None, release_version: str
) -> str | None:
    """Decide what a build should add to its version, given what git said.

    Pure, and separated from `_git` for that reason: what to display is the
    part worth testing, and testing it against this checkout's own state would
    assert whatever happens to be true today rather than the rule.

    Args:
        described: `git describe --tags --always --dirty` output, or None.
        revision: Short commit hash, or None.
        release_version: The installed distribution's version.

    Returns:
        None where the running code is the released tag, or where git could
        not answer; otherwise the local-version segment to append.
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

#: What the interface shows: the bare version on a release build, and the
#: version plus the commit on anything else. PEP 440 local-version syntax
#: (`0.4.10+g8d46af8`), so it reads as a version rather than as debug output.
#:
#: **Absence means "the release, or a build that cannot be identified", not
#: "the release".** No git, no repository, a timeout and a failed call all give
#: the bare version, the same as a clean checkout of the tag. Distinguishing
#: them would mean printing "unknown build" on every installed copy - noise on
#: the shipped product to serve a development need - and an installed wheel
#: genuinely has nothing better to say. The conflation is stated here so a
#: reader does not take a bare version as proof.
APP_BUILD_VERSION = APP_VERSION if APP_BUILD is None else f"{APP_VERSION}+{APP_BUILD}"

APP_BUNDLE_ID = "org.openanesthesia.simulator"
