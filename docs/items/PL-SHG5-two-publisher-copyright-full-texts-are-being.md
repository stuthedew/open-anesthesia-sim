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

**Filed with GitHub Support, ticket 4733783** (2026-09-06), after the
`git filter-repo` pass and force-push landed on 2026-09-06. The ticket asks
GitHub to dereference or remove the roughly 388 `refs/pull/*/head` refs still
pinning the pre-rewrite commits, run a server-side garbage collection, and
purge cached commit and blob views. Those refs are read-only to the repository
owner, so nothing local can clear them; the repository has zero forks, and
every branch and tag was verified clean from a fresh clone before the ticket
was raised. Framed as a redistribution problem rather than a leaked credential,
because GitHub's documented sensitive-data assistance is scoped to risk that
cannot be mitigated by rotating a secret, and there is no secret here.

Two consequences of the rewrite are recorded rather than fixed. It stripped
every commit signature - 375 signed commits before, none after - which no tool
could have avoided for the commits at and after the removal point, since a
signature covers parent hashes the rewrite changes. And it force-updated every
branch ref to a snapshot taken before the push, dropping two commits pushed
into that window on another session's branch; `PL-YGF3` carries that finding
and the guard gap behind it.

**Where.** `docs/references/README.md`, the two PDFs beside it, and whatever
mechanism is chosen so the next visibility change cannot repeat this.

**Decided, 2026-09-06 (project owner).** Rewrite history now rather than
accept the exposure: run on the day the breach was found, with the citations
kept in the README as text, which is the part designed to survive a removal.
Both halves are done and verified.

**Still open, and the durable half.** Nothing deterministic guards this. Two
cited files left the tree and `make check` reported zero errors, because
`tools/doc_check.py` validates the paths `docs/MODEL.md` cites and does not
read `docs/references/`. The candidate is a check that fails when a file under
`docs/references/` has no recorded licence permitting redistribution, and that
fails when an entry in that README names a file the directory does not hold.
Both halves are decidable by reading the tree, which is where `CLAUDE.md` says
the work belongs. The same trap is armed for every future upload, and the
visibility change that sprang it is not repeatable - so the guard has to key on
the file and its licence, not on a visibility transition nobody will make
twice.

**Done when.** No file in `docs/references/` is redistributed without a licence
that permits it, `docs/references/README.md` describes the repository's actual
visibility, and the rule that was violated is either enforced by a check or
recorded where the next session filing a PDF will read it.
