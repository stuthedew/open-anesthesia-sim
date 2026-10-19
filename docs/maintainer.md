# Notes for the project owner

Everything here is addressed to the person running the sessions, not to the
sessions themselves. It lives outside `CLAUDE.md` for that reason: a rule a
session cannot act on still costs every session the context to read it.
`docs/worker.md` is the opposite document — instructions to a worker agent.

## Rules for sessions live in the repository

**Every rule about how a session works has one record, the repository, and
the Projects trial's instructions carry none of their own** (project owner,
2026-10-03, ratified, over a dated copy of the instructions kept in the
repository for sessions outside the Project, `PL-PDVF`). `CLAUDE.md`, the
`docket` skill, the rules under `.claude/rules/` and what `bin/docket` prints
reach every session, in a Project or not; a Project's instructions reach only
its coordinator and its threads. A rule given there alone left the
repository's copy missing or older, so a session outside the Project followed
the old one and a Project thread read two that disagreed, each carrying your
authority: the review ask's summary (`PL-8XQS`), re-running `tag-release.yml`
(`PL-F23S`), the arm rule for read holds (`PL-KKHD`), and the direct squash
merge the instructions asked for from 2026-09-27 while the hook refused it
from 2026-09-30 (`PL-NXRJ`). Nothing in the repository can read the
instructions, so no check can catch the split; the routing is what prevents
it.

**What the instructions keep** is the trial's own coordination and nothing
else: the Goal, the Order and its pause, the thread caps and which model each
thread runs, where threads post and record - the review summary in the project
chat, one line on a merge, the project's shared folder - and one line saying every
other rule is the repository's. `PL-PDVF` carries the cut-down text as written
on 2026-10-03 and the table of where each rule went.

**When you give a rule for sessions in the Project, it goes to the repository
in the same sitting.** Say it to the coordinator, which starts a thread that
writes it in by `CLAUDE.md`'s routing - a check, the `docket` skill, a
path-scoped rule, then resident - under `CLAUDE.md`'s rule that a behavior
change takes effect in the session that asks for it, recording your words and
the date beside it. The instructions then name nothing about it. A thread that
meets a rule in the instructions and one in the repository that disagree
reports both to you rather than choosing, and the repository is where the fix
lands; a rule you give in one of your own sessions already takes this route.

## Match model capability to the work

A session cannot switch its own model, so this is the owner's lever.

**Reasoning-heavy work warrants the strongest available model at a high
effort setting**, for both the change and the review of the final diff:

- architecture and design decisions;
- new scientific-model design;
- ambiguous problems and genuine trade-offs;
- non-obvious debugging and root-cause analysis;
- anything within the scope of `CLAUDE.md` § "Safety-critical
  clinical-output standard" — which includes the presentation of clinical
  values and the scientific content of `docs/MODEL.md`, neither of which is
  routine execution however mechanical the edit looks.

**Executing an already-agreed plan does not.** `bin/docket next` states which
model an item warrants, so the queue answers this per item rather than per
session. It prints one of two flags, and § "Which model each flag means"
below is where they resolve.

### Which model each flag means

**A dated instance, not a rule** (`.claude/rules/expert-review.md`). What
falsifies the two names below is a new model release, nothing about how this
project works, so check the lineup before trusting them; everything else in
this section holds whoever is at the top.

- **As of 2026-10-18 the strongest available model is still Claude Fable
  5.1** (`claude-fable-5-1`), which is what `use your strongest model` asks
  for. Anthropic's models overview recommends Claude Opus 5.5 for most work,
  and Fable 5.1 "for demanding reasoning and long-horizon agentic work, or when
  your evals on Claude Opus 5.5 at higher effort still fall short"
  (https://platform.claude.com/docs/en/about-claude/models/overview, read
  2026-10-18). The project owner confirmed on 2026-09-19 that Fable is
  stronger than Opus. That settles it against the assumption that whatever
  model a session already runs satisfies the flag. Claude Opus 5.5
  (`claude-opus-5-5`) is the step below and the substitute when Fable is
  unavailable. The owner moved this project's Projects threads from Fable 5.1
  to Opus 5.5 on 2026-10-14 (`PL-XJV3`). Which model a session runs is the
  owner's choice, and this line only says what the flag asks for.
- **As of 2026-10-18 `delegable` still means Claude Sonnet 5.5**
  (`claude-sonnet-5-5`), not Claude Haiku 5.5, and one named tier rather than
  a choice between two. The project owner asked for a cheap-model offer on
  clear-cut items and specified the asymmetry it must have (2026-09-19): *"I'd
  rather err on the side of default opus if any question and miss items that
  could have been safe with a lower model than try to catch every lower model
  opportunity and find out later I should have actually used opus."* Naming
  one tier follows from that and is this session's reading of it rather than
  their own words. A second tier would bring back, at the moment of reading,
  exactly the per-item judgment the asymmetry exists to remove.

Three facts decided Sonnet 5 over Haiku 4.5 on 2026-09-19. None of them holds
for Haiku 5.5, by the models overview read on 2026-10-18:

1. **Haiku 4.5 was a generation behind.** Haiku 5.5 belongs to the same
   generation as Opus 5.5 and Sonnet 5.5.
2. **Haiku 4.5's context window was 200K against the others' 1M.** A session
   spending its whole 150,000-token budget ended around 231K–265K of context,
   past Haiku 4.5's entire window (`PL-W80S`). Haiku 5.5's window is 1M, the
   same as the other three models.
3. **Haiku 4.5 did not take the effort parameter**, so § "Match effort to the
   standard the work is held to" below could not be honoured on it. Haiku 5.5
   takes it, and Claude Code opens it at `medium`.

