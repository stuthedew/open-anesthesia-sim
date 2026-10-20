---
id: PL-15TY
title: tools/headless_worker.py reports a failed git clone by the first line of git's stderr, which is the 'Cloning into ...' progress line, so the real cause (authentication, a missing reference repository) is never shown: report the last non-progress line, or the whole stderr
priority: P2
effort: S
status: ready
classes: defect
touches: tools/headless_worker.py, subprojects/docket/src/docket/vcs.py, tests/unit/test_headless_worker.py
added: 2026-10-20
payoff: a failed clone says why it failed, so the owner does not rerun it by hand to find out
verify: grep -q 'PL-15TY' tests/unit/test_headless_worker.py
---

**Problem.** tools/headless_worker.py reports a failed git clone by the first line of git's stderr, which is the 'Cloning into ...' progress line, so the real cause (authentication, a missing reference repository) is never shown: report the last non-progress line, or the whole stderr

**Why it matters.** On 2026-10-20 the project owner's MacBook printed `headless_worker: \`git clone\` exited 128: Cloning into '/Users/.../pl-k88z-worker-20261020T041633'...` and nothing else. `GitCall.said` in `subprojects/docket/src/docket/vcs.py` keeps the first non-empty stderr line, and `git clone` always writes its progress line first. So every clone failure reads the same, and the owner has to rerun the clone by hand to learn why. That breaks the apparatus rule that an answer must be true or say what it could not read.

**Done when.** A failed clone's message names git's actual error line, such as `fatal: could not read Username` or `fatal: reference repository ... is not a local repository`, and a test pins that against stderr that opens with `Cloning into`.

**Generator check.** Not a head: one reader of `GitCall.said` whose first stderr line is progress, not the error.
