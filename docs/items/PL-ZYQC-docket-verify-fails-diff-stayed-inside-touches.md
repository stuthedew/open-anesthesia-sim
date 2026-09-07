---
id: PL-ZYQC
title: docket verify fails 'diff stayed inside touches' on any close-out that follows the skill's instruction to let docket record ride the commit it is already making
status: untriaged
added: 2026-09-07
---

**Problem.** docket verify fails 'diff stayed inside touches' on any close-out that follows the skill's instruction to let docket record ride the commit it is already making.

Two instructions in the apparatus give opposite answers about the same commit.
The `docket` skill's close-out, step 1, says of `bin/docket record`: "Let the
write ride a commit you are already making; do not compose one for it, and do
not open a pull request for it alone." `bin/docket verify <id>` then reads that
same commit against the item's `touches` and reports every `docs/items/*.md`
the record wrote as a path outside the commission.

Observed 2026-09-07 closing `PL-X204` (the accounting guard reading the
validator it is called on). `bin/docket record` wrote `pr:` onto `PL-0ZGK`,
`PL-2B7B` and `PL-BKDP` — the three numbers `docket check`'s own advisory said
the base was owed, and the advisory cleared once they were written. `bin/docket
verify PL-X204` then returned `REJECT` with:

```text
FAIL  diff stayed inside `touches` - 3 path(s) outside
        docs/items/PL-0ZGK-main-s-quality-run-has-failed-on-its-last-three.md
        docs/items/PL-2B7B-triage-the-seven-captures-open-on-the-evening.md
        docs/items/PL-BKDP-a-v0-4-8-tag-exists-on-the-commit-that-closed.md
```

**Why it matters.** It is not a wrong answer that a reader can act on — the
paths are named, and a session that knows what `record` does can see what
happened. The cost is that the failure is unavoidable rather than
informative: any session that follows the close-out as written and then runs
`verify` gets it, so the check fires on correct work and cannot distinguish
correct work from the thing it exists to catch. `CLAUDE.md` calls that a
defect in the check — "a check that fires every run without changing a
decision costs attention forever and trains a session to skim the output
where a real advisory also appears" — and the real advisory here is the
*other* `FAIL` in the same block, the protected-path one, which is the line
a reader of a delegated `core/` change actually needs to see.

**Where.** `bin/docket verify`'s `touches` audit, against the `docket` skill's
close-out step 1 (`.claude/skills/docket/SKILL.md`).

**Decision needed.** Which of the two moves. Three candidates, unranked
because the trade is real:

- Exempt a `pr:`-only edit to another item's front matter from the `touches`
  audit. Narrow and mechanical — the write is tool-dictated and `record`
  refuses to overwrite a differing number — but it puts a second reading of
  what `record` may write into `verify`.
- Have `record` report which paths it wrote so `verify` can subtract exactly
  those, rather than pattern-matching the shape of the edit.
- Change the close-out to give `record` its own commit, and teach `verify` to
  ignore commits whose whole diff is `docs/items/`. This reverses an
  instruction that was written deliberately, so it needs the reasoning behind
  "do not compose one for it" checked before it is taken.

**Found.** Closing `PL-X204` and running `bin/docket verify` on the result, as
that item's close-out calls for.
