---
id: PL-B2NS
title: doc_check candidates matches short identifiers against ordinary prose, so one function named settle produced 30 false lines
priority: P2
effort: M
status: done
classes: defect, session-cost
feature: dev-tooling
milestone: v0.4.0
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-05
closed: 2026-09-05
pr: 335
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_candidates_does_not_report_an_identifier_used_as_ordinary_prose' tests/unit/test_doc_check.py
---

**Problem.** `python3 tools/doc_check.py candidates --base <ref>` prints the
documentation lines mentioning anything the diff touched, and it matches
identifier names as bare words. An identifier that is also an ordinary English
word therefore matches prose that has nothing to do with the code.

**Observed 2026-09-05.** A local function named `settle` was added to
`vcs.py` while closing `PL-X3WZ`. The candidates run for that diff returned 34
lines, of which 30 were the word "settle" in unrelated prose - eleven in
`docs/MODEL.md`, eight in `ROADMAP.md`, one in `CLAUDE.md`. The four genuine
candidates were the ones matching `vcs.py` and `cli.py` as filenames. The
function was renamed to `credit_claims` to clear it, which fixes that instance
and not the tool.

**Why it matters.** The close-out sweep is where a session spends judgment on
whether each documentation statement is still true, and it is the last guard
before stale documentation reaches a reader - which `CLAUDE.md` treats as a
safety issue rather than tidiness. A block of obvious false positives is what
trains a session to skim that output, and the genuine lines get skimmed with
them. `CLAUDE.md`'s own test applies: an advisory being routed around is one of
the three that make a finding worth acting on.

**Where.** `tools/doc_check.py`, the `candidates` subcommand.

**Possible readings, none decided.** Require a match to look like code -
adjacent to backticks, a `()` call form, or `snake_case`/`CamelCase` shape;
skip identifiers below a length or on a stop-list of common words; or rank
filename matches above bare-identifier ones and print the latter under a
heading that says what they are. The first is probably enough on its own, since
this project writes code references in backticks throughout.

**Done when.** A diff adding a common-word identifier produces candidate output
whose lines are about the code, and the check still finds a documentation line
that names a renamed symbol in prose.

**Three more captures of the same noise, folded in at triage 2026-09-05.**
The `settle` measurement above is one of four; the others were filed
separately and dropped into this item, because all four are one decision
about which terms enter the search and one fix in the same function.

- `PL-MZJS`: a changed file contributes its *stem* as a bare word. For
  `subprojects/docket/src/docket/render.py` that word is `render`, which runs
  through `ROADMAP.md`, `docs/MODEL.md` and `docs/ARCHITECTURE.md` in its
  ordinary English sense. Measured on `PL-YHD3`'s two-file diff: 37 lines
  reported for `render.py`, none of them about the module.
- `PL-03GZ`: a diff touching `settings.json`, or a test carrying a helper
  named `_run`, emits around 200 lines naming nothing relevant.
- `PL-5ZP5`: the search also draws terms from a touched *item's* declared
  `touches`, so editing one queue file floods the sweep with every
  documentation line mentioning that item's paths.

So the fix has to decide about three kinds of term - an identifier, a file
stem, and a path read out of an item's front matter - and the **Done when.**
above is met only when all three produce output about the code.
