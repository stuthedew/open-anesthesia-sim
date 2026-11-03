"""PreToolUse hook on the Projects tools: refuse an unrecorded read or merge ask.

**What it refuses** (`PL-TLPH`). A Projects message whose text asks the owner
to read or merge a pull request, unless it carries the `Owner-ask:` line that
`bin/docket arm --owner-ask` prints. Everything else passes untouched:
progress replies, merge reports, and any message that matches none of `ASKS`.

**Why a hook and not more text.** Whether the owner may be asked was text for a
session to read, three times over. `PL-9KHK` changed the wording, `PL-DKBG`
narrowed what holds, and `PL-9JHM` made the ask an `Owner-ask:` record that
`arm` prints. On `#1612` and `#1676` a session still read `arm` through `head`,
missed the line saying to send nothing, and sent the owner a bare "read #N and
merge it". Text fails whenever it is read short, so this checks the message
itself, at the one moment it goes out.

**What an ask is: a listed phrase in a sentence that asserts it** (`PL-ZCF9`).
The hook decides in two steps. First, `ASKS` names the phrasings sessions have
used, the closing-block lines that carry them, and close variants of each. A
hand-off such as "over to you" or "your call" counts only in a sentence that
also names a pull request. A hand-off that reports a decision already recorded,
such as "recorded your choice", does not count (`PL-YGR6`). Second,
`unasserted` reads the context of each phrase found. It lets the phrase through
when the phrase is quoted, when it is negated, when its clause points at a
decision card, or when "each" or "both" puts it in the future. Its docstring
gives each rule and its limits.

Clinical text processing splits the problem the same way. ConText decides,
from words near a condition that a report names, whether the report asserts
the condition, negates it, puts it in the past or the future, or gives it to
someone other than the patient (Harkema H, Dowling JN, Thornblade T, Chapman
WW, J Biomed Inform 2009;42(5):839-851, doi:10.1016/j.jbi.2009.05.002). It
extends NegEx, which does this for negation alone (Chapman WW et al., J Biomed
Inform 2001;34(5):301-310, doi:10.1006/jbin.2001.1029).

Six items recorded messages that asked for nothing and were refused, between
2026-10-19 and 2026-11-03. Until `PL-ZCF9`, each fix exempted one phrasing from
one pattern, so the next phrasing in the same context was refused again. Each
rule in `unasserted` applies to every phrase in `ASKS`, so a new phrasing in a
context the rules know passes with no change. A new kind of context still needs a new
rule. A wording that `ASKS` does not name still passes, so a new one seen in a
thread is added there with a test row. A message that matches by accident is
told to reword. A false refusal costs a rewording, while a missed ask costs the
owner's attention, so each rule is narrow and a doubtful case is refused.

**Which tools: every Projects tool but a named few** (`PL-YN60`). The hook is
wired on every `mcp__hearthbot__` tool and reads every string in the call's
input, at any depth. It skips only the tools in `NOT_TO_THE_OWNER`, whose text
goes to another session or names a thread. It first listed the tools it read,
`reply`, `update_message` and `ask_decision`. The harness renamed them to
`post_message`, `edit_message` and `request_decision`, so a thread's edits and
decision cards went unchecked and nothing said so. Naming the skipped tools
instead means a renamed or new tool is checked until someone says otherwise. A
wrong refusal then costs a rewording and files an item, which is the direction
this hook leans. Nobody has read these tools' schemas, so the hook does not
guess which field holds the text (`PL-646J`).

**Which check: the one `arm` can answer for.** The hook cannot tell a thread
from the coordinator, because both post with `post_message`. So it asks `arm`
about this checkout's branch, which costs about two seconds and no fetch
(measured 2026-10-19), and only for a message that matches `ASKS`.

- When `arm` prints a recorded ask, the message must carry that line word for
  word. This is a thread driving its own pull request.
- Otherwise the message must carry a line in the form `arm --owner-ask`
  renders. This is the coordinator relaying a thread's ask from a checkout on
  no pull request's branch, where `arm` cannot answer (`PL-YV90`). It is also a
  thread whose `arm` says nothing may be sent, or cannot answer at all.
  `docket.arming.renders_owner_ask` recognizes the form from the templates the
  renderer uses, so the hook holds no copy of it.

This check cannot tell the recorded line from a well-formed wrong one. Having
`arm` answer for a named pull request would, at the cost of a fetch and a
worktree per post (project owner, 2026-10-24, ratified, over building that
now). Nobody has seen that failure. Until `PL-YN60` a thread on a pull request
with no recorded ask was refused outright; it now gets this check too, because
the hook can no longer tell it from the coordinator.

**Fails open only where it cannot read the call**: a payload that is not
JSON, or an error in the hook itself. A guard that breaks a thread's replies
costs more than the round it saves. A `bin/docket` that is missing, times out
or cannot answer falls back to the rendered-line check above, which refuses
only an ask. `OWNER_ASK_GUARD_ARM` names a Python script run in place of
`arm` for the tests, and is set nowhere else. `NO_ASK` is read from
`docket.arming`, found through `shell_split.py` as the Bash guards find it,
and so is `renders_owner_ask`.

Standard library only, since a hook runs before any virtualenv is known.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hook_input
import shell_split  # noqa: F401 - puts docket's src on sys.path

# isort: split
from docket.arming import NO_ASK, renders_owner_ask
from docket.lines import split_lines

#: The prefix of every Projects tool. The hook is wired on all of them.
PROJECTS_TOOL = "mcp__hearthbot__"

#: The Projects tools whose text does not reach the owner as a message: a
#: message to another session, or a thread's name. Every other Projects tool is
#: read, so a tool the harness renames or adds is checked until it is named
#: here (`PL-YN60`). Names read from a thread's tool list on 2026-11-02.
NOT_TO_THE_OWNER = frozenset(
    PROJECTS_TOOL + name for name in ("message_coordinator", "message_thread", "rename_thread")
)

#: Where an imperative starts: a line, a list item or a sentence.
_START = r"(?:^[ \t]*(?:[-*+]|\d+[.)])?[ \t]*|[.!?:;][ \t]+)"

#: Verbs that report a decision the owner has already made, as in "recorded
#: your choice" or "your choice is recorded". A noun hand-off in either of
#: those forms is a status report, not an ask. The hook refused two such
#: reports during the v0.6.0 cut on 2026-10-20 (`PL-YGR6`). The list is short
#: on purpose: a report worded some other way is still refused, which is the
#: direction this hook leans.
_RECORDED = ("recorded", "noted", "applied", "logged", "saved", "followed", "implemented")

#: A noun hand-off that is the subject of a recording verb in the passive:
#: "your choice on the card is recorded", "your call has been noted". At most
#: three words may come between the noun and the verb, and none of them may
#: start a question, so "your call on whether #1688 is applied" is still an ask.
#: A verb followed by "when", "once", "after", "if" or "as soon" describes a
#: decision still to come, so "your choice is applied when you merge #1700" is
#: still an ask too.
_REPORTED_AFTER = (
    r"(?!(?:[ \t]+(?:on|for|about|in|from|at)"
    r"(?:[ \t]+(?!(?:whether|if|which|what|how|who|when)\b)[\w#'-]+){1,3})?"
    r"[ \t]+(?:is|was|has[ \t]+been|have[ \t]+been)[ \t]+(?:now[ \t]+)?"
    r"(?:" + "|".join(_RECORDED) + r")\b"
    r"(?![ \t]+(?:when|once|after|if|as[ \t]+soon)\b))"
)

#: A noun hand-off that is the object of a recording verb: "recorded your
#: choice". Python's lookbehind needs a fixed width, so each verb gets its own,
#: with exactly one space or tab before "your".
_REPORTED_BEFORE = "".join(rf"(?<!\b{verb}[ \t])" for verb in _RECORDED)

#: Words that hand a decision to the owner. They are an ask only beside a pull
#: request, since "the colour is your call" asks for no read. A noun hand-off
#: that reports a recorded decision is not one either (`_RECORDED`). The group
#: named `core` is the hand-off itself, which `unasserted` reads around.
_HANDOFF = (
    r"(?P<core>\b(?:over[ \t]+to[ \t]+you|up[ \t]+to[ \t]+you"
    r"|"
    + _REPORTED_BEFORE
    + r"your[ \t]+(?:call|decision|choice|go)\b"
    + _REPORTED_AFTER
    + r"|let[ \t]+me[ \t]+know|thoughts[ \t]+on|what[ \t]+do[ \t]+you[ \t]+think)\b)"
)

#: A pull request named by number or by name.
_PULL_REQUEST = r"(?:#\d+|\bpull[ \t]+requests?\b|\bprs?\b)"

#: The text between two phrases in one sentence: no sentence end or line break.
_SAME_SENTENCE = r"[^.!?\n]{0,80}?"

#: A pull request held for the owner: "It waits on your read", "#1676 is ready
#: for your review". The group named `core` is the whole hold.
HOLD_FOR_YOUR_READ = (
    r"(?P<core>\b(?:waiting|waits|wait|awaiting|awaits|needs|need|ready)[ \t]+"
    r"(?:(?:for|on)[ \t]+)?your[ \t]+(?:read|review|approval|merge|go-ahead)\b)"
)

#: A pull request named in any form.
_NAMES_A_PULL_REQUEST = re.compile(_PULL_REQUEST, re.IGNORECASE)

#: The end of a sentence: a full stop, question mark or exclamation mark
#: followed by a space or the end of the text, or a line break. A dot inside
#: `MODEL.md` or `v0.7.0` does not end one.
_SENTENCE_END = re.compile(r"[.!?](?=\s|$)|\n")

#: The end of a clause, for the negation and decision-card rules: a sentence
#: end, a comma, semicolon, colon, bracket or dash, or a word that opens a new
#: clause. Short clauses keep a rule from reaching an ask in the next clause,
#: so a doubtful case is refused.
_CLAUSE_END = re.compile(
    r"[.!?](?=\s|$)|[\n,;:()\[\]\u2013\u2014]|[ \t]-[ \t]"
    r"|\b(?:and|but|so|because|while|although|though|whereas|however|unless|until)\b",
    re.IGNORECASE,
)

#: Text between two straight double quote marks on one line. `asked` finds
#: quotations in a copy of the text whose backticks are double quote marks, so
#: a code span counts too.
_DOUBLE_QUOTED = re.compile(r'"([^"\n]*)"')

#: Text between two single quote marks on one line. The opening mark must
#: start a word and the closing mark must end one, so the apostrophes in
#: "it's" and "#1688's" open and close nothing.
_SINGLE_QUOTED = re.compile(r"(?<![\w'])'(?=[^\s'])((?:[^'\n]|'(?=\w))*?)(?<=[^\s'])'(?!\w)")

#: A negation just before an ask phrase: "does not need your read", "isn't
#: ready for your review", "no longer needs your read", "is not your call",
#: "merge without waiting on your read".
_NEGATED_JUST_BEFORE = re.compile(
    r"(?:\bnot|n't|\bnever|\bwithout|\bno[ \t]+longer)[ \t]+(?:(?:be|been|yet|still)[ \t]+)?$",
    re.IGNORECASE,
)

#: A clause that opens with a negative subject: "Nothing below needs your
#: read", "None of them need your review", "No pull request waits on your
#: read". At most three words may come between the negative and the ask
#: phrase, and none of them may be a pull request's number.
_NEGATIVE_SUBJECT = re.compile(
    r"^[^\w#]*(?:\d+[.)][ \t]*)?(?:nothing|none|neither|no)\b(?:[ \t]+[\w'/.-]+){0,3}[ \t]+$",
    re.IGNORECASE,
)

#: An exception that follows a negated ask and names a pull request, as in
#: "Nothing needs your read except #1950" or "#1950 doesn't need your read,
#: but #1951 does". The sentence then asks after all.
_EXCEPTION = re.compile(
    r"\b(?:but|except|other[ \t]+than|apart[ \t]+from|besides|save[ \t]+for|only)\b"
    + _SAME_SENTENCE
    + _PULL_REQUEST,
    re.IGNORECASE,
)

#: A decision card, named in a clause as where the owner's answer goes.
_DECISION_CARD = re.compile(r"\bcards?\b", re.IGNORECASE)

#: A future put on an ask phrase by a distributive subject just before it:
#: "each will wait for your read", "both would need your review", "each one is
#: going to be ready for your read". One word may come between the modal and
#: the phrase, as "be" does. The hook refused "each will wait for your read"
#: in a reply that planned pull requests not yet opened, on 2026-11-02
#: (`PL-VHMS`). The subject is a short list, not any word, because "I will
#: wait for your read", "Merging will wait for your go-ahead" and "This change
#: will need your review" are asks about a pull request that exists.
_FORETELLING_SUBJECT = re.compile(
    r"(?:^|[^\w'#-])(?:each(?:[ \t]+one|[ \t]+of[ \t]+them)?|both(?:[ \t]+of[ \t]+them)?"
    r"|all[ \t]+of[ \t]+them|every[ \t]+one)"
    r"[ \t]+(?:will|would|(?:is|are)[ \t]+going[ \t]+to)(?:[ \t]+\w+)?[ \t]+$",
    re.IGNORECASE,
)


def quotations(shown: str) -> list[tuple[int, int]]:
    """Where each quoted stretch of `shown` starts and ends, without its quote marks."""
    return [
        found.span(1)
        for quoted in (_DOUBLE_QUOTED, _SINGLE_QUOTED)
        for found in quoted.finditer(shown)
    ]


def _around(shown: str, ends: re.Pattern[str], start: int, end: int) -> tuple[int, int]:
    """Where the sentence or clause that holds `shown[start:end]` starts and ends."""
    begin = 0
    for found in ends.finditer(shown, 0, start):
        begin = found.end()
    following = ends.search(shown, end)
    return begin, following.start() if following is not None else len(shown)


def unasserted(shown: str, quoted: list[tuple[int, int]], start: int, end: int) -> bool:
    """Whether the ask phrase at `shown[start:end]` sits where it asks for nothing.

    Four rules read the phrase's context, and each applies to every phrase in
    `ASKS`:

    - **Quoted.** The phrase lies wholly inside quote marks or a code span
      that names no pull request, so it is a mention, as in a reply that lists
      what the hook counts (`PL-XR8B`, `PL-0W6J`). A quotation that names a
      pull request can be a thread's bare ask passed on, so it is still
      refused. "Reply 'Merge it'" is refused too, because the phrase there is
      the verb "Reply", outside the quote marks.
    - **About a decision card.** The phrase's clause names a card and no pull
      request, as in "waiting on your go-ahead on the decision card"
      (`PL-Q0TK`). The card is a `request_decision` call, which this hook
      reads like any other message, so the line points at an ask the hook has
      already checked.
    - **Negated.** "not", "n't", "never", "without" or "no longer" stands just
      before the phrase, or its clause opens with "nothing", "none", "neither"
      or "no", as in "Nothing below needs your read now" (`PL-VNRM`). An
      exception later in the sentence that names a pull request, as in
      "except #1950", makes it an ask again.
    - **Foretold.** `_FORETELLING_SUBJECT` stands just before the phrase and
      its sentence names no pull request, as in a plan for pull requests not
      yet opened (`PL-VHMS`). The rule reads only that sentence, so "#1944 is
      open. Each will wait for your read." passes. That is the hole it leaves.
    """
    if any(
        left <= start and end <= right and _NAMES_A_PULL_REQUEST.search(shown, left, right) is None
        for left, right in quoted
    ):
        return True
    sentence = _around(shown, _SENTENCE_END, start, end)
    clause = _around(shown, _CLAUSE_END, start, end)
    if (
        _DECISION_CARD.search(shown, *clause) is not None
        and _NAMES_A_PULL_REQUEST.search(shown, *clause) is None
    ):
        return True
    before = shown[clause[0] : start]
    if (
        _NEGATED_JUST_BEFORE.search(before) is not None
        or _NEGATIVE_SUBJECT.match(before) is not None
    ) and _EXCEPTION.search(shown, end, sentence[1]) is None:
        return True
    return (
        _FORETELLING_SUBJECT.search(shown[sentence[0] : start]) is not None
        and _NAMES_A_PULL_REQUEST.search(shown, *sentence) is None
    )


#: The phrasings of an ask to read or merge a pull request (`PL-TLPH`). Each is
#: matched case-insensitively against the text with its Markdown emphasis
#: removed.
ASKS = tuple(
    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for pattern in (
        # "Read #1676 and merge it", "Please review PR #1612".
        _START + r"(?:please[ \t]+)?(?:read|review|look[ \t]+(?:at|over))[ \t]+"
        r"(?:and[ \t]+merge[ \t]+)?(?:(?:the[ \t]+)?(?:pull[ \t]+request|pr)[ \t]+)?#\d+",
        # "Read the pull request", "Review this PR".
        _START + r"(?:please[ \t]+)?(?:read|review)[ \t]+(?:the|this|its|my)[ \t]+"
        r"(?:pull[ \t]+request|pr)\b",
        # "Could you read it", "please merge".
        r"\b(?:please|can[ \t]+you|could[ \t]+you|would[ \t]+you)[ \t]+"
        r"(?:read|review|merge|approve)\b",
        # "It waits on your read", "ready for your review".
        HOLD_FOR_YOUR_READ,
        # `arm`'s own words, copied into a reply.
        r"\bwaits?[ \t]+on[ \t]+the[ \t]+owner'?s[ \t]+read\b",
        # "Say Merge it", "reply 'Merge it'". The verb is the `core`, so quote
        # marks around "Merge it" do not make the ask a mention.
        r"\b(?P<core>say|reply|send|type|give|answer|tap)[ \t]+(?:me[ \t]+)?[\"']?merge[ \t]+it\b",
        # "Merge it when you have read it."
        _START + r"merge[ \t]+it\b",
        # "Shall I merge?", "Merge #1676?"
        r"\b(?:shall|should|can|may)[ \t]+i[ \t]+(?:go[ \t]+ahead[ \t]+and[ \t]+)?merge\b",
        r"\bmerge[ \t]+(?:(?:pull[ \t]+request|pr)[ \t]+)?#\d+[ \t]*(?:now[ \t]*)?\?",
        # "Over to you for #1688", "#1688 is your call": a hand-off and a pull
        # request named in one sentence, in either order.
        _HANDOFF + _SAME_SENTENCE + _PULL_REQUEST,
        _PULL_REQUEST + _SAME_SENTENCE + _HANDOFF,
    )
)

#: How long `arm` may take. It answered in 2.2 s on 2026-10-19; the wiring
#: gives the hook 60 s, so this leaves room to fail open rather than be cut off.
ARM_TIMEOUT_S = 45


def every_string(value: object) -> list[str]:
    """Every string in `value`, at any depth of its dictionaries and lists, in order."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [found for item in value.values() for found in every_string(item)]
    if isinstance(value, list):
        return [found for item in value for found in every_string(item)]
    return []


