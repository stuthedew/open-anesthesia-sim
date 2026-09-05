---
id: PL-MPZ0
title: Route Lee 2018's ten rules for documenting scientific software into this repository's standards, adopting only the rules that are not already practice here
status: untriaged
feature: documentation-standard
touches: .claude/rules/expert-review.md
added: 2026-09-05
---

**Problem.** The project owner supplied Lee BD, *Ten simple rules for
documenting scientific software* (PLoS Comput Biol. 2018;14(12):e1006561,
doi:10.1371/journal.pcbi.1006561) to be used as a standing guide "as
applicable". Adopting ten rules wholesale into a repository that already meets
most of them would add resident prose without changing a single decision, which
is the failure `CLAUDE.md`'s routing rule exists to stop. So the rules were
audited one at a time against the tree, and only the gaps were routed.

**The audit, 2026-09-05.**

| Rule | State here | Disposition |
| --- | --- | --- |
| 1. Comment as you code | Exceeded. `Makefile` and `pyproject.toml` carry measurement and reasoning inline; the 548-line resident total and `PL-H7XN`, which `CLAUDE.md` cites for the routing rule, are the standing pressure in the other direction | Declined as written — see below |
| 2. Examples, doubling as tests | `tests/reference/test_published_wash_in.py` is the paper's own recommendation, against Yasuda et al. rather than against the code | Already practice |
| 3. Quickstart | README carries Requirements, Setup, Running and Development | Owned by `PL-N092`, behind the README freeze |
| 4. README basics | Install, test, license, docs map and per-target `make` descriptions all present; how to cite is not | Citation half → `PL-BFV8` |
| 5. CLI help | `bin/docket --help` lists 20 subcommands with a one-line description each, and every subcommand has its own | Already practice |
| 6. Version-controlled documentation | Documentation is in-repo; `docs/MODEL.md` § Status is deliberately version-generic and says why, and `check_baseline` enforces that no second copy of the current version exists | Already practice, and better reasoned than the paper's advice |
| 7. Document the API: inputs, outputs, errors | Strict mypy settles inputs and outputs. Errors are prose and missing in 8 of 23 public raising functions | → `.claude/rules/expert-review.md`, `PL-HXKC`, `PL-GZPX` |
| 8. Generated documentation site | None, and no external API consumer to serve one to | Declined |
| 9. Error messages that carry state and a fix | Split: `core/supported_ranges.py` is exemplary, `core/validation.py` names the parameter and nothing else | → `.claude/rules/expert-review.md`, `PL-T137` |
| 10. Say how to cite the software | Absent entirely — no `CITATION.cff`, no DOI | → `PL-BFV8` |

**Why rules 1 and 8 are declined rather than deferred.** Rule 1's advice is to
err toward more comments. That advice is calibrated for the paper's stated
audience — biologists with no software training — and inverting this
repository's actual failure mode is not a neutral cost: `CLAUDE.md` holds the
workflow apparatus to staying streamlined, and the resident instruction total
is measured on every run precisely because prose accretes. Rule 8 asks for
Sphinx or an equivalent site. Its verification half — doctest, examples that
run — is the valuable part and is already covered by `tests/reference/` against
published data; the site half is apparatus for an audience that does not exist.

**Where.** `.claude/rules/expert-review.md` § "What a docstring and an error
message owe a reader", added 2026-09-05. Path-scoped to `src/**`, `docs/**` and
`tests/**`, so it loads when a session opens the simulator and costs nothing
resident — `doc_check.py` confirms the resident total unchanged at 548 lines.

**Done when.** Done: the audit is this item, the two adopted rules are in
`expert-review.md`, and the four gaps are filed as `PL-HXKC`, `PL-T137`,
`PL-GZPX` and `PL-BFV8`. Close on triage.
