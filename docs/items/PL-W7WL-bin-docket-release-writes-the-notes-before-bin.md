---
id: PL-W7WL
title: bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it
priority: P2
effort: S
status: ready
classes: defect
feature: cut-backfills-pr-numbers
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_checks.py, docs/releases
added: 2026-09-20
payoff: stops an item that merged just before a cut shipping a release note with no route back to the change that made it
verify: uv run pytest subprojects/docket/tests/test_cli.py::test_a_cut_backfills_a_pull_request_number_the_base_already_names subprojects/docket/tests/test_cli.py::test_record_restates_a_released_bullet_that_shipped_without_a_number -q
recurrences: 2026-09-13 PL-66X4, 2026-09-14 PL-2M5T, 2026-09-20 PL-3HMQ
---

**Problem.** bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it

**Observed 2026-09-20, cutting v0.4.32 (`PL-V3GD`).** `PL-TGFY` merged as #745
minutes before the cut, so it carried no `pr:` when `make release
VERSION=0.4.32` generated `docs/releases/v0.4.32.md`. Its notes line shipped as

```
- PL-TGFY PL-Z34C is a frozen gate entry ... so the gate holds an entry nothing can clear
```

while its five siblings all carry `— #742`, `— #743`, `— #739`, `— #740` and
`— #744`. `bin/docket record` then wrote `pr: 745` onto the item correctly, but
the notes were already on disk and `bin/docket release --dry-run` answers
`Nothing to release: no finished work since 0.4.32`, so there is no supported
way to regenerate them. The line was corrected by hand on that branch.

**The documented procedure is what produces it.** The `docket` skill's release
mode, and `PL-V3GD`'s own brief, both order the steps `make release` first and
`bin/docket record` second. That order is right for everything else — `record`
wants the merge on the base — but it guarantees this outcome for any item that
merged between the previous cut and this one without its number being
backfilled first.

