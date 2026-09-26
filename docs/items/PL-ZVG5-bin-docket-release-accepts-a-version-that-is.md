---
id: PL-ZVG5
title: bin/docket release accepts a VERSION that is not a semantic version, so a typo such as 0.5.12x is carried into pyproject.toml's version field, the notes file name and every milestone stamp
status: untriaged
added: 2026-09-25
---

**Problem.** bin/docket release accepts a VERSION that is not a semantic version, so a typo such as 0.5.12x is carried into pyproject.toml's version field, the notes file name and every milestone stamp

**Observed 2026-09-25 under `PL-3DN1`.** `bin/docket release 0.5.12x --dry-run
--no-fetch` on a tree at 0.5.11 prints `0.5.11 -> 0.5.12x` and the notes, and
refuses only because the branch holds no release-train claim - a branch that
held one would cut it. `PL-3DN1`'s `release.below_current` compares only
numbers `SEMVER_RE` parses, deliberately, because an unparsable one is not
"below" anything; nothing else between `cmd_release` and `prepare_bump`
checks the grammar, and `prepare_bump` substitutes whatever string it is
given. `version_key` reads an unparsable name as `(0, 0, 0)`, so a notes file
named `v0.5.12x.md` would also sort below every real release.
