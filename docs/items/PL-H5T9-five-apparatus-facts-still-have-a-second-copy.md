---
id: PL-H5T9
title: Five apparatus facts still have a second copy under a different name, which tools/fact_home_check.py cannot see: roadmap.SECTION_ID_RE repeats store.CITED_ID_RE, pr_body_check.FRONT_MATTER repeats frontmatter.DELIMITER, fixture_id_check.FENCE_OPENING_RE and markdown._FENCE_OPEN are two grammars for a CommonMark fence, pr_body_check.repo_slug and headless_worker read origin's URL beside open_pull_requests.repo_slug, and the product package's path is spelt in agent_identity_check, glyph_check, literal_home_check, doc_check and import_boundary_check
status: untriaged
feature: one-source-of-truth
touches: tools/, subprojects/docket/src/docket/
added: 2026-10-24
---

**Problem.** `PL-LGDV` emptied `tools/fact_home_check.py`'s baseline. Reading the code it changed found five more facts that live in two places under two names, so the check's rule 2, which matches by name, does not report them:

1. `roadmap.SECTION_ID_RE` is `re.compile(ID_PATTERN)`, which `store.CITED_ID_RE` already compiles.
2. `pr_body_check.FRONT_MATTER` is `"---"`, the front matter fence that `frontmatter.DELIMITER` holds.
3. `fixture_id_check.FENCE_OPENING_RE` and `markdown._FENCE_OPEN` are two different regular expressions for the line that opens a CommonMark code fence.
4. `pr_body_check.repo_slug` and `headless_worker.py` each ask git for `origin`'s URL, beside `open_pull_requests.repo_slug`, the reading every other tool now shares. `headless_worker.py` also spells the remote as `"origin"` rather than `vcs.REMOTE`.
5. The product package's location, `src/anesthesia_sim`, is spelt in `agent_identity_check.APP`, `glyph_check.PYTHON_TREES`, `literal_home_check.TREE` and `CORE`, `doc_check.PACKAGE_ROOT` and six times in `import_boundary_check.py`.

**Why it matters.** Each pair agrees today and can drift apart the next time one copy is edited, which is the failure the one-source-of-truth principle in `CLAUDE.md` exists to prevent.

**Done when.** Each of the five facts is read from one home. For the first four that means importing the existing home. The fifth has no home yet, so it needs one module that states the product package's paths and is read by the others. `pr_body_check`'s tests serve git through its `_git`, so routing its `repo_slug` needs those tests moved to `open_pull_requests._git`.
