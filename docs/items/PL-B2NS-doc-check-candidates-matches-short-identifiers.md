---
id: PL-B2NS
title: doc_check candidates matches short identifiers against ordinary prose, so one function named settle produced 30 false lines
status: untriaged
added: 2026-09-05
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