What still decides Sonnet is the owner's asymmetry quoted above, not a
measurement. Anthropic describes Haiku 5.5 as "for high-volume,
latency-sensitive tasks such as classification, extraction, and routing". A
delegated item here is a real defect with a real fix, and no trial here has
measured Haiku 5.5 on one. The `model-evidence` feature is where such a trial
would be recorded, so moving `delegable` to Haiku waits on its evidence rather
than on a reading of the lineup.

The saving now differs more than it did. At first-party API rates per 1M
tokens, Claude Fable 5.1 costs $10 input and $50 output, Claude Opus 5.5 $4 and
$20, and Claude Sonnet 5.5 $2 and $10. Claude Haiku 5.5 costs $0.10 and $0.50
for prompts up to 100,000 tokens, and $0.50 and $2.50 for longer ones
(*Pricing*, https://platform.claude.com/docs/en/about-claude/pricing, read
2026-10-18). Measured against Opus 5.5, moving to Sonnet 5.5 captures 51% to
57% of the largest saving available, depending on prompt length. On the
2026-09-19 lineup it captured **75%**.

**`delegable` is an offer, never an instruction.** It is derived from
`Item.delegability` — `ready`, no `safety` or `science` class, no open
decision, a `verify:` command that proves it done, `touches` declared and
wholly outside `protected_paths` and `gate_paths`, and `S` or `M` effort.
There is deliberately no field that *grants* delegability, only
`not-delegable:` to withhold it. Declining the offer and running the
strongest model anyway is always available and never wrong; the flag exists
so the cheap case is visible, not so it is taken.

### Why `opusplan` is not the default for the split here

Claude Code's `opusplan` mode "uses `opus` for complex reasoning and
architecture decisions" in plan mode and "automatically switches to `sonnet`
for code generation and implementation" in execution mode — read at
https://code.claude.com/docs/en/model-config on 2026-09-19. The split is fixed
to those two families; that page offers no equivalent pairing a non-Opus
strong model with a cheap one, and points at the advisor tool for a mid-task
consultation instead.

**So on the 2026-09-19 lineup `opusplan` plans one tier below the strongest
model**, and the rule at the top of this section asks for the strongest. That
is the whole objection: it is not that the mode is broken, it is that its
strong half is named by family rather than by rank, and the family stopped
being top on 2026-09-19. Use it when Opus-level planning is enough for the
item in hand — not as the default for work this section calls reasoning-heavy.

For that work, set the model deliberately (`/model fable`, or `--model
claude-fable-5-1` at launch) and switch back for execution. Two caveats
survive whichever way the split is made:

1. Execution returns to the cheaper model, so the strong-model review of a
   safety-critical diff is a deliberate step, not an automatic one.
2. Switching models mid-session starts a cold cache, so group design and
   execution into runs rather than alternating between them.

One convergence worth noting: `opusplan`'s execution half is `sonnet`, which
is the same tier § "Which model each flag means" names for `delegable`. The
cheap end of both splits is the same model, so nothing here asks you to hold
two answers.

Model choice never changes what a change must satisfy before it lands, and the
maintainer still reviews every safety-critical diff regardless of which model
drafted it.

## Match effort to the standard the work is held to

Effort is the owner's lever for the same reason model choice is: a session
cannot change its own.

A session that sets no level runs at its model's default. Opus 5.5, Sonnet 5.5
and Haiku 5.5 default to `medium`, and most older models default to `high`.
Each model calibrates the scale separately, so one level name does not mean the
same amount of reasoning on two models. Anthropic reports that "Opus 5.5 at
`medium` matches or exceeds Opus 5 at `high` on coding and knowledge-work
evaluations" (Claude Code docs, *Model configuration*, section "Adjust effort
level", https://code.claude.com/docs/en/model-config, read 2026-10-17).

**On Opus 5.5, every session opens at `high` for now, simulator and apparatus
alike** (project owner, 2026-10-19, over `max` and `xhigh`, `PL-6XZG`). The
`effortLevel` key in `.claude/settings.json` sets it, so a session the owner
opens without choosing a level runs at `high`. A level the owner picks when
opening a session still wins over the file, because Claude Code ranks an
explicit choice above settings (Claude Code docs, *Model configuration*,
section "Adjust effort level", https://code.claude.com/docs/en/model-config,
read 2026-10-19). This is the owner's own judgement: the published gain from `xhigh` over `high` is
small. It replaces two ratified records whose stated reason was cost: `high`
for apparatus sessions (2026-10-17, `PL-SW0B`) and `max` for simulator
sessions (2026-09-19, below). Cost alone never justifies a lower setting
(project owner, 2026-10-19), so a session does not argue for `high` on cost.
On Anthropic's SWE-bench Pro subset, Opus 5.5 solved 95.3% of
tasks at `high` for $0.29 each and 96.7% at `xhigh` for $0.74 each. That is 1.4
points for about 2.5 times the cost, and the page calls its figures directional
(*Optimizing for cost and intelligence*,
https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
read 2026-10-17). The same page reports 88.4% at `high` and 91.1% at `xhigh`
on an internal agentic-coding set, and gives no figure for `max` (read
2026-10-19).

**The owner wants evidence on whether `high` causes real problems** (project
owner, 2026-10-19). The session ledger records each session's model and
effort so that this can be measured. Once the data is adequate, the model
review (`PL-63CB`) tests whether work done at `high` shows more rework,
reopened items, unintended behavior or other real-world issues than work done
at `xhigh` or `max`. When it finds a statistically significant difference, it
tells the owner, with the size of the effect and its uncertainty. `PL-63CB`
holds the method.

