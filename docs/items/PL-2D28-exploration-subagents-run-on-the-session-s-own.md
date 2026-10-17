---
id: PL-2D28
title: Exploration subagents run on the session's own model, Opus 5.5 in this project's threads, because CLAUDE_CODE_SUBAGENT_MODEL never reaches the built-in Explore subagent and a cloud session applies none of the env block in .claude/settings.json: decide whether a project Explore agent pins a cheaper model, and whether the variable stays (found in PL-KLN5)
priority: P2
effort: S
status: needs-decision
classes: session-cost
touches: .claude/settings.json, .claude/agents, docs/maintainer.md
deferred-from: v0.6.0 - apparatus session-cost work: which model an exploration subagent runs on changes nothing the milestone ships
added: 2026-10-17
payoff: exploration subagents run on a model chosen for search rather than inherited by default, and the settings file stops claiming a lever it does not have
---

**Problem.** Exploration subagents run on the session's own model, Opus 5.5 in this project's threads, because CLAUDE_CODE_SUBAGENT_MODEL never reaches the built-in Explore subagent and a cloud session applies none of the env block in .claude/settings.json: decide whether a project Explore agent pins a cheaper model, and whether the variable stays (found in PL-KLN5)

**What is known.** Each fact below was read on 2026-10-17 from the
documentation page's own Markdown, not from a summary of it.

The built-in Explore subagent runs on the main conversation's model. When the
main conversation runs Fable on a Claude subscription, Explore runs on the
Opus model that the `opus` alias points to. Explore starts without the
CLAUDE.md files and the git status snapshot, "to keep research fast and
inexpensive", and its tools are read-only
(https://code.claude.com/docs/en/sub-agents, § "Built-in subagents", Explore
tab). Setting `CLAUDE_CODE_SUBAGENT_MODEL` by itself does not change the model
Explore or Plan run on. Claude Code chooses a subagent's model in this order: a
`model` passed on the invocation, then the definition's `model` field, then
the variable, then the main conversation's model (same page, § "Choose a
model"). So in this project's Opus 5.5 threads Explore runs on Opus 5.5, and in
a Fable session it runs on Opus.

In a cloud session the variable does not apply at all. There are now four
measurements. `PL-KLN5` found it unset in the Bash shell of two one-repository
sessions on 2026-10-01, and on 2026-10-17 a `general-purpose` subagent in a
Projects thread ran on `claude-opus-5-5`, its parent's model. This design
round's session is the fourth: a one-repository cloud session
(`CLAUDE_CODE_ENTRYPOINT=remote_desktop`,
`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1`) whose diagnostics log records
`settings_load_completed` with four sources, whose two SessionStart hooks ran,
and whose shell still has `CLAUDE_CODE_SUBAGENT_MODEL` unset. The settings
guide says that most `env` values "apply only after each teammate trusts the
folder" (https://code.claude.com/docs/en/settings, § "A committed key doesn't
reach teammates"). Claude Code keeps trust decisions in `~/.claude.json`, and
in this session that file's `projects` map is empty, so the checkout has no
trust record. That fits the trust step being the cause. It is not a proof,
because nothing read here says what the hosted harness does with the block.

A session added the variable on 2026-08-23, in commit `182a015c`, because
`CLAUDE.md` then named it and nothing set it. `CLAUDE.md` no longer names it.
The decision's kind is unrecorded, so ordinary evidence reopens it.

**Routes, and the one recommended.**

