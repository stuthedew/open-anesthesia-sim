---
id: PL-T4YD
title: Surface the wave line in the session-start digest, so the roadmap nags as the queue does
status: dropped
feature: planning-cadence
touches: .claude/hooks/docket-digest.sh, subprojects/docket
added: 2026-08-29
closed: 2026-08-30
reason: merged into PL-F58L, which asked for the same line from the digest's side and has shipped it; this item's contribution was the budget - one line, not wave's five - and that constraint is recorded in PL-F58L and in subprojects/docket/README.md
---

**Problem.** `docket wave` computes which beat of the cadence is due, but
nothing runs it unprompted. The session-start hook emits `docket digest`, so
the queue still nags every session while the plan nags only a session that
thinks to ask.

**Why it matters.** `PL-6G8C` was filed because sessions answer "what next"
from whatever ranks highest in `docs/items/`, which is a question above the
queue's altitude. A command nobody runs does not change that. The skill now
tells a session to run it in the recommend-what-to-work-on mode, which covers
the case where the owner asks — not the case where a session simply starts
work.

**Where.** `.claude/hooks/docket-digest.sh`, which today runs `bin/docket
digest` alone. The obvious form is a second line of output, or a `--wave` flag
on `digest` so one invocation produces both.

**The trade to decide.** The digest is resent on every turn of the session, so
its length is a standing cost. `docket wave` prints five to seven lines today;
a digest line would want to be one or two — the beat and the step, with the
gate's split, and nothing else. Whether that fits, and whether it displaces
anything currently in the digest, is the decision.

**Done when.** A session starting cold knows which beat is due without running
anything, and the digest has not grown by more than a line or two.
