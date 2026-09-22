---
id: PL-P669
title: Eleven tagged release spans cover a closing pull request their own notes never name, and nothing points a reader from the tag to where that work is described
priority: P3
effort: M
status: done
classes: docs
feature: commit-provenance
touches: docs/releases, ROADMAP.md, docs/ARCHITECTURE.md, tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md
added: 2026-09-14
closed: 2026-09-22
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def check_tag_span_covers_its_notes' tools/doc_check.py
recurrences: 2026-09-22 PL-YKSD
---

**Problem.** Eleven tagged release spans cover a closing pull request their own notes never name, and nothing points a reader from the tag to where that work is described

**The eleven were not re-counted here**, and that is the first thing whoever
picks this up should do - the count was taken at capture and the history has
moved since, including the `v0.4.25` cut. What can be said from this pass is
that the mechanism is real and is the same one two other items describe:
`PL-2M5T` (notes written before `bin/docket record` backfills `pr`, so 9 of
v0.4.22's 15 bullets name no pull request) and `PL-028F`, which v0.4.22 records
as having closed the case of work landing *between* a cut and its merge.

**Why it matters.** A tag is what a reader resolves a commit to, and the notes
are where that release's reasoning lives. Where a span covers a closing pull
request its notes never name, the two records disagree about what shipped and
neither points at the other - so the work is findable only by someone who
already knows it happened. This is provenance of the permanent kind: nothing
rewrites a cut release's notes, so each instance is permanent once tagged.

**Done when.** The count has been re-taken against today's tags; each span whose
closing pull request its notes do not name is either repaired or recorded as
knowingly left, with the reason; and a check fails the *next* one rather than
leaving it to be noticed - which is the half that stops this recurring.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and the fault
reproduces at the newest tag.** No check exists
(`grep -c 'def check_tag_span_covers_its_notes' tools/doc_check.py` → 0); the
only mechanism is docket's advisory at `checks.py:838,852`, which landed in the
same commit that filed this item. Re-counted today by docket's own definition:
**12 closing pull requests across 9 spans**, against the brief's "12 … in 11
distinct spans" of 2026-09-14 - the pull request count is unchanged and the
span count should be treated as approximate, since a definitional difference
behind 9-versus-11 could not be excluded. The v0.4.27..v0.4.28 span covers
`#702` and `#703` and `docs/releases/v0.4.28.md` names neither `PL-1YT5` nor
`PL-V1F4`.

One correction: "nothing points a reader from the tag to where that work is
described" is false at the *class* level - `ROADMAP.md:121-125` says the two
records answer different questions and that the work is described in the next
release's notes. That paragraph landed in the same commit as this item, so it
is not later work; what no individual notes file carries is a pointer of its
own, which is the narrower claim to make.

**Closed 2026-09-22.** The count was re-taken first, as the brief asks. By the
closure definition - a `pr:` recorded on a `done` item, matched to the squash
subject that names it - **20 closing pull requests across 16 tagged spans**,
out of 65 spans, are named nowhere in the notes of the release they resolve to.
The pull request count has grown from the brief's 12 and the span count from
11; v0.5.1 and v0.5.2, the two most recent completed spans, each carry one, so
the mechanism had not decayed.

Two definitional facts the sweep of 2026-09-19 could not settle, and which
explain the 9-versus-11 it could not exclude:

- **The release's own cut accounts for most of it.** 40 of the 63
  span-crossing closures are a release's cut pull request, which is inside its
  own span by construction and stamped by the next release every time.
  `ROADMAP.md` § "Tags" already writes that down, so it is exempt - and the
  exemption is taken from the commit that *added* the notes file rather than
  from a subject reading "cut vX.Y.Z", which is prose.
- **Reading every `(#N)` in a span rather than every closure gives 250 across
  54 spans.** The extra 230 are triage and capture commits, which close
  nothing and were never going to appear in any notes. "Closing pull request"
  is the load-bearing word in the title.

**What was built, and what was deliberately not.** `check_tag_span_covers_its_notes`
asks for a *pointer* and nothing else, so it does not reopen the judgment
`PL-028F` left with a person: absorbing a newcomer into the release that
shipped it and letting it go to the next release both satisfy it. Hard failure
rather than an advisory is safe here because the state is always clearable -
every one of the 23 item closures resolves to a release whose notes do name
its pull request, so a pointer can always be written - and because the newest
tag's span is exempt, so a fresh tag cannot redden `make check` on a state
nobody can clear. That was the failure `PL-8HJ2` removed and the one
`check_tags` stays silent on.

**The 16 spans were repaired rather than recorded as left.** Each notes file
gained an `### also inside this tag's span` section naming the pull request and
the release that does describe it. Additive, so the cut's own account of what
it stamped is untouched, and written after the tag, which is the one moment a
notes file is safely edited because a tagged release is never re-cut.

**One collision, and it is the reason `subprojects/docket/` is in `touches`.**
The pointer bullets are the exact shape `checks._check_release_notes` reads as
a claim, so all 16 repaired files reported the notes and the store disagreeing
about what that release shipped - the thing the pointer says.
`release.notes_claims` splits a file at `SPAN_HEADING`, and the three readers
take the first half; `restate_references` puts the second back byte for byte,
which is what stops `make fix` appending a second reference to a line that
already carries one.

**One correction to the brief's framing carried into `ROADMAP.md`.** "The work
is described in the *next* release's notes" is not always true: `#412` was
attributed back to v0.4.6, the release its code shipped in, and `#225` was
recorded twelve releases later by v0.4.15. The pointer names the release rather
than assuming one.

**Two floors, stated rather than hidden.** A closure whose squash subject
carries no `(#N)` cannot be placed in a span at all - 85 of this store's
recorded pull requests, every one numbered 3 to 105, from before the
convention. And a truncated clone declines rather than reporting, because a
span it cannot walk and one whose notes are genuinely short are identical from
inside it.
