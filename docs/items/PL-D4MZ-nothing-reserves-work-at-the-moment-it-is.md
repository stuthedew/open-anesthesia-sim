---
id: PL-D4MZ
title: Nothing reserves work at the moment it is recommended, so two sessions handed the same closing recommendation both start it
priority: P2
effort: M
status: done
classes: infra
feature: parallel-sessions
touches: .claude/rules/instruction-writing.md
added: 2026-09-02
closed: 2026-09-04
verify: python3 tools/doc_check.py check && grep -qF 'post_turn_summary.needs_action' .claude/rules/instruction-writing.md
---

**Problem.** Every guard this project holds against two sessions doing one
piece of work keys on an item id observed in a **pushed ref** or a **renamed
session title**. `plan.recommend` excludes in-flight ids from `docket next`
(`PL-5KR2`); `docket show` and `docket triage` mark an item `IN FLIGHT` and
name the refs they could not read (`PL-PRHN`); the `docket` skill adds a
`list_sessions` scan for a session that has pushed nothing (`PL-SK88`). All of
it fires when a session **starts** an item.

The collision the project owner reports is created one step earlier. Several
sessions finish around the same time; each closes with a next-steps block,
which rule 14 of `.claude/rules/instruction-writing.md` requires of every
reply; the owner agrees with each; and two sessions begin the same work.
Reported 2026-09-02 as having happened more than once, most often on
repository housekeeping rather than on queue items.

**Why it matters.** A recommendation is prose in a chat reply. It sits in no
ref, no branch, no item field and no session title, so at the moment the
collision is created there is nothing for any existing mechanism to see — and
those mechanisms are not failing. They answer "is anybody on this item?"
correctly; nobody is, yet.

Determinism is what makes this a systematic collision rather than a
coincidence. `docket next` ranks one store the same way for every caller, so
two sessions asking the same question get the same answer *by design*. The
property that makes the queue trustworthy everywhere else is the one
generating the duplicates here, and it gets worse as sessions get better at
converging on the same judgment.

The price is what `PL-PRHN` measured: a session and a merge conflict, against
a queue of ~98 open items where sending the second session somewhere else
costs almost nothing.

**Where.** Undecided — choosing the mechanism *is* this item, and it wants a
design round rather than an implementation. Four directions, with what each
costs:

- **Reserve at recommendation time.** The closing block writes a claim a later
  `docket next` can read. Closes the window properly; poisons the queue with
  reservations on work the owner never approved, so it needs an expiry and a
  way to tell a live claim from an abandoned one — the same problem
  `bin/docket stranded` already solves for branches.
- **A lease with an owner and a timestamp**, taken at start and refreshed as
  work proceeds. The textbook answer; adds a second state store to keep
  honest, and the container is ephemeral, so a lease routinely outlives the
  session holding it.
- **Recommend a spread rather than a rank.** Have the closing block offer work
  keyed to something that differs per session, so two sessions converging on
  the same store do not converge on the same item. Cheapest by far and needs
  no new state; it deliberately degrades `docket next`'s "best item first",
  which is the ranking's whole point.
- **Do nothing at recommendation time and make detection cheaper instead.**
  Accept the duplicate start and let `PL-YHD3` (a yield rule for two sessions
  that discover each other) end it early. Costs the duplicated minutes before
  detection; costs no new machinery at all.

`PL-CP74` (unfiled housekeeping carries no id, so the guards are blind to it)
is the other half of the reported case and stands alone. `PL-YHD3` is
independent of whatever this decides: the `docket` skill already records that
"two sessions starting in the same minute still race", so a yield rule is
needed under every design above, including the ones that work.

**Done when.** The mechanism is chosen and recorded with the reasoning, and
either implemented or split into the items that implement it. A session that
closes with a recommendation, and a session that acts on one, both have a
documented answer to "is anybody else about to do this?" that does not depend
on the other session having pushed first.