**About one session in four runs at `xhigh` as a randomized comparison
group, assigned automatically** (project owner, 2026-10-19, over `high` for
every session and an observational comparison only). The owner asked that
they not have to set the level by hand. The trial starts after Friday
2026-10-23 at 11 pm CDT (2026-10-24 04:00 UTC), and only once the automatic
assignment is built and tested (`PL-HYRM`). Until then every session
runs at `high`. The trial runs until the owner ends it.

**Superseded on 2026-10-19: apparatus sessions at `high` and simulator sessions
at `max`** (project owner, 2026-09-19, ratified, over running every session at
`max`). The split
follows the two standards `CLAUDE.md` already draws rather than a new
judgment: `.claude/rules/apparatus-standard.md` governs the apparatus paths
that `CLAUDE.md` lists, and asks for working reliably rather than for specialist quality; `src/`, `tests/`, `docs/MODEL.md`
and `README.md` are the opposite case, and the safety-critical standard reaches
them.

`ultracode` is deliberate rather than default — worth it for a design round, a
safety-critical review, or a genuinely multi-angle problem, and not for
mechanical work. On 2026-09-19 seven concurrent sessions were all running at
`max`, including one whose whole task was renaming seven item files.

Two mechanics worth knowing. Lower effort produces fewer and more consolidated
tool calls, so it cuts the turn count as well as the output tokens - and since
every turn re-reads the whole conversation, those multiply. And each effort
level keeps its own cache, so changing effort mid-session starts a cold one:
set it when the session opens rather than toggling it.

## The session ledger records what model and effort worked each item

`docs/session-ledger.tsv` has one row per session in this repository. Each row
gives the session's configured model, the model its session context names, the
model that served its last turn, any model the owner switched to, its effort
level, its tokens by kind, its cost in USD as the harness reports it, and the
date the row was written. A closed item reaches its sessions through its `pr:`
field. The squash commit for that pull request carries the session's
`Claude-Session:` trailer, and `docs/pr-bodies/` is the fallback.

**Only the model review writes the ledger, from the harness's own record**
(project owner, 2026-10-17, ratified, over a field or trailer that each working
session writes about itself, `PL-92ZN`). A working session writes nothing about
itself, so the ledger costs working sessions nothing. A self-report would also
name the configured model, while a fallback can serve another one. The facts
belong to a session rather than an item: about two closed items share each
session, and a session keeps spending after it closes its item. So the ledger
stores each session once, and an item is joined to it when it is read (project
owner, 2026-10-19, ratified, over model and effort fields on each closed item,
`PL-70M6`).

**The model review refreshes it monthly**, and after any generator or cluster
appears (project owner, 2026-10-19, ratified, over a weekly or a quarterly
cadence, `PL-63CB`). Until `.claude/skills/model-review/SKILL.md` exists, a
refresh has three steps:

<!-- absent: .claude/skills/model-review/SKILL.md -->

1. Page through `list_sessions` (`mine: true`, `limit: 100`) from the
   `claude-code-remote` MCP server. A page is too large to show inline, so the
   harness saves it to a file. Copy each file unchanged and parse it with a
   script, so that no model retypes a value. Keep a session when any of its
   sources is this repository, not only its first.
2. Fetch every Projects thread with `get_session`. `list_sessions` leaves
   threads out, because they carry the `hearth-thread` tag, and a session
   cannot pass the `tags` filter. Find them as the session ids in
   `Claude-Session:` trailers on `main` and in `docs/pr-bodies/` that have no
   ledger row yet.
3. Rewrite the file, sorted by creation time, and keep any row whose session
   the harness no longer returns. The harness's retention is unknown, and the
   ledger exists so that this record outlives it.


## Settings that make sessions cheaper

- `subagentPromptCacheTtl` is set to `1h` in `.claude/settings.json`. On a Max
  subscription the main conversation defaults to a 1-hour prompt cache but
  subagents, workflows and background tasks default to 5 minutes, and
  `CLAUDE.md` tells every session to delegate broad search to subagents. A
  subagent whose turns are more than five minutes apart - routine when several
  queue behind the concurrency cap - re-pays its prefix at full input price
  instead of the 0.1x cache-read rate. The 1-hour write costs 2x rather than
  1.25x and pays back after two cache reads, which any subagent doing real work
  clears many times over.
