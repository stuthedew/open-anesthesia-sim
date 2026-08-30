---
id: PL-Q2BJ
title: The session-start digest still leads with work the current step excludes
status: untriaged
added: 2026-08-30
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
