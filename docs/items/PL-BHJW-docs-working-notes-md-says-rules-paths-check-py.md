---
id: PL-BHJW
title: docs/WORKING_NOTES.md says rules_paths_check.py is wired into CI's floor job, which PL-D551 folded into checks
priority: P3
effort: S
status: ready
classes: docs
touches: docs/WORKING_NOTES.md
added: 2026-09-06
verify: python3 tools/doc_check.py check && ! grep -qE "into .make check. and CI.s .floor. job" docs/WORKING_NOTES.md
---

**Problem.** `docs/WORKING_NOTES.md:837` reads "`PL-LLWN` added
`tools/rules_paths_check.py`, wired into `make check` and CI's `floor` job".
`PL-D551` folded the `floor` job into `checks` and deleted it, so the wiring
statement names a job that no workflow defines. The same file gets it right 40
lines earlier, at `:797` — "section of CI's `checks` job (where `PL-D551`
folded the former `floor` job)" — so the file already carries the correct
spelling and contradicts itself.

**Why it matters.** Same defect class as `PL-HDDJ`, which cleared the two
instances inside `.github/workflows/`. This is the instance outside it, and
`PL-HDDJ`'s "Done when" was deliberately scoped to the workflow directory, so
nothing there reaches it. Nothing checks it either: `tools/doc_check.py`
resolves cited *paths* against the tree, and this line cites no path — the
stale half is a job name inside prose, which no tool reads.

**The judgment this needs, and why it was captured rather than fixed.** The
sentence sits under a dated **Closed 2026-09-05** heading, and `WORKING_NOTES`
is narrative history where a dated entry may legitimately describe the world as
it stood. So there are two defensible answers — correct it to `checks`, or
leave it as a record of where the check was wired that day — and which one this
file's convention wants is a question about the whole file rather than this
line. Decide that first; the edit is one word either way.

Whichever way it goes, `:797`'s spelling is the model: it names `checks` *and*
`floor` together with the item that moved it, which reads correctly whether the
reader wants today's wiring or the history.

**Where.** `docs/WORKING_NOTES.md`, the **Closed 2026-09-05** paragraph on
`PL-LLWN`.

**Line numbers, re-checked at triage 2026-09-06.** The file has grown since
capture: the stale statement is now at `:845` and the correct spelling it
should follow at `:805`. Both are still verbatim what the brief quotes, so the
finding stands; find them by their text rather than by the numbers above.

**No `feature`, deliberately.** `PL-HDDJ` — the sibling that cleared the two
instances inside `.github/workflows/` — sits in `ci-cost`, which is finished and
in the unreleased set. Filing this there would reopen a completed feature and
change what the next release is said to complete, for a one-word edit. Left
outside any feature instead.

**The `verify:` command allows either answer.** It matches only the stale
spelling `into `make check` and CI's `floor` job`, so correcting it to `checks`
passes, and so does `:805`'s history-preserving form, which puts `checks`
immediately after "CI's" and names `floor` only as the job that was folded. What
it refuses is leaving the sentence as it stands.

**Found.** During `PL-KPP1`/`PL-HDDJ`'s doc sweep, which grepped `floor`
across `docs/` and `.claude/` to confirm the workflow-directory fix was
complete.

**Done when.** No line in `docs/` names `floor` as a job CI currently runs,
either by correcting the wiring statement or by marking it as history the way
`:797` does.
