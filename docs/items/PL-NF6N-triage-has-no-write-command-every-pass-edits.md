---
id: PL-NF6N
title: Triage has no write command: every pass edits item front matter by hand, which is the decidable half CLAUDE.md asks to be moved into code
status: untriaged
added: 2026-09-12
---

**Problem.** Triage has no write command: every pass edits item front matter by hand, which is the decidable half CLAUDE.md asks to be moved into code

**What this pass actually did.** Triaging 46 captures meant setting `priority`,
`effort`, `classes`, `touches`, `feature` and often `status` and `verify` on 46
files. `bin/docket` has `new`, which writes the capture, and `triage`, which
*prints* what is unset and the rules the answers must satisfy - and then nothing.
The answers go in by hand, one file at a time.

**Why that is the shape `CLAUDE.md` asks to be moved into code.** The judgment -
what an item is worth, how big it is, what it belongs with - is exactly the half
a tool must not guess at, and none of this proposes it should. What is decidable
is everything around it: the field order in the front matter, that `classes` is
comma-separated, that a value is in `known_classes`, that setting `status: ready`
without `verify:` will fail `docket check`, that `dropped` needs `reason` and
`closed`. A session currently re-derives that from the file it is looking at, and
a mistake surfaces only when `docket check` runs.

**Evidence it recurs rather than being a one-off.** This pass wrote a throwaway
script to do it and threw it away, which is the `PL-ZG5J` pattern - the fourth
session to build the same scaffolding. Triage is a standing mode in the skill,
the digest raises untriaged counts in every session, and `untriaged_stale_days`
exists because the pile is expected to recur.

**What it would look like.** `bin/docket set <id> priority=P2 effort=S ...`,
validating each field against `docket.toml`'s own vocabulary and refusing an
unknown key, writing the front matter in the canonical order. `docket new`
already owns the write path, so the store-writing half exists.

**The gate this has to pass first.** `CLAUDE.md`: build where the work recurs
*and* the answer is deterministic, and not where upkeep would cost more than the
passes it saves. The argument against is that a session can edit a markdown file
perfectly well and the command is a thin wrapper over that. The argument for is
that the wrapper is where the validation lives, and that the errors it would
prevent are currently found by a checker one step later. Decide that before
building it.
