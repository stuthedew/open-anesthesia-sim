---
id: PL-KND7
title: main has been red since #634 because PL-D1RT's Done when. was overtaken by two owner decisions, and the only check that sees it is one no local make check runs
priority: P2
effort: S
status: needs-decision
classes: defect
feature: queue-hygiene
touches: docs/items
added: 2026-09-16
---

**Problem.** main has been red since #634 because PL-D1RT's Done when. was overtaken by two owner decisions, and the only check that sees it is one no local make check runs

**Found 2026-09-16** while opening `#639`, from the session-start digest's note
that `main`'s run on `ff4be610` had failed.

**The measurement.** `quality.yml` runs on `main`: `#2102` (`57fdb8c`) green,
then `#2103` (`52205f6`), `#2104` (`ff4be61`) and `#2106` (`d7a3b05`) all
failed. Three consecutive commits. One error, from the `bin/docket check
--verify` step:

```
PL-D1RT is open but its `verify:` command already passes (1 of 164 checked).
```

Every other step of that job passes - `ruff format`, `ruff check`, `mypy`,
2 979 tests, 100% core coverage.

**Why no local run sees it.** `--verify` is passed by CI and by nothing else;
`make check` runs `bin/docket check` bare. `.claude/skills/docket/SKILL.md` says
so in terms - "CI is what passes that flag, so this is caught after the item is
written *and* after it is pushed" - so the gap is known and its cost was not.
Every session on this repository has run `make check`, seen it exit 0, and had no
way to learn that `main` was red.

**Nor does a pull request see it, which is the structural half.**
`.github/workflows/quality.yml:271-280` runs two different commands: on
`pull_request` it is `bin/docket check --verify --verify-base "$VERIFY_BASE"`,
**scoped to what the branch changed**, and only on `push` to `main` is it the
bare `--verify` over the whole store. So a `verify:` command that goes stale
through *another* item's work is invisible on every branch that does not touch
it, and becomes visible the moment it is merged. Measured on `#639`: `checks`
green in 2m50s on the `pull_request` event, against 6m14s and one error for the
same store on `main`. The scoping is deliberate and its cost is this: the
whole-store replay has no pre-merge run anywhere.

**The cause, and it is not what the error's two dispositions assume.**
`PL-D1RT`'s command is:

```
python3 tools/doc_check.py check && ! grep -qF '`v0.5.x - the interface pass` row of "The timeline"' ROADMAP.md
```

`PL-PHKP` (`#634`) renumbered that row `v0.5.x` to `v0.7.x`. The string vanished,
the negated `grep` began passing, and the command was satisfied by another item's
work. `52205f6` is `#634`, which is the commit `main` went red on.

**So the item needs re-scoping rather than closing or a new command.** The error
offers two dispositions - the work landed, close it; or the command does not
discriminate, rewrite it - and `PL-D1RT`'s `Done when.` fits neither, because
**two decisions taken since have contradicted its premise**:

- It requires "item 33's placement note says it is **absorbed by the port
  milestone**". `ROADMAP.md:308` now records that absorption **reversed on
  2026-09-16** (project owner, on `PL-L9RD`), and item 33 is restored to a row of
  its own.
- It assumes the `v0.5.x - the interface pass` row was **deleted**. `PL-PHKP`
  **kept** it and renumbered it `v0.7.x` (project owner, 2026-09-16, ratified).

Its other clause - that neither `ROADMAP.md` nor `docs/WORKING_NOTES.md` cites a
`v0.5.x` interface-pass row - is satisfied today, but both files now carry the
rename as recorded history rather than the absorption the item asked for.

**Why it matters.** A red default branch makes every branch's red CI unreadable:
a session cannot tell its own failure from the inherited one without reading the
job log, and `#639` is already in that position. It is also `CLAUDE.md`'s
silent-wrong-answer test exactly - `make check` passes while the guarantee it
stands for is void - and the population is every session, not one.

**Decision needed.** What becomes of `PL-D1RT`? Its own `Done when.` is no longer
achievable as written. Three dispositions, and this is the project owner's
because two of their own decisions are what overtook it:

1. **Drop it with a reason** naming `PL-L9RD` and `PL-PHKP` as what superseded
   it. The substance it was about - that a reader of the planned-milestone
   narrative gets the wrong sequence - may simply no longer be true.
2. **Re-scope it** to whatever prose is *still* stale against the current order,
   with a `verify:` naming something only that work creates.
3. **Close it** if the sweep is genuinely complete, and record that `PL-PHKP`
   did the work.

Whichever is chosen, `main` goes green with it.

**Done when.** `PL-D1RT` carries one of the three dispositions below, `bin/docket
check --verify` reports no error on `main`, and the green run is on a commit at or
after the one carrying that disposition. The second finding below is recorded
here and answered wherever `PL-Q8RQ` is answered, not as a condition of this.

**A second finding, recorded rather than fixed here.** A `verify:` command whose
sentinel is an *absence* (`! grep -qF`) can be satisfied by any change that
removes the string, including another item's. That is the class `PL-Q8RQ` names
for a bare `pytest -k`, arriving through a different door: the paired shape
`.claude/skills/docket/SKILL.md` prescribes pins the *presence* of something the
work creates, and a negated `grep` inverts exactly that property. Whether
`docket check` can refuse a negated-grep sentinel the way `PL-Q8RQ` would have it
refuse a bare `-k` is worth deciding alongside that item.
