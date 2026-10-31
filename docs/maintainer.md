# Notes for the project owner

Everything here is addressed to the person running the sessions, not to the
sessions themselves. It lives outside `CLAUDE.md` for that reason. A rule that
a session cannot act on still costs every session the context it takes to read
it. `docs/worker.md` is the opposite kind of document. It holds instructions to
a worker agent.

## Rules for sessions live in the repository

**Every rule about how a session works is recorded in one place, the
repository. The Projects trial's instructions carry no rules of their own**
(project owner, 2026-10-03, ratified, over a dated copy of the instructions
kept in the repository for sessions outside the Project, `PL-PDVF`). Every
session sees `CLAUDE.md`, the `docket` skill, the rules under `.claude/rules/`
and what `bin/docket` prints, whether or not it runs in a Project. Only a
Project's coordinator and its threads see that Project's instructions. When a
rule was given only in the instructions, the repository's copy of it was
missing or older. A session outside the Project then followed the old rule. A
Project thread read two rules that disagreed, and each carried your authority.
The cases were the review ask's summary (`PL-8XQS`), re-running
`tag-release.yml` (`PL-F23S`), the arm rule for read holds (`PL-KKHD`), and the
direct squash merge (`PL-NXRJ`). The instructions asked for that merge from
2026-09-27, while the hook refused it from 2026-09-30. Nothing in the
repository can read the instructions, so no check can catch the split. Sending
every rule to the repository is what prevents it.

**What the instructions keep** is the project's own state and nothing else.
That is the Goal, the Order and its pause, the compaction rule, and a pointer
to `.claude/skills/docket/modes/coordinator.md`. The mode file holds the
coordination rules: the thread caps, which model each thread runs, what every
brief says, where threads post and record, merging, and releases (project
owner, 2026-10-25, ratified, over keeping them in Project settings,
`PL-NZC0`). `PL-PDVF` holds the cut-down text as it was written on 2026-10-03,
and the table of where each rule went.

**When you give a rule for sessions in the Project, it goes to the repository
in the same sitting.** Say it to the coordinator. The coordinator starts a
thread that writes the rule into the repository by `CLAUDE.md`'s routing: a
check, the `docket` skill, a path-scoped rule, then resident. The thread works
under `CLAUDE.md`'s rule that a behavior change takes effect in the session
that asks for it. It records your words and the date beside the rule. The
instructions then say nothing about the rule. A thread may find a rule in the
instructions and a rule in the repository that disagree. It then reports both
to you rather than choosing between them, and the fix lands in the repository.
A rule you give in one of your own sessions already takes this route.

## Match model capability to the work

A session cannot switch its own model, so the model is the owner's lever.

**Reasoning-heavy work warrants the strongest available model at a high
effort setting**, for both the change and the review of the final diff:

- architecture and design decisions;
- new scientific-model design;
- ambiguous problems and genuine trade-offs;
- non-obvious debugging and root-cause analysis;
- anything within the scope of `CLAUDE.md` § "Safety-critical
  clinical-output standard". That scope includes the presentation of clinical
  values and the scientific content of `docs/MODEL.md`. Neither of these is
  routine execution, however mechanical the edit looks.

**Executing an already-agreed plan does not.** `bin/docket next` states which
model an item warrants. So the queue settles this for each item rather than
for each session. It prints one of two flags. The section
§ "Which model each flag means" below says which model each flag stands for.

**Whether a cheaper setting holds up is measured, not assumed.** The model
review, `.claude/skills/model-review/SKILL.md`, scores closed items by how
their work held up and brings its recommendations to you with their evidence.
`docs/model-review.md` holds its trials and its dated findings (`PL-63CB`).

### Which model each flag means

