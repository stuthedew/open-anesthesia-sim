---
id: PL-NVT6
title: docket claim gives up on git ls-remote after its ten-second git timeout, but ls-remote to GitHub took 10.2 to 12.0 seconds in a Projects thread on 2026-11-03, so two claims in a row stayed local and the session pushed by hand, skipping the check for a claim published meanwhile
status: dropped
added: 2026-11-03
closed: 2026-11-03
reason: PL-TFY2 (#1977) gave every git call that reaches the remote, ls-remote included, a 60-second bound eight minutes after this was filed, so docket claim no longer gives up at ten seconds
---

**Problem.** docket claim gives up on git ls-remote after its ten-second git timeout, but ls-remote to GitHub took 10.2 to 12.0 seconds in a Projects thread on 2026-11-03, so two claims in a row stayed local and the session pushed by hand, skipping the check for a claim published meanwhile

**Reproduced 2026-11-03: the premise no longer holds.** `docket claim` asks the
remote through `vcs.remote_heads`, which runs `git ls-remote --heads origin`
through `call_git`. Since `PL-TFY2` (#1977, merged 2026-11-03 20:18 UTC), a git
call that reaches the remote gets `NETWORK_GIT_TIMEOUT`, 60 seconds.
`vcs.timeout_for(["ls-remote", "--heads", "origin"])` returns 60 on this tree,
against 10 for a local read. This item was filed at 20:10 UTC in #1981, eight
minutes before that fix merged. The 10.2 to 12.0 seconds it measured are well
inside the new bound.

**Generator check.** One-off. It is the same defect as `PL-TFY2` at a sibling
site, and `PL-TFY2`'s fix already covers it, so it is not a re-entry.
