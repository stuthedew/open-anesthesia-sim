---
id: PL-0QRP
title: A verify: clause that counts occurrences of a symbol passes as soon as any unrelated change adds one, so the skill's verify guidance should name counting beside the -k and --cov traps
priority: P2
effort: S
status: ready
classes: docs
feature: verify-command-meaning
touches: .claude/skills/docket/SKILL.md
added: 2026-09-19
verify: grep -rqF 'nothing unrelated can drive it there' .claude/skills/docket/
---

**Problem.** A verify: clause that counts occurrences of a symbol passes as soon as any unrelated change adds one, so the skill's verify guidance should name counting beside the -k and --cov traps

**Found 2026-09-19 on `PL-R0P3`, by `bin/docket check --verify` in CI.** Its
command asked for three call sites of a helper, expecting the two conversions
it wanted to take the count from one to three. Two *unrelated* new callers
arrived instead - one merged to `main` from another branch, one added by the
branch that was running - and the command passed with none of the work done.

**Why it matters, and why it is a shape rather than one bad command.** The `-k` trap and the
`--cov=` trap are already in the skill's `verify:` guidance, and both are about
a command that fails for the wrong reason. This is the mirror: a command that
*passes* for the wrong reason, and it has a property neither of those has - it
gets more likely to fire the longer the item stays open, because every commit
to the file is another chance for the count to drift over the line. An item
left open for months is exactly the one whose proof quietly stops proving
anything.

**The rule to write down:** a clause must test the property the work
establishes, not count a symptom of it. `grep -c ... = 0` for a spelling the
work removes is safe, because nothing unrelated can drive it to zero. `grep -c
... -ge N` for a spelling the work adds is not, because anything at all can
drive it up. The asymmetry is worth stating in the skill, since counting looks
like the obvious mechanical test for a refactor item.

**Where.** `.claude/skills/docket/SKILL.md`, § "The `verify:` command, and
running it before writing it down" - the table of shapes and the paragraph
about watching it fail for the right reason. Deliberately not done on
`PL-HWW1`'s branch: that pull request was fixing the instance, and the
drive-to-green rule keeps a CI fix minimal rather than widening it.

**Not a duplicate of `PL-CWD4`**, which is a command that can never pass on any
tree and so reads like unfinished work. This is a command that starts passing
without the work.

**Done when.** `.claude/skills/docket/SKILL.md`'s `verify:` section names counting
as a third trap beside the `-k` and `--cov=` ones, states the asymmetry that makes
it a trap - a count the work drives to *zero* is safe, because nothing unrelated
can drive it there, and a count the work drives *up* is not, because anything at
all can - and says what to write instead: the `grep` for the spelling or the test
name the work adds, which no unrelated commit satisfies.