**The answer is `docket.toml`'s `[models]` table** (`PL-0XDM`). It holds a
default model and effort, and rules that override them for a kind of work,
matched on an item's class, lane, feature, status, size, area or role. An area
is a set of paths, such as the simulator's core or the interface. `bin/docket
next` and `bin/docket show` print the model and effort it chooses beside each
flag, and the headless worker and the model review tool read it too. To change
a choice, edit the table; `subprojects/docket/README.md` § "The model table"
has the format. `tools/model_home_check.py` refuses a model id written
anywhere else, and `tools/config_home_check.py` holds the two copies that
Claude Code reads to it. This section records why the table says what it
does.

**A dated instance, not a rule** (`.claude/rules/expert-review.md`). What
falsifies the two names below is a new model release or a new word from the
owner, nothing about how this project works.

- **`use your strongest model` means Claude Opus 5.5, the table's default.**
  The `[models]` table decides which model each kind of work uses, and
  nothing here uses Claude Fable 5.1 because the table names it for nothing.
  That replaces this section's reading of 2026-10-18, which named Fable 5.1 as
  the strongest model and so as what the flag asked for. An open item went on
  recommending Fable after nothing else used it, which is why the answer now
  has one home. `tools/model_home_check.py` refuses a model id written outside
  the table, the records and the tests. The project owner's point was the one
  home, not Fable: "It was more about having a single source of truth (fable
  just being an example of a stale model)" (project owner, 2026-10-25). Anthropic's models overview recommends
  Opus 5.5 for most work
  (https://platform.claude.com/docs/en/about-claude/models/overview, read
  2026-10-18). The owner moved this project's Projects threads from Fable 5.1
  to Opus 5.5 on 2026-10-14 (`PL-XJV3`).
- **As of 2026-10-18 `delegable` still means Claude Sonnet 5.5**, the table's
  `delegable` rule, not Claude Haiku 5.5, and one named tier rather than
  a choice between two. The project owner asked for a cheap-model offer on
  clear-cut items. They also specified the asymmetry that the offer must have
  (2026-09-19): *"I'd rather err on the side of default opus if any question
  and miss items that could have been safe with a lower model than try to
  catch every lower model opportunity and find out later I should have
  actually used opus."* Naming one tier follows from that asymmetry. It is
  the reading of the session that wrote this, not the owner's own words. A
  second tier would bring back exactly the per-item judgment that the
  asymmetry exists to remove, at the moment the flag is read.

Three facts decided Sonnet 5 over Haiku 4.5 on 2026-09-19. None of them is
true for Haiku 5.5, according to the models overview read on 2026-10-18:

1. **Haiku 4.5 was a generation behind.** Haiku 5.5 belongs to the same
   generation as Opus 5.5 and Sonnet 5.5.
2. **Haiku 4.5's context window was 200K, while the others' was 1M.** A
   session that spent its whole 150,000-token budget ended with around
   231K–265K of context. That is past Haiku 4.5's entire window
   (`PL-W80S`). Haiku 5.5's window is 1M, the same as the other three models.
3. **Haiku 4.5 did not take the effort parameter**, so § "Match effort to the
   standard the work is held to" below could not be followed on it. Haiku 5.5
   takes the parameter, and Claude Code starts it at `medium`.

The choice of Sonnet still rests on the owner's asymmetry quoted above, not on
a measurement. Anthropic describes Haiku 5.5 as "for high-volume,
latency-sensitive tasks such as classification, extraction, and routing". In
this project a delegated item is a real defect with a real fix. No trial here
has measured Haiku 5.5 on such an item. Such a trial would be recorded under
the `model-evidence` feature. So moving `delegable` to Haiku waits on that
feature's evidence, not on a reading of the lineup.

The models' savings now differ more than they did. At first-party API rates
per 1M tokens, Claude Fable 5.1 costs $10 for input and $50 for output. Claude
Opus 5.5 costs $4 and $20, and Claude Sonnet 5.5 costs $2 and $10. Claude
Haiku 5.5 costs $0.10 and $0.50 for prompts up to 100,000 tokens, and $0.50
and $2.50 for longer ones (*Pricing*,
https://platform.claude.com/docs/en/about-claude/pricing, read 2026-10-18).
Measured against Opus 5.5, moving to Sonnet 5.5 captures 51% to 57% of the
largest saving available, depending on prompt length. On the 2026-09-19
lineup it captured **75%**.

**`delegable` is an offer, never an instruction.** It is derived from
`Item.delegability`. An item qualifies when it is `ready`, has no `safety` or
`science` class and no open decision, and has a `verify:` command that proves
it done. Its `touches` must also be declared and lie wholly outside
`protected_paths` and `gate_paths`, where a directory holding one of those
paths counts as inside it. Each `touches` path outside `tests/` must also be
placed by `workflow_paths` or `product_paths`, and its effort must be `S` or
`M`. There is deliberately no field that *grants* delegability. There is only
`not-delegable:`, which withholds it. Declining the offer and running the
strongest model anyway is always available and never wrong. The flag exists
so that the cheap case is visible, not so that it is taken.

### Why `opusplan` is not the default for the split here

Claude Code's `opusplan` mode "uses `opus` for complex reasoning and
architecture decisions" in plan mode. It "automatically switches to `sonnet`
for code generation and implementation" in execution mode. Both phrases were
read at https://code.claude.com/docs/en/model-config on 2026-09-19. The split
is fixed to those two families. That page offers no equivalent that pairs a
strong model other than Opus with a cheap one. For a mid-task consultation, it
points at the advisor tool instead.

**So on the 2026-09-19 lineup `opusplan` plans one tier below the strongest
model**, and the rule at the top of this section asks for the strongest. That
is the whole objection. The mode is not broken. Its strong half is named by
family rather than by rank, and that family stopped being the top one on
2026-09-19. Use `opusplan` when Opus-level planning is enough for the item in
hand. Do not use it as the default for work that this section calls
reasoning-heavy.

**Since 2026-10-25 that objection no longer applies as written.** The
`[models]` table names Opus 5.5 as the strongest model in use, so `opusplan`'s
planning half is no longer a tier below. Where a rule in the table names a
stronger model for a piece of work, set it deliberately with `/model` and
switch back for execution. Two caveats survive whichever way the split is made:

1. Execution returns to the cheaper model, so the strong-model review of a
   safety-critical diff is a deliberate step, not an automatic one.
2. Switching models mid-session starts a cold cache, so group design and
   execution into runs rather than alternating between them.

One convergence is worth noting. `opusplan`'s execution half is `sonnet`,
which is the same tier that § "Which model each flag means" names for
`delegable`. So the cheap end of both splits is the same model, and nothing
here asks you to hold two answers.

Model choice never changes what a change must satisfy before it lands. The
maintainer still reviews every safety-critical diff, whichever model drafted
it.

## Match effort to the standard the work is held to

Effort is the owner's lever for the same reason that model choice is. A
session cannot change its own effort level.

A session that sets no level runs at its model's default. Opus 5.5, Sonnet 5.5
and Haiku 5.5 default to `medium`, and most older models default to `high`.
Each model calibrates the scale separately, so one level name does not mean the
same amount of reasoning on two models. Anthropic reports that "Opus 5.5 at
`medium` matches or exceeds Opus 5 at `high` on coding and knowledge-work
evaluations" (Claude Code docs, *Model configuration*, section "Adjust effort
level", https://code.claude.com/docs/en/model-config, read 2026-10-17).

**On Opus 5.5, every session opens at `high` for now, simulator and apparatus
alike** (project owner, 2026-10-19, over `max` and `xhigh`, `PL-6XZG`). Its
home is the default effort in `docket.toml`'s `[models]` table (`PL-0XDM`).
The `effortLevel` key in `.claude/settings.json` is the copy Claude Code
reads, and `tools/config_home_check.py` fails when the two differ. So a
session the owner opens without choosing a level runs at the table's default. A level the owner picks when
opening a session still wins over the file, because Claude Code ranks an
explicit choice above settings (Claude Code docs, *Model configuration*,
section "Adjust effort level", https://code.claude.com/docs/en/model-config,
read 2026-10-19). Opening at `high` is the owner's own judgement. The published
gain from `xhigh` over `high` is small.

The decision replaces two ratified records whose stated reason was cost. One
set `high` for apparatus sessions (2026-10-17, `PL-SW0B`). The other set `max`
for simulator sessions (2026-09-19, below). Cost alone never justifies a lower
setting (project owner, 2026-10-19), so a session does not argue for `high` on
cost. On Anthropic's SWE-bench Pro subset, Opus 5.5 solved 95.3% of tasks at
`high` for $0.29 each and 96.7% at `xhigh` for $0.74 each. That is 1.4 points
for about 2.5 times the cost. The page calls its figures directional
(*Optimizing for cost and intelligence*,
https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
read 2026-10-17). The same page reports 88.4% at `high` and 91.1% at `xhigh`
on an internal agentic-coding set. It gives no figure for `max` (read
2026-10-19).

**The owner wants evidence on whether `high` causes real problems** (project
owner, 2026-10-19). The session ledger records each session's model and
effort so that this can be measured. Once the data is adequate, the model
review (`PL-63CB`) tests whether work done at `high` shows more rework,
reopened items, unintended behavior or other real-world issues than work done
at `xhigh` or `max`. When the review finds a statistically significant
difference, it tells the owner about it, with the size of the effect and its
uncertainty.
`PL-63CB` describes the method.

**Half of the sessions run at `xhigh` as a randomized comparison group,
assigned automatically** (project owner, 2026-10-19, over `high` for every
session and an observational comparison only). The owner asked not to have to
set the level by hand. The split was one session in four until 2026-10-24.
The owner then moved it to 50/50, because an equal split needs about a quarter
fewer sessions for the same statistical power (project owner, 2026-10-24,
ratified, over keeping 1 in 4 to spend less of the usage allowance on `xhigh`,
`PL-TN18`). The effort trial starts on Friday 2026-10-23 at 11 pm CDT
(2026-10-24 04:00 UTC). Until then, every session runs at `high`.

This is how the trial works (`PL-HYRM`, `PL-8MZ9`). The session-start hook
runs `tools/effort_trial.py session-start` in every cloud session, including a
resumed one. The script picks the session's arm from a hash of its session id,
so a resumed session keeps the same arm. The script writes the arm as both
`effortLevel` and `maxEffortLevel` in `.claude/settings.local.json`. It then
prints a line that names the arm. The `maxEffortLevel` cap applies from the
session's first request, and it outranks the app's effort picker. A cap only
lowers a level, though. A session in the `xhigh` arm whose picker sent `high`
runs at `high`. So keep the picker at `xhigh` for the length of the trial.

Each session's start-of-session digest names its arm, and the session tells
you the arm in its first reply. The digest line stays in the session's
transcript. That line is the trial's record of the arm, and the model review
reads it from the transcript by session id. Sessions on your own computer are
not in the trial, and the script writes nothing there.

Until 2026-10-24, the cloud environment's setup script drew the arm. That
script runs only when the environment's snapshot is built, about once a week.
So it put no session in either arm (`PL-8MZ9`). The `effort_trial.py` line in
that script now does nothing, and you can remove it from the environment's
settings.

The trial runs until the owner ends it. The monthly model review asks the
owner whether to end it once both arms have adequate data. The review asks in
any case at its run on 2027-04-24, six months in (`PL-63CB` § "Effort
monitoring").

**Superseded on 2026-10-19: apparatus sessions at `high` and simulator sessions
at `max`** (project owner, 2026-09-19, ratified, over running every session at
`max`). The split follows the two standards that `CLAUDE.md` already draws,
rather than a new judgment. `.claude/rules/apparatus-standard.md` governs the
apparatus paths that `CLAUDE.md` lists. It asks for working reliably rather
than for specialist quality. `src/`, `tests/`, `docs/MODEL.md` and `README.md`
are the opposite case, and the safety-critical standard applies to them.

Use `ultracode` deliberately, not by default. It is worth it for a design
round, a safety-critical review, or a genuinely multi-angle problem. It is not
worth it for mechanical work. On 2026-09-19, seven concurrent sessions were all
running at `max`, including one whose whole task was renaming seven item
files.

Two mechanics are worth knowing. First, lower effort produces fewer and more
consolidated tool calls. So it cuts the turn count as well as the output
tokens. Every turn re-reads the whole conversation, so those two savings
multiply. Second, each effort level keeps its own cache, so changing effort
mid-session starts with a cold cache. Set the level when the session opens
rather than toggling it.

## The session ledger records what model and effort worked each item

`docs/session-ledger.tsv` has one row per session in this repository. Each row
gives the session's configured model, the model its session context names, the
model that served its last turn, any model the owner switched to, its effort
level, its tokens by kind, its cost in USD as the harness reports it, and the
date the row was written. A closed item is linked to its sessions through its
`pr:` field. The squash commit for that pull request carries the session's
`Claude-Session:` trailer. `docs/pr-bodies/` is the fallback source.

**Only the model review writes the ledger, from the harness's own record**
(project owner, 2026-10-17, ratified, over a field or trailer that each working
session writes about itself, `PL-92ZN`). A working session writes nothing about
itself, so the ledger costs working sessions nothing. A self-report would also
name the configured model, but a fallback can serve a different model. The
facts belong to a session rather than to an item. About two closed items share
each session. A session also keeps spending after it closes its item. So the
ledger stores each session once, and an item is joined to its sessions when
the ledger is read (project owner, 2026-10-19, ratified, over model and effort
fields on each closed item, `PL-70M6`).

**The model review refreshes it monthly**, and after any generator or cluster
appears (project owner, 2026-10-19, ratified, over a weekly or a quarterly
cadence, `PL-63CB`). `.claude/skills/model-review/SKILL.md` § "Refresh the
records first" has the steps. The review also refreshes `docs/ci-runs.tsv`,
the CI run history, with `python3 tools/ci_runs.py refresh`, because GitHub
deletes a workflow run 90 days after it ran (`PL-4SFQ`).


## Settings that make sessions cheaper

- `subagentPromptCacheTtl` is set to `1h` in `.claude/settings.json`. On a Max
  subscription, the main conversation defaults to a 1-hour prompt cache, but
  subagents, workflows and background tasks default to 5 minutes. This matters
  because `CLAUDE.md` tells every session to delegate broad search to
  subagents. A subagent whose
  turns are more than five minutes apart re-pays its prefix at full input price
  instead of the 0.1x cache-read rate. Such gaps are routine when several
  subagents queue behind the concurrency cap. The 1-hour cache write costs 2x
  rather than 1.25x. It pays back after two cache reads, and any subagent doing
  real work clears that many times over.
- Exploration subagents run on Opus, by the project owner's decision of
  2026-10-17 (ratified, over Haiku 5.5, Sonnet 5.5 and a per-call cheaper
  model for quick lookups; `PL-2D28` carries the case). The project's own
  Explore definition, `.claude/agents/Explore.md`, writes `model: opus`, no
  `effort` line, `omitClaudeMd: true` and the read-only tools Read, Grep and
  Glob. Its `model:` is a copy of the `exploration` rule in `docket.toml`'s
  `[models]` table, and `tools/config_home_check.py` fails when the two
  differ (`PL-0XDM`). In an Opus session the `opus` alias resolves to the session's own
  model. In a Fable session on a Claude subscription it resolves to the Opus
  model the alias points to. That is what the built-in Explore did in both
  ([subagents](https://code.claude.com/docs/en/sub-agents), "Choose a model"
  and "Built-in subagents", read 2026-10-17). So the file changes no model.
  What it adds is a report footer that names what was searched and what was
  not, and the narrow tool set. A search runs at the session's effort level.
  Correctness, not cost, settles the model question. The owner would rather
  pay for Opus and get correct work than take incorrect work from a cheaper
  model for free. So price is never the reason to choose a weaker model
  (project owner, 2026-10-19). A session therefore never argues for a cheaper
  model by trading correctness against cost. Opus stays unless a measurement
  shows that a cheaper model is no less correct at the task. A cloud session
  loads this definition. In an Opus 5.5 cloud session started after the
  definition merged, the Explore subagent's transcript records the
  definition's own system prompt. Every turn ran on `claude-opus-5-5` at the
  session's effort level (measured 2026-10-17, `PL-PTHZ`).
- `CLAUDE_CODE_SUBAGENT_MODEL` is set nowhere in this repository. It left the
  `env` block of `.claude/settings.json` on 2026-10-17 (`PL-2D28`). It never
  chose the model for the built-in Explore and Plan subagents, which run on
  the main conversation's model. It was a default for any subagent that gets
  no model from anywhere else, such as `general-purpose` (subagents page,
  "Choose a model", read 2026-10-17). In a cloud session it did not even do
  that. It was unset in the Bash shell of four cloud sessions on 2026-10-01
  and 2026-10-17. And a `general-purpose` subagent started with no model ran
  on its parent's model (`PL-KLN5`, `PL-2D28`). In a local
  session whose folder is trusted, the variable would have put every
  `general-purpose` subagent on Haiku with no per-item judgment. That is what
  § "Which model each flag means" rules out. So a subagent that names no model
  runs on the session's own model. A session does not ask for a cheaper model
  for any subagent unless the owner approves it for that task (project owner,
  2026-10-19, ratified, over asking for a cheaper model per call). `PL-2D28`
  reached the same answer for searches on 2026-10-17. The owner then added
  the reason in their own words: price, even a price of zero, does not justify
  a model that may be less correct (project owner, 2026-10-19). The same rule
  applies to effort. A subagent runs at the session's own effort level unless
  the owner approves a lower one for that task (project owner, 2026-10-19).
  This rule covers subagents that copy values as well as those that search.
  On 2026-10-19, a session set Sonnet runners to work on the session ledger's
  values because of the old wording here, and the owner asked why.
- **A session asking you to type `/compact` is resetting at its budget**
  (project owner, 2026-09-25, ratified, over pasting a handoff prompt into a
  new session, `PL-YJG1`). The session pushes everything first, so anything
  the summary drops is already on disk. It also keeps its branch, its claim
  and its pull-request watch. `/compact` works in cloud sessions and takes
  optional focus text (`/compact keep the open question about X`). `/clear`
  does not work in cloud sessions. **Type it within the hour. The session
  names the clock time.** One more request, over the whole history, writes
  the summary. While the prompt cache is warm, that request reads the history
  from the cache. On the API, a cache read bills at 0.05x the input price on
  Opus 5.5 and 0.1x on most models. After a break longer than the cache
  lasts, the request reprocesses the whole history as uncached input
  ([prompt caching](https://code.claude.com/docs/en/prompt-caching),
  "Compacting the conversation";
  [pricing](https://platform.claude.com/docs/en/about-claude/pricing)). In the
  one reset that was measured, that came to 248,803 tokens (`PL-384P`). The
  cache lasts an hour on your plan's included usage, and five minutes once
  usage credits are drawn. Once the cache has expired, a fresh session is
  cheaper by about that one read, as long as the work is pushed and nothing
  needs the pull-request watch. For an unrelated topic, start a fresh session
  instead. That is where a clean prompt beats a carried-over conversation.
- **When you create a Claude Code project, set its cloud environment to
  `Default` before you send it work.** The **New project** dialog asks only
  for a name, a goal and context, and "Cloud threads use a default
  Anthropic-hosted environment until you pick one in
  **Project settings > Environment**"
  ([Projects](https://code.claude.com/docs/en/claude-projects),
  "Choose an environment for threads", read 2026-10-01). That environment
  runs none of `Default`'s setup script. So each of its threads finds a `uv`
  older than `pyproject.toml` requires, and no `libegl1`. The thread has to
  repair both before `make check` will run (`PL-QKXZ`). Both projects so far
  started in that environment. To fix it, open the project and click the gear
  icon in its header to open **Project settings**. Go to **Environment**, and
  set **Cloud environment** to **Default**. The setting saves as you change
  it. The change applies to new threads only, so make it before the first
  task. A thread can confirm the setting: `get_session` returns
  `environment_id` `env_01JWikdPctorEBXoFK7bJnCq`.
- **Auto mode as your default applies only to the sessions on your Mac, and no
  file in this repository can set it** (`PL-ZLS5`). Your
  `"permissions": {"defaultMode": "auto"}` in `~/.claude/settings.json` is
  the right place for it. A project file would be ignored without an error.
  The documentation says that
  "`permissions.defaultMode` values `auto` and `bypassPermissions` don't take
  effect from project or local settings; set them in user or managed settings
  instead, or pass `--permission-mode` for one session"
  ([Settings](https://code.claude.com/docs/en/settings), "A value you set is
  ignored", read 2026-10-18). A cloud session reads neither of your own files.
  `~/.claude/settings.json` and `.claude/settings.local.json` are "not read.
  Both stay on your machine" (same page, "Settings in cloud sessions"). So a
  cloud session takes its mode from the menu instead: "You pick a cloud
  session's permission mode from the mode dropdown, both when you create the
  task and while the session runs"
  ([Use Claude Code in the cloud](https://code.claude.com/docs/en/claude-code-on-the-web),
  "Permission modes in cloud sessions", read 2026-10-18). A cloud session
  that asks for permissions you thought you had turned off is in the mode its
  dropdown names, so change the mode there.

## What comes to you before it merges

**A pull request comes to you only for a real decision or a high-risk change,
and housekeeping merges on green** (project owner, 2026-10-17, `PL-DKBG`). A
real decision is one that `.claude/skills/docket/modes/design.md` step 4
already makes yours. A high-risk change is any of three kinds. It changes a
clinical value that the simulator computes or displays, or what
`docs/MODEL.md` says such a value means. It is a rule that sessions run under
and that you did not ask for in your own words. Or CI would not show its
breakage, or a revert would not undo it. For a high-risk change, the ask gives
the case for the change, its risks, and what was checked. `#1516` set this
rule. The path list held that pull request for you, although nothing in it
needed a decision.

