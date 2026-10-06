---
id: PL-B3MK
title: quality.yml's concurrency comment reads queue: max from SchemaStore because docs.github.com and github.blog are blocked, but docs.github.com answered on 2026-10-05 (github.blog is still refused at CONNECT), so the claim can be checked against GitHub's own prose and the comment re-dated
priority: P3
effort: S
status: done
classes: docs
touches: .github/workflows/quality.yml, tests/unit/test_ci_concurrency.py
added: 2026-10-05
closed: 2026-10-06
pr: 1387
payoff: the reason CI does not queue main's runs rests on GitHub's own documentation rather than a schema read around a block that has lifted, so the next session weighing the concurrency block can check the claim instead of repeating it
verify: ! grep -qF 'are both blocked by this container' .github/workflows/quality.yml
---

**Problem.** quality.yml's concurrency comment reads queue: max from SchemaStore because docs.github.com and github.blog are blocked, but docs.github.com answered on 2026-10-05 (github.blog is still refused at CONNECT), so the claim can be checked against GitHub's own prose and the comment re-dated

**Found 2026-10-05 by `PL-848V`'s thread (`#1366`)**, which read GitHub's
workflow syntax and trigger pages on docs.github.com for its trigger reader.
Probed from the cloud container that day: `curl` to
`https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions`
answered 301 past CONNECT, and `https://github.blog/` was refused at CONNECT
(403). The comment is the one above `concurrency:` in
`.github/workflows/quality.yml`, reading "are both blocked by this container's
egress proxy"; `tests/unit/test_ci_concurrency.py` holds the group to it.
Whether `queue: max` can be scoped by expression, and whether it combines with
`cancel-in-progress`, can now be read from GitHub's own prose rather than the
schema's declaration, and the comment can say when the hosts were measured.

**Reproduced 2026-10-05 at triage** on `main` at `b67dace8`: `curl -sS -o
/dev/null -w '%{http_code}\n'` to the workflow-syntax URL above answered 301,
and followed (`-L`) it lands on
`https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax`
with 200, whose `concurrency` section documents `queue` and says "The
combination of queue: max and cancel-in-progress: true is not allowed and will
result in a workflow validation error". `https://github.blog/` was refused at
CONNECT (`CONNECT tunnel failed, response 403`). The comment above
`concurrency:` still says the two hosts "are both blocked", undated. Whether
GitHub's prose also says `queue` takes no expression is the work, not read here.

**Why it matters.** The comment is the recorded reason `quality.yml` does not
use `queue: max`, and it tells the next reader the claim is the schema's alone
because GitHub's own page cannot be reached. That is false today, so a session
weighing the concurrency block either repeats an unverified claim or skips a
check it could make in one request; and a reachability statement with no date
reads as permanent, the failure `PL-M701` repaired for `blender.org`.

**Done when.** The comment above `concurrency:` in
`.github/workflows/quality.yml` cites GitHub's workflow-syntax page for each of
its two claims about `queue` (no expression form; refused beside
`cancel-in-progress: true`), or says plainly where that page is silent and the
schema remains the only source; it no longer says the hosts "are both blocked",
and any host it still calls unreachable carries the date it was probed.
`test_the_block_does_not_ask_for_the_larger_queue`'s docstring in
`tests/unit/test_ci_concurrency.py` agrees with the comment.

**Generator check.** The misread fact is whether a host answers through this
container's egress proxy: the environment on the day it was probed, which the
owner changes in settings no file reads. No head's `misread:` states it
(`bin/docket generators --misread`, 2026-10-05). Two other items misread it:
`PL-M701` (closed 2026-09-26, `blender.org` written as blocked) and `PL-P5NB`
(open, `docs/references/README.md` calling `doi.org` blocked, which answered
301 past CONNECT on 2026-10-05). By triage's rule that is one fact misread by
two or more other items with no head, so a generator, and this is also a
re-entry of `PL-M701` at a sibling site: its fix re-dated the `blender.org`
sentences and gave rule 14 its reader-side probe, but swept no other file,
though its own brief listed `docs.github.com` among the allowed domains that
day. The head is `PL-CLW5`, filed by the same pass, which records this item, `PL-M701` and `PL-P5NB` in its `root-cause-of:` as `live`: `w3.org` is still called `EGRESS_BLOCKED` in `src/anesthesia_sim/app/qt_widgets.py` and `tools/contrast_check.py`, refused at CONNECT today but stated as permanent.
