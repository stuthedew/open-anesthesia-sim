---
id: PL-2D28
title: Exploration subagents run on the session's own model, Opus 5.5 in this project's threads, because CLAUDE_CODE_SUBAGENT_MODEL never reaches the built-in Explore subagent and a cloud session applies none of the env block in .claude/settings.json: decide whether a project Explore agent pins a cheaper model, and whether the variable stays (found in PL-KLN5)
priority: P2
effort: S
status: ready
classes: session-cost
touches: .claude/settings.json, .claude/agents, docs/maintainer.md
deferred-from: v0.6.0 - apparatus session-cost work: which model an exploration subagent runs on changes nothing the milestone ships
added: 2026-10-17
payoff: exploration subagents run on a model chosen for search rather than inherited by default, and the settings file stops claiming a lever it does not have
verify: grep -q '^model: opus' .claude/agents/Explore.md && grep -qi 'not search' .claude/agents/Explore.md && ! grep -q CLAUDE_CODE_SUBAGENT_MODEL .claude/settings.json
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
   Recommended, and taken.** [superseded 2026-10-17: the `model: haiku` in
   the quotation below was this route's first form; the decision below pins
   `model: opus`.] The documentation says: "A user or project subagent named
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

**Recommendation:** keep Explore on the session's model and effort, and
cheapen no search by any route. Build the project Explore file anyway, with
`model: opus` and no `effort` line, for what it adds at any model: the report footer
naming the scope searched and not searched, and read-only tools. Remove the
variable. Take the saving where it is free of recall: a lookup that is
genuinely quick, one symbol or one path, is a Grep or Glob in the main
session, which is exhaustive, and never an Explore call at all. A per-call
cheaper model and lower effort for "quick lookups" was recommended earlier
on 2026-10-17 and withdrawn the same day, when the owner asked whether it
survived the test that withdrew the cheaper defaults. It does not. The
session judges a search quick before running it, so the judgment is made by
the one party that does not yet know what the search will find; a wrong
judgment is a thorough search run cheap, which is the tail; the upside of a
right one is about $0.50 per lookup; and Explore exists for broad searches,
so the class of quick Explore calls is small and ill-defined. A rule with a
bounded, small, infrequent upside and the tail as its failure is the same
shape the cheaper defaults had. The same reasoning sets effort, under
*Effort* below. Revised a third time on 2026-10-17, from Sonnet 5.5, after the owner asked whether the
cost of an escaped miss counts only the fix. It had: the arithmetic under
*Silent misses* priced an escaped miss at one later fix, $10, and nothing for
the work done under the wrong result before it was found. *The tail of an
escaped miss* below prices that. With it, the expected saving of either
cheaper model on a thorough search falls to zero or below inside the error of
the estimates: Sonnet 5.5 pays only if its excess miss rate on thorough
searches is under about 1 in 20, Haiku 5.5 under about 1 in 11, and this
session's estimates put each at or above its line. The saving on a quick
lookup is real for both, because the excess miss rate there is near zero, so
it is taken per call, where the session can see that the lookup is quick. The
forgotten case under this default is a quick lookup run at Opus 5.5, about
$0.39, and is bounded. The forgotten case under a cheaper default is a
thorough search run cheap, with the tail. The owner's recorded preference,
default to Opus whenever in doubt, was set for delegated items and applies to
search for the same reason: its output enters the record. The earlier
recommendations stay as the record of the round: Haiku 5.5 first, then Sonnet
5.5 after the owner asked whether a miss is silent. The number that would
return either: a measured excess miss rate on thorough searches under its
line above, from `PL-G2D4`, the pre-registered measurement: 60 thorough
searches per model by the rule of three, since 20 with no miss observed only
bounds the rate at about 15 percent, above both lines; the union of leads
across the three models as the reference; and Opus 5.5 at `medium` against
`xhigh` as the effort arm. About $140 at most by the table below, repaid in
weeks at the saving computed there. On estimates the choice is undetermined,
so it stays at the status quo until `PL-G2D4` reports.

**Decided** (project owner, 2026-10-17, ratified, over Haiku 5.5, Sonnet 5.5
and a per-call cheaper model for quick lookups): keep Explore on the
session's model and effort, cheapen no search by any route, build the
project Explore file only for the scope footer and read-only tools, and
remove the variable. Two corrections the owner specified in the same answer.
First, the file writes `model: opus` rather than no `model` line: a
definition without `model` falls through to the main conversation's model
(sub-agents page, § "Choose a model", step 4), so in a Fable session it would
run on Fable, while the built-in Explore there runs on the Opus model the
`opus` alias resolves to (§ "Built-in subagents", Explore tab). In an Opus
session the alias resolves to the session's own Opus model (§ "Choose a
model", the family-alias note), so `model: opus` names the built-in's
behaviour in both. No `effort` line is right, and the transcript probe
stays. Second, the measurement is `PL-G2D4`, which pre-registers the sample
size, the reference set and the effort arm, and not the 20-search set this
brief first named; the choice between models is undetermined on estimates
and stays at the status quo until `PL-G2D4` reports. The verify adds
`grep -q '^model: opus'`.

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
replace these estimates is `PL-G2D4`: 60 thorough searches per model, the
union of their leads as the reference, about $140 at most and repaid in weeks
of the saving. The per-call `model` override is the mitigation either way: a
session can ask for Opus on one hard search, and the file sets a default and
not a ceiling.

