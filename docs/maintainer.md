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
- anything within the scope of `CLAUDE.md`'s "Safety-critical
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
- Prefer starting a fresh session over compacting a long one. Compaction costs
  a summarization pass and drops the detail this repository's provenance and
  safety requirements depend on. `docs/items/` and `docs/WORKING_NOTES.md`
  exist so a new session can pick up cold.
