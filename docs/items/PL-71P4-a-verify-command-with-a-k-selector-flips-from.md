---
id: PL-71P4
title: "A verify: command with a -k selector flips from correctly failing to falsely passing when unrelated work adds a matching test name, so the already-passes set grows on its own"
status: untriaged
added: 2026-09-02
---

**Problem.** `PL-L9JS` records eight open items whose `verify:` command passes
on a tree without their work, and scopes itself to repairing those eight. The
set is not static. On 2026-09-02 `bin/docket check` named **nine**, and the new
one arrived without anybody touching it:

- `PL-6P9Y` carries `uv run pytest subprojects/docket/tests/test_roadmap.py -k
  out_of_scope`. On 2026-09-01 it was one of the twenty items `PL-5QKT`
  recorded as *selecting no test* - exit 5, reading as a command that correctly
  fails.
- `PL-Q2BJ` (rank the digest's Top line against the plan, #144, merged
  2026-09-01) added `test_the_digest_names_the_milestone_when_only_out_of_scope_work_is_ready`
  to that same file. Unrelated work; it was not about `PL-6P9Y` at all.
- `-k out_of_scope` now matches that test, the command exits 0, and `PL-6P9Y`
  moved from the "selects nothing" advisory to the "already passes" one. Its
  own work - reading a milestone's *Explicitly out of scope* list - has not
  been started.

Verified by `git log -S` on the test name against `test_roadmap.py`.

**Why it matters.** Two consequences, and the second is the one that changes a
decision.

1. **The flip is silent and in the wrong direction.** A command that selects
   nothing exits 5, so `docket verify` rejects the branch: the worst case is a
   round trip. A command that passes exits 0, so `docket verify` returns
   `ACCEPT` on a branch that did none of the work. The transition above turns
   the safe failure mode into the unsafe one, with no commit, no review and no
   advisory at the moment it happens.
2. **`PL-L9JS`'s scope does not converge.** It is written as "eight small edits
   to item files", to be made as each item is started. That is right for the
   eight, but it is a repair with no prevention behind it: every remaining
   `-k`-shaped command is a latent member of the set, converting whenever some
   future test name happens to match. `bin/docket check` counted 14 open items
   selecting nothing on 2026-09-02, down from `PL-5QKT`'s 20. So the arithmetic
   is 14 latent conversions against a repair pass that clears 9 - the set can
   be worked to zero and be non-zero again the following week, from work that
   did nothing wrong.

**Why the existing decision does not already cover this.** `PL-5QKT` left the
selects-nothing case an *advisory rather than an error*, deliberately: the exit
code cannot separate `-k` naming a test the work will add (correct, and the
shape the skill recommends) from `-k` naming a test nobody will ever write
(broken), and only the item's author can. That reasoning is sound and specific
to `-k`. It does not transfer to the already-passes case, because there is no
benign reading of it: the skill's own definition is that a `ready` item's
command fails on a tree without its work and passes with it, so exit 0 at
`status: ready` is unambiguously wrong whoever wrote it. The exit code *does*
separate the cases here, which is exactly what `PL-5QKT` said it could not do
there.

**Where.** `subprojects/docket/src/docket/checks.py` (`_check_landed`, which
already computes the fact), `docket.toml`, `subprojects/docket/tests/test_checks.py`.
`PL-L9JS` carries the repair half and should cross-reference this; `PL-5QKT`
carries the reasoning this item distinguishes itself from.

**Candidate mechanism, not yet decided.** The store already has the pattern:
`verify_required_from = 2026-08-30` grandfathers a closed set of items and
makes the rule binding for everything after it, so the rule started working
immediately without turning the store red on the day it landed. The analogue
would be a dated cutoff past which an item at `status: ready` whose command
exits 0 is an **error** rather than an advisory. The nine existing ones stay
advisory and burn down as their items are started, per `PL-L9JS`; nothing new
can enter the set, including by the silent flip above, because the run that
first sees exit 0 fails `make check` and CI.

Open design question, and the reason this is not written as settled: an item at
`in-progress` on a branch may legitimately start passing partway through its
own work, so the error must be scoped to `ready` at minimum, and possibly to
what `docket next` is about to offer - the scoping `PL-JWXF` already applied to
the sibling advisory.

**Done when.** A `verify:` command that passes on a tree without its work
cannot be newly recorded or silently acquired without something failing at the
moment it happens, and the reasoning for treating this differently from
`PL-5QKT`'s selects-nothing case is written down where the next session
reading either advisory will find it.
