---
id: PL-035
title: Consider a `**Docs.**` entry field naming the docs a task will touch
status: dropped
added: 2026-08-24
closed: 2026-08-25
reason: taxes capture, predicts unwritten work, and would present a guess as a checked field; the absence case it targets is better served structurally, per PL-036
---

**Problem.** Close-out has to work out which documents a change could have
invalidated after the change is written. The session that captured the item
often already knew — it just had nowhere in the entry format to say so.

**Why it matters.** `tools/doc_check.py candidates` narrows the sweep from a
diff, but it only finds documents that already name something the diff
touched. A document that *should* mention a new feature and does not is
exactly what it cannot see, and is a failure mode that has happened here.

**Where.** The item format in `subprojects/docket/README.md`, validation in
`subprojects/docket/src/docket/checks.py`, and `tools/doc_check.py`. (The
original text cited `docs/PUNCH_LIST.md`, `tools/punch_list.py` and
`.claude/skills/punch-list/SKILL.md`, none of which survived the docket
migration.)

**Decided.** Not adding the field. Four reasons, in order of weight:

1. **It taxes capture.** `CLAUDE.md` is firm that capture must cost nothing —
   `docket new "..."` is the whole procedure, with no field to choose. Ideation
   often happens when usage is nearly spent. A field the capturing session is
   meant to fill in adds friction exactly where the rules remove it, and
   optionality does not fully rescue it, since an optional field still has to
   be considered and declined.
2. **It predicts work that has not been written.** The capturing session would
   be guessing which documents a change it has not yet made will invalidate.
   That is the least informed moment in the item's life; close-out, which has
   the diff, is the best informed, and that is already where `candidates` runs.
3. **A partly-populated, never-verified field is worse than none.** This
   repository's own tooling doctrine says a tool that guesses at the judgment
   half is worse than no tool, because its output looks authoritative and is
   not. A `Docs.` line reading "MODEL.md provenance table" invites close-out to
   check that and stop when the change also touched `ARCHITECTURE.md`.
   Validating that the named paths exist — the sub-question this item asked —
   makes it worse, by adding a green check to a guess.
4. **The absence cases with consequence are better handled structurally**, and
   the two largest already are: a new module missing from the tree is
   `check_package_maps`, and a new constant missing from the provenance table
   is `check_provenance`. Both are derived from the tree at check time, so they
   cannot go stale and nobody has to remember them. PL-036 extends that pattern
   to the displayed-outputs list.

What is given up: when a capturing session does know something non-obvious
about which document a change will invalidate, there is no structured place
for it. The brief prose already carries that, without pretending to be a
checked field.

**Done when.** Closed by this decision.
