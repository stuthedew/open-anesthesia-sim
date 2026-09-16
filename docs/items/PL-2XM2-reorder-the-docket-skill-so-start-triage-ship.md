---
id: PL-2XM2
title: Reorder the docket skill so start, triage, ship and close-out survive the 5,000-token post-compaction truncation
priority: P2
effort: M
status: needs-decision
classes: session-cost, docs
feature: worker-instructions
touches: .claude/skills/docket/SKILL.md
added: 2026-09-16
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
