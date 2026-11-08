---
id: PL-7XTS
title: Nothing routes a close-out to bin/docket verify --self, so a session auditing its own branch runs the delegated mode PL-69JZ fixed and still gets a REJECT on correct work
priority: P2
effort: S
status: done
classes: defect, docs
feature: delegation
milestone: v0.4.26
touches: .claude/skills/docket/SKILL.md
added: 2026-09-12
closed: 2026-09-15
pr: 595
verify: python3 tools/doc_check.py check && grep -qF 'verify --self' .claude/skills/docket/SKILL.md
---

**Problem.** Nothing routes a close-out to bin/docket verify --self, so a session auditing its own branch runs the delegated mode PL-69JZ fixed and still gets a REJECT on correct work

**Observed 2026-09-12**, on this session's own close-out of `PL-KY7M` (the uv
`UV_NATIVE_TLS` translation), hours after `#496` merged the `--self` mode:

```text
FAIL  the checks themselves are unedited - Makefile
REJECT
```

`bin/docket verify --self PL-KY7M` on the same branch reports `NOTE ... this is
a self-audit, not a delegated review` and `ACCEPT`, which is exactly what
`PL-69JZ` built. The session only found the flag by reading `PL-69JZ`'s own
brief, because nothing on the path it was following names it.

**Mechanism - an absence rather than a stale line.**
`.claude/skills/docket/SKILL.md`'s "Mode: close out an item" has five steps and
none of them is the audit; its only two mentions of `docket verify` are about
`verify:` commands. `CLAUDE.md`'s fix-now rule names the command once -
"`bin/docket verify` reads the diff for files outside an item's declared
`touches`" - and that is the delegated mode. So the resident instruction points
a session at the refusing mode and the skill never mentions the flag.
`subprojects/docket/README.md` documents `--self` correctly, at lines 36 and
1687, which is the reference a session reads when it already knows what it is
looking for.

**Why it matters.** `PL-69JZ` closed on the reasoning that a `REJECT` fired on
correct work "trains a reader to skim the block where the *protected-path*
failure, the one that matters, is printed" - `CLAUDE.md`'s named failure mode
for a check. The code no longer does that; the documented procedure still leads
every session into it, so the defect survives its own fix wherever a session
follows the skill rather than the README.

**Done when.** A session following the close-out procedure reaches
`bin/docket verify --self <id>` without reading an item's brief to find it.

**Confirmed at triage, 2026-09-12.** `grep -- '--self' .claude/skills/docket/SKILL.md
CLAUDE.md` returns nothing from either file, so the absence this item describes is
exact rather than approximate: the flag appears in neither document a session
follows.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". This item is also named in paragraphs quoted in the brief of `PL-0C6W`. The paragraph that disposed of it counts it among its entries without naming it, and is quoted in `PL-0QQP`'s brief.

> - PL-7XTS (S) Nothing routes a close-out to bin/docket verify --self, so a session auditing its own branch runs the delegated mode PL-69JZ fixed and still gets a REJECT on correct work — closed in v0.4.26
