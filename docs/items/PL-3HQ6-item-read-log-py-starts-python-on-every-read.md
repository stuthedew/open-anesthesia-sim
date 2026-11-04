---
id: PL-3HQ6
title: item_read_log.py starts Python on every Read, Grep and Glob call, about 50 ms each, never sees bin/docket show, and serves no open decision since PL-NB35 and PL-KM3X closed; retire it
priority: P3
effort: S
status: done
classes: perf
feature: guard-review-2026-11
milestone: v0.6.15
touches: .claude/hooks/item_read_log.py, tools/item_reads.py, tests/unit/test_item_read_log.py, .claude/settings.json, docs/apparatus.md, docket.toml, tests/unit/test_line_splits.py, subprojects/docket/src/docket/store.py, tests/unit/test_generator_check.py, ROADMAP.md, docs/items/PL-V9L3-the-working-method-write-up-states-the-dead.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: every Read, Grep and Glob call stops paying for a Python start that records a measurement nobody will read
verify: ! grep -qF 'item_read_log.py' .claude/settings.json
---

**Problem.** item_read_log.py starts Python on every Read, Grep and Glob call, about 50 ms each, never sees bin/docket show, and serves no open decision since PL-NB35 and PL-KM3X closed; retire it

**Why it matters.** The hook was built to measure whether sessions follow
citation edges between items, for two design arguments, `PL-KM3X` and
`PL-NB35`, both now closed. Sessions read items through `bin/docket show`,
which runs in Bash and which the hook never sees, so its log cannot answer the
question even if one were open. It costs a Python start on every Read, Grep and
Glob call. `CLAUDE.md` § "Prefer deterministic tooling over repeated model
work" retires a check that serves no decision.

**Done when.** `.claude/settings.json` wires no item-read hook, and
`.claude/hooks/item_read_log.py`, `tools/item_reads.py`, their test and their
mentions in `docs/apparatus.md` and `docket.toml` are gone.

**Generator check.** A one-off: a measurement that outlived its question.
