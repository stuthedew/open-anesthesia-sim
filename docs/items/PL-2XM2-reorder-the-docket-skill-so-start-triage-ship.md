---
id: PL-2XM2
title: Reorder the docket skill so start, triage, ship and close-out survive the 5,000-token post-compaction truncation
status: untriaged
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
