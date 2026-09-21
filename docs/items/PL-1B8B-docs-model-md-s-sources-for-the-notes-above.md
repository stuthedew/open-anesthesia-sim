---
id: PL-1B8B
title: docs/MODEL.md's 'Sources for the notes above' block in Known limitations lists only the five vaporizer and altitude sources, but its heading claims every note in the section
priority: P3
effort: S
status: ready
classes: docs
touches: docs/MODEL.md
added: 2026-09-20
payoff: a reader checking where a Known-limitations note comes from is not sent to a source list that never held it
verify: grep -q 'Sources for the vaporizer' docs/MODEL.md
---

**Problem.** docs/MODEL.md's 'Sources for the notes above' block in Known limitations lists only the five vaporizer and altitude sources, but its heading claims every note in the section

**Why it matters.** The block is a provenance statement, and it is read as one:
`.claude/rules/citing-sources.md` makes the route and depth of a reading the
thing a later reviewer checks a value against. A heading that claims to source
"the notes above" while listing five vaporizer and altitude sources tells a
reader checking any other note in § "Known limitations" that its source is in
that block, which it is not - so the reader either concludes the note is
sourced when it is not, or goes looking for a list that was never written.
`docs/MODEL.md` is the authoritative specification, so a wrong statement about
where a claim comes from is the failure `CLAUDE.md`'s provenance requirement
exists to stop.

**Reproduced 2026-09-20.** `docs/MODEL.md:8175` carries `**Sources for the notes
above**, none of which is the authority for any`, and the block under it lists
the five vaporizer and altitude sources only.

**Done when.** The block's heading names the notes it actually sources - the
vaporizer and altitude ones - rather than every note in the section, so a
reader checking any other note is not sent to a list that does not hold it.
