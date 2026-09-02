---
id: PL-9GCV
title: Nothing checks that a merge commit subject leads with the ids it closes, so PR #220 closed three items with no recoverable pull request
status: dropped
closed: 2026-09-02
reason: Duplicate of PL-2XTF, which covers the same #220 incident with a full brief, names this item, and carries the prevention half this title asks for as one of its options.
added: 2026-09-02
---

**Problem.** Nothing checks that a merge commit subject leads with the ids it
closes, so PR #220 closed three items with no recoverable pull request.

**Why it matters.** Nothing is lost by dropping this. `PL-2XTF` was filed for
the same incident by a session that could not see this one, reached the same
conclusion, and states the mechanism with the timestamps that decide it. The
specific thing this title asks for — a check that the subject leads with its
ids — is `PL-2XTF`'s prevention option, refined there into a check on the
*pull request title* before the merge, because a check on the merge subject
can only fire on `main` after the damage is done.

Three sessions filed this defect within an hour, none seeing the others: this
one, `PL-2XTF`, and `PL-Q8QX` on `claude/breathing-circuit-default-tckz8n`.
That is worth knowing on its own, and `PL-2XTF` records it.

**Done when.** Dropped as a duplicate; the work is `PL-2XTF`'s.