1. **A project `Explore` definition at `.claude/agents/Explore.md`.
   Recommended.** The documentation says: "A user or project subagent named
   `Explore` overrides the built-in and keeps its own `model` field, so define
   one with `model: haiku` to run exploration on a lower-cost model"
   (sub-agents page, Explore tab). A cloud session loads the repository's
   `.claude/agents/` because the directory is part of the clone
   (https://code.claude.com/docs/en/cloud-environments, § "What carries over
   from your setup"). A `model` passed on the invocation still wins over the
   file, so the file sets a default and not a ceiling: a session can still ask
   for Opus on one hard search. The file replaces the built-in's own prompt
   and settings, so the build must carry three things. First,
   `omitClaudeMd: true`, so the agent keeps the built-in's cheap start without
   the CLAUDE.md files; the field exists since Claude Code v2.1.271 and the
   cloud container runs 2.1.302. Second, a body that keeps the three
   thoroughness levels the main conversation passes (quick, medium, very
   thorough) and asks for paths and symbols plus what was not searched. Third,
   read-only tools: `Read, Grep, Glob` is the narrow set, and the built-in
   also allows Bash. One limit: Claude Code's file watcher covers only an
   `agents` directory that existed when the session started, so the first
   session to see the file is one started after it merges. This round cannot
   probe it.
2. **`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`. Refused.** It forces one model onto
   every subagent, teammate and workflow agent and ignores every definition's
   `model` field (sub-agents page, § "Run every subagent on one model"). That
   would move review and fix subagents to the cheap model too, which
   `docs/maintainer.md` § "Which model each flag means" records the owner
   refusing. It also rides the `env` block that does not apply in cloud
   sessions.
3. **A prose rule telling sessions to pass `model: haiku` on each Explore
   call. Refused.** It needs no file, but a session has to remember it on
   every call. `CLAUDE.md` § "Prefer deterministic tooling over repeated model
   work" prefers the form that cannot fail to fire, and route 1 keeps the
   per-call override anyway.
4. **The variable set on the cloud environment. Refused.** The settings guide
   names an environment variable on the cloud environment as the way to set a
   cloud session's env. It would reach `general-purpose` subagents and not
   Explore, so it would downgrade exactly the subagents route 2 is refused
   for.

**Why it matters.** `CLAUDE.md` § "Session and tool-use efficiency" tells
every session to delegate broad search to exploration subagents, so an
Explore run is routine, and each one is billed at the session's model. The
current list prices per million input tokens are $4 for Claude Opus 5.5, $2
for Claude Sonnet 5.5 and from $0.10 for Claude Haiku 5.5
(https://platform.claude.com/docs/en/about-claude/models/overview, read
2026-10-17). On the owner's subscription the saving arrives as usage against
the session and weekly limits rather than as dollars. The Claude Code costs
guide says those limits are "shared across all models"
(https://code.claude.com/docs/en/costs, § "When a developer asks about a
limit") and publishes no per-model weighting, so the price ratio is the only
authoritative measure of how much one Explore run on Haiku saves.

The number that would change the recommendation is how often this project's
sessions start an Explore subagent, and how often a cheaper model's leads
would mislead one. Neither is in the tree. Five briefs mention an exploration
subagent, which counts mentions and not runs, and no session has compared two
models on the same search. So the count cannot be taken, and reversibility
decides (`.claude/rules/expert-review.md` § "Count what undoing it would cost,
before taking the cheaper route"): the change is one file, a session can
override it per call, and reverting it is deleting the file.

The variable also misleads as it stands. Two sessions read its absence from
the shell as `.claude/settings.json` not loading (`PL-9DYK`, `PL-0MLZ`), and
`docs/maintainer.md` told the owner for seven weeks that it chose the
exploration model.

**Decided in this round, not put to the owner: `CLAUDE_CODE_SUBAGENT_MODEL`
leaves `.claude/settings.json`** (design round, 2026-10-17). It applies in no
cloud session, on the four measurements above. It never chose Explore's model
anywhere. And in a local session, once the folder is trusted, it would put
every `general-purpose` subagent on Haiku with no per-item judgment, which the
owner's recorded preference refuses and `docs/maintainer.md` § "Which model
each flag means" settles at Sonnet. One option is clearly correct, so the
round takes it and the build removes the line. If the owner answers no to the
question above, this part still happens.

**Decision needed.** Should exploration subagents run on a cheaper model, and
which one?

**Recommendation:** yes, Claude Haiku 5.5, as `model: haiku`. Three reasons.
The documentation's own example for this exact override is `model: haiku`,
and the costs guide says "For simple subagent tasks, specify `model: haiku`
in your subagent configuration" (https://code.claude.com/docs/en/costs,
§ "Choose the right model"). Explore's output is leads that the session
checks against the source by rule (`CLAUDE.md` § "Session and tool-use
efficiency"), so a weak lead costs a verification and not a wrong commit. And
the three reasons `docs/maintainer.md` § "Which model each flag means" gives
for Sonnet over Haiku are about Haiku 4.5: Claude Haiku 5.5 is the current
generation, has a 1M-token context window and takes the effort parameter
(models overview, read 2026-10-17; `PL-XJV3` updates that passage). Claude
Sonnet 5.5 is the hedge if lead quality worries you more than usage. It costs
half of Opus 5.5 where Haiku costs a fortieth, so it gives up most of the
saving. The owner's recorded preference, default to Opus whenever in doubt,
was stated for delegated items, which carry fixes; search output is checked
by construction. Either way the per-call `model` override stays, so a session
that wants Opus for one hard search can ask for it. This replaces the
capture's recommendation of Sonnet, whose reasons were Haiku 4.5's.

**Risks, likelihood and magnitude, per option.** Added 2026-10-17 at the
owner's request. Where a figure is a measurement it names its source; where it
is this session's estimate it says so and names what would measure it.

*Cost per Explore run, API-equivalent, from the pricing page read 2026-10-17
(1-hour cache writes, because `subagentPromptCacheTtl` is `1h`; cache hits at
5% of base on Opus 5.5 and Sonnet 5.5, 10% on Haiku 5.5; Haiku 5.5 priced per
request by prompt length, with a higher tier above 100,000 tokens). The run
shapes are assumptions: a light run grows from 25K to 40K tokens of context
over 6 turns, a medium one to 90K over 12, a heavy one to 150K over 20, each
turn emitting 400 output tokens.*

| Run shape | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
| --- | --- | --- | --- |
| light | $0.40 | $0.20 | $0.011 |
| medium | $0.94 | $0.47 | $0.027 |
| heavy | $1.69 | $0.85 | $0.14 |

Sessions seen today cost $6 to $53 API-equivalent each (`list_sessions`,
2026-10-17), so two medium runs on Opus 5.5 are between 4% and 30% of a
session. On the owner's subscription the saving is usage against the weekly
limit rather than dollars; the published docs give no per-model weighting, and
third-party guides agree cheaper models draw down more slowly but disagree on
the ratio, so the price ratio is the only authoritative measure.

*Break-even.* A worse lead costs a redo: one more search at the session's
model plus the session turns around it, about $1.50 for a medium run. Haiku
5.5 saves about $0.92 per medium run, so it stays cheaper unless more than
about 6 runs in 10 need a redo; Sonnet 5.5 saves about $0.47, so it stays
cheaper unless more than about 3 in 10 do. No plausible miss rate reaches
either line, so the question is not cost. It is how often a worse lead is
tolerable and what happens when one is not noticed.

*Quality risk, per model.* No benchmark measures codebase search, and
Anthropic's model pages give positioning only: Haiku 5.5 "is built for
high-volume, latency-sensitive work such as classification, routing,
extraction, and subagent tasks"; Sonnet 5.5 "offers the best combination of
speed and intelligence"; Opus 5.5 "is built for long-running agentic coding
and knowledge work" (each model's overview page, read 2026-10-17). This
session's estimate, not a measurement: on a "very thorough" search, Haiku 5.5
returns a noticeably worse set of leads than Opus 5.5 in roughly 1 run in 5 to
1 in 10, mostly by missing an indirect reference; Sonnet 5.5 in roughly 1 in
10 to 1 in 20; on a "quick" lookup the difference is near zero for both. The
magnitude of a noticed miss is a redo. The magnitude of an unnoticed one is a
wrong edit, which `CLAUDE.md`'s rule to verify leads against the source,
the test suite and the owner's read of `src/` each stand in front of; this
session's estimate is that fewer than 1 miss in 10 gets past the first of
those, and the floor catches most of the rest. The measurement that would
replace these estimates is about 20 searches run on each model against known
answers; it was not run, because it would cost more than several months of
the saving. The per-call `model` override is the mitigation either way: a
session can ask for Opus on one hard search, and the file sets a default and
not a ceiling.

*Risks the file carries whatever model it names.* The file replaces the
built-in Explore's prompt with ours. Estimate: roughly 1 in 3 that the first
draft regresses something the built-in does, such as the thoroughness levels
or the output shape; magnitude small, fixed by editing the file, and the next
session picks the edit up. Whether a cloud session loads `.claude/agents/`
is documented as yes; given that the `env` block's documented behaviour did
not hold here, estimate roughly 1 in 10 that this does not either; magnitude
zero, since the result is the status quo, and the first session's probe shows
it. Heavy runs on Haiku 5.5 cross the 100,000-token tier and pay five times
its base rate; certain for heavy runs, and the run still costs a twelfth of
Opus 5.5.

*The refused routes are not equivalent to these.* `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`
moves every subagent, teammate and workflow agent with certainty, review and
fix subagents included, and silently: the largest magnitude in the set, which
is why it is refused and not weighed. A prose rule to pass `model: haiku` per
call would be skipped on roughly 1 call in 4, on the measured analogue that
the session-rename rule is followed about three times in four
(`.claude/skills/docket/modes/start.md`); the magnitude is forgone saving
only. The variable on the cloud environment would move `general-purpose`
subagents with certainty and Explore not at all.

*Removing the variable.* In cloud sessions it changes nothing, on four
measurements. In a local session whose folder is trusted, the documentation
says the variable has applied since 2026-08-23, so `general-purpose`
subagents there have run on Haiku without a per-item judgment; removing it
returns them to the session's model, which raises local cost and matches the
owner's recorded rule. This session cannot read a local machine, so that is
the documentation's claim and not a measurement.

**Done when.** With a yes: `.claude/agents/Explore.md` exists with
`model: haiku` (or `model: sonnet`, if the hedge is chosen),
`omitClaudeMd: true`, read-only tools and a body that carries the thoroughness
levels; `CLAUDE_CODE_SUBAGENT_MODEL` is gone from `.claude/settings.json`;
`docs/maintainer.md` § "Settings that make sessions cheaper" says what Explore
runs on and no longer says the answer waits on this item; and the first
session started after the merge records in this item the model its Explore
subagent's transcript shows, read the way `PL-KLN5` read it, with
`jq -r 'select(.type=="assistant") | .message.model'` over the subagent's
transcript under `~/.claude/projects/`. With a no: the variable is removed,
and `docs/maintainer.md` says, dated, that Explore runs on the session's model
by the owner's decision.

**Verify, to set when the item goes `ready`:**
`test -f .claude/agents/Explore.md && grep -q '^model: haiku' .claude/agents/Explore.md && ! grep -q CLAUDE_CODE_SUBAGENT_MODEL .claude/settings.json`

**Generator check.** Not a member of a head. It follows from `PL-KLN5`'s
measurement of how Claude Code chooses a subagent's model, an external
behaviour nothing in the tree models, and no other open item rests on that
fact.
