---
id: PL-18ZB
title: A debt-gate bullet that writes its id as code is read as commentary and never as an entry, and nothing a session reads before writing a gate says so
priority: P3
effort: S
status: ready
classes: docs
feature: gate-list-integrity
touches: .claude/skills/docket/modes/release.md
added: 2026-10-01
payoff: a session writing a gate entry learns before writing it that an id written as code takes the entry off the gate
verify: grep -qiF 'read as commentary' .claude/skills/docket/modes/release.md
---

**Problem.** A debt-gate bullet that writes its id as code is read as commentary and never as an entry, and nothing a session reads before writing a gate says so

**Why it matters.** `roadmap._gate_entries` reads an entry's ids through
`vcs.leading_ids`, which deliberately takes no backtick: `ROADMAP.md` cites ids
as code in the bullets that *explain* a gate, five of them on 2026-10-01, three
naming the items v0.6.0 deferred off its gate, and read as entries they would
put those items back on (`PL-SVRW`). So the convention is load-bearing in the
other direction too. An entry written as code, `` - `PL-B1C2` (S) ... ``, is not
on the gate, and the gate reads clearer than it is with nothing saying so. The
rule lives only in the comment above `vcs.LEADING_IDS_RE` and in
`test_a_bullet_citing_an_id_as_code_explains_the_gate_and_is_not_on_it`;
neither `ROADMAP.md`'s rules for the frozen list nor
`.claude/skills/docket/modes/release.md`'s freeze mode states it. The freeze
mode writes the list by hand from `bin/docket gate`, which prints bare ids but
not the entry's format, so the exposure is a session formatting an id as code
while writing an entry.

**Done when.** The text a session reads before writing a gate entry says that
an entry opens with its bare id and that a bullet citing an id as code is read
as commentary.

**Reproduced 2026-10-01.** `grep -ciF 'read as commentary' .claude/skills/docket/modes/release.md` prints 0, and the freeze mode says nothing about an id written as code.

**Generator check.** The fact is `PL-HWW1`'s - which ids a milestone section declares as members, as distinct from ids its prose cites - at the frozen list rather than `Required scope`, filed after that head closed. No reader has misread it yet; this is the anticipated exposure, so it records no re-filing and is not a new generator.
