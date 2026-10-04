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

- **As of 2026-09-19 the strongest available model is Claude Fable 5.1**
  (`claude-fable-5-1`) — what `use your strongest model` is asking for. The
  project owner confirmed on 2026-09-19 that Fable is stronger than Opus,
  which is what settles it against the assumption a session running Claude
  Opus 5 would otherwise make: that whatever it is already on satisfies the
  flag. Claude Opus 5 (`claude-opus-5`) is the step below and the right
  substitute when Fable is unavailable.
- **As of 2026-09-19 `delegable` means Claude Sonnet 5** (`claude-sonnet-5`)
  — *not* Claude Haiku 4.5, and one named tier rather than a choice between
  two. The project owner asked for a cheap-model offer on clear-cut items and
  specified the asymmetry it must have (2026-09-19): *"I'd rather err on the
  side of default opus if any question and miss items that could have been
  safe with a lower model than try to catch every lower model opportunity and
  find out later I should have actually used opus."* Naming one tier follows
  from that and is this session's reading of it rather than their own words —
  a second tier would reinstate, at the moment of reading, exactly the
  per-item judgment the asymmetry exists to remove.

Three facts decide Sonnet over Haiku, and none of them is a preference:

1. **Haiku 4.5 is a generation behind.** Claude Opus 5 and Claude Sonnet 5
   are the Claude 5 family; Haiku 4.5 is not. A delegated item here is a real
   defect with a real fix — `bin/docket delegable` currently offers 141 of
   them — not a typo sweep.
2. **Haiku 4.5's context window is 200K against the others' 1M.**
   `CLAUDE.md` budgets 150,000 tokens of *spend* on top of whatever a session
   starts with, and that baseline measured 81,048 bare and 115,320 with the
   `docket` skill loaded (`PL-W80S`, 2026-09-21). A session spending its whole
   budget therefore ends around 231K–265K of context: **past Haiku's entire
   window before it reaches the hand-off**, and about a quarter of Sonnet's.
   This line previously read "roughly 50K of headroom on Haiku", which the
   2026-09-21 re-anchoring of the budget to spend made backwards rather than
   merely stale. The resident instruction set alone measured 2.5–5.6% of the
   contexts seven concurrent sessions carried on 2026-09-19 (`PL-H253`).
3. **Haiku 4.5 does not take the effort parameter**, so § "Match effort to
   the standard the work is held to" below — open apparatus sessions at
   `high` — cannot be honoured on a Haiku session at all. The lever this file
   spends a section on does not exist there.

And the saving barely differs: at first-party API rates Claude Sonnet 5 costs
$2/$10 per 1M tokens against Claude Opus 5's $5/$25 and Haiku 4.5's $1/$5, so
moving to Sonnet already captures **75%** of the largest saving available.
The remaining 25% is what the three costs above would be bought with.

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
cannot change its own. Claude Code's documented default is `high`.

**Open apparatus sessions at `high` and simulator sessions at `max`** (project
owner, 2026-09-19, ratified, over running every session at `max`). The split
follows the two standards `CLAUDE.md` already draws rather than a new
judgment: `.claude/rules/apparatus-standard.md` governs `subprojects/docket/`,
`tools/`, `.claude/`, `.github/` and `docs/worker.md`, and asks for working
reliably rather than for specialist quality; `src/`, `tests/`, `docs/MODEL.md`
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
- `CLAUDE_CODE_SUBAGENT_MODEL` picks the model for exploration subagents.
  `CLAUDE.md` tells sessions to delegate broad codebase search to them; a
  small, fast model is appropriate, because their transcripts stay out of the
  main context and what they return is verified against the source anyway.
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

## Read a simulator change before you arm it

`bin/docket arm` holds a pull request for your read where it changes `src/`,
`tests/` outside `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/`
or `README.md` - the paths where a wrong clinical value could reach the screen
- or `.github/workflows/`, `.claude/hooks/` and
`subprojects/docket/src/docket/arming.py`, which decide what merges and what
is tagged and could loosen the rule (the Projects trial's instructions,
2026-10-03, kind unrecorded, over holding every path outside `docs/items/`,
`docs/pr-bodies/` and `subprojects/docket/`; the workflows and hooks project
owner, 2026-10-03, ratified, over leaving them armed on green; built by
`PL-KKHD`). A session leaves a held pull
request unarmed, asks for the read with the plain-language summary `arm`
prints under the hold (`PL-8XQS`), and merges it on your word alone - "Merge
it" - by the route § "Bring a stale base in when you merge, with Update
branch" describes. Every other change arms on green: the store, the body
records (`PL-979D`) and the queue's tooling as before (project owner,
2026-09-25, ratified, over holding every path outside `docs/items/`,
`PL-SQTR`; built by `PL-K6B2`), and since 2026-10-03 `CLAUDE.md`, `ROADMAP.md`,
`tools/`, the rest of `.claude/` and `.github/`, and everything else. `arm` names the paths
outside the store it armed, so the session's report carries the reason the
old hold would have given, and the session still holds a change it judges
raises a question for you, whatever path it is on. The old hold fired on
every change outside the store, and you confirmed on 2026-09-25 that those
holds were being clicked through, so it was guarding nothing; `PL-CBDX` reads
the diffs merged unread since 2026-09-23.

Two answers of 2026-10-03, recorded so that the list reads as decided rather
than defaulted. `ROADMAP.md` and `docs/WORKING_NOTES.md` arm on green, where
`PL-0JGZ` (project owner, 2026-09-26, ratified) had held them because the
roadmap is where you set direction: your list reopened it, and you settled it
so (project owner, 2026-10-03, ratified, over holding them as before,
`PL-KKHD`). `.github/workflows/` and `.claude/hooks/` joined the list, since
`update-armed.yml`, `tag-release.yml` and `direct-merge-guard.sh` decide
merges and tags as `arming.py` does, at about one read a day lately (project
owner, 2026-10-03, ratified, over leaving them armed on green, `PL-KKHD`).

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

If a check fails after the update, the branch and the new `main` do not work
together. That is the merge skew the setting now stops at the pull request
instead of on `main`. Leave auto-merge armed and ask a session to fix the
branch; auto-merge lands it once the fix is green. If the merge box shows
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
