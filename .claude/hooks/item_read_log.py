"""Record which item files a session opens, so the store's shape can be argued from evidence.

Every claim this project has made about `docs/items/` describes its *shape* -
814 files, 70.8% terminal, 86.1% of items citing another, 2,773 edges. Not one
of them is a measurement of the store being *used*. The citation graph is
counted at authoring time; whether a session ever follows an edge is unknown,
and two of the larger design arguments about the store rest on assuming it
does (`PL-KM3X`, dropped, and `PL-NB35`). This closes that gap the only way it
can be closed, which is by watching.

**What it records, and deliberately nothing more:** a timestamp, the session
id, the tool, and the path or pattern. It resolves nothing - not the item's
status, not whether the read followed a citation - because status changes after
the read and a hook that interprets is a hook that has to be right twice.
`tools/item_reads.py` does the interpreting, against the store as it stands
when the question is asked.

**Why a `PostToolUse` hook rather than a wrapper or a shell alias.** The
question is which files a *session* opens, and a session opens them through the
harness's own tools. Nothing else sees that. The cost is one append per
matching tool call and nothing at all for the rest, because the matcher in
`.claude/settings.json` narrows to the three read tools before this runs.

**It fails silently, always, and that is load-bearing rather than tidy.** A
hook that errors interrupts the session it is measuring, which would make the
measurement the most expensive thing in the repository. Malformed JSON, an
unwritable log, a missing key: every one of them exits 0 having done nothing.

**The log is local and untracked** - `.docket-reads.log`, covered by
`.gitignore`'s existing `*.log`. It is per-checkout by nature: a container is
ephemeral, so what it holds is one machine's sessions and it is not a shared
record. That is the honest scope of the measurement and
`tools/item_reads.py` says so in its output rather than letting a reader
assume otherwise.

Standard library only, and parses at the floor
`tests/unit/test_tools_portability.py` holds `.claude/hooks/` to.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

LOG_NAME = ".docket-reads.log"

# A line is about 80 bytes. The cap is generous because the whole value of this
# record is the sequence - truncating the front would destroy exactly the
# edge-traversal question it exists to answer - and 4 MB is roughly 50,000
# reads, far more than a container lives to produce. Past it the hook stops
# writing rather than rotating: a log that silently discards its own history is
# worse than one that stops and says nothing, because the analysis downstream
# cannot tell the two apart.
MAX_LOG_BYTES = 4_000_000

# The tool inputs that name a file or a search. `file_path` is Read and Edit;
# `path` and `pattern` are Grep and Glob. Order matters only in that the first
# hit wins, and a tool never sets two of them meaningfully.
PATH_KEYS = ("file_path", "path", "notebook_path")


def repo_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def interesting(payload: dict[str, object]) -> tuple[str, str] | None:
    """Return `(tool, target)` when this call touched the item store, else None.

    Two shapes count. A read whose path is inside `docs/items/` is a session
    opening an item. A search whose *pattern* names an item id is a session
    looking one up by id, which is the traversal shape - it happens whether or
    not the session knows which file holds that id, and a path-only test would
    miss it entirely.
    """
    tool = payload.get("tool_name")
    if not isinstance(tool, str):
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None

    for key in PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and "docs/items" in value.replace("\\", "/"):
            return tool, value

    pattern = tool_input.get("pattern")
    if isinstance(pattern, str) and "PL-" in pattern:
        return tool, pattern

    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0

    try:
        hit = interesting(payload)
        if hit is None:
            return 0
        tool, target = hit

        log = repo_root() / LOG_NAME
        if log.exists() and log.stat().st_size > MAX_LOG_BYTES:
            return 0

        session = payload.get("session_id")
        session = session if isinstance(session, str) else "unknown"

        stamp = datetime.now(UTC).isoformat(timespec="seconds")
        # Tabs separate, and every field has them stripped: a Grep pattern is
        # arbitrary user text and a literal tab in one would otherwise shift
        # every column after it.
        fields = [f.replace("\t", " ").replace("\n", " ") for f in (stamp, session, tool, target)]
        with log.open("a", encoding="utf-8") as handle:
            handle.write("\t".join(fields) + "\n")
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