- Exploration subagents run on Opus, by the project owner's decision of
  2026-10-17 (ratified, over Haiku 5.5, Sonnet 5.5 and a per-call cheaper
  model for quick lookups; `PL-2D28` carries the case). The project's own
  Explore definition, `.claude/agents/Explore.md`, writes `model: opus`, no
  `effort` line, `omitClaudeMd: true` and the read-only tools Read, Grep and
  Glob. In an Opus session the `opus` alias resolves to the session's own
  model. In a Fable session on a Claude subscription it resolves to the Opus
  model the alias points to. That is what the built-in Explore did in both
  ([subagents](https://code.claude.com/docs/en/sub-agents), "Choose a model"
  and "Built-in subagents", read 2026-10-17), so the file changes no model.
  What it adds is a report footer naming what was searched and what was not,
  and the narrow tool set. A search runs at the session's effort level. The
  model question is settled by correctness, not cost. The owner would rather
  pay for Opus and correct work than take incorrect work from a cheaper model
  for free, so price is never the reason to choose a weaker model (project
  owner, 2026-10-19). So a session never puts a trade of correctness against
  cost as the case for a cheaper model. Opus stays unless a measurement shows
  a cheaper model is no less correct at the task. A cloud
  session loads this definition. In an Opus 5.5 cloud session started after
  it merged, the Explore subagent's transcript records the definition's own
  system prompt. Every turn ran on `claude-opus-5-5` at the session's effort
  level (measured 2026-10-17, `PL-PTHZ`).
- `CLAUDE_CODE_SUBAGENT_MODEL` is set nowhere in this repository. It left the
  `env` block of `.claude/settings.json` on 2026-10-17 (`PL-2D28`). It never
  chose the model for the built-in Explore and Plan subagents, which run on
  the main conversation's model. It was a default for a subagent that nothing
  else gives a model, such as `general-purpose` (subagents page, "Choose a
  model", read 2026-10-17). In a cloud session it did not do even that: it
  was unset in the Bash shell of four cloud sessions on 2026-10-01 and
  2026-10-17, and a `general-purpose` subagent started with no model ran on
  its parent's model (`PL-KLN5`, `PL-2D28`). In a local session whose folder
  is trusted it would have put every `general-purpose` subagent on Haiku with
  no per-item judgment, which § "Which model each flag means" refuses. So a
  subagent that names no model runs on the session's own model. A session
  does not ask for a cheaper model for any subagent unless the owner approves
  it for that task (project owner, 2026-10-19, ratified, over asking for a
  cheaper model per call; `PL-2D28` reached the same answer for searches on
  2026-10-17). The owner then added the reason in their own words: price,
  even a price of zero, does not justify a model that may be less correct
  (project owner, 2026-10-19). The same holds for effort: a subagent runs at
  the session's own effort level unless the owner approves a lower one for
  that task (project owner, 2026-10-19). This covers subagents that copy values as well as those that
  search: on 2026-10-19 a session put Sonnet runners on the session ledger's
  values on the strength of the old wording here, and the owner asked why.
- **A session asking you to type `/compact` is resetting at its budget**
  (project owner, 2026-09-25, ratified, over pasting a handoff prompt into a
  new session, `PL-YJG1`). It pushes everything first, so what the summary
  drops is already on disk, and it keeps its branch, claim and pull-request
  watch. `/compact` works in cloud sessions and takes optional focus text
  (`/compact keep the open question about X`); `/clear` does not. **Type it
  within the hour; the session names the clock time.** The summary is written
  by one more request over the whole history. While the prompt cache is warm
  that request reads the history from it, which on the API bills at 0.05x the
  input price on Opus 5.5 and 0.1x on most models; after a break longer than
  the cache lasts it reprocesses all of it as uncached input
  ([prompt caching](https://code.claude.com/docs/en/prompt-caching),
  "Compacting the conversation";
  [pricing](https://platform.claude.com/docs/en/about-claude/pricing)). That
  was 248,803 tokens in the one reset measured (`PL-384P`). The cache lasts an
  hour on your plan's included usage, and five minutes once usage credits are
  drawn. Past that, a fresh session is cheaper by about that one read, as long
  as the work is pushed and nothing needs the pull-request watch. Start a
  fresh session for an unrelated topic instead: that is where a clean prompt
  beats a carried conversation.
- **When you create a Claude Code project, set its cloud environment to
  `Default` before you send it work.** The **New project** dialog asks only
  for a name, a goal and context, and "Cloud threads use a default
  Anthropic-hosted environment until you pick one in
  **Project settings > Environment**"
  ([Projects](https://code.claude.com/docs/en/claude-projects),
  "Choose an environment for threads", read 2026-10-01). That environment
  runs none of `Default`'s setup script, so each of its threads finds a `uv`
  older than `pyproject.toml` requires and no `libegl1`, and has to repair
  both before `make check` will run (`PL-QKXZ`). Both projects so far started
  there. Open the project, click the gear icon in its header to open
  **Project settings**, go to **Environment**, and set **Cloud environment**
  to **Default**; it saves as you change it. The change reaches new threads
  only, so make it before the first task. A thread can confirm it:
  `get_session` reads `environment_id` `env_01JWikdPctorEBXoFK7bJnCq`.
- **Auto mode as your default reaches only the sessions on your Mac, and no
  file in this repository can carry it** (`PL-ZLS5`). Your
  `"permissions": {"defaultMode": "auto"}` in `~/.claude/settings.json` is
  the right place for it. A project file would be ignored without an error:
  "`permissions.defaultMode` values `auto` and `bypassPermissions` don't take
  effect from project or local settings; set them in user or managed settings
  instead, or pass `--permission-mode` for one session"
  ([Settings](https://code.claude.com/docs/en/settings), "A value you set is
  ignored", read 2026-10-18). A cloud session reads neither of your own files:
  `~/.claude/settings.json` and `.claude/settings.local.json` are "not read.
  Both stay on your machine" (same page, "Settings in cloud sessions"). So a
  cloud session takes its mode from the menu instead: "You pick a cloud
  session's permission mode from the mode dropdown, both when you create the
  task and while the session runs"
  ([Use Claude Code in the cloud](https://code.claude.com/docs/en/claude-code-on-the-web),
  "Permission modes in cloud sessions", read 2026-10-18). A cloud session
  that asks for permissions you thought you had turned off is in the mode its
  dropdown names, so change it there.

## What comes to you before it merges

**A pull request comes to you only for a real decision or a high-risk change,
and housekeeping merges on green** (project owner, 2026-10-17, `PL-DKBG`). A
real decision is one `.claude/skills/docket/modes/design.md` step 4 already
makes yours. A high-risk change is one that changes a clinical value the
simulator computes or displays, or what `docs/MODEL.md` says one means; a rule
sessions run under that you did not ask for in your own words; or a change
whose breakage CI would not show or a revert would not undo. For that one the
ask gives the case for the change, its risks, and what was checked. `#1516` set
this rule: the path list held it with nothing in it to decide.

The session decides which a change is, and records it on a commit as
`Owner-read: needed - <why>` or `Owner-read: not needed - <why>`. `bin/docket
arm` reads that record. A change to `src/`, to a test under `tests/` that
imports the simulator, to `docs/MODEL.md`, to `src/anesthesia_sim/data/` or to
`README.md` holds until a record made after its newest change covers it. So a
session that never judges holds the pull request rather than merging a
clinical change unread. `not needed` arms it on green, with the reason in the
pull request body. `needed` holds it for you on any path.
`subprojects/docket/src/docket/arming.py` decides what merges without you. A
change to it waits on you only when it changes or deletes an existing test
that pins `arm`'s answers, moves the file, or carries a `needed` record, and
otherwise merges on green (project owner,
2026-10-19, ratified, over holding every change to it, `PL-9JHM`). Until then
every change to it waited on you (`PL-VKHD`). A pinned test is one in
`subprojects/docket/tests/test_cli.py`: a `test_arm_` test, a test that runs
`arm` or reads `arming`, or one of those tests' `_arm` helpers and `ARM_`
constants. The modules `arm` reads through, such as `vcs.py`, `claims.py` and
`cli.py`, arm on green, so a change there that loosens an answer has to edit a
pinned test, and that edit waits on you (project owner, 2026-10-12, ratified,
`PL-WW0Q`). The hold covers the tests that pin `arm`'s answers, not the code
they test: a new test arms, and so does a loosening that no test pins, in
`arming.py` itself too.

**A hold reaches you with its question or its risk, never a bare "read #N"**
(project owner, 2026-10-18, `PL-9JHM`). The session records what to ask you
as an `Owner-ask:` trailer on a commit, and `arm` prints it as the ask's
opening line. It is either a decision or a risk review. A decision has at
least two options, each saying what it changes for you or a learner, and a
recommendation. It is worded in clinical or learner terms, and a choice
between approaches to the interface comes with one annotated screenshot per
option (project owner, 2026-10-19, `PL-KYTY`). A risk review says what could
go wrong and for whom, what was
checked, and the one thing to look at. Until a record made after the newest
change covers it, `arm` tells the session to send you nothing, on the first
line of its answer and with an exit status of its own. A thread cannot send it
anyway: `.claude/hooks/owner_ask_guard.py` refuses a thread's reply that asks
you to read or merge unless `arm` has a recorded ask and the reply carries its
line (`PL-TLPH`). A question
whose answer is obvious is wrong, as on `#1516`. When there is nothing to
decide or review, the session records `Owner-read: not needed` and the change
merges on green without asking you. A change to a test pinning `arm`'s
answers still holds whatever that record says, so its ask is a risk review.

A held pull request merges on your word
alone - "Merge it" - by the route § "Bring a stale base in when you merge,
with Update branch" describes.

Before 2026-10-17 those simulator paths held for your read by themselves,
whatever the change was (the Projects trial's instructions, 2026-10-03, kind
unrecorded, over holding every path outside `docs/items/`, `docs/pr-bodies/`
and `subprojects/docket/`; built by `PL-KKHD`). A workflow item needs no merge
confirmation from you (project owner, 2026-10-12, `PL-KPM2`), so a change to
`.github/workflows/`, `.claude/hooks/` or docket's lexer arms on green beside
the rest of the workflow lane, where those had waited on your read since
2026-10-03 and 2026-10-10. Every other change arms on green: the store, the
body records (`PL-979D`) and the queue's tooling as before (project owner,
2026-09-25, ratified, over holding every path outside `docs/items/`,
`PL-SQTR`; built by `PL-K6B2`), and since 2026-10-03 `CLAUDE.md`,
`ROADMAP.md`, `tools/`, the rest of `.claude/` and `.github/`, and everything
else. `arm` names the paths outside the store it armed, so the session's report
carries the reason. The hold before that fired on every change outside the
store, and you confirmed on 2026-09-25 that those holds were being clicked
through, so it was guarding nothing; `PL-CBDX` reads the diffs merged unread
since 2026-09-23.

Two answers of 2026-10-03, recorded so that the list reads as decided rather
than defaulted. `ROADMAP.md` and `docs/WORKING_NOTES.md` arm on green, where
`PL-0JGZ` (project owner, 2026-09-26, ratified) had held them because the
roadmap is where you set direction: your list reopened it, and you settled it
so (project owner, 2026-10-03, ratified, over holding them as before,
`PL-KKHD`). `.github/workflows/` and `.claude/hooks/` joined the list, since
`update-armed.yml`, `tag-release.yml` and `direct-merge-guard.sh` decide
merges and tags as `arming.py` does, at about one read a day lately (project
owner, 2026-10-03, ratified, over leaving them armed on green, `PL-KKHD`), and
left it on your rule of 2026-10-12 above.

One answer of 2026-10-05. A test of the tooling under `tests/` - a file pytest
collects that imports no `anesthesia_sim` - arms on green, as
`subprojects/docket/tests/` does: 16 of the 51 merges held for a read since
2026-10-03 had been held by such tests alone, with nothing in them for you to
judge (project owner, 2026-10-05, ratified, over keeping every change under
`tests/` on the read list, `PL-552M`). A test of the simulator still waits for
the session's `Owner-read` record, and so does a branch that drops a test's simulator import or deletes a simulator
test, because `arm` reads the file before and after the change. So do
`tests/conftest.py` and every other file pytest does not collect, which serve
the simulator's tests whatever they import, and any test `arm` could not read,
with the reason beside the hold. The rule is the one
`tools/workflow_paths_check.py` sorts the lanes by, spelt once in `arming.py`.
Since 2026-10-19 changing it waits on your read only where the change edits a
test pinning `arm`'s answers (`PL-9JHM`).

## Merge on the Mac or by auto-merge, never in the GitHub app

You merge by three routes: the Mac's browser, auto-merge armed through Claude,
and the GitHub iPhone app (project owner, 2026-09-22). Squash-merge and arm
auto-merge by the first two, and not in the app (project owner, 2026-09-22,
ratified, over leaving after-the-fact detection as the whole remedy). A pull
request's description is this repository's squash commit message, and that
body on `main` is the record of the change's reasoning (`PL-3PH2`; project
owner, 2026-09-26, ratified, over keeping `PL-979D`'s copy of every body in
the tree behind `pr-title`'s required check). The GitHub iPhone app submits the
squash with an empty message, which GitHub honours over the repository's
default, so a merge there empties the record with nothing saying so. `#918`, merged in the app, reached `main` with no body.
GitHub has acknowledged the defect since 2023, in community discussion
[#51016](https://github.com/orgs/community/discussions/51016); `PL-WFFX` holds
the measurements.

- In the Mac's browser, the commit message box should hold the pull request's
  description before you confirm.
- Auto-merge is the safer route when nothing sets its message: all 49
  auto-merges armed that way by 2026-09-22 kept their body. The nine that lost
  theirs carried an explicitly empty message, six of them armed in the
  away-from-desk hours when the app is in use. It is not a guarantee: `#1044`,
  armed by a session with nothing set, landed with an empty body on 2026-09-25,
  and `#1015` did too that day by a merge path nobody established. Both bodies
  are recovered under `docs/pr-bodies/` (`PL-HZ0M`).
- If the app is the only option, check the message behind its cog icon first.
- A body a merge empties anyway is recovered at the next release: the release
  step runs `python3 tools/pr_body_check.py`, which names every squash commit
  that reached `main` with no body and no file under `docs/pr-bodies/`, and
  `--recover` fetches each back from GitHub into that folder. `--compare`
  reports a squash body that says something other than its pull request; that
  drift is accepted rather than repaired, so it is a measurement you run by
  hand.

**A description you edit on GitHub after auto-merge is armed does not reach
`main`.** Auto-merge takes its message when it is armed, so the squash lands
the body as it stood then (`PL-M7W1`), which is accepted as part of the record
(`PL-3PH2`). To land the edit, disarm auto-merge and arm it again, or merge in
the Mac's browser, where the message box shows what will land.

## Bring a stale base in when you merge, with Update branch

Since 2026-09-23 `main` requires a pull request's branch to be up to date
before it merges (`PL-6MW8`, after the third merge-skew instance). Sessions
leave a pull request behind `main` while it waits on you, deliberately: each
update re-runs CI in full, two to five minutes, and one made before you merge
goes stale as soon as another pull request lands. So the update is yours, once,
when you come to merge:

1. Open the pull request in the Mac's browser and scroll to the merge box at
   the bottom of the Conversation tab. If it offers **Update branch**, click
   it: the button itself merges `main` in. Do not use **Update with rebase**
   from its dropdown, which rewrites the branch's history under any session
   still working on it. A "Merge branch 'main' into ..." commit appears and
   the checks restart. If it offers **Squash and merge** and no Update branch,
   the branch is already current: merge it as the section above says, and
   stop. If the pull request is still a draft, leave it: a session's claim
   rides it, GitHub will not merge it, and that session marks it ready when
   the claimed item closes or is blocked (`PL-H14W`).
2. If the merge box already says auto-merge is enabled, as it does on a
   captures-only pull request a session armed, skip this step: your update
   leaves it armed. Otherwise click **Enable auto-merge**, check that the
   message box holds the pull request's description, and click **Confirm
   auto-merge**. Since 2026-10-03 `main`'s rule has **Do not allow bypassing
   the above settings** on (`PL-NXRJ`), so its checks and the up-to-date rule
   bind you as they bind everyone else. To merge past a broken CI, switch it
   off first: **Settings**, then **Branches**, then **Edit** beside the `main`
   rule; untick it and click **Save changes**, merge, then tick it again the
   same way. While it is off, a session will not merge a pull request that is
   already green and current, and hands it to you.
3. Come back in about five minutes. Success is the pull request marked
   **Merged**. If another pull request landed first, `update-armed.yml` has
   brought `main` in again and the checks are running: come back in another
   five. If the merge box still offers **Update branch**, that workflow could
   not update it, and its newest run under **Actions** says why: click the
   button and come back in another five.

With several ready at once, arm auto-merge on each and update just one. When it
merges, `update-armed.yml` brings `main` into every other armed one it left
behind, which re-runs each one's checks, and the next to go green merges.

**Switching auto-merge off holds a pull request back, and its session leaves
it off.** GitHub names your account for every switch, the ones a session makes
through its tools included, so a session records each switch it makes itself
as an `Auto-merge: off - <why>` trailer on its next commit. `bin/docket arm`
asks GitHub for the latest switch, and holds a pull request whose auto-merge
is off when no commit since carries that record. The session then arms or
merges it only on your word (`PL-8TPV`).

If a check fails after the update, the branch and the new `main` do not work
together. That is the merge skew the setting now stops at the pull request
instead of on `main`. Leave auto-merge armed and ask a session to fix the
branch; auto-merge lands it once the fix is green. The session's `bin/docket
arm` tells it the same, so it leaves your arm in place. If the merge box shows
conflicts and no Update branch, do not use **Resolve conflicts**. Ask a
session to merge `main` in and resolve them.

Instead of steps 1 to 3, you can ask the session that opened the pull request
to merge it: it arms auto-merge and brings the base in itself, with the same
merge the button makes. GitHub never updates an armed pull request that falls
behind, so `update-armed.yml` does, on each push to `main`, and one whose
session has ended does not wait for you (`PL-S5MF`, and its token in the next
section). **A pull request already green and current the session
squash-merges itself**, since GitHub offers auto-merge "only on pull requests
that cannot be merged immediately" ([GitHub
Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request))
(project owner, 2026-10-03, ratified, over keeping that merge yours,
`PL-NXRJ`, which reopened `PL-V2X5`). That is safe only while `main`'s rule
binds admins. A session's GitHub calls are yours, and with admins exempt its
merge would pass the up-to-date check `main` holds everyone else to, landing a
stale branch whenever another pull request merged between its read and its
call. So `.claude/hooks/direct-merge-guard.sh` asks GitHub at each merge call
and refuses the merge while **Do not allow bypassing the above settings** is
off (`PL-S17R`, `PL-NXRJ`). The session then tells you it cannot arm the pull
request and the Squash and merge is yours: merge it on the Mac, as step 1 says
for a branch that is already current.

## Give update-armed its token, and renew it

`.github/workflows/update-armed.yml` brings `main` into each armed pull request
that `main` has moved past, on every push to `main` (`PL-S5MF`). The update
needs a token only you can make: one made with the workflow's own token starts
the pull request's checks in an approval-required state, so they would wait on
you. Until the secret exists, each run lists what it would have updated and
changes nothing.

**To make the token**, on the Mac:

1. Open [the token form, filled in for this](https://github.com/settings/personal-access-tokens/new?name=update-armed&description=open-anesthesia-sim+update-armed.yml+brings+main+into+armed+pull+requests&target_name=stuthedew&expires_in=366&contents=write&pull_requests=write&workflows=write).
   It is GitHub's **Settings > Developer settings > Personal access tokens >
   Fine-grained tokens > Generate new token**, with the name, description,
   owner, a 366-day expiry and the permissions set.
2. Under **Repository access**, choose **Only select repositories** and pick
   `stuthedew/open-anesthesia-sim`. The link cannot set this.
3. Under **Permissions**, check that the repository permissions are these and
   no others: **Contents**, **Pull requests** and **Workflows**, each *Read and
   write*, and **Metadata**, *Read-only*, which GitHub adds itself.
4. Click **Generate token** and copy it. GitHub shows it only once.

**To store it:**

5. On the repository's page, click **Settings**, then **Secrets and variables >
   Actions** under **Security** in the sidebar, then **New repository secret**.
6. Enter `UPDATE_BRANCH_TOKEN` as the **Name**, paste the token as the
   **Secret**, and click **Add secret**. Success is `UPDATE_BRANCH_TOKEN` listed
   under **Repository secrets**. From a terminal, `gh secret set
   UPDATE_BRANCH_TOKEN --repo stuthedew/open-anesthesia-sim` does steps 5 and 6
   and prompts for the value.

**Why those permissions.** GitHub's permission table lists only *Pull
requests* for the update call
([Permissions required for fine-grained personal access tokens](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)).
Its reference for the call adds that a GitHub App must also be able to write
the head repository's contents
([Update a pull request branch](https://docs.github.com/en/rest/pulls/pulls#update-a-pull-request-branch))
and does not say whether that holds for a token, so *Contents* is included
rather than found missing at the first update. GitHub refuses an update that
brings in a change to a workflow file without *Workflows*: Mergify's app met
that refusal updating branches behind a workflow change
([Mergifyio/mergify#5055](https://github.com/Mergifyio/mergify/issues/5055)). A
run GitHub refuses turns red, and its summary names the permission GitHub asked
for.

**To see it work**, open **Actions > update-armed** after the next merge. The
newest run's summary lists each armed pull request it read, with *updated*
beside each one it brought `main` into.

**To renew it**, before its expiry date or when runs turn red with HTTP 401,
make a new token the same way and paste it over the old value: the edit icon
beside `UPDATE_BRANCH_TOKEN` on the same settings page, or the `gh secret set`
line again, which overwrites it. The 366 days is a choice, not a limit: a token
that never expires saves the yearly renewal, but a copy that leaked would then
work for good.

## Sweep branches now, or restore one the sweep deleted

`.github/workflows/branch-sweep.yml` deletes each finished `claude/*` branch at
06:17 UTC daily, after copying its tip to `refs/archive/<branch>/<tip>`
(`PL-X8SV`). A session cannot run it or undo it, since both push to branches
other than its own, so both are yours.

**To sweep now:** on the repository's page click **Actions**, then
**branch-sweep** in the left sidebar, then **Run workflow** above the list of
runs. Tick **dry_run** to list what would go and push nothing, then click
**Run workflow**. The run's log, under its **sweep** job, lists each branch it
swept and why each other one stayed.

**To restore one:** the log prints the command beside each branch it swept. Run
it on the Mac from any clone of this repository:

```
git fetch origin refs/archive/claude/NAME/TIP && git push origin FETCH_HEAD:refs/heads/claude/NAME
```

Success is `* [new branch]` on the last line. `git ls-remote origin
'refs/archive/*'` lists every archived tip, if the log has expired. An archive
ref is not shown on GitHub's Branches page and no clone fetches it unasked.

## Spend the monthly API credit on delegable items

Max 20x includes $200 a month of Claude Platform API credit. It pays for
`claude -p` only with an API key from the Console organization linked to the
credit, never for a cloud session, and it expires unused at the end of each
billing cycle (https://support.claude.com/en/articles/17154008, read
2026-10-19). `tools/headless_worker.py` spends it on the items
`bin/docket delegable` lists (`PL-80R5`). Each run clones the repository,
works one item on Opus 5.5 under `docs/worker.md`, pushes a branch named
`claude/<id>-worker`, and adds its reported cost to a ledger in
`~/.local/state/open-anesthesia-sim/`. It stops before a run that the
credit left cannot cover. A run on an item that reaches the simulator uses
`max` effort, and a run on apparatus work uses `high`, as § "Match effort to
the standard the work is held to" sets for sessions (`PL-KFJY`). Run it on
your Mac, from a checkout of `main`, with `claude` and `uv` installed. Start it through `uv run python`, never a
bare `python3`: macOS's own `python3` is Xcode's 3.9, older than the 3.11
the tools need, and `uv run` also puts the project's Python first on `PATH`
for the workers (`PL-W38C`).

1. Claim the credit: claude.ai, Settings, Billing, API credits, Link
   organization. This links one Console organization, and changing it later
   needs support.
2. Create a key in that organization: platform.claude.com, API keys, Create
   key.
3. `export ANTHROPIC_API_KEY=<the key>` in the shell you run from.
4. `uv run python tools/headless_worker.py --dry-run --runs 3` prints the items it
   would run and the credit left, and starts nothing.
5. `uv run python tools/headless_worker.py --runs 3` runs them, one after another.
   Each prints one line: the item, its effort, the cost, and the branch it
   pushed.
   A run that pushed everything it made removes its clone and keeps its log
   in `~/.local/state/open-anesthesia-sim/workers/`. A failed run, or a
   `--no-push` one, keeps both, and its line names the clone to read
   (`PL-TX7K`).

Each branch is a worker's, so review it as delegated work: `bin/docket verify
<id>` on the branch, then open its pull request. `--item <id>` runs one named
item, `--per-run-usd` caps a run (default $15), and `--cycle-day` sets the day
your billing cycle starts. `--no-push --model claude-sonnet-5-5` is
`PL-6FX6`'s trial form: the clone cannot push, so the work stays on your
machine. The cost is Claude Code's own estimate, which can differ from the
bill, so compare the ledger with the Console's usage page after the first
runs.

## Run tag-release yourself where a session cannot

`.github/workflows/tag-release.yml` tags each release on the commit that cut
it, once that commit reaches `main`. When a run fails, the session fixes the
cause and starts a new run itself. Two cases are left to you (`PL-F23S`,
`PL-S641`). `bin/docket release` refuses the next release while one is
untagged, and its refusal names both.

**When GitHub refuses the session's run.** Start it yourself, in either of two
ways:

- On the repository's page click **Actions**, then **tag-release** in the left
  sidebar, then **Run workflow** above the list of runs. Leave **Branch** on
  `main`, which the workflow requires, and click **Run workflow**. The log of
  its **tag** job ends with `Tagged VERSION and pushed it to origin.`
- Or run `python3 tools/tag_release.py --apply` on the Mac, from a clone that is
  up to date with `main`. It tags with your own credentials, because a tag a
  session pushes is dropped without an error (`PL-N936`). It prints the same
  last line once `origin` holds the tag.

The `gh` command `gh workflow run tag-release.yml --ref main` starts the same
run. GitHub's
[Manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
gives both routes (read 2026-10-18). Check the result with
`git ls-remote --tags origin refs/tags/VERSION`, which prints the tag where
`origin` holds it and nothing where it does not.

**When `origin` already holds the tag on another commit.** The run declines
and tags nothing. Its log says `Declined: origin holds VERSION on COMMIT, not
on its cut, CUT.` Which of the two commits is right is your decision. The cut
is the commit that added the version's notes under `docs/releases/`. If the tag
on `origin` is the right one, nothing needs to change. If it is wrong, first
copy the `git ls-remote` line above, so that the old commit is recorded. Then
delete the tag from `origin` with `git push origin --delete refs/tags/VERSION`
and start the run again as above. To undo the deletion, push the old commit
back as the tag with `git push origin COMMIT:refs/tags/VERSION`.

## Retire the stop hook patch once Anthropic fixes it

The cloud container's `Stop` hook, `~/.claude/stop-hook-git-check.sh`, is
Anthropic's and is rewritten at every container start, so
`.claude/hooks/stop_hook_patch.py` corrects it at each session start, for this
project only (`PL-WW08`, `PL-483K`). Both false push demands it corrects are
already reported at Anthropic's public tracker, so neither needs a new report
(`PL-90CJ`; both open on 2026-10-03):

- [anthropics/claude-code#83490](https://github.com/anthropics/claude-code/issues/83490),
  the stale `origin/<branch>` a merged pull request leaves behind. Claude Code
  2.1.288 still ships the unpushed count it reports. You commented there on
  2026-10-03 with the reproduction drafted in `PL-90CJ` - a runnable script
  against the shipped hook, and a five-line fix - so do not post it again.
  Commenting subscribed you, so GitHub notifies you when the issue closes
  ([About notifications](https://docs.github.com/en/subscriptions-and-notifications/concepts/about-notifications),
  section "Default subscriptions").
- [anthropics/claude-code#82624](https://github.com/anthropics/claude-code/issues/82624),
  whose second false positive is a `git clone --depth 1` that fetches `main`
  only, so a push records no `origin/<branch>`. The half of the patch that
  answers it costs nothing to keep running, so it needs no watching.

**Once either closes as fixed,** ask a session to retire the half of
`stop_hook_patch.py` that the fix covers. Nothing in this repository will say
so for #83490 if the fix is the one the comment proposes, since the patch then
finds its own line already in place and stays silent. A fix in any other form
makes it print, at every session start, that the line it rewrites is not there.
