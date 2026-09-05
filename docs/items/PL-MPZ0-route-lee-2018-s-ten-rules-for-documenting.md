---
id: PL-MPZ0
title: Route Lee 2018's ten rules for documenting scientific software into this repository's standards, adopting only the rules that are not already practice here
priority: P2
effort: M
status: done
classes: docs, planning
feature: documentation-standard
touches: .claude/rules/expert-review.md
added: 2026-09-05
closed: 2026-09-05
verify: python3 tools/doc_check.py check && grep -qF 'What a docstring and an error message owe a reader' .claude/rules/expert-review.md
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
| 1. Comment as you code | Coverage is near-total: every module and class under `src/` carries a docstring and 160 of 172 public functions do | Already practice |
| 2. Examples, doubling as tests | `tests/reference/test_published_wash_in.py` is the paper's own recommendation, against Yasuda et al. rather than against the code | Already practice |
| 3. Quickstart | README carries Requirements, Setup, Running and Development | Owned by `PL-N092`, behind the README freeze |
| 4. README basics | Install, test, license, docs map and per-target `make` descriptions all present | Already practice |
| 5. CLI help | `bin/docket --help` lists 20 subcommands with a one-line description each, and every subcommand has its own | Already practice |
| 6. Version-controlled documentation | Documentation is in-repo; `docs/MODEL.md` § Status is deliberately version-generic and says why, and `check_baseline` enforces that no second copy of the current version exists | Already practice, and better reasoned than the paper's advice |
| 7. Document the API: inputs, outputs, errors | Strict mypy settles inputs and outputs. Errors are prose and missing in 8 of 23 public raising functions | → `.claude/rules/expert-review.md`, `PL-HXKC`, `PL-GZPX` |
| 8. Generated documentation site | None, and no external API consumer to serve one to | Declined |
| 9. Error messages that carry state and a fix | Split: `core/supported_ranges.py` is exemplary, `core/validation.py` names the parameter and nothing else | → `.claude/rules/expert-review.md`, `PL-T137` |
| 10. Say how to cite the software | Absent when this audit ran against `af1804b`; `PL-8DDG` landed `CITATION.cff` as #338 while this branch was open | Already practice, concurrently |

**Rule 1 is already practice, and two drafts of this item said otherwise before
the project owner corrected each.** Both errors are recorded because the second
is easy to repeat.

The first declined rule 1 citing the *apparatus* side of `CLAUDE.md`'s two
standards — "polishing it past sufficient", the resident instruction total,
`PL-JK0M` — for a rule that governs `src/` and `tests/`, which are the product
side. That is the wrong half of a split `CLAUDE.md` draws deliberately, and
`PL-6SBB` is the scoping fix that came out of it.

The second declined it citing `PL-XXBD`, reading that item as asking for fewer
comments. It does not. `PL-XXBD` asks that each comment communicate
efficiently — fluff is the defect — which is a claim about how a comment is
*written*, not about how many exist. The two are independent axes, and Lee's
rule 1 is on the coverage one: comment as you code, land in the Goldilocks
zone. Measured 2026-09-05, that is met — every module and class under `src/`
carries a docstring and 160 of 172 public functions do — so "when in doubt, err
on the side of more" has almost no doubt left to arbitrate. Nothing in it
argues against `PL-XXBD`; Lee makes the same point himself, that readers "will
get lost in the sea of comments".

So there is nothing in rule 1 to adopt and nothing to decline.

**Rule 8** asks for Sphinx or an equivalent site, and is the one genuine
decline. Its verification half — doctest, examples that run — is the valuable
part and is already covered by `tests/reference/` against published data; the
site half is apparatus for an audience that does not exist.

**Why it matters.** The paper is the project owner's standing guide, and a
guide nobody has audited against the tree is either ignored or adopted whole.
Adopting whole is the expensive failure: ten rules of resident prose, most of
them describing what this repository already does, which is exactly the growth
`CLAUDE.md`'s routing rule exists to stop. The audit is what lets the guide act
on the two places it changes something and stay silent everywhere else.

**Where.** `.claude/rules/expert-review.md` § "What a docstring and an error
message owe a reader", added 2026-09-05. Path-scoped to `src/**`, `docs/**` and
`tests/**`, so it loads when a session opens the simulator and costs nothing
resident — `doc_check.py` confirms the resident total unchanged at 548 lines.

**Done when.** Done: the audit is this item, the two adopted rules are in
`expert-review.md`, and the gaps are filed as `PL-HXKC`, `PL-T137` and
`PL-GZPX`. `PL-BFV8` was the fourth and is dropped as a duplicate of `PL-8DDG`,
which landed the citation file from a concurrent session reading the same
paper. Close on triage.
