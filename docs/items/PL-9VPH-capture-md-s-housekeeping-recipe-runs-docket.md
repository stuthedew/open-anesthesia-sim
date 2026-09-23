---
id: PL-9VPH
title: capture.md's housekeeping recipe runs docket new before it sets touches, on a clean tree, so the near-duplicate search has no paths and never runs: PL-4CPP duplicated PL-BYN2 at similarity 0.29 against the 0.15 floor
priority: P3
effort: S
status: ready
classes: defect, docs
feature: recurrence-signal
touches: .claude/skills/docket/modes/capture.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-23
payoff: an item filed by the housekeeping recipe meets the near-duplicate search, so a second filing of open work is caught at capture instead of by a later session reading both briefs
verify: grep -qF 'bin/docket new --touches docs/items' .claude/skills/docket/modes/capture.md
---

**Problem.** capture.md's housekeeping recipe runs docket new before it sets touches, on a clean tree, so the near-duplicate search has no paths and never runs: PL-4CPP duplicated PL-BYN2 at similarity 0.29 against the 0.15 floor

**Mechanism.** `near_duplicates` in `subprojects/docket/src/docket/duplicates.py`
returns nothing without paths ("No paths means no answer"), and `PL-THLT`
supplies them from the working tree only when the capture declares none. A tree
is clean when an item is filed before its work starts, which is the order
`.claude/skills/docket/modes/capture.md` § "Mode: housekeeping nobody filed"
prescribes: `bin/docket new "..."`, then `bin/docket set ... --touches
docs/items`. So an item filed by that recipe never meets the search.

**Measured on the instance, 2026-09-22.** `similarity` between the two titles
is 0.29, and `docs/items` covers `PL-BYN2`'s declared path, so `bin/docket new
--touches docs/items "..."` would have printed `PL-BYN2`. The flag already
exists on `new`; the recipe's example simply does not use it.

**Reproduced 2026-09-23**, on a scratch copy of the store as it stood when
`PL-4CPP` was filed (`PL-BYN2` reopened, `PL-4CPP` removed). `--no-git` stands
in for the clean tree, since both leave `new` no inferred paths. `bin/docket new
--no-git "TITLE"` with `PL-4CPP`'s title, which is the recipe's shape, prints the
new id and nothing else. `bin/docket new --no-git --touches docs/items "TITLE"`
prints `PL-BYN2 (ready) ... shares docs/items` and records the filing on it. The
recipe's `set` line still works after the change: carrying `--touches
docs/items` again, it prints "`touches` already records `docs/items`; nothing
to write" and writes the rest.

**Why it matters.** This recipe is the one capture the skill tells a session to
make before its work starts, so it is the capture likeliest to be made on a
clean tree, where `PL-THLT`'s working-tree paths are empty. That is the one case
the duplicate search was left unable to answer. A second filing costs a brief
nobody needed, and a later session then has to read both to find they are one.
`PL-4CPP` was exactly that, and was dropped the same day. Housekeeping recurs by
nature (a stranded sweep, a triage pass), so its titles are the likeliest to be
filed twice.

**Done when.** The recipe in `.claude/skills/docket/modes/capture.md` §
"Mode: housekeeping nobody filed" passes `--touches docs/items` to `bin/docket
new` itself, ahead of the title (`bin/docket new --touches docs/items "..."`),
and its `bin/docket set` line no longer repeats it.

**Generator check.** An instance of `PL-TZ7T`'s mechanism, filed after that
head closed (2026-09-20: `bin/docket new` files a duplicate without noticing).
`PL-4CPP` (2026-09-22) fell through the gap `PL-THLT` left, a clean-tree capture
declaring no paths. `PL-6SV4`, filed the same day as an unnoticed duplicate of
`PL-VYK1`, is a second post-close instance through a different gap: the older
item's `touches` predates a file move. A third would make `PL-TZ7T` a generator
whose fix did not hold.
