---
id: PL-SK88
title: The in-flight answer needs a push to be true; a session-title read would close the window a push only shrinks
priority: P2
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md
added: 2026-09-02
closed: 2026-09-02
pr: 211
---

**Problem.** `bin/docket flight`, `show` and `next` answer "is anybody already
on this item?" by reading refs, so an item is invisible until the session
working it has *pushed*. The `docket` skill's "Mode: start an item" already
hardened the reading side — `git fetch origin` then `bin/docket show <id>` —
and records that it still failed: "Observed 2026-09-01: a session checked, was
told nothing was in flight, and a branch carrying the item was pushed four
minutes later — the owner caught it, not the tooling." Observed again
2026-09-02, from the other side: this session was told `PL-007` had been
started elsewhere, and `show PL-007` marked nothing, because that session had
not pushed.

**Why it matters.** Two sessions doing one item costs a whole session plus a
merge conflict; `PL-PRHN` records exactly that happening on a triage pass. The
reading side cannot be hardened further — the skill's own words are that a
clean result means "nothing visible", never "nothing" — so what is left is
either to make sessions push sooner, which shrinks the window, or to read a
signal that does not depend on a push, which closes it.

**The alternative.** Sessions are already named after the item they work
(`CLAUDE.md`, "Name the work after the item"), and the harness can enumerate
other sessions and their titles. A pre-start check that read those titles
would see a session that has committed nothing at all, which no ref-based
answer can.

**What it costs, and why this is a question rather than a plan.**
`subprojects/docket/` is standard-library-only and has to answer in a bare or
offline checkout — that premise is why `flight` and `show` read refs the
checkout already holds rather than calling anything. A session-title read
cannot live in `docket` without breaking it. So the shape would be a check the
*session* runs before starting, with `docket` unchanged, and the design
question is whether a guard that exists only inside one harness is worth
having beside one that works everywhere.

**Decision needed.** Should a pre-start session-title check exist at all,
given it can only ever work inside this harness?

The two answers produce different software. *Build it* and the start-an-item
guard becomes two checks: `docket`'s ref read, which works anywhere, and a
title read that works only where the harness exposes one - closing the window
for the sessions that have it, and leaving a guard that reads as authoritative
but silently degrades to nothing in a bare checkout or a different tool.
*Reject it* and the window stays open by the width of one push, mitigated by
the push-early rule the skill now carries, with the residual failure being two
sessions that start within a minute of each other.

The push-early half landed on 2026-09-02 and is not part of this item. What is
left is only whether to close the remaining window or accept it.

**Decision (2026-09-02): build it, in the narrow form below.** The check
exists, as prose in the `docket` skill's "Mode: start an item", beside the
fetch. It is not in `docket` and must not be.

*What the read actually returns, which settled it.* `list_sessions` from the
`claude-code-remote` MCP server was run against a twenty-session window on
2026-09-02. It returns more than titles: per session, the title, the branch
(`external_metadata.current_branches`), `session_status`, `status_bucket` and
`updated_at`. So archived and completed sessions can be excluded and a stale
one is visible by its timestamp, which removes the false-positive objection
before it is raised.

Coverage in that window: **nine of twenty titles carried an id, and three of
twenty branches did** - titles are the better signal and branches the worse,
because a harness-generated branch is named from the opening prompt and cannot
be renamed. Of the sessions demonstrably working one specific item, at least
three had never been renamed (`Transactional simulation step` was `PL-026`;
`Wash-in validation against human measurement` was `PL-9Y42`), so the rename
rule runs at roughly three in four.

The window also held a live instance of exactly the failure this item was
raised for, and it is what tipped the decision: a session titled `PL-007 -
make the payload/public-dataclass pattern self-evident`, running on branch
`claude/pl-nv9w-hws7tk`. The branch names `PL-NV9W`, which is finished; the id
`PL-007` appears **only** in the title. `docket show PL-007` marks nothing and
is right to - no ref carries it. A title read is the only mechanism in the
project that can see it.

*Why the "reads as authoritative, degrades silently" objection does not
sink it.* That risk is real and it is entirely a wording problem, which this
project has already solved twice - `format_unread`, and this skill's "a clean
result means 'nothing visible', never 'nothing'". The check is therefore
written one-directional: it may add a warning and may never contribute to a
clean answer. `docket show` stays the thing that answers, with its declared
bound. This matters more here than for the ref read, and the difference is
worth stating: `show` can *name* what it could not compare, and a title read
cannot - a session working an item under a generic title is indistinguishable
from a session working no item at all. A guard that cannot report its own gaps
must never be read as evidence of absence, which is what one-directional
means.

*Two sub-options rejected, so they are not re-argued.* **Putting the read in
`docket`** - no: the package is standard-library only and has to answer in a
bare or offline checkout, the premise `flight` and `show` are built on, and a
harness call breaks it. **A `docket` subcommand for the matching half**, fed
the session list on stdin, keeping the package offline and putting the rule in
code with tests - no, and this is the closer call: the matching is "does this
id appear in the title or the branch", a substring read of output already on
screen. A subcommand for it is a mechanism larger than its job, which is the
specific way `CLAUDE.md` says this project wastes a session.

*The arithmetic.* Two collisions are on record (2026-09-01, the four-minute
push; 2026-09-02, the triage collision `PL-PRHN`). Each costs a session plus a
merge conflict - the `PL-PRHN` one discarded most of one session's work. The
check costs one tool call at item start, roughly 6 KB of context, paid once per
item rather than per turn. Even at three-in-four coverage it is cheap against
what one collision costs.

**Done when.** A decision is recorded: either a session-title pre-start check
exists and the `docket` skill's start-an-item mode names it alongside the
fetch, or the option is recorded as rejected with the reason, so it is not
re-argued.