**Decision needed.** Which of the four directions under **Where** does this
project take, and is any mechanism warranted at all?

The choice is not free in either direction. A reservation store is a second
piece of state to keep honest in an ephemeral container, and this project has
already paid for one such mechanism (`bin/docket stranded`) to recover what
another leaves behind. Doing nothing costs the duplicated minutes before two
sessions notice each other, which `PL-YHD3` (which of two sessions yields)
bounds independently of whatever is decided here.

**Recommended: decide this against `PL-CP74`, `PL-MC8Z` and `PL-QTSB` rather
than on its own.** Those three are the cheap, already-shaped parts of the
same reported problem - file housekeeping under an id, the file-overlap
question in the start-an-item guard, and an in-flight mark on a `docket
check` advisory - and each removes a slice of the collisions this item would
otherwise have to catch. What is left over after all three have landed is the
real size of the problem a reservation mechanism would be built for, and it
may be small enough that direction four is the answer. That sequencing is
itself the recommendation; the design round is worth having only once the
remainder is known.

**Design round, 2026-09-04: the remainder, measured.** The sequencing above is
spent. `PL-CP74` (file housekeeping under an id) landed in v0.3.7, `PL-MC8Z`
(the file-overlap question in the start-an-item guard) in v0.3.5, `PL-QTSB` (an
in-flight mark on a `docket check` advisory) was dropped, and `PL-YHD3` (which
of two sessions yields) landed in v0.3.8. So the question this item deferred -
how big is what is left - is now answerable, and the answer is that it is not
small, and that it is not shaped the way this brief assumed.

*The remainder is id-less work.* Every collision recorded since the brief was
written is on work that carries no `PL-` id at the moment it is recommended.
`PL-66FP` is the worked example: two sessions cut v0.3.7 within the same hour
on 2026-09-04, one merging as #301 and the other reaching #302 with a duplicate
version bump, lock, release note, seven `milestone:` stamps, a version-table row
and a whole baseline section, all of which had to be discarded at the merge.
`branch_id_check` prints "a release commit, which owes no id" for exactly that
work, so no id-matching guard could have seen it - and the guards `PL-CP74` and
`PL-MC8Z` added are id-matchers too. They removed the slice of the problem that
had ids. What is left is the slice that never had one, which is also the slice
whose per-collision cost is highest.

*The premise about visibility is false, and that is what changes the answer.*
This brief says a recommendation "sits in no ref, no branch, no item field and
no session title, so at the moment the collision is created there is nothing for
any existing mechanism to see". There is. The harness writes every session's
closing recommendation to `post_turn_summary.needs_action`, returned by the same
`list_sessions` call the `docket` skill already makes at item-start for the
title read `PL-SK88` added. It is written automatically at the end of a turn, so
it does not depend on any session following a rule; it is absent mid-turn and
present exactly once a turn has closed, which is when a recommendation exists;
and it clears when the session is archived, so it expires without anybody
maintaining an expiry.

Read on 2026-09-04 it carried both collisions:

- Retrospective. `session_012ZXvmV` closed with "Confirm 0.3.7 release or pass"
  and `session_01XN8mu1` with "confirm version (0.3.7 or other) to cut release",
  both live at the same time. That is `PL-66FP` visible in the session list
  before it happened.
- Live. `session_01M5UJAm` closed with "tag v0.3.8 ... before merging #313" and
  `session_01JwiP9q` with "git fetch origin main && git tag -a v0.3.8 ... && git
  push origin v0.3.8". Two sessions, one recommendation, neither able to see the
  other.

