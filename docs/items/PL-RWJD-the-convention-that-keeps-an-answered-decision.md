---
id: PL-RWJD
title: The convention that keeps an answered decision section readable - leave the question, write the dated answer underneath - is written down nowhere a triaging session reads, so the practice holding delegable's open-brief count at zero is an accident
priority: P3
effort: S
status: ready
classes: docs
feature: brief-state-agreement
touches: .claude/skills/docket/modes/triage.md
added: 2026-09-22
payoff: a session recording an owner's answer keeps the question and dates the answer because its own mode says to, not because it happened to read docs/worker.md
verify: grep -qiE 'answer[^.]*underneath' .claude/skills/docket/modes/triage.md
---

**Problem.** The convention that keeps an answered decision section readable - leave the question, write the dated answer underneath - is written down nowhere a triaging session reads, so the practice holding delegable's open-brief count at zero is an accident

**Reproduced 2026-09-22 (`PL-14QR`, triage).** The convention is written down once, in
`docs/worker.md` line 360 ("leave the question standing and write the answer
*underneath* it"), which is addressed to a worker reading a brief.
`.claude/skills/docket/modes/triage.md` does not contain the word `underneath`,
and that is the mode which writes a `**Decision needed.**` section and its
marked recommendation.

**Why it matters.** The convention is needed by whoever writes an answer, and
no mode a writing session reads carries it. A session recording an owner's
answer can just as easily overwrite the question, or add the answer with no
date. Either one destroys what the convention protects: a later reader's
ability to tell a settled question from an open one, and to see what was
weighed. `PL-X4RX` shows what an undated one looks like.

**Done when.** The mode a session is in when it records an owner's answer states
the convention: the question stays standing, and the answer goes beneath it with
its date and its kind (`ratified` or not, per `CLAUDE.md`). `triage.md` carries
it at the least.
