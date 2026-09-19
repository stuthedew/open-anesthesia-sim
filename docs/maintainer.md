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
session.

Claude Code's `opusplan` mode is a reasonable default for that split, with two
caveats:

1. It returns to the cheaper model for execution, so the strong-model review
   of a safety-critical diff is a deliberate step, not an automatic one.
2. Switching models mid-session starts a cold cache, so group design and
   execution into runs rather than alternating between them.

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
