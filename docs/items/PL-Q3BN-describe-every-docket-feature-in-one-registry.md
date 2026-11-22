---
id: PL-Q3BN
title: Describe every docket feature in one registry, show each description in status and feature, and refuse an item whose feature is not listed
status: untriaged
feature: feature-registry
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_config.py, docs/features.toml, docket.toml, .claude/skills/docket/modes/capture.md
added: 2026-11-22
---

**Problem.** Describe every docket feature in one registry, show each description in status and feature, and refuse an item whose feature is not listed

A docket feature is only the free-text `feature:` field on an item. Nothing in
the repository says what any of the 211 names in use covers, so a session
filing an item guesses which group it joins from the name alone, and a reader
of `bin/docket status` sees a list of names with no meaning attached. GitHub
and GitLab both keep labels as a registry, one name and one short description
each
([GitHub](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels),
[GitLab](https://docs.gitlab.com/user/project/labels)).

The project owner said yes to building it (project owner, 2026-11-22, on the
coordinator's proposal).

**Build.**

1. One registry file listing every feature any item carries, each with a
   one-line plain description of what belongs in it, written from its items.
2. `bin/docket status` and `bin/docket feature` print the description beside
   the name.
3. `bin/docket check` refuses an item whose feature is not in the registry.

**Approach.** The registry is `docs/features.toml`, one `name = "description"`
line per feature, named by a new `features_file` key in `docket.toml`. It is a
file of its own, not a table in `docket.toml`, because every new feature adds a
line to it and `docket.toml` is one of the `gate_paths` that mark a delegated
diff as having edited its own checks. The package default is empty, which
turns the check off and prints no descriptions, so a project that keeps no
registry sees no change. The check applies to closed items as well as open
ones: the registry describes every name in use, and `bin/docket feature` on a
finished feature should still say what it was.

`bin/docket new` refuses an unlisted feature with nothing written, and `bin/docket
set` already refuses a write that adds a check error, so the registry line comes
first. `bin/docket status` prints the description under each underway and
unstarted feature only. Its "Finished" line stays a list of names, because 150
descriptions there would bury the open work.

**Generator check.** None: this is new work the project owner asked for, not a
repair of a defect that recurs.

**Consolidation.** The project owner asked to combine features where
appropriate (project owner, 2026-11-22). Each merge below folds a name into
one that already describes the same completing goal, and retags every item
carrying the folded name, closed items included, so `bin/docket feature` keeps
one history per group. Retired names, and names the project's Order cites,
stay as they are. Release notes that name a folded feature stay as written,
because they record what a past release finished. Each target's description
is widened to cover what it took in, and each folded name stays in the
registry as a redirect to its target. The retagging waited for the triage pull
requests #2203 and #2208, which held most open items. 58 names fold, and 211
names become 153.

| Folded name | Into |
| --- | --- |
| `verify-assertion-check` | `verify-false-reject` |
| `verify-assertion-evidence` | `verify-false-reject` |
| `verify-close-out` | `verify-false-reject` |
| `verify-command-meaning` | `verify-command-health` |
| `sentinel-verify-commands` | `verify-command-health` |
| `replay-hermeticity` | `verify-command-health` |
| `verify-invalidation` | `verify-command-health` |
| `stranded-ahead-or-behind` | `stranded-report-fidelity` |
| `unmerged-item-edits` | `stranded-report-fidelity` |
| `stranded-triage-sweep` | `stranded-recovery` |
| `landing-deletions` | `landed-elsewhere` |
| `carrier-collapse` | `carrier-detection` |
| `inflight-verdict` | `carrier-detection` |
| `claim-integrity` | `claim-record` |
| `gate-disposition-store` | `gate-list-integrity` |
| `gate-remaining-cost` | `gate-prerequisites` |
| `generator-machinery-rank` | `generator-identification` |
| `generator-measurement` | `generator-heads` |
| `guard-tool-names` | `guards-keyed-on-the-action` |
| `gate-status-guard` | `bash-guard-bound` |
| `owner-ask-refusals` | `owner-ask-by-state` |
| `tag-error-names-its-cause` | `doc-consistency-checks` |
| `required-check-trigger-reading` | `reader-checks` |
| `shell-reads-as-bash` | `reader-checks` |
| `one-id-grammar` | `read-facts-through-docket` |
| `git-silence-channel` | `evidence-declines` |
| `remote-copy` | `one-snapshot` |
| `refresh-before-reporting` | `one-snapshot` |
| `cut-backfills-pr-numbers` | `commit-provenance` |
| `model-requirements-tested` | `model-claims-held-by-tests` |
| `model-boundary-statements` | `model-spec-accuracy` |
| `delivery-semantics` | `model-spec-accuracy` |
| `circuit-boundary-docs` | `model-spec-accuracy` |
| `mac-awake-reference-text` | `model-spec-accuracy` |
| `late-washout-evidence` | `validation-resolving-power` |
| `test-effectiveness-measurement` | `tests-detect-wrong-values` |
| `mutation-run-first-step` | `tests-detect-wrong-values` |
| `dead-test-limits` | `tests-detect-wrong-values` |
| `two-change-run-has-two-changes` | `unit-test-review` |
| `numbers-outside-their-valid-range` | `floating-point-domain` |
| `one-home-for-constants` | `one-source-of-truth` |
| `interface-provenance-adoptions` | `interface-areas` |
| `area-layout-sizing` | `interface-areas` |
| `layout-sliver-areas` | `interface-areas` |
| `interface-pass-narrative` | `interface-pass-design-round` |
| `compartment-trace-legibility` | `chart-readout` |
| `supported-run-length-text` | `presentation-safety` |
| `platform-palette` | `chrome-colour-audit` |
| `branch-run-set-integrity` | `scenario-branching` |
| `reset-aftermath` | `scenario-branching` |
| `resident-gauge-basis` | `instruction-staleness-audit` |
| `repo-copy-edit` | `copy-editor` |
| `reader-first-prose` | `prose-quality` |
| `stale-blocked-routing` | `blocked-means-blocked` |
| `api-credit-runs` | `worker-runs` |
| `model-capability-routing` | `model-evidence` |
| `open-item-overlap-detection` | `recurrence-signal` |
| `settings-panel-prerequisite` | `preferences-store` |