The session decides which kind a change is. It records that decision on a
commit as `Owner-read: needed - <why>` or `Owner-read: not needed - <why>`.
`bin/docket arm` reads that record. Some changes wait until a record made
after their newest change covers them. These are changes to `src/`, to a test
under `tests/` that imports the simulator, to `docs/MODEL.md`, to
`src/anesthesia_sim/data/` or to `README.md`. So if a session never makes the
decision, the pull request waits, rather than merging a clinical change that
nobody reviewed. `not needed` arms the pull request to merge on green, with
the reason in the pull request body. `needed` holds it for you, whatever paths
it changes. `subprojects/docket/src/docket/arming.py` decides what merges
without you. A change to that file waits on you in only three cases. It
changes or deletes an existing test that pins `arm`'s results, it moves the
file, or it carries a `needed` record. Otherwise it merges on green (project
owner, 2026-10-19, ratified, over holding every change to it, `PL-9JHM`).
Before that decision, every change to it waited on you (`PL-VKHD`). A pinned
test is one of these, in `subprojects/docket/tests/test_cli.py`: a `test_arm_`
test, a test that runs `arm` or reads `arming`, or one of those tests' `_arm`
helpers and `ARM_` constants. The modules that `arm` reads through, such as
`vcs.py`, `claims.py` and `cli.py`, arm on green. So a change there that
loosens one of `arm`'s results has to edit a pinned test, and that edit waits
on you (project owner, 2026-10-12, ratified, `PL-WW0Q`). The hold applies to
the tests that pin `arm`'s results, not to the code they test. So a new test
arms on green. So does a loosening that no test pins, even in `arming.py`
itself.

