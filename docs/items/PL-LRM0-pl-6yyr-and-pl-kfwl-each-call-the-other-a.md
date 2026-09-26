---
id: PL-LRM0
title: PL-6YYR and PL-KFWL each call the other a probable duplicate and both stand ready at P2, and nothing reports a mutual duplicate claim
priority: P3
effort: S
status: done
classes: housekeeping
feature: queue-hygiene
touches: docs/items/PL-6YYR-a-release-tag-can-be-pushed-for-a-version-that.md, docs/items/PL-KFWL-the-v0-4-8-tag-is-pushed-onto-a-commit-where.md
added: 2026-09-22
closed: 2026-09-26
pr: 1065
payoff: docket next stops being able to hand out one release-tag problem under two ids
verify: ! { grep -q '^status: ready' docs/items/PL-6YYR-*.md && grep -q '^status: ready' docs/items/PL-KFWL-*.md && grep -q 'Probable duplicate of' docs/items/PL-6YYR-*.md docs/items/PL-KFWL-*.md; }
---

**Problem.** PL-6YYR and PL-KFWL each call the other a probable duplicate and both stand ready at P2, and nothing reports a mutual duplicate claim

**Found 2026-09-22 (`PL-8YXJ`, counting stale queue-state prose).** `PL-6YYR`
(a release tag can be pushed for a version that was never cut) opens a section
"**Probable duplicate of `PL-KFWL`**"; `PL-KFWL` (the v0.4.8 tag pushed onto a
commit where the release was never cut) opens one "**Probable duplicate of
`PL-6YYR`**". Both are `ready` at P2.

**Why it matters.** `docket next` can hand either one out, so a session works
the problem twice or closes the half that carried the better brief. No check
is proposed on one instance.

**Done when.** One of the two is `dropped` with a reason naming the other, or
both briefs say why they are distinct and drop the "probable duplicate" line.

**Closed 2026-09-26 under `PL-QHCW`.** Neither route in "Done when" was taken:
both items close as members of one generator in one commit, which answers the
question they each raised about the other. They were one problem - a tag off
its release's cut - seen from the rule and from an instance, and `PL-QHCW`'s cut
check closes both.