*Silent misses.* Added 2026-10-17 after the owner asked whether a missed
lead is silent, whether anything checks that a search did an adequate job,
and whether a miss carries downstream cost. It is silent. A subagent "returns
only the summary" (sub-agents page, read 2026-10-17), nothing in Claude Code
scores that summary, and the one built-in signal, the partial marking when a
`maxTurns` limit stops a run, says the run was cut short and nothing about
its quality. The session cannot see what it was not told, so a missed
reference is invisible at the boundary on every model, Opus 5.5 included.
`CLAUDE.md`'s rule to treat leads as things to verify against the source
checks that what came back is true. It cannot check that nothing was left
out. So the paragraph above was right about a wrong lead and too optimistic
about a missed one: the first guard it names catches none of those.

What catches a miss sits downstream and depends on what was missed. The
escape figures are this session's estimates.

| What the search missed | What catches it, deterministically | Estimated escape |
| --- | --- | --- |
| a caller or sibling in `src/anesthesia_sim/core/` | `make check`: mypy, pytest at 100% branch coverage of `core`, `tools/literal_home_check.py`, `tools/fact_home_check.py`; then the owner's read of `src/` | under 1 in 10 where the miss leaves the code inconsistent; higher where it leaves two independently valid copies |
| a caller in `src/anesthesia_sim/app/` | mypy and the tests that exist; no coverage floor | about 1 in 3 |
| a second statement of a fact in docs or rules, or a sentence the change makes stale | nothing: `tools/doc_check.py` checks that a cited path exists, not that the sentence is true | about 1 in 2; found later by a reader and filed |
| a prior decision or related item, in a design round | `tools/dead_ends.py` for the recorded dead ends; otherwise the owner's memory | about 1 in 2; the magnitude is a reopened decision or a duplicate item, which spends the owner's attention |

The store cannot say how often this has happened. 30 items mention a
subagent and none attributes a defect to a missed lead (grep over
`docs/items/`, 2026-10-17). That has two readings the store cannot separate:
misses are rare, or a miss that escapes surfaces later as an ordinary defect
and is never traced back. The second is the owner's point.

*Expected cost per session, under the estimates above.* Take a session that
runs one quick and one thorough search, and put a caught-late miss at $10 of
a later session's turns. Opus 5.5 pays $1.34 for the two runs. Sonnet 5.5
pays $0.67, and its excess misses on the thorough search cost $0.05 to $0.50
in expectation (5 to 10 points of excess miss rate, times an escape of 1 in
10 to 1 in 2, times $10), so it nets $0.17 to $0.62 of saving. Haiku 5.5 pays
$0.04 and its excess misses cost $0.10 to $1.00, so it nets $0.30 to $1.20,
with twice the variance and twice the rate of the one cost the arithmetic
leaves out, a reopened decision put to the owner. Against sessions of $6 to
$53, either saving is 1% to 10% of a session. So the dollars do not separate
the options inside the error of the estimates; what a forgotten override
costs does. The next paragraph revises the $10 figure, and the
recommendation above follows from the revised one.

*The tail of an escaped miss.* Added 2026-10-17 after the owner asked whether
the saving counts only tokens, and whether the $10 assumes the miss is found
at once. It did. The figure priced one later fix and nothing for the interval
between the miss and the find, during which the session that missed it, and
any session reading its output, works from a wrong or incomplete result. In
this repository that interval has a measured shape, because sessions have no
memory and the record is read as true. `docs/maintainer.md` said the variable
picked the exploration model from 2026-08-23; `PL-KLN5` found the claim
unverified on 2026-10-01; resolving it took that item, a probe and this round,
at least three sessions and the owner's attention, for one wrong recorded
sentence. `PL-38PN` repaired two citations by hand and `PL-JXVD` was filed
because the repairs went stale: two generations of rework from one class of
wrong record (`.claude/rules/citation-drift.md`). Neither began as a subagent
miss, and both are the path a miss that enters an item brief or a document
would follow. So the cost of an escape is a distribution. This session's
estimate: about 7 in 10 cost one fix, $10; about 1 in 4 cost an item and a
design round, $50; about 1 in 20 cost a decision built on and reverted across
several sessions, $300. The expectation is about $35 per escape, three and a
half times the figure above, and the owner's hours on the two larger buckets
sit on top of it. A cheaper model returns sooner per token, a small gain in a
session's wall time the figures leave out; it does not change the sign.

