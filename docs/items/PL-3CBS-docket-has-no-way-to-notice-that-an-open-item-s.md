---
id: PL-3CBS
title: docket has no way to notice that an open item's work already landed on main
priority: P2
effort: S
status: ready
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-08-30
verify: uv run pytest subprojects/docket/tests/test_checks.py -k landed
---

**Problem.** An item is closed by hand, so an item whose work merges without
its `status` being set stays `ready` forever. Nothing notices. It keeps its
place in `docket next`, it is counted as open by `docket wave` and `docket
gate`, and the next session picks it up and re-derives work that is already on
main before discovering that.

Two of v0.2.8's sixteen "open" gate entries are in exactly this state, found
2026-08-30 while answering what to work on next:

- **PL-XCYB** (a provenance check must refuse to answer in a shallow checkout).
  Implemented by `1561b2a`. Its `verify:` command passes, `checks.py`'s
  `_check_provenance` declines on a shallow history, and
  `test_a_shallow_clone_declines_and_says_why` covers the case. Every clause of
  its "Done when" is satisfied.
- **PL-ZQ9C** (record an item's pull request, so provenance survives
  squash-merge). Implemented by `55eedb6`. `Item.pr` exists, `docket check`
  refuses a `done` item without it, `_check_provenance` holds recorded numbers
  to what the default branch has seen, and `subprojects/docket/README.md`
  documents the field.

**Why it matters.** The gate is the project's measure of how much of a release
remains, and it is currently overstating by two on sixteen. That is a wrong
answer to the one question `docket wave` exists to answer. It also wastes a
whole session's opening: the item looks startable, and the fact that it is not
is the most expensive thing to discover late.

**Where.** `subprojects/docket/src/docket/checks.py`, beside `_check_provenance`
- the same place, because it is the same question asked the other way round.

**Approach - an advisory keyed on `verify:`, not on commit subjects.** The
tempting signal is an item id at the head of a commit subject on the default
branch. It cries wolf: of the thirteen open items whose id leads a commit
subject on `main` today, eleven are capture or triage commits ("PL-8HJ2 Capture
that make release always ends in a red test"), and only the two above are
implementations. An advisory with an 85% false-positive rate is one every
session learns to skim past, which is the failure mode `docket.toml`'s
`top_band_limit` comment already records for a different check.

`verify:` is the better key, because it is the item's own statement of what
would prove it done: report an open item whose `verify:` command passes as
worth a look. That is not proof either - PL-6GS0's command would have passed
before its work - which is why this is an advisory naming candidates for a
reader to judge, never an error and never an automatic status change. It fits
`CLAUDE.md`'s rule exactly: decide the decidable half (does the command pass),
leave the judgment (is it actually finished) alone.

Scope it to `ready` and `needs-decision` items carrying a `verify:` command,
and run it only under `check`, which is the command already permitted to read
git.

**Done when.** `docket check` raises a grooming advisory listing open items
whose `verify:` command passes, a test covers both the passing and the failing
case, `subprojects/docket/README.md` documents it, and running it against
today's store names PL-XCYB and PL-ZQ9C.

**Two further instances, and one more argument for the `verify:` key
(2026-08-31).** Folded in from `PL-SRCP`, captured separately on 2026-08-30 and
dropped as a duplicate of this item. PR 92 squash-merged `PL-1TPM` (mark a
suggestion the current step has not reached) and `PL-0RS6` (rank in-scope work
above out-of-scope work) into `main`; both item files still read
`status: ready` afterwards, both `verify:` commands passed on the merged tree,
and `PL-1TPM` was a frozen v0.2.8 gate entry - so `wave` read the gate one
entry larger than it was and `docket next` offered `PL-1TPM` as the second-best
thing to do, which is work a session would have started and found already
written. Closed out by hand in the session that found it. That is four known
instances now (`PL-XCYB`, `PL-ZQ9C`, `PL-1TPM`, `PL-0RS6`), and in both of
these the `verify:` command passing is precisely what would have flagged them,
which is the signal this item chooses.

`PL-SRCP` also noted that `PL-64LS` (detect items stranded on an unmerged
branch) asks this same question in the other direction and may share one git
pass. `PL-64LS` is `done`, so what is left of that observation is narrower:
reuse its ref-reading in `vcs.py` rather than adding a second traversal, and
keep the two advisories' wording symmetric so a reader meeting one recognizes
the other.