**A hold comes to you with its question or its risk, never a bare "read #N"**
(project owner, 2026-10-18, `PL-9JHM`). The session records what to ask you
as an `Owner-ask:` trailer on a commit. `arm` prints that trailer as the first
line of the ask. The ask is either a decision or a risk review. A decision has
at least two options and a recommendation. Each option says what it changes
for you or for a learner. The decision is worded in clinical or learner terms.
A choice between approaches to the interface comes with one annotated
screenshot per option (project owner, 2026-10-19, `PL-KYTY`). A risk review
says what could go wrong and for whom, what was checked, and the one thing to
look at. Until a record made after the newest change covers the pull request,
`arm` tells the session to send you nothing. It says so on the first line of
its output and with an exit status of its own. A thread cannot send the ask
anyway. `.claude/hooks/owner_ask_guard.py` rejects a thread's reply that asks
you to read or merge, unless `arm` has a recorded ask and the reply carries
that ask's line (`PL-TLPH`). The coordinator's post that relays such an ask is
rejected unless it carries a line in the recorded form. The hook cannot check
that the line is the recorded line itself (`PL-YV90`). A question whose answer
is obvious is a wrong question, as on `#1516`. When there is nothing to decide
or review, the session records `Owner-read: not needed`, and the change merges
on green without asking you. A change to a test that pins `arm`'s results
still waits for you whatever that record says, so its ask is a risk review.

