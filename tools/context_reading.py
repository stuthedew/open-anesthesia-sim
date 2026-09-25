"""Read this session's own context size, live, from its transcript.

`CLAUDE.md` § "Session and tool-use efficiency" tells a session to check its
context before starting an item. The instrument it names - `get_session`, field
`external_metadata.context_usage.used_tokens` - cannot answer that question,
and this script exists because of how it fails rather than because a second
opinion is nice to have.

**The named instrument reads zero, not merely stale.** That field is written at
turn boundaries. A session that opens an item, implements it, tests it, commits
and pushes inside one turn - the normal shape of work here - crosses no
boundary, so the field it is told to read still holds whatever it held when the
turn began. `PL-BZVY` measured that: two calls, one before an item and one
after the whole item had shipped, returned a byte-identical 115,320. Measured
again on 2026-09-21 in a session still inside its first turn, the field read
**0** while this script read 88,100 from the same session. A gauge reading zero
is worse than one reading late, because a session reasonably concludes it has
spent nothing.

**What is read instead.** Claude Code appends every request to a JSONL
transcript as it happens, not at turn boundaries. Each assistant record carries
`message.usage`, and

    input_tokens + cache_read_input_tokens + cache_creation_input_tokens

is the exact context the API was billed for on that request. It is the same
quantity `used_tokens` reports, taken from the record the harness has already
written rather than from a field it has not yet refreshed. Verified on
2026-09-21: the series moved 81,048 -> 88,100 across six requests inside a
single turn, while `get_session` held at 0 throughout.

**Three numbers, because the rule does not yet say which it wants.**

`baseline` is the first request of the session: the system prompt, the resident
instruction set, the session-start digest, and any skill the harness loaded
before the session did anything. The session did not choose it and cannot
reduce it except by ending - and it is therefore also the floor a reset
restarts at, which is what makes it the interesting denominator rather than
just an overhead.

`context` is the most recent request: what every further turn now resends.

`spend` is the difference: what this session has added by its own reading,
searching and writing. It is the only one of the three the session controls.

Which of them the budget is stated against was `PL-W80S`'s question, and
the project owner chose `spend` (2026-09-21). This script deliberately decides
nothing - it prints the reading and stops, per `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work": the decidable half is finding the number, and the
judgment half is what to do about it.

**What it cannot tell you.** It reads the transcript of the session whose id is
in `CLAUDE_CODE_SESSION_ID`, so it answers only for the session that runs it; a
subagent's context is in a transcript of its own and is not counted here, which
is correct, since a subagent's transcript never enters this context. After a
compaction the series is not monotonic and `spend` measures from the session's
original floor rather than from the post-compaction one. That is the reading
the budget wants, since `CLAUDE.md` now resets a session with `/compact`
(`PL-YJG1`): what the compacted context holds above the floor it started at is
what the next item has to fit beside. Untested, since no compaction has been
observed in a measured session.

Per `.claude/rules/apparatus-standard.md`, an answer here has to be true or has
to say what it could not read: records that fail to parse, and assistant
records carrying no usage block, are excluded from the numbers and counted back
on an `unread` line rather than rounded off. Finding no transcript at all is
not a zero - it exits non-zero and names the paths it looked in.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

TRANSCRIPT_ROOT = "projects"


@dataclass(frozen=True)
class Request:
    """One API request, as the transcript recorded it."""

    request_id: str
    context: int
    output: int
    timestamp: str


@dataclass(frozen=True)
class Reading:
    """What a session's transcript says about its own context.

    `unread` carries what was skipped, so a partial read never leaves here
    dressed as a complete one.
    """

    requests: tuple[Request, ...]
    turns: int
    unread: int

    @property
    def baseline(self) -> int:
        return self.requests[0].context if self.requests else 0

    @property
    def context(self) -> int:
        return self.requests[-1].context if self.requests else 0

    @property
    def spend(self) -> int:
        return self.context - self.baseline


def transcript_path(session_id: str, config_dir: Path) -> Path | None:
    """Locate `session_id`'s transcript, or None.

    Matched on the session id rather than on the directory name, which is the
    working directory with its separators rewritten by a rule this script would
    otherwise have to guess at and keep in step with.
    """
    root = config_dir / TRANSCRIPT_ROOT
    if not root.is_dir():
        return None
    for candidate in sorted(root.glob(f"*/{session_id}.jsonl")):
        if candidate.is_file():
            return candidate
    return None


def read(text: str) -> Reading:
    """Parse a transcript into a Reading.

    Several assistant records share one `requestId` - the harness writes one
    per content block - and they report the same usage, so the first of each
    wins and the rest are duplicates rather than further spend. Sidechain
    records belong to a subagent and are skipped: that context was never in
    this session's window.
    """
    seen: set[str] = set()
    requests: list[Request] = []
    turns = 0
    unread = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            unread += 1
            continue
        if not isinstance(row, dict) or row.get("isSidechain"):
            continue

        kind = row.get("type")
        message = row.get("message")
        message = message if isinstance(message, dict) else {}

        if kind == "user":
            # A real user message starts a turn; a tool result continues one.
            if "toolUseResult" not in row and not row.get("isMeta"):
                turns += 1
            continue
        if kind != "assistant":
            continue

        usage = message.get("usage")
        if not isinstance(usage, dict):
            unread += 1
            continue

        request_id = str(row.get("requestId") or message.get("id") or "")
        if not request_id or request_id in seen:
            continue
        seen.add(request_id)

        context = sum(
            int(usage.get(field, 0) or 0)
            for field in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
        )
        requests.append(
            Request(
                request_id=request_id,
                context=context,
                output=int(usage.get("output_tokens", 0) or 0),
                timestamp=str(row.get("timestamp") or ""),
            )
        )

    return Reading(requests=tuple(requests), turns=turns, unread=unread)


def report(reading: Reading) -> list[str]:
    """The four lines a session reads before deciding whether to start an item."""
    over = ""
    if reading.baseline:
        over = f", {reading.spend / reading.baseline:.0%} over baseline"
    lines = [
        f"context   {reading.context:>9,}   now",
        f"baseline  {reading.baseline:>9,}   first request of this session",
        f"spend     {reading.spend:>9,}   this session's own work{over}",
        f"turns     {reading.turns:>9,}   user message(s), across "
        f"{len(reading.requests):,} request(s)",
    ]
    if reading.unread:
        lines.append(
            f"unread    {reading.unread:>9,}   record(s) skipped; the numbers above exclude them"
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--series", action="store_true", help="print the context of every request, oldest first"
    )
    parser.add_argument("--json", action="store_true", help="print the reading as JSON")
    args = parser.parse_args(argv)

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    config_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude")).expanduser()

    if not session_id:
        print(
            "context_reading: CLAUDE_CODE_SESSION_ID is unset, so this session's "
            "transcript cannot be identified. No reading was taken.",
            file=sys.stderr,
        )
        return 2

    path = transcript_path(session_id, config_dir)
    if path is None:
        print(
            f"context_reading: no transcript for session {session_id} under "
            f"{config_dir / TRANSCRIPT_ROOT}/*/. No reading was taken.",
            file=sys.stderr,
        )
        return 2

    reading = read(path.read_text(encoding="utf-8", errors="replace"))
    if not reading.requests:
        print(
            f"context_reading: {path} holds no assistant record with a usage "
            "block. No reading was taken.",
            file=sys.stderr,
        )
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "session_id": session_id,
                    "transcript": str(path),
                    "context": reading.context,
                    "baseline": reading.baseline,
                    "spend": reading.spend,
                    "turns": reading.turns,
                    "requests": len(reading.requests),
                    "unread": reading.unread,
                },
                indent=2,
            )
        )
        return 0

    print("\n".join(report(reading)))
    if args.series:
        print()
        for request in reading.requests:
            print(f"{request.timestamp[:19]}  {request.context:>9,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