def message_text(tool_name: str, tool_input: object) -> str | None:
    """The text a call would show the owner, or None for a tool this hook does not read."""
    if not tool_name.startswith(PROJECTS_TOOL) or tool_name in NOT_TO_THE_OWNER:
        return None
    if not isinstance(tool_input, dict):
        return None
    return "\n".join(every_string(tool_input))


def plain(text: str) -> str:
    """`text` without Markdown emphasis, quote marks made straight, for matching."""
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return re.sub(r"[*_`>]", "", text)


def asked(text: str) -> str | None:
    """The first phrase in `text` that asks the owner to read or merge, or None.

    Each match of `ASKS` is checked by `unasserted`, which reads its `core`
    group where the pattern has one and the whole match where it has none. A
    match that asks for nothing is skipped, and the search goes on from the
    character after its start, so an ask that overlaps it is still found.
    """
    # The two copies differ only in what replaces a backtick, so a position in
    # one is the same position in the other. Matching reads a backtick as a
    # space, so "Read `#1950`" is still an ask.
    quoted = quotations(plain(text.replace("`", '"')))
    shown = plain(text.replace("`", " "))
    for pattern in ASKS:
        position = 0
        while (found := pattern.search(shown, position)) is not None:
            core = found.span("core") if "core" in pattern.groupindex else found.span()
            if not unasserted(shown, quoted, *core):
                return found.group(0).strip(" \t.!?:;-*+")
            position = found.start() + 1
    return None


