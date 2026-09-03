---
id: PL-J49T
title: "Enforce the verify: command as an error when a grandfathered item is closed, so the burn-down stops depending on anyone reading an advisory"
status: needs-decision
priority: P3
effort: S
classes: infra, session-cost
touches: subprojects/docket/src/docket/checks.py, docket.toml, .claude/skills/docket/SKILL.md
added: 2026-09-03
---

**Problem.** 22 `ready` items predate `verify_required_from` and name no
`verify:` command. `PL-5YK8` narrowed the resulting advisory to the one or two
items `docket next` is about to offer, which fixed the nag. It did not make
the burn-down happen: the advisory still only *asks*, and nothing detects an
item leaving the grandfathered set without gaining a command. The set shrinks
when a session chooses to read three lines of `make check` output and act.

**Why it matters.** `CLAUDE.md` says to find the decidable part of a mechanism
and put it in code, and not to script the judgment. This advisory has both
halves tangled into one signal:

- *Judgment*: what the command should be. Unscriptable, and `PL-5YK8`
  established why - a command written away from its work is wrong, which all
  six wrong ones in this store's history demonstrate.
- *Decidable*: whether a closed item carries one. A yes/no on a frontmatter
  field.

The decidable half is currently delivered as prose that repeats every run and
works only if read. Demonstrated on 2026-09-03: a session filtering
`make check` through `grep` for summary lines read "1 advisory" across several
runs without reading the advisory, while the item count moved 116 to 118. The
content had not changed, so nothing was lost - but the method would not have
noticed if it had, which is the failure mode `CLAUDE.md` predicts and this is
an instance of it.

**Decision needed.** Whether closing an item should require the field, and how
strictly:

1. **Error at close.** `docket check` fails when an item reaches `done`
   without a `verify:` and without a `not-delegable:` reason. Exact, fires
   once, and fires at the only moment the judgment is available - the work is
   in hand and what proved it is known. This *completes* `PL-5YK8` rather than
   reversing it: that item narrowed the nag, this makes the rule exact. The
   advisory then becomes a courtesy rather than the mechanism.
2. **Error at close, grandfathered items exempt.** Preserves the current
   promise exactly and changes nothing for the 22, which is also to say it
   fixes nothing.
3. **Leave it.** The advisory is narrow and the set is shrinking on its own -
   39 on 2026-08-31, 22 on 2026-09-03. It may drain before the enforcement is
   worth building.

Option 1 is the one worth arguing for, with the caveat that it is a **policy
change rather than a defect fix**: it makes a rule stricter at a moment where
nothing is currently refused, so it is the project owner's to take. The
`not-delegable:` escape already exists for work no command can prove, which is
what keeps option 1 from being a trap.

**Where.** `subprojects/docket/src/docket/checks.py` raises the advisory;
`verify_required_from` in `docket.toml` sets the cutover;
`.claude/skills/docket/SKILL.md` documents the at-start burn-down.

**Done when.** The decision is recorded. If it is option 1 or 2, closing an
item without a command fails `docket check` with a message naming the field
and the `not-delegable:` alternative, and a test covers both the refusal and
the escape.

**Found.** 2026-09-03, by the project owner, asking whether an advisory being
behavioural is itself the defect when the thing it guards is decidable.
