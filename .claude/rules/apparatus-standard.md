---
paths:
  - "/subprojects/docket/**"
  - "/tools/**"
  - "/.claude/**"
  - "/.github/**"
  - "/docs/worker.md"
---

# The bar for the workflow apparatus

`CLAUDE.md` § "Proactive expert review and domain best practices" splits this
repository into two standards and names the paths on each side. This is the
apparatus half, and it loads only on those paths.

That scoping is the point rather than a convenience. Applied to `src/`,
`tests/`, `docs/MODEL.md` or `README.md`, every sentence below is wrong — they
are held to the opposite standard, and one that argues for *more* investment,
not less. While this text was resident a session quoted it as the bar for
comment quality in `src/` and reached the wrong answer confidently, citing the
right file (`PL-6SBB`). A session that never opens an apparatus path now never
loads it.

The apparatus is held to **working reliably and staying streamlined**.
Reliability and the functionality it actually needs are the outcome;
"streamlined" describes how that gets built, never a ceiling on it. What to cut
is bloat — duplicated logic, an option nobody sets, prose restating what a
command already prints, a mechanism larger than its job because it was written
badly — and never function or robustness, which is the trade a size target
invites and this one refuses.

It is scaffolding, not product; nobody evaluating this project will read it.
Polishing it past sufficient is the most common way this project wastes a
session. Where the two standards compete for a session, the simulator wins.

## What a test on this side is for

A test here exists to keep the apparatus working, and a wrong answer costs a
session rather than a patient. So the bar is the one the simulator's standard
refuses: a test here earns its place if its **absence would let a real defect
through**. A script's own rule, the failure path it reports on, and the input
that once broke it are worth pinning; a getter, a constructor, or the standard
library's own behaviour are not. That is the whole bar, and nothing stricter
applies to the fifteen apparatus tests under `tests/unit/` or to
`subprojects/docket/tests/`.

**It does not reach a test that imports the product package.** That test is the
simulator's, and `CLAUDE.md`'s safety-critical standard asks of it what the
paragraph above does not: boundary, invalid-input, pathological-input and
regression tests, and validation against published reference cases or
independently calculated test vectors. The line is mechanical rather than a
judgment made per file — `tools/workflow_paths_check.py` decides it by exactly
that import, on the rule that "A test file under `tests/` is apparatus when it
does not import the product package, and product when it does."
