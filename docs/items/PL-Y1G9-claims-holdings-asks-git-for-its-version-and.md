---
id: PL-Y1G9
title: claims.holdings asks git for its version and its remotes, and neither subcommand is in GitRunner's _READ_ONLY, so every call empties the memo twice once PL-N162 puts it on the digest's path
priority: P3
effort: S
status: dropped
classes: perf
feature: claim-record
touches: subprojects/docket/src/docket/vcs.py
added: 2026-09-24
closed: 2026-09-24
reason: measured at triage: with holdings on the digest's path the digest runs 141 git processes against 139 with version and remote cached, and next 125 against 123; the second clear empties an already-empty memo, and remote cannot join _READ_ONLY whole because remote add writes, so two processes in about 140 is not worth a change
---

**Problem.** claims.holdings asks git for its version and its remotes, and neither subcommand is in GitRunner's _READ_ONLY, so every call empties the memo twice once PL-N162 puts it on the digest's path

**Measured at triage, 2026-09-24.** Counting the memo's clears during one
`holdings()` call printed `[1, 0]`: the second clear empties a memo that is
already empty. The cost was measured with `holdings` placed inside
`cli._flight`, to stand in for `PL-N162`:

- The digest ran 141 git processes, against 139 with `version` and `remote`
  cached.
- `next` ran 125, against 123.

`claim` and `yield` are the only callers today. `remote` cannot join
`_READ_ONLY` whole, because `remote add` writes.

**Why it matters.** It barely does: two git processes in about 140, once
`PL-N162` lands.
