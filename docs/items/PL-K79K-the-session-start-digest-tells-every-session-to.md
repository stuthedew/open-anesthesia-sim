---
id: PL-K79K
title: The session-start digest tells every session to run `bin/docket triage`, which does not exist
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.2.6
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-08-30
closed: 2026-08-30
commit: 54bdb5b
verify: uv run pytest subprojects/docket/tests -k triage
---

**Problem.** `render.py`'s digest emits "`bin/docket triage` to fold them into
the queue" whenever anything is untriaged, and no `triage` subcommand exists.
Every session that starts with an untriaged item is told at startup to run a
command that errors.

**Why it matters.** `defect`, not `infra`: this is a live mechanism `main`
depends on that does not work, which is the distinction `ROADMAP.md`'s "The
debt gate" draws explicitly under "What counts" — an unbuilt tooling idea
costs nothing to carry, a half-working mechanism the project already runs on
charges interest every session. The digest is the one piece of text every
session reads before doing anything, so an instruction in it that fails is the
most expensive kind of wrong: it costs a turn, and it teaches a session to
distrust the digest.

**Where.** `subprojects/docket/src/docket/render.py:132` emits the line;
`cli.py` holds the subcommands.

**Scope: a worklist and its constraints, not a decision-maker.** For each
untriaged item, print the body, the fields still unset, the brief sections
still missing, and the constraints that bind the answer — read from `Config`
and the checker rather than restated, so the rules cannot drift from what
`docket check` will say afterwards:

- a `safety`/`science` class forces `P0`/`P1`, since `checks.py` rejects
  `P2`/`P3` for them;
- how many of `top_band_limit` the top band already holds;
- which classes count as `process_classes`;
- which `protected_paths` would make the item non-delegable if `touches`
  names them;
- that an item set to `ready` must name a `verify:` command or record why
  none can (PL-G049).

It must not choose priority, effort, classes or feature. That is judgment and
it stays with the session. The point is that the session applies the rules
with them in front of it, instead of loading the skill to recall them and
finding out from `docket check` afterwards whether it guessed right — see
`CLAUDE.md`, "Prefer deterministic tooling over repeated model work", on
summarizing counts rather than only deciding.

**Done when.** `bin/docket triage` runs, prints every untriaged item with what
is unset and what constrains it, decides nothing, and the digest's line is
true.
