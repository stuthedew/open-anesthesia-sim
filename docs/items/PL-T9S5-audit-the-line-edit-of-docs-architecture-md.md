---
id: PL-T9S5
title: Audit the line edit of docs/ARCHITECTURE.md (#2044) section by section for dropped statements, qualifiers, requirements and reasons, as PL-B7V7 did for the machine docs, and restore each: #2044 was checked only for dropped names, numbers and item ids, the same gap that lost statements in the MODEL.md, machine-doc and interface-provenance edits
status: done
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
added: 2026-11-07
closed: 2026-11-07
pr: 2056
verify: grep -q 'Three rules rest on this layering' docs/ARCHITECTURE.md && grep -q 'Forgetting is the only way that a boundary' docs/ARCHITECTURE.md
---

**Problem.** Audit the line edit of `docs/ARCHITECTURE.md` (`#2044`) section by section for dropped statements, qualifiers, requirements and reasons, as `PL-B7V7` did for the machine documents, and restore each.

**Why.** `#2044` (`PL-KGY1`) line-edited every section of `docs/ARCHITECTURE.md` with the copy editor. It was checked only for dropped names, numbers and item ids. Its pull request says that every module, function and file name dropped from one place is still given elsewhere, and that only eight item ids and four dates left the document. Nothing compared statements. On `docs/MODEL.md` the same check passed while about 120 statements were lost or weakened (`PL-95SW`), and the machine documents (`PL-B7V7`) and `docs/interface-provenance.md` (`PL-S6WZ`) lost statements the same way.

**How.** This runs before the restructure, `PL-SVGH`, on the same branch. The line edit kept every heading, so each section can be compared with its own text before the edit (`3bbcd8e4^`, the fork of `#2044`), and the restructure's findings cite rows of that older text. Split the document at its headings, before and after `#2044`. For each section the edit changed, have a reviewer list every statement, qualifier, requirement ("must", "only", "never"), scope limit or stated reason present in the old text and missing or weaker in the new, quoting both, with the brief the `PL-95SW` audit used (`/mnt/project-files/v0.7.0/repo-copy-edit/audit-BRIEF.md`). Restore each finding in place. Put a section back to its earlier wording where it lost three or more. Decision history that `PL-SVGH` would cut anyway is recorded as a finding and left out.

**Done when.** Every section `#2044` changed has been compared, and each statement the comparison found missing or weakened is back, or is recorded here as one the restructure cuts on purpose, with the reason.

**Generator check.** One mechanism, the copy editor dropping requirements, qualifiers and reasons, caused these losses. It is filed as `PL-F0Q2`.

**What was found.** Four review agents compared each of the fourteen sections with its text before `#2044`, and a fifth read the other way, for facts the edit had added. Six sections had lost three or more statements, qualifiers or reasons:

- § "Layering": the three rules that rest on the layering, and the first of them, that simulation code stays independent of the UI toolkit; the reason the list of View kinds lives in `app/` (the `layout/` package holds none); that `.claude/rules/ui-calculations.md` loads with every file under `app/`; the data-file half of the third rule.
- § "Data flow": that a control mark is a third kind of chart series; why the drawn-value boundary is a type ("forgetting is the only way that a boundary stated in prose is ever crossed"); that the four setters are the four the interface offers and no fifth exists; why `app/chart_frame.py` is a layer of its own; four bold leads.
- § "What a branch is, and what it shares with its parent": that a branch's guarantees are stated in one place only; the pointer to which keyframe a branch uses; that sharing nothing is what lets both runs advance; that one test decides both that the marks are inherited and that the timeline is not; that the keyframe-at-the-halt route was measured and refused.
- § "How a learner takes one, and how a comparison ends": the selector's second kind of row became "each mark", which wrongly takes in MAC targets; which method offers the paused point and which takes it; the guarantee for any two controls labelled with one instant; that ordinary evidence suffices because the agent-lock decision was ratified, not specified.
- § "What a branch comparison asserts, and which part of it is structural": four statements, among them the warning against generalising the drawing into a wider facility and that the inheritance list is the audit of the claim.
- § "Where new code belongs": the path scope of `.claude/rules/ui-areas.md`; why the two placement rules carry over to Views; that `ChartFrame.visible` itself holds the narrowed selection; why a new trace declares no width.

Five sections lost one or two: § "Architecture overview" (that the document is a map, not a scientific specification), § "Data files" (that the script gates nothing by the owner's decision), the two User state chapters (the Blender precedents for when each file is saved), § "Dependencies" (that the import check, not the dependency list, keeps Flet out; that the CI workflow's own comment records the `ubuntu-latest` packages) and § "Tests" (why the frame-cost harness exists). § "Package map" and § "The workflow apparatus" were unchanged in substance. The findings are in the project's shared folder, `v0.7.0/arch-audit-findings-1.md` to `-4.md`.

**What was done.** The six sections are back to their wording before `#2044`. Into them went what the edit had added or corrected: the count of four layers; "the latest keyframe at or before it" for "the keyframe that brackets it"; "two runs" for "two branches" in the comparison chapter; and definitions of the fork, the crossing rule, the canonical state and the unconditional set. The single losses in the other five sections are restored in place. Decision history that `#2044` dropped and `PL-SVGH` cuts (`PL-4YY1`'s third directory, `PL-CNJ1`'s measurement, the Flet removal) is not restored. History that the revert brought back stays for `PL-SVGH` to place.
