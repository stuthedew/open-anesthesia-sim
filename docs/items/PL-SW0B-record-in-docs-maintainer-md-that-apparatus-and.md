---
id: PL-SW0B
title: Record in docs/maintainer.md that apparatus and analysis sessions run at high effort on Opus 5.5, and correct its sentence calling high Claude Code's default, which Opus 5.5 changed to medium
priority: P2
effort: S
status: done
classes: docs, session-cost
feature: model-evidence
milestone: v0.5.26
touches: docs/maintainer.md
added: 2026-10-17
closed: 2026-10-17
pr: 1520
payoff: the effort record matches what the owner runs and what Opus 5.5 defaults to, so a session that sets no level is not silently one step below the agreed split
verify: ! grep -qF 'documented default is' docs/maintainer.md
---

**Problem.** Record in docs/maintainer.md that apparatus and analysis sessions run at high effort on Opus 5.5, and correct its sentence calling high Claude Code's default, which Opus 5.5 changed to medium

**Decision** (project owner, 2026-10-17, ratified, over recording `xhigh` as
the uniform level). Apparatus sessions, including analysis and design rounds
about the apparatus, open at `high` on Opus 5.5. Simulator sessions are
unchanged. The owner agreed in session_016Hv97dHUS9f4zXzkt2bU2E, which
reviewed Anthropic's "Optimizing for cost and intelligence" page.

**Why it matters.** On 2026-10-17, six of the seven sessions in this repository ran at
`xhigh`. That matches neither half of the 2026-09-19 split in
`docs/maintainer.md` § "Match effort to the standard the work is held to",
which puts apparatus at `high` and the simulator at `max`. Anthropic measured
Opus 5.5 on its SWE-bench Pro subset at $0.29 per task and 95.3% solved at
`high`, against $0.74 and 96.7% (one run) at `xhigh`. The page calls these
figures directional
(https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
§ "Tune effort"). Claude Code's effort table recommends `high` for "fixing a
bug in an existing codebase". It warns that `max` "may show diminishing
returns and is prone to overthinking"
(https://code.claude.com/docs/en/model-config, § "Choose an effort level").

**What to change.** In that section, record the decision above with its
record line. Replace "Claude Code's documented default is `high`", which is
false for Opus 5.5: that model, Sonnet 5.5 and Haiku 5.5 default to `medium`
(same page, § "Adjust effort level"). Add that the effort scale is calibrated
per model, and that "Opus 5.5 at `medium` matches or exceeds Opus 5 at
`high`" on coding work, quoting the same page. Leave § "Which model each flag
means" to `PL-XJV3`.

**Done when.** The section states the decision and the Opus 5.5 default, and
no sentence calls `high` Claude Code's default.

**Generator check.** Not a member of a head: one decision recorded in one section.
