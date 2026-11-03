---
id: PL-T3KB
title: Re-run the current prose review over docs/MODEL.md's first four rewritten parts (Status through the source hierarchy), which were written before the review named each text's readers, and rewrite what it now fails with no value changed
priority: P2
effort: M
status: ready
classes: docs
feature: prose-quality
touches: docs/MODEL.md
added: 2026-11-03
payoff: the opening sections, conventions, equations, numerical method and source hierarchy of the model specification meet the same reader-named prose review as the later sections, so a clinician reads the whole document to one standard
verify: uv run python tools/model_rewrite.py ids "Status" "Intended use, and the safety class this project holds itself to" "Reasonably foreseeable misuse, and the hazards the presentation carries" "How this document is held to the tree" "Purpose" "Model boundary" "Conventions" "Symbols" "Compartment capacities" "Tissue groups" "Governing equations" "Conservation of agent mass" "Numerical method" "Source hierarchy: what may be cited as the authority for a value"
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** `PL-ZT47`'s first four section parts were rewritten and merged
before the prose review changed: `PL-J8CG` (#1944, § "Status" through
§ "Model boundary"), `PL-XTZW` (#1945, § "Conventions" through § "Conservation
of agent mass"), `PL-TZ47` (#1947, § "Numerical method") and `PL-HJDK` (#1949,
§ "Source hierarchy"). Since then the review names each kind of text's readers
(`PL-R7Q6`, #1957), asks what the named reader would take from each unit
(`PL-1XC7`, #1959), and refuses a rewrite longer than the text it replaces
(`PL-CWRZ`, #1962). The project owner asked on 2026-11-03 for those parts to go
back through the review as it now stands (project owner, 2026-11-03).

Parts 5 to 7 and the runtime-controls part are out of scope. Each ran the
current prompt, unchanged since #1962 (2026-11-03 02:37Z): `PL-QL0X` (#1953) at
03:14Z, `PL-70B2` (#1950) at 04:25Z, and `PL-WBR3` (#1952) and `PL-QHR2` (#1964)
after it.

**How.** Print each part's units with `tools/new_prose.py` against a base that
lacks that part's lines, give each part's output to one fresh reviewer as
close-out step 8 says, and apply the rewrites that keep every value, unit,
condition, identifier and citation. Move a fact the reviewer moves to the
place it names, such as a section's note for developers. No stored value or
equation changes. The checked rewrite merges on green without the owner's
read (project owner, 2026-11-02 19:40Z).

**Done when** the four parts' prose has been through the current review, the
rewrites are applied, and the branch's `Prose-review:` trailer records the
counts.
