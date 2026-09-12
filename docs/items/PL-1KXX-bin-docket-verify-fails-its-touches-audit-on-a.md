---
id: PL-1KXX
title: bin/docket verify fails its touches audit on a branch that rode bin/docket record, because the record writes another item's file and the audit cannot know the skill sanctioned it
status: dropped
added: 2026-09-07
closed: 2026-09-12
reason: Duplicate of PL-ZYQC (docket verify fails its touches audit on a close-out that let docket record ride the commit). Same defect, same mechanism, captured the same day; PL-ZYQC carries the fuller brief - the observed REJECT on PL-X204 naming all three item files, a recommendation, and the two alternatives it refuses - so it is the one kept.
---

**Problem.** bin/docket verify fails its touches audit on a branch that rode bin/docket record, because the record writes another item's file and the audit cannot know the skill sanctioned it

Observed 2026-09-07 on `PL-GZP6`'s branch. `bin/docket check` raised its
standing grooming advisory for `PL-BKDP` - marked done on `origin/main`,
recording no `pr`, with `#440` recoverable from its merge commit - and the
advisory's own wording, matching `.claude/skills/docket/SKILL.md`'s close-out
step 1, says to let `bin/docket record` "ride the commit you are already
making rather than composing one". The session did that.

`bin/docket verify PL-GZP6` then reported:

```text
FAIL  diff stayed inside `touches` - 1 path(s) outside
        docs/items/PL-BKDP-a-v0-4-8-tag-exists-on-the-commit-that-closed.md
```

Every other line passed, including the `verify:` command and `make check`,
and the overall verdict was `REJECT`.

**Why it matters.** Two project mechanisms give opposite instructions for the
same commit, and a session cannot satisfy both. The audit is right that the
path is outside `touches`; the skill is right that composing a separate commit
for a `record` write is friction the project decided against. The failure mode
is not a wrong result so much as a rule a careful session cannot follow, which
tends to get resolved by whichever document it read most recently - or by
widening `touches` to cover another item's file, which is the one resolution
that makes the audit meaningless.

Not caught by CI, which runs `bin/docket check` and `bin/docket check --verify`
rather than `bin/docket verify <id>`, so this surfaces only for a session that
audits its own branch or for delegated work being reviewed.

**Approach.** Undecided. The narrow fix is for the touches audit to exempt
exactly what `record` writes - a `pr:` field addition to a closed item's front
matter, which is a shape it could recognise rather than a path it has to be
told about. Alternatives: have `record` stage its writes for a separate commit
led by the current item's id, the way `CLAUDE.md`'s fix-now rule handles an
out-of-touches fix; or have the audit read the commit's own subject and accept
a `record` line. The first keeps one commit, which is what the close-out rule
wants.

**Where.** `subprojects/docket/` - the `verify` touches audit and `cmd_record`;
`.claude/skills/docket/SKILL.md` close-out step 1.