A held pull request merges when you say so, and nothing more is needed:
"Merge it" is enough. It merges by the route that § "Bring a stale base in
when you merge, with Update branch" describes.

Before 2026-10-17, those simulator paths waited for your review on their own,
whatever the change was (the Projects trial's instructions, 2026-10-03, kind
unrecorded, over holding every path outside `docs/items/`, `docs/pr-bodies/`
and `subprojects/docket/`). `PL-KKHD` built that hold. A workflow item needs
no merge confirmation from you (project owner, 2026-10-12, `PL-KPM2`). So a
change to `.github/workflows/`, `.claude/hooks/` or docket's lexer arms on
green, like the rest of the workflow lane. Until then those paths had waited
on your review, the first two since 2026-10-03 and the lexer since 2026-10-10.
Every other change arms on green. The store, the body records (`PL-979D`) and
the queue's tooling arm on green as before (project owner, 2026-09-25,
ratified, over holding every path outside `docs/items/`, `PL-SQTR`).
`PL-K6B2` built that rule. Since 2026-10-03, so do `CLAUDE.md`, `ROADMAP.md`,
`tools/`, the rest of `.claude/` and `.github/`, and everything else. `arm`
names each path outside the store that it armed, so the session's report
carries the reason. Before that, the hold fired on every change outside the
store. You confirmed on 2026-09-25 that those holds were being clicked
through, so the hold was guarding nothing. `PL-CBDX` reviews the diffs that
merged unread since 2026-09-23.

Two decisions of 2026-10-03 are recorded here, so that the list is seen as
decided rather than left at a default. First, `ROADMAP.md` and
`docs/WORKING_NOTES.md` arm on green. `PL-0JGZ` (project owner, 2026-09-26,
ratified) had held them, because the roadmap is where you set direction. Your
list reopened that question, and you settled it this way (project owner,
2026-10-03, ratified, over holding them as before, `PL-KKHD`). Second,
`.github/workflows/` and `.claude/hooks/` joined the list. The reason is that
`update-armed.yml`, `tag-release.yml` and `direct-merge-guard.sh` decide
merges and tags, as `arming.py` does. Holding them cost about one review a
day, at recent rates (project owner, 2026-10-03, ratified, over leaving them
armed on green, `PL-KKHD`). They left the list again under your rule of
2026-10-12 above.

One decision of 2026-10-05 is recorded here too. A test of the tooling under
`tests/` arms on green, as `subprojects/docket/tests/` does. A test of the
tooling is a file that pytest collects and that imports no `anesthesia_sim`.
Of the 51 merges held for a review since 2026-10-03, 16 had been held by such
tests alone, with nothing in them for you to judge (project owner, 2026-10-05,
ratified, over keeping every change under `tests/` on the read list,
`PL-552M`). A test of the simulator still waits for the session's
`Owner-read` record. So does a branch that drops a test's simulator import or
deletes a simulator test, because `arm` reads the file both before and after
the change. `tests/conftest.py` and every other file that pytest does not
collect also wait, because they serve the simulator's tests whatever they
import. So does any test that `arm` could not read, and `arm` gives the reason
beside the hold. This rule is the same one that
`tools/workflow_paths_check.py` uses to sort the lanes, and it is written
once, in `arming.py`. Since 2026-10-19, a change to the rule waits on your
review only where it edits a test that pins `arm`'s results (`PL-9JHM`).

## Merge on the Mac or by auto-merge, never in the GitHub app

You merge by three routes: the Mac's browser, auto-merge armed through Claude,
and the GitHub iPhone app (project owner, 2026-09-22). Squash-merge and arm
auto-merge by the first two routes, not in the app (project owner,
2026-09-22, ratified, over leaving after-the-fact detection as the whole
remedy). In this repository, a pull request's description becomes the squash
commit message. That body on `main` is the record of the reasoning behind the
change (project owner, 2026-09-26, ratified, over keeping `PL-979D`'s copy of
every body in the tree behind `pr-title`'s required check, `PL-3PH2`). The
GitHub iPhone app submits the squash with an empty message. GitHub uses that
empty message instead of the repository's default. So a merge in the app
empties the record, and nothing says that it did. `#918` was merged in the
app and reached `main` with no body. GitHub has acknowledged the defect since
2023, in community discussion
[#51016](https://github.com/orgs/community/discussions/51016). `PL-WFFX` has
the measurements.

- In the Mac's browser, check that the commit message box holds the pull
  request's description before you confirm.
- Auto-merge is the safer route when nothing sets its message. All 49
  auto-merges armed that way by 2026-09-22 kept their body. The nine that
  lost their body had carried an explicitly empty message. Six of those nine
  were armed in the hours away from the desk, when the app is in use.
  Auto-merge is not a guarantee, though. A session armed `#1044` with no
  message set, and it landed with an empty body on 2026-09-25. `#1015` also
  landed with an empty body that day, by a merge path that nobody identified.
  Both bodies have been recovered under `docs/pr-bodies/` (`PL-HZ0M`).
- If the app is the only option, check the message behind its cog icon first.
- If a merge empties a body anyway, the next release recovers it. The release
  step runs `python3 tools/pr_body_check.py`. That script names every squash
  commit that reached `main` with no body and no file under
  `docs/pr-bodies/`. Its `--recover` option fetches each missing body back
  from GitHub into that folder. Its `--compare` option reports a squash body
  that says something other than its pull request. That drift is accepted
  rather than repaired, so `--compare` is a measurement you run by hand.

**A description you edit on GitHub after auto-merge is armed does not land on
`main`.** Auto-merge takes its message at the moment it is armed. So the
squash lands the body as it stood then (`PL-M7W1`). That older body is
accepted as part of the record (`PL-3PH2`). To land the edit, disarm
auto-merge and arm it again. Or merge in the Mac's browser, where the message
box shows what will land.

## Bring a stale base in when you merge, with Update branch

Since 2026-09-23, `main` requires a pull request's branch to be up to date
before it merges (`PL-6MW8`, after the third merge-skew instance). Sessions
deliberately leave a pull request behind `main` while it waits on you. They do
so because each update re-runs CI in full, which takes two to five minutes,
and an update made before you merge goes stale as soon as another pull request
lands. So the update is yours to make, once, when you come to merge:

1. Open the pull request in the Mac's browser and scroll to the merge box at
   the bottom of the Conversation tab. If it offers **Update branch**, click
   it. The button itself merges `main` into the branch. Do not use **Update
   with rebase** from its dropdown, because it rewrites the branch's history
   under any session that is still working on it.
   A "Merge branch 'main' into ..." commit appears and the checks restart.
   If the box offers **Squash and merge** and no Update branch, the branch
   is already current. Merge it as the section above says, and stop. If the
   pull request is still a draft, leave it. The draft carries a session's
   claim, and GitHub will not merge it. That session marks it ready when the
   claimed item closes or is blocked (`PL-H14W`).
2. If the merge box already says auto-merge is enabled, skip this step,
   because your update leaves it armed. The box says this on a captures-only
   pull request that a session armed. Otherwise, click **Enable auto-merge**,
   check that the message box holds the pull request's description, and click
   **Confirm auto-merge**. Since 2026-10-03, `main`'s rule has **Do not allow
   bypassing the above settings** turned on (`PL-NXRJ`). So its checks and the
   up-to-date rule apply to you as they apply to everyone else. To merge past
   a broken CI, switch that setting off first. Go to **Settings**, then
   **Branches**, then **Edit** beside the `main` rule. Untick the setting and
   click **Save changes**. Merge, then tick it again the same way. While the
   setting is off, a session will not merge a pull request that is already
   green and current. It hands that pull request to you instead.
3. Come back in about five minutes. Success is the pull request marked
   **Merged**. If another pull request landed first, `update-armed.yml` has
   brought `main` in again and the checks are running. Come back in another
   five minutes. If the merge box still offers **Update branch**, that
   workflow could not update the branch. Its newest run under **Actions**
   says why. Click the button and come back in another five minutes.

When several pull requests are ready at once, arm auto-merge on each and
update just one. When that one merges, `update-armed.yml` brings `main` into
every other armed pull request that the merge left behind. That re-runs each
one's checks, and the next to go green merges.

**Switching auto-merge off holds a pull request back, and its session leaves
it off.** GitHub names your account for every switch, including the ones a
session makes through its tools. So a session records each switch that it
makes itself as an `Auto-merge: off - <why>` trailer on its next commit.
`bin/docket arm` asks GitHub for the latest switch. If auto-merge is off and
no commit since that switch carries the record, `arm` holds the pull request.
The session then arms or merges it only when you say so (`PL-8TPV`).

If a check fails after the update, the branch and the new `main` do not work
together. That is merge skew, which the up-to-date setting now stops at the
pull request instead of on `main`. Leave auto-merge armed and ask a session to
fix the branch. Auto-merge lands it once the fix is green. The session's
`bin/docket arm` tells it the same thing, so the session leaves your arm in
place. If the merge box shows conflicts and no Update branch, do not use
**Resolve conflicts**. Ask a session to merge `main` in and resolve them.

Instead of steps 1 to 3, you can ask the session that opened the pull request
to merge it. The session arms auto-merge and brings the base in itself, with
the same merge that the button makes. GitHub never updates an armed pull
request that falls behind, so `update-armed.yml` does that on each push to
`main`. So an armed pull request whose session has ended does not wait for you
(`PL-S5MF`, and its token in the next section). **The session itself
squash-merges a pull request that is already green and current**, because
GitHub offers auto-merge "only on pull requests that cannot be merged
immediately" ([GitHub
Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request))
(project owner, 2026-10-03, ratified, over keeping that merge yours,
`PL-NXRJ`, which reopened `PL-V2X5`). That is safe only while `main`'s rule
applies to admins. A session's GitHub calls are made as you. If admins were
exempt, a session's merge would pass the up-to-date check that `main` applies
to everyone else. It would then land a stale branch whenever another pull
request merged between the session's check of the branch and its merge call.
So `.claude/hooks/direct-merge-guard.sh` asks GitHub at each merge call. It
rejects the merge while **Do not allow bypassing the above settings** is off
(`PL-S17R`, `PL-NXRJ`). The session then tells you that it cannot arm the
pull request and that the Squash and merge is yours. Merge it on the Mac, as
step 1 says for a branch that is already current.

