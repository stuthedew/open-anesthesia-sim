---
id: PL-D4MZ
title: Nothing reserves work at the moment it is recommended, so two sessions handed the same closing recommendation both start it
status: untriaged
feature: parallel-sessions
added: 2026-09-02
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
