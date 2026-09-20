---
id: PL-2XM2
title: Reorder the docket skill so start, triage, ship and close-out survive the 5,000-token post-compaction truncation
priority: P2
effort: M
status: done
classes: session-cost, docs
feature: worker-instructions
touches: .claude/skills/docket, tools/doc_check.py, docs/items
added: 2026-09-16
closed: 2026-09-20
payoff: the close-out, triage and start-an-item procedures still exist after a compaction, instead of CLAUDE.md's pointer to them resolving to nothing
verify: test "$(wc -c < .claude/skills/docket/SKILL.md)" -lt 20000 && test -f .claude/skills/docket/modes/close-out.md
---

**Problem.** Compaction re-injects an invoked skill body "capped at 5,000
tokens per skill and 25,000 tokens total ... Truncation keeps the start of the
file" ([context window](https://code.claude.com/docs/en/context-window)).
`.claude/skills/docket/SKILL.md` is 72,405 characters, roughly 18,100 tokens.
After any compaction, about 27% of it survives.

Measured section offsets before the fix, against a cap falling near 20,000
characters: `Mode: start an item` 29,100; `Mode: triage` 40,322; `Mode: ship a
release` 57,592; `Mode: close out an item` 64,725; `Always` 71,677. Every one
is dropped. `CLAUDE.md` routes close-out to this skill by name — "The `docket`
skill's close-out carries what `make check` decides for you and what it cannot"
— so after a compaction that pointer resolves to nothing, silently.

**Partly fixed in this session.** The `Always` block (728 characters) was moved
from the end of the file to char 1,251, with a note saying why it is pinned
there. A block named `Always` that only an uncompacted session can read was the
one placement it must not have.

**Left open, and the reason it was not done here.** Moving `start`, `triage`,
`ship` and `close out` above the line is a real ordering decision, not a lift:
the modes are currently in workflow order, which is how a session reads the
file when it is whole. Ordering by survival makes the truncated copy correct
and the whole copy harder to follow. The alternatives are to split the skill
into two files, or to compress the four modes enough that all of them fit under
the cap. That choice wants its own session.

**Not today's cause.** These sessions run a 1,000,000-token window and peaked
at 519,237, so none had compacted. This is latent, and it fires the first time
one does.

**Why it matters.** `CLAUDE.md` routes the close-out procedure to this skill by
name - "The `docket` skill's close-out carries what `make check` decides for you
and what it cannot". After a compaction that pointer resolves to nothing and
nothing says so, so a session finishes an item without the procedure that
defines finishing: the docs sweep, the gate report, the `--self` audit. That is
the silent-wrong-answer shape `CLAUDE.md` names, in the apparatus rather than in
a number. It is latent only because no session here has compacted yet.

**Done when.** The four modes a session acts on - start an item, triage, ship a
release, close out - are readable in the post-compaction copy by whichever route
is chosen, and the whole copy is still followable by a session that never
compacts.

**Decision needed.** Which of three routes: reorder the modes by survival, split
the skill into two files, or compress the four modes enough that all of them fit
under the cap. They trade the truncated copy's correctness against the whole
copy's readability differently, and the present workflow order is deliberate. A
session can take this one - it rests on how the file is read, not on what the
project wants.

**Decided 2026-09-20: split, and the other two routes were not close calls -
they are arithmetically impossible.** Taken by this session under the item's own
"a session can take this one".

The file had grown to 93,454 characters, about 23,400 tokens, from the 72,405
recorded above. The four modes this item is named for total 51,138 characters,
roughly 12,800 tokens - **2.6 times the whole 5,000-token cap**. So route 1,
reordering the modes by survival, cannot satisfy this item's own `Done when.` at
any ordering: put all four first and the last two are still cut off, while
`capture` and `recommend what to work on` get displaced out of the surviving
region to buy it. Route 3, compressing until they fit, needs the *file* under
about 20,000 characters - a 79% cut - which is deleting rules for being wordy,
and `CLAUDE.md` forbids exactly that.

**The mechanism, re-read rather than recalled.** The numbers quoted above are
right but the citation had moved; they are now on the skills page, which states
it as re-attaching "the most recent invocation of each skill after the summary,
keeping the first 5,000 tokens of each", with re-attached skills sharing 25,000
tokens and the oldest dropped entirely. The same page settles the route: only
the rendered `SKILL.md` enters the conversation, supporting files in the skill
directory load on demand when `SKILL.md` names them, and its explicit guidance
is "Keep `SKILL.md` under 500 lines. Move detailed reference material to
separate files."

**Built.** `.claude/skills/docket/SKILL.md` is now a 5,101-character front page,
about 1,275 tokens - a quarter of the cap, so it survives compaction whole with
room to grow. It keeps the intro, `Always`, `The two modes this queue serves`
and a dispatch table. The thirteen modes moved verbatim into seven files under
`.claude/skills/docket/modes/`, grouped by the moment a session is in, so a
session reads exactly one: `ideas`, `capture`, `picking`, `start`, `triage`,
`release`, `close-out`. Proven by round-trip - the slices concatenate back to
the original byte for byte - after a first attempt whose `awk` byte offsets
sheared three characters off every boundary against Python's character offsets.

**The hazard this introduces, and what holds it.** A router makes reading
optional in practice: a session can act on a table row instead of the file. So
the rows are pointers rather than summaries, and the dispatch carries an
explicit rule that reading the file first is not optional. This is also cheaper
than what it replaces - a capture during ideation now costs the front page plus
one mode file, about 19,000 characters, against 93,454 for the old body.

**What the split forced, all of it decidable and none of it optional.**
`DOC_GLOBS` in `tools/doc_check.py` matched only `SKILL.md`, so the mode files
carrying most of the skill's prose and all of its path citations would have gone
unchecked - it now reaches `.claude/skills/**/*.md`. Nineteen citations in
`docs/` named a section that had moved; six cross-references inside the skill
pointed at another file with no path; and seven open items carried a `verify:`
grepping `SKILL.md`, three of them **negative** greps that would have started
exiting 0 because the string moved rather than because the work was done. Those
now search `.claude/skills/docket/` and still fail correctly. Three line-number
citations turned out to have drifted onto unrelated passages already - the check
could only see that the line existed, not that it was the right one - and are
re-anchored to sections.
