---
id: PL-S669
title: docs/WORKING_NOTES.md's self-description thread has no open item left after PL-XF89 closed, so the file's own deletion policy applies and nothing has decided whether its rejected-drafts record earns its place
status: untriaged
added: 2026-09-21
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
