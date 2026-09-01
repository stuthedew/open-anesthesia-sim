---
id: PL-Q2BJ
title: The session-start digest still leads with work the current step excludes
priority: P2
effort: S
status: done
classes: defect, infra
feature: planning-cadence
milestone: v0.2.8
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/README.md
added: 2026-08-30
closed: 2026-09-01
pr: 144
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -k "digest and scope"
---

**Problem.** `PL-1TPM` and `PL-0RS6` taught `docket next` to read the roadmap:
it now ranks what the current step names first and marks a suggestion the step
has not reached. The digest's `Top:` line does not go through `recommend` at
all - `render.format_digest` takes the first item of `sorted(open_items,
key=sort_key)`, which is priority order and nothing else. So the line every
session reads before it reads anything still opens with `PL-9Y42` (validate
wash-in against a published human measurement), which is `v0.4.0` scope, while
the beat two lines below it says `clear the gate`.

**Why it matters.** It is the same defect `PL-1TPM` describes, one surface
over, and this surface is the expensive one: `next` is run when a session asks
what to do, while the digest is printed to every session whether it asked or
not. The two lines now disagree with each other inside one block of output,
which is worse than either being wrong alone - a reader has to work out which
of them knows about the plan.

**Where.** `subprojects/docket/src/docket/render.py`, `format_digest`, the
`Top:` line; the plan is already threaded into that function as `plan`, so the
`Scope` it carries is in scope at the call site. `docket status` groups by
feature and is worth checking at the same time - it is the other command that
ranks without asking the plan.

**Found.** While closing `PL-0RS6` (2026-08-30). Not fixed there: that item is
about the ranking in `plan.recommend`, and the digest is a separate surface
with its own one-line budget to respect.

**Done when.** The digest's `Top:` line does not name work the current step
excludes while in-scope work is ready, and says nothing longer than it does
now.

**Triaged 2026-08-31, and still reproducing.** The digest that opened the
triage session read `Top: PL-9Y42 Validate wash-in against a published human
measurement` - `v0.4.0` science scope - two lines above `Beat  clear the gate
- 2 entries of 22 still open`. The contradiction this item describes is what
every session is reading today.

P2, `defect`/`infra`, `planning-cadence` beside `PL-1TPM` (`docket next` ranks
work the current milestone excludes) and `PL-0RS6` (marking does not reorder),
which are the same seam on the `next` surface.

The `verify:` command selects on `digest` *and* `scope`, which no test in
`test_roadmap.py` satisfies today, so it fails now and the new test has to
carry both words. The digest assertions live in that file rather than in a
`test_render.py`, which does not exist.

Not admitted to v0.2.8's frozen list, and `PL-0RS6` is the precedent that
settles it. `PL-0RS6` completes `PL-1TPM` far more directly than this does -
same command, same function, and `PL-1TPM`'s ranking is visibly half-fixed
without it - and it was nonetheless worked as an ordinary P2 queue item and
never recorded as a frozen entry. A third surface, one renderer further out,
cannot have a stronger claim than the second one did.

**Admitted to v0.2.8's frozen list, 2026-08-31, reversing the paragraph
above.** The `PL-0RS6` precedent it rests on does not say what the paragraph
takes it to say: `ROADMAP.md`'s "Friction that compounds is the clearest
presence case" records `PL-0RS6` as having *qualified* for the gate and been
"worked early rather than merely admitted", so it is a precedent for working
such a finding at once, not for keeping it off the list. Under the scope test
now recorded in "What the freeze closes", the session-start digest and the
queue's ranking are both machinery the release's goal names, and this item is
the one defect of the nine that every session reads on its first screen.
