# Notes for the project owner

Everything here is addressed to the person running the sessions, not to the
sessions themselves. It lives outside `CLAUDE.md` for that reason: a rule a
session cannot act on still costs every session the context to read it.
`docs/worker.md` is the opposite document — instructions to a worker agent.

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
  (`/compact keep the open question about X`); `/clear` does not. Start a
  fresh session for an unrelated topic instead: that is where a clean prompt
  beats a carried conversation.

## Read a simulator change before you arm it

`bin/docket arm` answers `arm` for a pull request whose every changed path is
under `docs/items/`, `docs/pr-bodies/` (`PL-979D`) or `subprojects/docket/`, so
a session arms it and it merges on green with no read from you. It holds
everything else for your read, and a change to
`subprojects/docket/src/docket/arming.py` as well, although that file is under
`subprojects/docket/`: it is the gate itself, and a change to it could loosen
the rule (project owner, 2026-09-25, ratified, over holding every pull request
that changes anything outside `docs/items/`, `PL-SQTR`; built by `PL-K6B2`). A
session leaves a held pull request unarmed. Read it before you arm it, most
closely where it changes `src/`, `tests/` outside `subprojects/`,
`docs/MODEL.md`, `src/anesthesia_sim/data/` or `README.md`, where a wrong
clinical value could reach the screen. The old hold fired on every docket
change as well, and on 2026-09-25 you confirmed those holds were being clicked
through, so it was guarding nothing. `PL-CBDX` reads the diffs merged unread
since 2026-09-23.

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
   auto-merge**. Leave **Merge without waiting for requirements to be met
   (bypass branch protections)** unticked. It is offered because `main`'s
   required checks bind non-admins only, and ticking it merges on the stale
   base, the merge skew the setting exists to stop. It stays as your escape
   hatch for a broken CI, not a route for ordinary merges.
3. Come back in about five minutes. Success is the pull request marked
   **Merged**. If the merge box offers **Update branch** again, another pull
   request landed first: click it again and come back in another five.

With several ready at once, arm auto-merge on each, but update one at a time,
and the next only once the previous has merged. Updating them together runs CI
on every one, and each merge sends the rest behind again.

If a check fails after the update, the branch and the new `main` do not work
together. That is the merge skew the setting now stops at the pull request
instead of on `main`. Leave auto-merge armed and ask a session to fix the
branch; auto-merge lands it once the fix is green. If the merge box shows
conflicts and no Update branch, do not use **Resolve conflicts**. Ask a
session to merge `main` in and resolve them.

Instead of steps 1 to 3, you can ask the session that opened the pull request
to merge it: it arms auto-merge and brings the base in itself, with the same
merge the button makes. GitHub never updates an armed pull request that falls
behind, so one whose session has ended waits for you. A captures-only pull
request is the usual case, and `PL-S5MF` holds the question of what should
pick it up instead. **A pull request already green and current is the
exception: the session tells you it cannot arm it, and the Squash and merge is
yours** (project owner, 2026-09-26, ratified, over the session merging it
directly through the API, `PL-V2X5`). GitHub offers auto-merge "only on pull
requests that cannot be merged immediately" ([GitHub
Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)),
and a session merges only by arming, because its GitHub calls are yours and an
admin's merge passes the up-to-date check `main` holds everyone else to:
merging directly, it would land a stale branch whenever another pull request
merged between its read and its call. Merge it on the Mac, as step 1 says for
a branch that is already current.

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
