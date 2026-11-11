---
id: PL-B3TQ
title: docs/maintainer.md § 'Match effort to the standard the work is held to' says a Projects thread runs at the level the coordinator started it with (PL-6LVZ), while .claude/skills/docket/modes/triage.md says a Projects thread sets its level with its own effort setting; say which holds, in one place (found by PL-GZFR's search, 2026-11-11)
priority: P3
effort: S
status: ready
classes: defect, docs
touches: docs/maintainer.md, .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value
added: 2026-11-11
payoff: a Projects thread finds one statement of the effort level it runs at
verify: ! grep -qF 'sets its level with its own effort setting' .claude/skills/docket/modes/triage.md
---

**Problem.** docs/maintainer.md § 'Match effort to the standard the work is held to' says a Projects thread runs at the level the coordinator started it with (PL-6LVZ), while .claude/skills/docket/modes/triage.md says a Projects thread sets its level with its own effort setting; say which holds, in one place (found by PL-GZFR's search, 2026-11-11)

**Checked 2026-11-11.** `docs/maintainer.md` says "A thread runs at the level the coordinator started it with (`PL-6LVZ`)." `.claude/skills/docket/modes/triage.md` § "Generators, how they rank, and the pause they set" says "A Projects thread is in neither arm already, and sets its level with its own effort setting."

**Why it matters.** A Projects thread that has to set its own effort level reads one of the two sentences and may act on the other's wording. Two statements of one fact break `CLAUDE.md`'s rule that a shared fact has one home, and they will drift further apart.

**Done when.** `triage.md` no longer states the level a Projects thread runs at, and points to the sentence in `docs/maintainer.md` instead.

**Generator check.** A one-off: a second copy of one sentence in prose. No head's `misread:` states the effort level a session runs at.
