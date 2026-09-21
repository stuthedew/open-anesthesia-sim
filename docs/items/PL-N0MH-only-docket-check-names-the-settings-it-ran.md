---
id: PL-N0MH
title: Only docket check names the settings it ran under, so next, digest, status and list under --items are read under the wrong policy in silence
status: untriaged
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, docs/items/PL-QNYF-docket-check-errors-on-an-item-whose-closure.md
added: 2026-09-21
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
it. The question is which of the other renderers should, and whether a line on
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