| Model | Saving per session, two runs | Expected rework at $35 per escape | Net |
| --- | --- | --- | --- |
| Opus 5.5 | none | baseline | none |
| Sonnet 5.5 | $0.67 | $0.17 to $1.75 | -$1.08 to +$0.50 |
| Haiku 5.5 | $1.30 | $0.35 to $3.50 | -$2.20 to +$0.95 |

At the middle escape rate, 3 in 10, Sonnet 5.5 breaks even on a thorough
search at an excess miss rate of about 1 in 20 and Haiku 5.5 at about 1 in
11; the estimates above put Sonnet at 1 in 10 to 1 in 20 and Haiku at 1 in 5
to 1 in 10. On a quick lookup the excess is near zero and the whole saving
is kept: about $0.39 per lookup for Haiku 5.5 against Opus 5.5.

*Effort.* Added 2026-10-17 after the owner asked whether the same reasoning
decides an effort level. It does, and effort is the lever the cost tables
above leave out. Effort steers adaptive thinking and "affects all tokens in
the response", thinking, text and tool calls, and "lower effort also means
fewer and terser tool calls" (platform effort page,
https://platform.claude.com/docs/en/build-with-claude/effort, read
2026-10-17). For a search subagent, fewer tool calls is fewer searches, and
the Haiku 5.5 guidance on that page says it outright: at `low`, in long agent
prompts, "the model is more likely to skip a search, stop early, or skip a
check". So effort sits on the same axis as the miss rate above, and more
directly than the model does. A subagent runs at the session's effort level
unless its definition or the call sets one (sub-agents page, the `effort`
field, and the model-config page § "Adjust effort level"). This session runs
at `xhigh`, read from `CLAUDE_EFFORT` in its own shell, so Explore here runs
Opus 5.5 at `xhigh` today, two levels above that model's own default of
`medium`. The documentation gives Opus 5.5 no level for search and says to
run an effort sweep on your own evals. The Opus 4.7 guidance, a different
model, names `xhigh` as the starting point for "exploratory tasks such as
repeated tool calling, detailed web search, and knowledge-base search", with
"meaningfully higher token usage than `high`".

What the tables leave out: they price 400 output tokens a turn and no
thinking. Output is priced at five times input on every model here, and at
`xhigh` the volume is not small. This session's own transcript, Fable 5.1 at
`xhigh` on a design conversation and so a proxy only, shows a median of about
1,900 and a mean of about 2,900 output tokens per assistant message over 172
messages. A twelve-turn Explore run at that volume on Opus 5.5 adds about
$0.70 to the $0.94 in the table; at `medium` an unmeasured fraction of that.
The term scales every model's figure by about the same ratio, because output
prices sit in the same 40:20:1 ratio as input prices, so it changes no
ranking. It raises every bounded forgotten-case figure, the quick lookup at
Opus 5.5 included, to perhaps $0.60.

Recommendation on effort, by the same rule as the model: no `effort` line in
the file, so every search inherits the session's level, and no per-call
lowering, for the reason given under *Recommendation*. Were a per-call
lowering ever taken on a measurement, `medium` is Haiku 5.5's own documented
starting level and `low` is the level the documentation says skips
searches. A per-subagent effort does not touch the main session's prompt
cache, since the subagent is its own conversation; changing the session's own
`/effort` part-way does, so the lever belongs on the subagent and not on the
session. The forgotten case under this default is a lookup
over-thought, bounded; under a lower default it is a thorough search that
skipped a search, with the tail. The number that would change it: an effort
sweep `PL-G2D4` pre-registers as its effort arm, Opus 5.5 at `medium`
against `xhigh` on the same 60 searches, which is the documentation's own
advice for Opus 5.5.

*What reduces the silent class at any model.* The file's body requires the
subagent to end every report with the scope it searched, the patterns and
directories, and what it did not search. A "did not look there" miss then
shows in two lines the session reads instead of in nothing. It does not catch
a "looked and did not recognize" miss; only a stronger model or a second
search does, which is what the per-call override is for. The build carries
this requirement whatever model the owner picks.

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

**Done when.** `.claude/agents/Explore.md` exists with `model: opus`, no
`effort` line, `omitClaudeMd: true`, read-only tools and a body that carries
the thoroughness levels and requires each report to end with the scope
searched and not searched; `CLAUDE_CODE_SUBAGENT_MODEL` is gone from
`.claude/settings.json`; `docs/maintainer.md` § "Settings that make sessions
cheaper" says, dated, that Explore runs on Opus by the owner's decision
pending `PL-G2D4`, and no longer says the answer waits on this item; and the
first session started after the merge records in this item the model its
Explore subagent's transcript shows, read the way `PL-KLN5` read it, with
`jq -r 'select(.type=="assistant") | .message.model'` over the subagent's
transcript under `~/.claude/projects/`.

**Verify.** Set in the front matter at `ready`, 2026-10-17: the file exists
with `model: opus` and the scope footer, and the variable is gone from the
settings file.

**Generator check.** Not a member of a head. It follows from `PL-KLN5`'s
measurement of how Claude Code chooses a subagent's model, an external
behaviour nothing in the tree models, and no other open item rests on that
fact.
