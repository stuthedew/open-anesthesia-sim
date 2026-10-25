---
id: PL-HDRN
title: bin/docket arm does not hold a simulator pull request whose blind generalist review passes were never run: PL-TDV9's close-out step 9 is prose only, and PL-W04Z measured that 5 of 6 simulator branches skipped close-out step 8's prose review until arm held for its Prose-review trailer; record the passes as a Blind-review trailer and hold on tools/blind_review.py --count
priority: P2
effort: S
status: done
classes: infra
feature: review-panel
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_arming.py, subprojects/docket/README.md, docket.toml, tools/blind_review.py, .claude/skills/docket/modes/close-out.md, .claude/skills/pull-request/SKILL.md, docs/apparatus.md
added: 2026-10-24
closed: 2026-10-25
pr: 1767
payoff: a simulator pull request cannot merge without the blind review passes that catch about half of later-filed defects, the way the prose-review hold stopped five skips in six
verify: grep -q 'def test_arm_holds_without_blind_review' subprojects/docket/tests/test_arming.py && grep -q 'def test_arm_holds_when_blind_count_fails' subprojects/docket/tests/test_arming.py && grep -q 'Blind-review: passes' .claude/skills/docket/modes/close-out.md && grep -q '^blind_count_command' docket.toml
---

**Problem.** `bin/docket arm` does not hold a simulator pull request whose
blind generalist review passes were never run. Close-out step 9 in
`.claude/skills/docket/modes/close-out.md` asks for one pass on every
simulator pull request and a second on one that changes the model's code, its
parameter files or `docs/MODEL.md` (project owner, 2026-10-24, ratified,
`PL-TDV9`). Nothing records that the passes ran, and nothing refuses a merge
without them. `tools/blind_review.py --count` already prints how many passes a
branch owes, read from `docket.arming.blind_passes`.

**Why it matters.** A step stated only in prose is skipped. `PL-W04Z`
measured that 5 of 6 simulator branches skipped close-out step 8's prose
review until `arm` held for its `Prose-review` trailer. The blind passes are
the project's main defence against a defect in a clinical value reaching
`main`: `PL-TBQS`'s replay found one blind generalist named about half of the
defects filed later. A skipped pass on a `core/` change is the costly case.
No simulator branch has merged since step 9 landed on 2026-10-25 (#1759), so
the skip rate cannot be measured yet; the hold costs a branch that ran the
passes one trailer line, which is why it is built now rather than after the
measurement.

**Done when.** A session records the passes as a `Blind-review: passes N,
findings F, fixed X, filed Y, rejected Z` trailer, as close-out step 9 says.
`bin/docket arm` holds a branch that changes a simulator path while the newest
such record on the branch records fewer passes than
`blind_count_command` (`tools/blind_review.py --count` in `docket.toml`) says
it owes, and holds where that count could not be read. A malformed record is
said beside the answer and covers nothing. The hold is off where no command is
configured. Tests in `subprojects/docket/tests/test_arming.py` pin each case.

**Generator check.** The fact misread is whether a simulator branch ran a
close-out review step, which only prose stated. `PL-W04Z` is the first
instance, for step 8, and no head's `misread:` states it; two items are not a
generator, so this is follow-up work on the owner's `PL-TDV9` decision.
