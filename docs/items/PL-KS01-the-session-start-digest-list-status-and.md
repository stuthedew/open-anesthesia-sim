---
id: PL-KS01
title: The session-start digest, list, status and concurrent answer from the working tree's copy of each item while next and show read origin/main's newer copy, so behind origin/main the digest's Top line can name an item next no longer offers
priority: P3
effort: M
status: needs-decision
classes: defect
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
payoff: the digest, list, status and concurrent answer from the same copy of each item as next and show, so a session resumed behind origin/main is not pointed at work main has closed
---

**Problem.** The session-start digest, list, status and concurrent answer from the working tree's copy of each item while next and show read origin/main's newer copy, so behind origin/main the digest's Top line can name an item next no longer offers

**Why it matters.** Found closing `PL-Y48N`, which scoped the base's newer copy to `next`, `show` and `claim` (`cli._from_base`, `vcs.base_copies`). The digest's `Top:` and `By lane` lines are `next`'s pick, so a resumed session behind `origin/main` can be pointed at an item `next` would no longer offer. Low harm as it stands: the hook's branch line above the digest already says the branch is behind, and `show` and `claim` now catch a closed item downstream. `cli._from_base` is read-only by construction; applying it to the digest would also move the open counts and the releasable count, which is the decision this item holds.

**Read 2026-09-26 against `origin/main` (`e586612e`).** `cli._from_base` has
two callers, `cmd_show` and `cmd_next` (with `_next_oldest`), and `claim` reads
`vcs.base_copies` for its own refusal. `cmd_digest`, `cmd_list`, `cmd_status`
and `cmd_concurrent` call neither, and `subprojects/docket/README.md` says so in
its `PL-Y48N` paragraph: "the digest, `list` and `status` still answer from the
working tree".

**Decision needed.** Should every read command answer from the base's newer
copy where `next` does, so that the digest's counts move with it? This is a
session's call, not the owner's. What it changes is which copy four apparatus
commands print, and no learner or clinical value sees it (rule 14 of
`.claude/rules/instruction-writing.md`).

- **A: one copy for every read command.** Apply the base's newer copy where a
  read command loads the store, not command by command. Then the digest,
  `list`, `status` and `concurrent` answer as `next` does, and each says how
  many copies it took from the base. `check`, `set`, `new` and `withdraw` keep
  the working tree's copy, which they validate or write. Cost: behind
  `origin/main`, the digest's counts stop matching this checkout's files, and
  the releasable count includes what `main` has closed since the fork.
- **B: only the lines that are `next`'s pick.** The digest's `Top:` and
  `By lane` lines take `next`'s reading. Its counts stay on the working tree
  and say so. Smaller, but one digest then answers from two moments, which is
  the mechanism `PL-XBV4` removed.

**Recommended: A.** It carries `PL-XBV4`'s fix to the one input that fix left
to each command, so a read command added later gets the base's copy by
construction. The counts moving is the correction rather than its cost: they
then describe the moment the digest's refs line already dates.

**Done when.** Under A: in a checkout behind `origin/main` whose base closed an
item, the digest, `list`, `status` and `concurrent` answer from the base's copy
as `next` does, and say so. The commands that validate or write the store still
read the working tree, and the README's `PL-Y48N` paragraph names which commands
read which copy. Under B: the digest's `Top:` and `By lane` lines name what
`next` names in that checkout. Its counts say they are the working tree's, and
`PL-XBV4`'s `generator:` line names the store as the input its snapshot does not
carry.

**Generator check.** Not a new head: this is the first post-close instance of
`PL-XBV4`'s fact, the working tree's moment read as the moment of the refs
beside it. It was filed after that head closed (spent, 2026-09-26, #1054), in
the commit that closed its member `PL-Y48N`, and `docket new` recorded it as
`PL-Y48N`'s one recurrence. The store is not part of the snapshot
(`cli.Invocation`: "The store itself is not held here"). So each read command
still picks the copy it answers from, and `PL-Y48N`'s fix moved `next`, `show`
and `claim` alone.
