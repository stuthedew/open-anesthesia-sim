---
id: PL-6WPD
title: bin/docket set --touches says nothing about whether the paths it writes owe a Generator check, so a capture triage marks undecided (12 of 22 on 2026-09-28) is decided by reading workflow_paths in docket.toml by hand, at the moment the question is likeliest to be skipped
status: untriaged
feature: generator-identification
added: 2026-09-28
---

**Problem.** bin/docket set --touches says nothing about whether the paths it writes owe a Generator check, so a capture triage marks undecided (12 of 22 on 2026-09-28) is decided by reading workflow_paths in docket.toml by hand, at the moment the question is likeliest to be skipped

**Found closing `PL-4NZ7`, 2026-09-28.** `bin/docket triage` now marks each
untriaged item whose `touches` name a `workflow_paths` path as owing a
Generator check, and says `undecided until touches is set` where capture left
them unset. But a triage pass usually writes `touches` and `--status ready` in
one `bin/docket set` call, after which the item has left the triage list, so
the mark for those twelve never prints: the session has to hold the rule and
check each path against the 60-entry list itself. A line from `set` naming the
declared paths under `workflow_paths`, where the brief carries no
`**Generator check.**` line (`checks.answers_generator_check`), would put the
answer where the paths are written. Captured, not built: `generator: live` items
are open, and this is new identification machinery for triage to rank.
