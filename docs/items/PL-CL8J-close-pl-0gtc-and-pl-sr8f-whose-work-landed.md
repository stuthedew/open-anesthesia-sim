---
id: PL-CL8J
title: Close PL-0GTC and PL-SR8F, whose work landed under other ids and left main's whole-store verify replay red for four consecutive merges
priority: P2
effort: S
status: done
classes: defect, docs
feature: dev-tooling
touches: docs/items
verify: python3 tools/doc_check.py check && bin/docket check
added: 2026-09-07
closed: 2026-09-07
---

**Problem.** `main`'s `quality` run has concluded `failure` on its last four
merges — #424, #425, #426 and #431 — on one error, every other step green:

    PL-0GTC, PL-SR8F are open but their `verify:` command already passes
    (2 of 116 checked)

`PL-0ZGK` diagnosed the *invisibility* of this (the whole-store replay runs only
on push to `main`, so a green pull request turns `main` red after it lands) and
says in its own closing note that the repair is **not** that item and should be
done first. `PL-0ZGK` is `needs-decision` on which notification mechanism to
build, so the repair itself was owned by nobody while `main` stayed red.

**What was wrong.** Both items were the benign horn of that error — work that
landed under another id and was never closed — rather than the dangerous horn,
a `verify:` command that does not discriminate and would let `docket verify`
accept a branch that did none of the work. Establishing *which* is the whole
job, because the two look identical from the error message and the remedies are
opposite.

    PL-0GTC   'RespiratorySystem' removed by d8deea5 (#376)
    PL-SR8F   'two orders milder'  removed by 67b279b (#420, PL-ZVS7)

**How it was established, and why the obvious method fails.** By replaying all
80 commits that touch `docs/MODEL.md` and testing each revision under the *same
whitespace normalisation the items' own `verify:` commands use*. This matters
more than it sounds: `docs/MODEL.md` is hard-wrapped prose, so a phrase can span
a newline, and both `grep` and `git log -S` are line-based. A first pass with
`grep` reported "two orders milder" absent from every revision in history —
which is false, and would have made the removal commit unrecoverable. `PL-SR8F`'s
own `verify:` command normalises whitespace before testing, which is the clue.

`PL-SR8F` is `classes: safety`, so its substance was verified rather than
inferred from the phrase's absence: § "Supported simulation step" now carries
the per-rate relation (about 21x milder at 1x, 19x at 20x, 16x at 60x, about 7x
at 300x) that replaced the "two orders milder at every rate" holding at no rate.
`PL-0ZGK` independently named `67b279b`; the replay agrees.

**Why it matters.** `main` red is upstream of everything — every merge passes
through it — and a branch already red is the state that trains a reader to stop
looking, which is `PL-0ZGK`'s own argument. It also blocks a release: cutting
one off a red default branch is not something to do knowingly.

**Where.** `docs/items/PL-0GTC-*.md` and `docs/items/PL-SR8F-*.md`, frontmatter
only. No source or documentation changes: the work these items describe already
shipped.

**Done when.** `bin/docket check --verify` reports zero errors on `main`.

**Found.** `PL-B1WW`, 2026-09-07, verifying that its own merge (#431) had not
been what turned `main` red. It had not: #431 was green through every step
including the full suite, and failed only on this pre-existing store error.

**Note.** This is the repair, not the guard. `PL-0ZGK` remains open and still
needs its decision — the next item finished without being closed turns `main`
red the same way and just as silently.