## Give update-armed its token, and renew it

On every push to `main`, `.github/workflows/update-armed.yml` brings `main`
into each armed pull request that `main` has moved past (`PL-S5MF`). The update
needs a token that only you can make. An update made with the workflow's own
token starts the pull request's checks in a state that requires approval, so
the checks would wait for you. Until the secret exists, each run lists what it
would have updated and changes nothing.

**To make the token**, on the Mac:

1. Open [the token form, filled in for this](https://github.com/settings/personal-access-tokens/new?name=update-armed&description=open-anesthesia-sim+update-armed.yml+brings+main+into+armed+pull+requests&target_name=stuthedew&expires_in=366&contents=write&pull_requests=write&workflows=write).
   The link opens GitHub's **Settings > Developer settings > Personal access
   tokens > Fine-grained tokens > Generate new token** page. The name,
   description, owner, a 366-day expiry and the permissions are already set.
2. Under **Repository access**, choose **Only select repositories** and pick
   `stuthedew/open-anesthesia-sim`. The link cannot set this.
3. Under **Permissions**, check that the repository permissions are these and
   no others: **Contents**, **Pull requests** and **Workflows**, each *Read and
   write*, and **Metadata**, *Read-only*. GitHub adds **Metadata** on its own.
4. Click **Generate token** and copy it. GitHub shows the token only once.

**To store it:**

5. On the repository's page, click **Settings**, then **Secrets and variables >
   Actions** under **Security** in the sidebar, then **New repository secret**.
6. Enter `UPDATE_BRANCH_TOKEN` as the **Name**, paste the token as the
   **Secret**, and click **Add secret**. When this has worked,
   `UPDATE_BRANCH_TOKEN` is listed under **Repository secrets**. From a
   terminal,
   `gh secret set UPDATE_BRANCH_TOKEN --repo stuthedew/open-anesthesia-sim`
   does steps 5 and 6 and prompts for the value.

**Why those permissions.** GitHub's permission table lists only *Pull
requests* for the update call
([Permissions required for fine-grained personal access tokens](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)).
GitHub's reference page for the call adds that a GitHub App must also be able
to write the head repository's contents
([Update a pull request branch](https://docs.github.com/en/rest/pulls/pulls#update-a-pull-request-branch)).
That page does not say whether the same applies to a token. So *Contents* is
included now, rather than found missing at the first update. Without
*Workflows*, GitHub refuses an update that brings in a change to a workflow
file. Mergify's app met that refusal when it updated branches that were behind
a workflow change
([Mergifyio/mergify#5055](https://github.com/Mergifyio/mergify/issues/5055)).
When GitHub refuses a run, the run turns red. Its summary names the permission
that GitHub asked for.

**To see it work**, open **Actions > update-armed** after the next merge. The
newest run's summary lists each armed pull request that the run read. It marks
*updated* beside each one that it brought `main` into.

**To renew it**, make a new token the same way before its expiry date, or when
runs turn red with HTTP 401. Then paste the new token over the old value. You
can use the edit icon beside `UPDATE_BRANCH_TOKEN` on the same settings page.
Or you can run the `gh secret set` line again, which overwrites the old value.
The 366 days is a choice, not a limit. A token that never expires saves the
yearly renewal. But if a copy of it leaked, that copy would then work for good.

## Sweep branches now, or restore one the sweep deleted

Every day at 06:17 UTC, `.github/workflows/branch-sweep.yml` deletes each
finished `claude/*` branch. Before it deletes a branch, it copies the branch's
tip to `refs/archive/<branch>/<tip>` (`PL-X8SV`). A session cannot run the
sweep or undo it, because both actions push to branches other than the
session's own. So both are yours to do.

**To sweep now:** on the repository's page click **Actions**, then
**branch-sweep** in the left sidebar, then **Run workflow** above the list of
runs. Tick **dry_run** to list what would be deleted without pushing anything,
then click **Run workflow**. The run's log, under its **sweep** job, lists each
branch that it swept. It also says why each other branch was kept.

**To restore one:** the log prints the command beside each branch that it
swept. Run that command on the Mac from any clone of this repository:

```
git fetch origin refs/archive/claude/NAME/TIP && git push origin FETCH_HEAD:refs/heads/claude/NAME
```

When the restore has worked, the last line shows `* [new branch]`. If the log
has expired, `git ls-remote origin 'refs/archive/*'` lists every archived tip.
GitHub's Branches page does not show an archive ref, and no clone fetches one
unless it is asked to.

## Spend the monthly API credit on delegable items

Max 20x includes $200 a month of Claude Platform API credit. The credit pays
for `claude -p` only when it runs with an API key from the Console
organization linked to the credit. It never pays for a cloud session. Credit
left unused expires at the end of each billing cycle
(https://support.claude.com/en/articles/17154008, read 2026-10-19).
`tools/headless_worker.py` spends the credit on the items that
`bin/docket delegable` lists (`PL-80R5`). Each run clones the repository and
works one item on Opus 5.5, following `docs/worker.md`. It pushes a branch
named `claude/<id>-worker`. It then subtracts its reported cost from the
figure for the credit left, which you give the runner at launch. The runner
stops before a run that the credit left cannot cover. It also stops after any
run that fails, because an empty credit, a lost connection or a sleeping Mac
makes every later run fail too (`PL-44SP`). Every run uses the effort level
in `.claude/settings.json`, which is `high`. That is the level that
§ "Match effort to the standard the work is held to" sets for sessions
(`PL-4N0K`). Run `tools/headless_worker.py` on your Mac, from a checkout of `main`, with
`claude` and `uv` installed. Start it through `uv run python`, never a bare
`python3`. macOS's own `python3` is Xcode's Python 3.9, which is older than
the 3.11 that the tools need. `uv run` also puts the project's Python first on
`PATH` for the workers (`PL-W38C`).

A worker runs `make check` before it commits, so the Mac needs the tools the
suite compares its readers against: bash 5.2 or newer, and GNU Make 4 or newer.
macOS ships bash 3.2 and GNU Make 3.81, and with them 89 tests fail whatever the
change, so a worker cannot see its own failures among them (`PL-TSH9`).
`brew install bash make` installs both. Homebrew installs the new make as
`gmake`, so also add `export PATH="$(brew --prefix)/opt/make/libexec/gnubin:$PATH"`
to the end of `~/.zshrc`, which makes it `make` in a new Terminal window
(the formula's own caveat, `Formula/m/make.rb` in Homebrew/homebrew-core,
read 2026-10-19). `bash --version` and `make --version` then print 5.3 and
4.4.1 or newer. The runner refuses to start, before it spends any credit,
while the bash or make on its `PATH` is older than bash 5.2 or GNU Make 4
(`PL-44R1`).

1. Claim the credit. On claude.ai, go to Settings, Billing, API credits, Link
   organization. This links one Console organization. Changing that
   organization later needs a request to support.
2. Create a key in that organization. On platform.claude.com, go to API keys,
   Create key.
3. Run `export ANTHROPIC_API_KEY=<the key>` in the shell you run from.
4. Read the credit left at platform.claude.com/settings/billing, under
   **Promotional credits**. The runner takes this figure from you as
   `--credit-left` for two reasons. This account cannot read the Console's
   Cost API. And a figure kept on your Mac would miss spending made anywhere
   else (`PL-NQ0M`).
5. Run
   `uv run python tools/headless_worker.py --credit-left 197.72 --dry-run --runs 3`,
   with the figure from step 4. It prints the items it would run and the
   credit left, and it starts nothing.
6. Run `uv run python tools/headless_worker.py --credit-left 197.72 --runs 3`
   to run those items, one after another. On macOS, the runner first keeps the
   Mac awake with `caffeinate -i` until the batch ends. So you no longer need
   to start the runner under `caffeinate` yourself. Keep the lid open, because
   caffeinate's manual does not say that it keeps the Mac awake with the lid
   closed (`PL-BT70`). Each run prints one line: the item, its effort, the
   cost, and the branch it pushed. A run that pushed adds a second line that
   names its record.
   A run that pushed everything it made removes its clone. It keeps its log
   in `~/.local/state/open-anesthesia-sim/workers/`. A failed run, or a
   `--no-push` one, keeps both the clone and the log. Its line names the
   clone to read (`PL-TX7K`).

Each branch belongs to a worker, so review it as delegated work. Run
`bin/docket verify <id>` on the branch, then open its pull request. A pushed
run also commits its record to the branch, as
`docs/worker-runs/<branch>-<started>.json`. The run's line names that file.
Before it opens the pull request, the reviewing session runs
`python3 tools/worker_runs.py review <file> --outcome accepted|fixed|sent-back --note "<one line>"`.
`make check` fails until the session does this (`PL-87BR`). The records are
how headless work is compared with chat-session work. So the record of a
sent-back branch still belongs on `main`. Carry its two record commits to a
branch of their own. Once that lands, the daily branch sweep deletes the
sent-back worker branch, so its item returns to `bin/docket next` (`PL-W5JR`). `--item <id>` runs one named item. `--per-run-usd` caps
the cost of one run (default $15). `--no-push --model claude-sonnet-5-5` is
the form used for `PL-6FX6`'s trial. In that form the clone cannot push, so the
work stays on your machine. The cost that each run reports is Claude Code's
own estimate, which can differ from the bill. So read the Console's figure
again at each launch, rather than carrying forward the runner's last figure.
Runners before `PL-NQ0M` kept a ledger at
`~/.local/state/open-anesthesia-sim/api-credit-ledger.jsonl`. Nothing reads
it now, so you can delete it.

## Have a strong model read the model document against the data, once

`tools/model_doc_review.py` sends `docs/MODEL.md` and every data file under
`src/anesthesia_sim/data/` through the Message Batches API, on the same API
credit as the headless workers (`PL-5S71`). The model, its effort and its
price come from `docket.toml`'s `[models]` table, for the role `review`; on
2026-10-25 that was Opus 5.5 at `high`. The project owner chose on 2026-10-25
to run it once on the table's model, over dropping it. It sends one request per
`##` section, 25 on 2026-10-25, and each request carries the whole document and
the data. The model reports statements in its section that contradict a stored
value, another statement or their own units. A session then checks each one and
files the confirmed ones. Run it on your Mac from a checkout of `main`, with the
key exported as in § "Spend the monthly API credit on delegable items", steps 1
to 3.

1. `uv run python tools/model_doc_review.py estimate` prints the number of
   requests, the model and effort, and the most the batch could cost, and
   sends nothing. On 2026-10-25 the bound was $27.05 on Opus 5.5. The bound assumes no prompt-cache hit and
   every request using its full output allowance, so the bill should be well
   below it.
2. `uv run python tools/model_doc_review.py submit --credit-left 197.72`, with
   the figure from platform.claude.com/settings/billing, sends the batch. It
   refuses when the bound is more than the credit left. It prints a batch id
   that starts `msgbatch_`, and saves a manifest in
   `~/.local/state/open-anesthesia-sim/model-doc-review/`.
3. `uv run python tools/model_doc_review.py fetch <batch id>` reports progress
   until the batch ends. Most batches end within an hour, and all within 24
   hours. Once it has ended, it prints one line per section and writes
   `<batch id>.findings.json` in the same folder.
4. Attach that findings file to a project thread and ask for `PL-5S71`'s
   findings to be checked. A section marked `not reviewed` names its reason,
   and can be sent again in a later batch.

## Run tag-release yourself where a session cannot

`.github/workflows/tag-release.yml` tags each release on the commit that cut
it, once that commit reaches `main`. When a run fails, the session fixes the
cause and starts a new run itself. Two cases are left to you (`PL-F23S`,
`PL-S641`). While a release is untagged, `bin/docket release` refuses to cut
the next one, and its refusal message names both cases.

**When GitHub refuses the session's run.** Start the run yourself, in either
of two ways:

- On the repository's page click **Actions**, then **tag-release** in the left
  sidebar, then **Run workflow** above the list of runs. Leave **Branch** on
  `main`, which the workflow requires, and click **Run workflow**. The log of
  its **tag** job ends with `Tagged VERSION and pushed it to origin.`
- Or run `python3 tools/tag_release.py --apply` on the Mac, from a clone that is
  up to date with `main`. The script tags with your own credentials, because a
  tag that a session pushes is dropped without any error (`PL-N936`). It
  prints the same last line once `origin` holds the tag.

The `gh` command `gh workflow run tag-release.yml --ref main` starts the same
run. GitHub's
[Manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
gives both routes (read 2026-10-18). Check the result with
`git ls-remote --tags origin refs/tags/VERSION`. It prints the tag when
`origin` has it, and prints nothing when `origin` does not.

**When `origin` already holds the tag on another commit.** The run declines
and tags nothing. Its log says `Declined: origin holds VERSION on COMMIT, not
on its cut, CUT.` You decide which of the two commits is right. The cut is the
commit that added the version's notes under `docs/releases/`. If the tag on
`origin` is the right one, nothing needs to change. If it is wrong, first copy
the line that the `git ls-remote` command above prints, so that the old commit
is recorded. Then delete the tag from `origin` with
`git push origin --delete refs/tags/VERSION` and start the run again as
described above. To undo the deletion, push the old commit back as the tag
with `git push origin COMMIT:refs/tags/VERSION`.

## Retire the stop hook patch once Anthropic fixes it

The cloud container's `Stop` hook, `~/.claude/stop-hook-git-check.sh`, belongs
to Anthropic, and it is rewritten at every container start. So
`.claude/hooks/stop_hook_patch.py` corrects the hook at each session start, for
this project only (`PL-WW08`, `PL-483K`). The hook makes two false demands to
push, and the patch corrects both. Both are already reported on Anthropic's
public issue tracker, so neither needs a new report (`PL-90CJ`). Both issues
were open on 2026-10-03:

- [anthropics/claude-code#83490](https://github.com/anthropics/claude-code/issues/83490)
  is about the stale `origin/<branch>` that a merged pull request leaves
  behind. In Claude Code 2.1.288 the hook still counts commits as unpushed
  against that stale ref. You commented on the issue on 2026-10-03 with the
  reproduction drafted in `PL-90CJ`. The comment gives a runnable script that
  tests the shipped hook, and a five-line fix, so do not post it again.
  Commenting subscribed you to the issue, so GitHub notifies you when it closes
  ([About notifications](https://docs.github.com/en/subscriptions-and-notifications/concepts/about-notifications),
  section "Default subscriptions").
- [anthropics/claude-code#82624](https://github.com/anthropics/claude-code/issues/82624)
  lists more than one false positive. The second is a `git clone --depth 1`
  that fetches only `main`, so a push records no `origin/<branch>`. The
  half of the patch that handles this case costs nothing to keep running, so
  you do not need to watch this issue.

**Once either issue closes as fixed,** ask a session to retire the half of
`stop_hook_patch.py` that the fix covers. For #83490, nothing in this
repository will tell you that the fix has landed if it is the fix that the
comment proposes. In that case the patch finds its own line already in
place and stays silent. If the fix takes any other form, the patch prints a message at every
session start saying that the line it rewrites is not there.

## Give Projects threads the repository's hooks with one setup script

A Claude Projects thread does not load `.claude/settings.json`, so none of the
repository's hooks run in it: not the guards, not the session-start digest and
not the stop hook patch. Claude Code's documentation says so, in
[What threads pick up from your repositories](https://code.claude.com/docs/en/claude-projects.md#what-threads-pick-up-from-your-repositories)
(read 2026-10-26), and `PL-CR81` records the measurement. A thread does read
the user settings file, `~/.claude/settings.json`. `.claude/hooks/thread_hooks.py`
uses that file to give a thread the hooks (`PL-X6VN`).

The setup script below adds one `SessionStart` entry to the user settings. At
each session start in a Projects thread, that entry runs `thread_hooks.py` from
the checkout. The hook copies the repository's `hooks` block into the user
settings, and Claude Code applies the copy from its next tool call on. In any
other session the hook does nothing, because those sessions load the
repository's settings themselves. The script holds no copy of the hooks, so a
change to `.claude/settings.json` reaches the next thread without a change
here. `python3 .claude/hooks/thread_hooks.py --setup-script` prints the script,
and `tests/unit/test_thread_hooks.py` fails if the copy here differs from it.

To add it:

1. In the project, open **Project settings > Environment** and note which
   cloud environment new threads use.
2. At [claude.ai/code](https://claude.ai/code), open the environment selector,
   the first control under the message box. Under **Cloud**, hover over that
   environment's row and select the settings icon on its right.
3. Select the **Setup script** row. Paste the script below at the end of what
   the box already holds, and select **Save changes**.

```bash
mkdir -p ~/.claude
python3 - <<'EOF' || true
import json, pathlib
path = pathlib.Path.home() / ".claude" / "settings.json"
try:
    data = json.loads(path.read_text())
except (OSError, ValueError):
    data = {}
group = {"hooks": [{"type": "command", "command": "test -f \"$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py\" && python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py\" || true"}]}
starts = data.setdefault("hooks", {}).setdefault("SessionStart", [])
if group not in starts:
    starts.append(group)
path.write_text(json.dumps(data, indent=2) + "\n")
EOF
```

Changes to the environment reach new threads, not the ones already running,
and saving the script rebuilds the environment's cache. To check that it
worked, ask a new thread to run `uv run pytest --version | head -1`. The
repository's `gate-status-guard.sh` refuses that command when the hooks are
loaded. If the thread prints a pytest version instead, the hooks are still off,
and the thread should record that in `PL-CR81`.

A plugin may replace this setup script. Plugins added in **Project settings >
Plugins** load into each new thread, and a plugin can carry hooks and skills.
This repository is a plugin marketplace with one test plugin, `thread-probe`,
in `.claude/thread-probe-plugin/`. `PL-XFDQ` records whether its hook and skill
reach a thread. Until it does, do not add both the plugin and this script to
one project, because a refusal in a thread could then come from either.
