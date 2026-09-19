---
id: PL-6TN8
title: A verify: command whose discriminating half greps for a test name can exit 1 because the name was guessed, not because the work is outstanding, so watching it fail proves less than the rule assumes
priority: P2
effort: S
status: done
classes: defect
feature: verify-command-health
milestone: v0.4.28
touches: .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-17
closed: 2026-09-19
pr: 680
not-delegable: the outcome is a disjunction the count decides - either the skill gains a sentence or this item records why one instance did not justify one - so nothing can be named in advance that the work adds. Pinning a `grep` on a sentence not yet written would be exactly the name-bet this item is about.
---

**Problem.** A verify: command whose discriminating half greps for a test name can exit 1 because the name was guessed, not because the work is outstanding, so watching it fail proves less than the rule assumes

**Found closing `PL-3DC7`** (dropped 2026-09-17 as already fixed on `main`),
during the `PL-Y4D6` triage pass, on an item that pass had itself triaged an
hour earlier.

**The instance.** `PL-3DC7` was set `ready` with

```
uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_dropped_item_naming_no_command_still_runs_the_integrity_checks' subprojects/docket/tests/test_verify.py
```

run and seen to exit 1, which is exactly what
`.claude/skills/docket/SKILL.md` asks for: an ordinary failure, not the 5 a
bare `-k` gives, with the suite half proving the file healthy. The behaviour it
described was **already on `main`**, under three differently-named tests
(`test_dropped_close_out_is_not_a_missing_command` and two others), landed by
`#655` two hours before. The command failed because the *name* was invented, and
it would have gone on failing until somebody wrote a test called that.

**Why it matters.** The skill's table presents the paired shape as a
specification - "the pytest half proves the file's suite healthy, and the `grep`
half names the exact test the work owes, which makes the command a specification
rather than a bet on a name". Against an unstarted item that is true. Against an
item whose work may already exist it is precisely a bet on a name: a negative
`grep` for a name nobody has agreed to cannot distinguish *the behaviour is
absent* from *the behaviour is present under another name*, and the failure it
produces is indistinguishable from the intended one. The rule's own words -
"watch it fail for the right reason" - are what this defeats, so a session
following the rule exactly gets false confidence rather than a warning.

**Why it is not `PL-XMNC` or `PL-LBW5`.** `PL-XMNC` catches a command that
*starts passing* because another branch changed a file it reads; this is a
command that keeps failing when it should have passed. `PL-LBW5` is about paths a
command reads that its `touches` omits. Neither reaches a command that was wrong
the moment it was written.

**Count before building anything**, per `CLAUDE.md`'s gate and `PL-879R`'s
precedent - that item was dropped because a shape advisory would have printed 31
correct ids every run. The count that decides this one: of the open items whose
`verify:` greps for a `def test_` name, how many name a test that does not exist
*and* describe behaviour that does. One instance is not a population.

**Done when** the count is taken and recorded here, and either the skill's
verify-command guidance says that a name-pinning `grep` on an item whose work may
already exist has to be checked against the code rather than against the test
names, or this item records why one instance did not justify the sentence.

**Counted and closed under `PL-6TP8`, 2026-09-19.** The mechanical half of the
count: 63 open items pin a `def test_…` name with a `grep`, and none of the 63
names a test that already exists in the tree, so no such command passes today
for the wrong reason. The judgment half - how many describe behaviour already
present under another name - is not countable by a script, and that is the
finding rather than a gap in it: `PL-6TP8`'s contract records the case as
undecidable by any exit status, which makes the sentence this item asked for a
consequence of the contract rather than a rule a count has to justify. The
sentence is in the `docket` skill's `verify:` section: a name-pinning `grep` on
an item whose work may already exist is checked against the code before it is
written.
