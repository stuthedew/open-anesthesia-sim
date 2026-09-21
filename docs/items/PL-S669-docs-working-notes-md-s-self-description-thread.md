---
id: PL-S669
title: docs/WORKING_NOTES.md's self-description thread has no open item left after PL-XF89 closed, so the file's own deletion policy applies and nothing has decided whether its rejected-drafts record earns its place
priority: P3
effort: S
status: done
classes: docs
feature: project-introduction
milestone: v0.5.2
touches: docs/WORKING_NOTES.md
added: 2026-09-21
closed: 2026-09-21
pr: 871
verify: python3 tools/doc_check.py check && ! grep -q 'one-line self-description' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's self-description thread has no open item left after PL-XF89 closed, so the file's own deletion policy applies and nothing has decided whether its rejected-drafts record earns its place

**Problem.** `docs/WORKING_NOTES.md` § "Settled: the project's one-line
self-description" cites `PL-4MHK`, `PL-N092` and `PL-XF89`, and all three are
now `done`. The file's preamble says a fully resolved thread's "entry here
should be deleted rather than left stale", and nobody has made that call for
this one.

**Why it is not obvious, which is why it is an item rather than a fix-now.**
The thread is *accurate* as of `PL-75R0` - its three statements, the settled
scope word and the educational-only limit were all repaired against the tree
on 2026-09-21. What is undecided is whether its record still earns its place.
The case for keeping it is the block headed "What was tried, and why each
direction failed", three rejected drafting directions "recorded so the next
attempt starts past these rather than at them". The case for deleting it is
that the wording is settled and there is no next attempt: `README.md`, the
GitHub About field and `pyproject.toml` each carry their sentence, and
`PL-XF89`'s own brief holds the reasoning for the one word they disagreed on.
That is `PL-DG84`'s "whether the outcome is recorded somewhere that maintains
itself" test, applied to one section, and a reasonable person could answer it
either way - which is what puts it outside `CLAUDE.md`'s fix-now test 3.

**It is an instance `PL-DG84`'s shipped advisory will never name**, and that
is the coverage statement rather than a complaint. Clause 1 requires the
heading to begin `Open`, and this one began "Mostly settled", so the signal
catches a resolved thread only while its heading is *also* wrong. `#861` added
the preamble paragraph that closes the gap from the other side - "Head an open
thread `Open thread:` or `Open:`, and a resolved one with what it resolved to
- `Settled:`, `Decided:`, `Measured`, `Built`, `Shelved`". "Mostly settled"
was in neither list, which made this thread the first test of that convention.
`PL-75R0` has since renamed it to `Settled:` - see below - so what is left
here is the deletion judgment alone.

**Measured after `PL-75R0`, for whoever picks this up:** `bin/docket check`
names exactly **one** thread in this file - § "Open thread: what makes
desflurane wash out too fast" - which the file's own text declares a correct
and permanent fire. So this item is not competing with a backlog; it is the
next instance, and the advisory cannot see it.

**One unverified line goes with it.** The thread closes: "Repository topics
were proposed in the same discussion and are still not applied; they are
independent of the wording and can be set whenever." The GitHub search API's
repository object for `stuthedew/open-anesthesia-sim` returned no `topics`
array on 2026-09-21, which does not distinguish "none set" from "not returned
by this endpoint", so the sentence was left alone rather than repaired on a
guess. Settle it with a call that does report topics, and either delete the
sentence with the thread or correct it.

**Where.** `docs/WORKING_NOTES.md`, § "Settled: the project's one-line
self-description".

**The heading question is closed, and the way it closed is worth the four
lines.** `PL-75R0` renamed it to `Settled:` and `tools/doc_check.py` failed
with two errors: `PL-XF89`'s brief quotes the old heading twice as a section
citation, and `PL-XF89` is `done`. `.claude/rules/citation-drift.md` treats a
closed brief as a historical record that is not repaired, so the rename was
reverted and filed here instead - the check was refusing on the exact ground
the ratified rule says is not a finding. `PL-ZM8P` landed that same day in
`#866`, pointing `_quoting_sources` at `_live_item_briefs` so a closed brief
is no longer held to current prose, and `PL-75R0` merged it and re-applied the
rename: 0 errors where there were 2. Nothing here is blocked on it any more.