**Why it matters.** The notes are the permanent record of what shipped where,
and `pr:` is how a reader gets from a released item back to the change that
made it. A missing number is not wrong, but it is unrecoverable through the
tool: the one command that would rewrite the line refuses, correctly, because
re-cutting a shipped release is what leaves two sets of notes disagreeing about
the same items (`PL-1MKQ`'s territory).

**Two candidate fixes, and the cheap one looks right.** Either `bin/docket
release` runs the same backfill `bin/docket record` does before it writes the
notes — it already fetches, so the information is in hand — or the documented
order is swapped so `record` runs first. The first is better: it removes the
failure rather than asking every future cut to remember, which is `CLAUDE.md`'s
preference for deterministic tooling over a rule a session has to hold.

**Done when.** A cut whose finished set includes an item that merged without a
`pr:` still writes that item's pull request number into the release notes, with
a test driving that case.

**This mechanism has now been filed four times, and the other three are closed
into this one** (`PL-JKML`'s duplicate sweep, 2026-09-20). `PL-66X4` was
dropped into `PL-2M5T` before this item existed; `PL-2M5T` and `PL-3HMQ` are
dropped here. Four sessions diagnosed one defect from four cuts, none of them
able to see the others, which is the cost `PL-TZ7T` names for `bin/docket new`
filing a near-duplicate without noticing. The evidence each of them paid for is
carried below rather than lost with the item.

**How much of a release it takes, from `PL-2M5T` (measured 2026-09-14).**
`docs/releases/v0.4.22.md` carries fifteen item bullets and **nine of them name
no pull request at all**. So this is not an edge case that catches the
occasional late merge: it took the majority of one release's notes, and the
items it takes are systematically the most recently finished - the ones a
reader is most likely to be looking up.

**Two more releases, from `PL-3HMQ` (2026-09-20).** `v0.4.33` shipped without
`PL-LPLD`'s `#758`, and `v0.4.34` would have lost three more had they not been
caught by hand at the cut.

**The second half `PL-2M5T` carried, and it is a decision rather than code.**
A cut release's notes are never regenerated - `bin/docket release --dry-run`
answers `Nothing to release` once the version is cut, correctly, because
re-cutting a shipped release is what leaves two sets of notes disagreeing
(`PL-1MKQ`'s territory). So the numbers already missing from `v0.4.22`,
`v0.4.32` and `v0.4.33` do not come back when this is fixed. Either those files
are repaired by hand as part of this item, or the item records why a shipped
release's notes are left standing as they were published. Decide it here; do
not leave it to be rediscovered a fifth time.

**Grouped as `feature: cut-backfills-pr-numbers`** (`PL-JKML`'s duplicate
sweep, 2026-09-20, confirmed on independent refutation). `PL-W7WL` and
`PL-WXX8` are the two halves of a pull request number never reaching the place
that needs it. `PL-WXX8` is the number never landing on the item at all, because
`bin/docket record`'s advisory addresses a session that has already finished;
`PL-W7WL` is the number existing but arriving after the notes are rendered.
Both are answered by the same move - the cut performing `record`'s backfill
itself, rather than a rule a session has to remember - and neither is finished
while the other stands.

Named for what completes rather than for the theme: `commit-provenance` is
eleven items and answers no question about whether anything finished, which is
the test `.claude/skills/docket/SKILL.md` sets for a feature name.

**Decision on the already-shipped notes: repaired, by command rather than by
hand** (2026-09-21). The brief asked for this to be settled here rather than
rediscovered a fifth time, and the measurement decided it. 128 of the 853
bullets across 22 of this project's 40 releases name no pull request, and the
store already holds a `pr` for **all 128** — so the repair is a re-render from
data on disk, not a search of the history. Ten sampled at random were checked
against the commit that actually introduced `status: done` on `origin/main`,
and all ten matched the number the store records.

Three things make this not a re-cut, which is the practice `PL-1MKQ` refuses.
The repair only *appends*: the id and the title are left exactly as they
shipped, so no release changes what it claims, and `docs/releases/v0.4.22.md`
still names the same fifteen items in the same order. It is not `docket
release` doing it, so no `milestone:` is re-stamped and no second set of notes
exists. And it runs from the store rather than from a re-derivation, so a
repaired line is byte-for-byte what the cut would have written — a property
with a test on it, because otherwise the notes would carry two spellings of
one fact.

**What was built, in three pieces.**

1. **Prevention.** `cmd_release` runs `closures_on_base` — `docket record`'s
   own reading — over the items about to ship, before the notes are rendered,
   and writes the number onto the item files as well as onto the objects the
   notes are built from. It rides the fetch the duplicate-cut guards already
   pay for. Never a refusal: a number a shallow clone cannot reach leaves the
   bullet as it was and is reported, because holding a release over provenance
   that is one `git fetch` away is the wrong side to err on for the one
   command whose output is permanent.
2. **Repair.** `docket record`'s bare form now also appends the reference to
   released bullets missing one, through `release.restate_references`. It is
   the only supported route to a bullet already shipped, and `make fix` runs
   it, so the repair costs no commit of its own. Not in the `--number` path:
   that writes the number of a merge that has just happened, and an item
   cannot be in a release's notes before it has merged.
3. **Detection.** `checks._check_notes_references` reports what is left, as an
   advisory rather than an error — the repair is one command, and a cut made
   from the shallow clone that is an agent session's normal state can produce
   one that no amount of refusing would fix. It counts only bullets the store
   can actually supply a reference for, so a store with nothing to add reports
   nothing and every line printed has a command behind it. This is the axis
   nothing compared, which is why four sessions each diagnosed it alone.

`PL-WXX8`, the other half of `cut-backfills-pr-numbers`, is what piece 2 was
built against and is answered by it for the released half; its own `Done when`
also asks that a cut leave `docket check` reporting zero closures owed, which
piece 1 delivers for everything shipping.