def squeezed(said: str) -> str:
    """`said` without emphasis, its quote marks straight and its spacing single, for matching."""
    return " ".join(plain(said).split())


def carries(text: str, line: str) -> bool:
    """Whether `text` holds `line` word for word, ignoring emphasis, case and spacing."""
    return squeezed(line).casefold() in squeezed(text).casefold()


def owner_ask(root: Path) -> tuple[int, str] | None:
    """The exit status and first line of `bin/docket arm --no-fetch --owner-ask`, or None."""
    override = os.environ.get("OWNER_ASK_GUARD_ARM")
    command = (
        [sys.executable, override]
        if override
        else [str(root / "bin" / "docket"), "arm", "--no-fetch", "--owner-ask"]
    )
    try:
        done = subprocess.run(
            command, cwd=root, capture_output=True, timeout=ARM_TIMEOUT_S, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode not in (0, NO_ASK):
        return None
    lines = [
        line.strip() for line in split_lines(done.stdout.decode("utf-8", "replace")) if line.strip()
    ]
    if not lines:
        return None
    return done.returncode, lines[0]


def mistaken(phrase: str) -> str:
    """What to do when the message was not an ask, so a wrong refusal is recorded.

    The refused session is the only one that sees a refusal, and it would
    otherwise reword and carry on, so a pattern of wrong refusals would never
    reach the owner. Filing an item leaves a record that outlives the session,
    and `bin/docket` flags a title filed more than once (project owner,
    2026-10-19, ratified, over a shared refusal log or no record, `PL-TLPH`).
    """
    quoted = phrase.replace('"', "'")
    return (
        "\n\nIf this message is not an ask, the hook is wrong. Record that before "
        "rewording, with:\n\n"
        f'    bin/docket new "owner_ask_guard.py refused a message that asked for nothing: '
        f'{quoted}"\n\n'
        "Then reword the message so that it does not read as an ask."
    )


def refusal(text: str, root: Path) -> str | None:
    """Why this message may not go to the owner, or None to let it through."""
    phrase = asked(text)
    if phrase is None:
        return None
    opening = f'This message asks the owner to read or merge a pull request ("{phrase}"). '
    answer = owner_ask(root)
    if answer is not None and answer[0] == 0:
        line = answer[1]
        if carries(text, line):
            return None
        return (
            opening + "This branch has a recorded Owner-ask, but the message does not carry it. "
            "Open the ask with this line, word for word, and keep the rest short:\n\n"
            f"    {line}\n\n"
            "That line is what the owner judges, so a bare 'read #N' or 'Merge it' without "
            "it is refused (PL-TLPH)." + mistaken(phrase)
        )
    if renders_owner_ask(squeezed(text)):
        return None
    said = (
        f"`bin/docket arm --owner-ask` says, for this checkout's branch:\n\n    {answer[1]}\n\n"
        if answer is not None
        else "`bin/docket arm --owner-ask` gave no answer for this checkout's branch.\n\n"
    )
    return (
        opening + "It carries no Owner-ask line. " + said + "On a thread's own branch, run "
        "`bin/docket arm` and read all of its output, not through head or tail: it says what "
        "to do. Usually that is to record `Owner-read: not needed - <why>` so the change "
        "merges on green, or, for a real decision or a high-risk change, to record an "
        "`Owner-ask:` and then send the line arm prints. When relaying a thread's ask, "
        "forward the thread's Owner-ask line word for word, or send the owner nothing about "
        "that pull request. On #1612 and #1676 a bare ask reached the owner (PL-TLPH)."
        + mistaken(phrase)
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    tool_name = str(payload.get("tool_name", ""))
    text = message_text(tool_name, payload.get("tool_input"))
    if not text:
        return 0
    reason = refusal(text, hook_input.project_root())
    if reason is None:
        return 0
    sys.stdout.write(
        hook_input.deny("owner_ask_guard", "bare-read-ask", reason, json.dumps(payload))
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    # A broken guard must never block a reply.
    except Exception:
        sys.exit(0)
