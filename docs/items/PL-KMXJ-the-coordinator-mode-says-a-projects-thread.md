---
id: PL-KMXJ
title: The coordinator mode says a Projects thread does not load .claude/ and lists none of the repository's skills, but the thread that sorted the launch instructions on 2026-11-21 loaded the three resident rules and a path-scoped rule on read, and its Skill tool listed docket, model-review, pull-request and run-the-app; only the guard hooks were missing (its first command printed 5 passed)
priority: P3
effort: S
status: done
classes: defect, docs
feature: projects-trial
milestone: v0.6.20
touches: .claude/skills/docket/modes/coordinator.md
deferred-from: v0.7.0 - a new problem: the two sentences were written after the freeze (PL-CR81, filed 2026-10-25; moved into the coordinator mode by #2192, f4c5ef27), and the platform behaviour they describe changed after that
added: 2026-11-21
closed: 2026-11-22
pr: 2224
payoff: Projects threads are told what they actually load, so none works around rules and skills it already has, and the hook probe is still run.
verify: grep -qF 'What a Projects thread loads, as last observed on 2026-11-22' .claude/skills/docket/modes/coordinator.md
---

**Problem.** The coordinator mode says a Projects thread does not load .claude/ and lists none of the repository's skills, but the thread that sorted the launch instructions on 2026-11-21 loaded the three resident rules and a path-scoped rule on read, and its Skill tool listed docket, model-review, pull-request and run-the-app; only the guard hooks were missing (its first command printed 5 passed)

**Checked 2026-11-22**, at `d4e8200c`. `grep -n 'does not load\|lists none' .claude/skills/docket/modes/coordinator.md`
prints line 100, "A Projects thread does not load `.claude/` (`PL-CR81`)",
and line 107, "A thread's Skill tool lists none of the repository's skills".
A triage worker run under a Projects coordinator on 2026-11-22 was again given
`CLAUDE.md` and the three resident rules at launch, and its Skill tool listed
`docket`, `model-review`, `pull-request` and `run-the-app`. So both sentences
are out of date. The instruction to run the test file first, as a probe for the
guard hooks, still applies, because only the hooks were missing.

**Why it matters.** The coordinator mode is what every Projects thread reads
before it starts. A thread told that the rules and skills are absent works
around something it has, and a later session reading the two sentences learns
a fact about the platform that is no longer true.

**Done when.** The coordinator mode says what a Projects thread loads as last
observed, with the date: the resident rules and the skills, and no guard hooks
unless the setup script adds them. It keeps the first-command probe for the
hooks, and drops or rewrites the closing line that waited on threads loading
`.claude/`.

**Generator check.** The fact is what a Projects thread loads from `.claude/`.
That is an outside platform's behaviour, which changed after the two sentences
were written, and the sentences state a dated observation as a standing one.
One-off: no other open item misreads it. `PL-4J4H` (a thread started above its
checkout) is about where a thread starts, which is a different fact.

**Done 2026-11-22.** `.claude/skills/docket/modes/coordinator.md` now says what a Projects thread loads, as observed on 2026-11-22: `CLAUDE.md` and the resident rules, path-scoped rules on read, the skills, and the guard hooks only from the setup script. The thread "Finish all open defects" had the hooks that day, because the gate-status guard refused its first command. The first-command probe stays. Files checked: `docs/maintainer.md` § on the setup script, which already matches.
