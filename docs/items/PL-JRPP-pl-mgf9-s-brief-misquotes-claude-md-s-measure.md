---
id: PL-JRPP
title: PL-MGF9's brief misquotes CLAUDE.md's measure of success as 'still enjoyed in a year', a leftover of the pre-correction one-year horizon
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
touches: docs/items/PL-MGF9-the-process-work-grooming-advisory-only.md
added: 2026-09-05
closed: 2026-09-05
verify: grep -q 'still being worked on and enjoyed years from now' docs/items/PL-MGF9-the-process-work-grooming-advisory-only.md && ! grep -q 'enjoyed in a year' docs/items/PL-MGF9-the-process-work-grooming-advisory-only.md
---

**Problem.** `2f8c6bb` (PL-QSWS, #238) corrected this project's horizon in
`CLAUDE.md` from one year to multi-year, rewriting two sentences:

> the measure of success is that it is still being worked on and enjoyed **in a
> year** → **years from now**
>
> the failure this project is guarding against is **a year of effort**
> abandoned → **years of effort**

`PL-MGF9`'s brief quotes the first of those in its pre-correction form. Line 43:

> Whether that is the right balance for a solo project whose measure of success
> is that it is still enjoyed in a year is the owner's judgment and nobody
> else's

`PL-MGF9` is `status: ready`, so this is live text a session reads when it picks
the item up, not a historical record.

**Why it matters.** The project owner reports repeatedly re-encountering the
one-year framing after correcting it, and this is the surviving instance. The
misquote is worse than a stale sentence of the item's own, because it is
attributed to `CLAUDE.md`: a session reading it acquires a wrong belief about
the resident file without opening the resident file, and the belief it acquires
is the specific one the correction was made to remove — the horizon that makes
trading internal quality for speed rational. `PL-QSWS` records that the shorter
horizon "hides" the drift failure mode; a session working `PL-MGF9` is
adjudicating apparatus-versus-simulator proportion, which is exactly the
judgment the horizon governs.

**Where.** `docs/items/PL-MGF9-the-process-work-grooming-advisory-only.md:43-44`.

**Swept, and deliberately not changed.** The whole tree was searched for both
pre-correction phrasings and for the semantic form (short-horizon reasoning
carrying no "year"), across every remote branch as well as this checkout.
Two other instances exist and both are correct as they stand:

- `CLAUDE.md:24` — "internal quality in the simulator that a one-year project
  could rationally trade for speed is worth paying for here" was the
  correction's own contrast, arguing this project is *not* one, so it was not
  a leftover for this sweep to remove. Raised with the owner instead as a
  separate question, since a foil is read as an assertion once the negation is
  dropped; approved the same day and carried out under `PL-MHFK`, which is why
  the phrase no longer appears in `CLAUDE.md`.
- `PL-QSWS:35,87` — a closed item, where line 87 records the correction event
  itself. Rewriting it would destroy the audit trail for why the horizon
  changed.

`docs/worker.md`, `docs/maintainer.md`, `docs/ARCHITECTURE.md`, all of
`.claude/rules/` and the `docket` skill contain no horizon language at all.
Re-run after merging `origin/main` at `513d029..`, which brought in `PL-6SBB`
and eleven other item files: still clean.

**Done when.** No open item's brief quotes the pre-correction wording, and the
quotation in `PL-MGF9` matches `CLAUDE.md`'s current text.
