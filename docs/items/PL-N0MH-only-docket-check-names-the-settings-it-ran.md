---
id: PL-N0MH
title: Only docket check names the settings it ran under, so next, digest, status and list under --items are read under the wrong policy in silence
priority: P3
effort: S
status: done
classes: defect
feature: dev-tooling
milestone: v0.5.15
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docs/items/PL-QNYF-docket-check-errors-on-an-item-whose-closure.md
added: 2026-09-21
closed: 2026-09-27
pr: 1176
payoff: a command reading a store under settings that are not that store's own says so, so a band size or lane split judged against library defaults is visible rather than silent
verify: grep -q 'def test_next_names_the_settings_it_ran_under' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-25 PL-397Q withdrawn 2026-09-25 PL-397Q
---

**Problem.** Only docket check names the settings it ran under, so next, digest, status and list under --items are read under the wrong policy in silence

**Why it matters.** `docket check` names the settings it ran under as of
`PL-K5PW` (2026-09-21), so a store read under library defaults says so. Every
other command that calls `_load` does not. `docket next`, `digest`, `status`,
`list` and `trend` under `--items <a store below the root>` silently apply
library defaults to it, and the answers they give are wrong in the quiet
direction rather than the alarming one: a band size judged against the default
`top_band_limit` instead of the project's, a lane split judged against default
`process_classes`, a grooming advisory judged against a `verify_required_from`
the project never wrote. `PL-K5PW`'s 280 vocabulary errors were at least
visible. These are not.

**Where.** `cli._settings_source` already computes the answer and
`checks.Report.settings` already carries it; only `render.format_check` prints
it.

**Since `PL-NGBM` (2026-09-23), the settings reach every command.** Each
command resolves one `cli.Invocation`, whose `settings` field is the
`SettingsSource` that `_settings_source` computes, so `next`, `digest`,
`status`, `list` and `trend` already hold the answer and nothing is left to
thread. What remains is the print decision in the paragraph above: which of
those renderers says it, and whether a line on every `digest` earns its place. The question is which of the other renderers should, and whether a line on
every `digest` — which the session-start hook prints — earns its place, or
whether these commands should say it only when no config was found.

**Not the same problem as `PL-QNYF`.** `docket new` matched this filing to it
on 2026-09-21 and the match is wrong: `PL-QNYF` is `_check_closures` erroring
on a closure that landed in a queue-only commit, and naming no reachable
remedy. The two share `checks.py` and the words "docket check" in their titles,
and nothing else — different function, different failure, different fix. The
entry is withdrawn on that item rather than deleted, per the README's rule.

**Done when.** A command reading a store under settings that are not that
store's own says so, or it is recorded why `check` is the only one that needs
to.

**Built, 2026-09-27 - the render question answered.** Every command that loads
an item says so at its foot where no `docket.toml` was found, and none but
`check` names a config that was found. Three decisions, each the session's under
`.claude/rules/instruction-writing.md` rule 14:

- **Every store-reading command, not the five named.** 23 of the 27 commands
  load the store, most through several returns, so a line per renderer is the
  per-call-site drift `PL-NGBM`'s `Invocation` ended. `_load` marks the
  invocation once the store yields an item and `main` prints through
  `_say_settings` after the command answers; `branch`, `claim`, `yield` and
  `arm` load no store and say nothing. `check` is left out, its report naming
  the settings already. `test_every_store_read_in_the_cli_goes_through_load`
  fails a read that goes round `_load`.
- **The not-found case only.** `check`'s reason for naming the found case is
  that silence would be ambiguous. Once every other command names the
  not-found case their silence means a file was found, and the regression left
  - root resolution moving to a different file that exists - is caught by
  `check`, which pins the path on every `make check` and CI run. A found line on
  every `digest` would reach every session start and change no decision.
- **At the foot, beside the refs line.** Both say what bounds the answer rather
  than being any of it, and the foot keeps `next | head -3` reading the pick.
  An empty store yields no item, so its digest stays silent.
