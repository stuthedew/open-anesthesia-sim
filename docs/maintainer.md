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

## Settings that make sessions cheaper

- `CLAUDE_CODE_SUBAGENT_MODEL` picks the model for exploration subagents.
  `CLAUDE.md` tells sessions to delegate broad codebase search to them; a
  small, fast model is appropriate, because their transcripts stay out of the
  main context and what they return is verified against the source anyway.
- Prefer starting a fresh session over compacting a long one. Compaction costs
  a summarization pass and drops the detail this repository's provenance and
  safety requirements depend on. `docs/items/` and `docs/WORKING_NOTES.md`
  exist so a new session can pick up cold.