*What that does to the four directions.* Direction one was costed as a new
reservation store needing an expiry and an abandoned-claim rule; the store
exists, is populated, and expires on its own, so what it actually costs is one
field added to a read the skill already performs. Direction three is already
implemented in its principled form - the digest's `By lane, for a second
session:` line is a spread, and a stable one, which a randomized rank would not
be. Direction two remains what it was. Direction four remains available and is
no longer free: it leans on `PL-YHD3`, which resolves two branches carrying one
id, and the remainder has no id for it to resolve on.

*The decidable half belongs in code, and it is already an item.* `PL-66FP`
proposes that `bin/docket release` refuse or warn when the version it is about
to write already exists on the default base, readable from `git show
origin/<base>:pyproject.toml` with no network beyond a fetch. That is a `make
check`-tier answer for the single most collision-prone id-less change, and it is
independent of whatever this item decides.

**Decision, 2026-09-04 (project owner).** Direction one - reserve at
recommendation time - built as a *read* of `post_turn_summary.needs_action`
rather than as the new reservation store the brief costed it as. Recorded as a
bullet in rule 14 of `.claude/rules/instruction-writing.md`, which is where it
fires: rule 14 requires a closing block of every reply, so the check runs at the
moment the recommendation is written, in every session, without the `docket`
skill having to be loaded.

*Why resident rather than routed.* The four dispositions in `CLAUDE.md` were
weighed. It is not a check or a script, because the decidable half - is there
another live session holding an open recommendation - is worth nothing without
the judgment half, which is whether that session's prose describes the same work
as yours; scripting that would be the guessed-judgment failure `CLAUDE.md`
warns about. It is not a skill, because the collisions observed came from
sessions that had no reason to load one: `session_01JwiP9q` was working a
product item when it closed recommending the v0.3.8 tag. It is not path-scoped,
because no file read precedes writing a closing block. That leaves resident,
which is the right answer on `CLAUDE.md`'s own test - a session writing its
closing block would not think to look anything up. The cost is 18 lines on the
resident total, against a measured collision cost of one session's release work.

*Why not the other three.* A lease rebuilds by hand the store the harness
already keeps. Spreading the rank is already implemented in its principled form
- the digest's `By lane, for a second session:` line is a stable spread, which a
randomized rank would not be - and it modifies `docket next`, which is not where
these collisions happen. Doing nothing leans on `PL-YHD3` (which of two sessions
yields), which resolves two branches carrying one id, and the remainder has no
id for it to resolve on.

*What it deliberately does not do.* It shrinks the window rather than closing
it, on the same bound as every other guard here: two sessions writing closing
blocks in the same minute still collide. The match is a judgment on another
model's prose. A session still mid-turn has not written its `needs_action` yet.
So it warns and never certifies - finding nothing means nothing, finding
something is decisive - which is the same reading `PL-SK88` (the session-title
read) established for the item-start scan. Its one structural advantage over
that read is that the field is written by the harness rather than by a rule
anybody has to follow, so its reliability is bounded by the reading session's
behavior rather than by the other session's.

*The code half stands alone.* `PL-66FP` (two sessions cut the same release
independently) carries the decidable guard - `bin/docket release` refusing a
version already on the default base - and is independent of this decision.

**First application, 2026-09-04.** The rule caught a duplicate on its first
real use, against the closing block of the session that wrote it. Two replies
in this session had already asked the project owner to tag v0.3.8. Running the
check before repeating it a third time returned three `IDLE` sessions all
asking for the same thing: `session_016tdyzs` ("merge PR #316 and tag
v0.3.8"), `session_01HAk6A9` ("(1) tag v0.3.8 or say go to push; (2) confirm
0.3.9 as version") and `session_01M5UJAm` ("(1) git tag -a v0.3.8 e64ab14 -m
'v0.3.8' ... (2) merge PR #317"). The request was a fourth copy, and the tag was
genuinely still missing in all four - so the duplication was not of the work but
of the *ask*, which is the cheaper half of the same failure and the half that
happens far more often.

Worth recording because it is the case the brief did not anticipate. It reasoned
about two sessions both *starting* one piece of work; what the check finds most
of the time is several sessions queueing the same request at one owner, who then
has to work out that four lines are one action. The remedy is the same either
way - name the sessions already asking rather than asking again - and the second
case is the one that recurs.
