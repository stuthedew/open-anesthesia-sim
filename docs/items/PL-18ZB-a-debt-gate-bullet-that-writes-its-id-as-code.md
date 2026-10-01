---
id: PL-18ZB
title: A debt-gate bullet that writes its id as code is read as commentary and never as an entry, and nothing a session reads before writing a gate says so
status: untriaged
feature: gate-list-integrity
added: 2026-10-01
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