**Done when.** The thread is either deleted, with a line in the reply saying
what carries its record, or kept with a sentence saying why the rejected-drafts
block is still worth its space; and the repository-topics claim is verified
rather than assumed. The heading is no longer part of this: `PL-75R0` settled
it.

**Found.** 2026-09-21, while closing `PL-75R0` (deleting the resolved
"the repository has no README" thread from the same file). The two threads are
adjacent and share `PL-N092`; repairing the drift in this one was inside
`.claude/rules/citation-drift.md`'s repair-in-place clause, and deleting it
was not.

**Why it matters.** `docs/WORKING_NOTES.md` is read through `bin/docket show
<id>`, which splits the file at its `##` headings and points a session only at
threads naming its item's id. A resolved thread left in place is therefore not
merely untidy: it is 72 lines of the 95 KB every reader of the file pays for,
recording repository state the preamble explicitly excludes ("The repository's
own current state is not a thread here"), with no mechanism that will ever
correct it when `README.md` or `pyproject.toml` moves underneath it. The file's
deletion policy exists because a stale thread here is read as current.

**Decision needed.** Delete the thread, or keep it with a sentence saying why
the rejected-drafts block still earns its space.

## Answered 2026-09-21: deleted, because every part of the record has a better carrier and the thread is unreachable

**The fact the brief above did not have: the thread cannot be discovered.** All
three ids it cites — `PL-4MHK`, `PL-N092`, `PL-XF89` — are `done`, and `show`
keys on ids. No open item cites them, so no session will ever be pointed at
this section again. That settles the case *for* keeping it, which was that the
rejected-drafts block is "recorded so the next attempt starts past these rather
than at them": a record the project's own discovery path cannot surface is not
available to the next attempt, whatever it says.

**Where each part of the record went, checked against the tree rather than
assumed.** This is the line `Done when` asks for:

1. **The three statements and their wording** — `README.md`'s opening sentence,
   `pyproject.toml`'s `description`, and the GitHub "About" field each carry
   their own sentence. Those are
   the artifacts, so they maintain themselves; the notes copy was a snapshot of
   them with nothing keeping it true.
2. **The deliberate `inhaled`/`volatile` split, and why** — carried three times,
   each at the moment a session needs it. `pyproject.toml` carries a comment
   directly above its `description` key, which `PL-XF89` put there
   because it is "the line a maintainer would otherwise 'fix' into agreement
   with README". `README.md` § "What it does not simulate" states the split,
   the reason, and the falsifier ("nitrous oxide is a planned substance") for
   the reader-facing side. `PL-XF89`'s brief holds the full reasoning.
3. **Rejected drafting directions 1-3** — direction 2's substance, that the
   volatile set "is the current build rather than the goal", is carried by
   `README.md`'s paragraph above and by `ROADMAP.md`'s "Beyond" row sequencing
   intravenous agents at items 13-15. Directions 1 and 3 are records of drafts
   of a sentence now written three times over, with no next attempt pending.
4. **"Constraints any future draft has to meet"** — the block says itself that
   none of the three was why a draft was rejected. The educational-only limit is
   `CLAUDE.md`'s presentation-correctness standard and is carried by all three
   statements; "anything claimed as planned must match `ROADMAP.md`" is
   `CLAUDE.md`'s rule that `ROADMAP.md` is authoritative; the 350-character
   field limit "has never been the binding constraint".
5. **The transferable lesson** — that a one-liner is easier to derive from a
   finished long document than to invent alongside one, which is why `PL-4MHK`
   needed no design round. It is one case's observation rather than a rule, and
   this brief is now its carrier.

**The repository-topics claim is verified, not assumed, and it was the one live
thing in the thread.** `GET /repos/stuthedew/open-anesthesia-sim/topics`
returned `{"names": []}` and the repository object's `topics` key returned `[]`
on 2026-09-21 — two endpoints that do report topics, against the search API's
omission that left this unresolved before. Topics are genuinely unset, so the
sentence was true. Setting them is a repository setting no session can reach,
so it is rehomed as `PL-VCJ2` rather than deleted with the thread.
