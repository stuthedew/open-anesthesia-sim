---
id: PL-SHG5
title: Two publisher-copyright full texts are being redistributed from the now-public repository, against docs/references/README.md's own stated prerequisite
status: untriaged
classes: docs
touches: docs/references
added: 2026-09-06
---

**Problem.** `docs/references/README.md` states, of the two physiology PDFs it
holds: *"This repository is **private**, which is what makes that ordinary
personal use rather than redistribution"*, and *"Those two must come out before
this repository is ever made public"*. The repository went public on
2026-09-06 under `PL-XYRN` (open the go-public gate; closed the same day, #370),
and both files are still on `origin/main`:

- `docs/references/baker-farmery-2011-inert-gas-transport-in-blood-and-tissues.pdf`
  — Baker & Farmery, *Comprehensive Physiology* 2011;1(2):569–92 (Wiley).
- `docs/references/schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf`
  — Schüttler & Schwilden (eds), *Modern Anesthetics*, Springer 2008, 497 pp.

Confirmed 2026-09-06 against the GitHub API (`"private": false`,
`"visibility": "public"`) and `git ls-tree -r origin/main -- docs/references/`.
The third file, Jugel et al. 2014, is CC BY-NC-ND 3.0 per its own first page and
is unaffected — the README already says so.

**Why it matters.** The prerequisite was written down, the gate condition
occurred, and nothing fired: `PL-XYRN` was a queue item about human-facing
readiness and named no reference-directory precondition, so the two documents
that were only lawful *because* the repository was private became public with
it. Two consequences, and the second outlasts the first:

- The repository is now redistributing two publisher-copyright works. Wiley's
  and Springer's terms are the relevant ones, not this project's Apache-2.0
  licence, which covers only what the project itself authored.
- `docs/references/README.md` now asserts something false about the repository
  it sits in. `CLAUDE.md` treats a stale statement in project documentation as
  a safety issue in its own right, and this one is load-bearing: it is what a
  future session reads before deciding whether it may add a fourth PDF. This
  session was about to make exactly that decision, which is how the breach was
  found rather than by any check.

Removing the blobs means rewriting history — `git filter-repo` and a
force-push, per the README's own note — and the window in which the files were
publicly fetchable does not close by deleting them in a later commit. The
repository has been public for under a day, which is the reason to decide now
rather than at the next release.

**Where.** `docs/references/README.md`, the two PDFs beside it, and whatever
mechanism is chosen so the next visibility change cannot repeat this.

**Decision needed.** Three things, and the first is the project owner's alone:
whether to rewrite history now, or to accept the exposure and take the files
out in an ordinary commit; whether the two citations stay in the README as
text (they should — that is the part designed to survive removal); and whether
anything deterministic should guard it, e.g. a `make check` rule that fails
when a file under `docs/references/` has no recorded licence permitting
redistribution. The third is the durable half, since the same trap is now armed
for every future upload.

**Done when.** No file in `docs/references/` is redistributed without a licence
that permits it, `docs/references/README.md` describes the repository's actual
visibility, and the rule that was violated is either enforced by a check or
recorded where the next session filing a PDF will read it.

**Update, 2026-09-06, after recovery.** This item was captured before the
history rewrite and its premise has since half-changed. Both named PDFs are
gone from `origin/main` and from its history - the purge did what this item
asked for. What remains is that `docs/references/README.md` still carries a
full entry for each, so the repository still asserts in prose that it
distributes them; that residue is `PL-69K6`, together with the fact that
`doc_check` does not verify a documented reference file exists. Read this item
as the record of why the purge happened rather than as outstanding work, and
confirm against `git ls-tree origin/main` rather than against the text above.
