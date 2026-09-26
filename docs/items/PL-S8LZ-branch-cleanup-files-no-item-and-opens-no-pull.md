---
id: PL-S8LZ
title: Branch cleanup files no item and opens no pull request: deleting remote branches changes nothing in the repository, so the reply hands the owner the list and nothing is committed
priority: P2
effort: S
status: done
classes: infra
touches: CLAUDE.md, .claude/rules/instruction-writing.md, .claude/skills/docket/modes/capture.md, docs/items/PL-P99G-delete-the-13-remote-branches-whose-work-main.md
added: 2026-09-26
closed: 2026-09-26
pr: 1110
payoff: a session asked to clean up branches hands the owner the list in its reply and opens no pull request, so nothing waits to be merged or closed for work that changed nothing in the repository
verify: grep -q 'Not for deleting remote branches' CLAUDE.md && grep -q 'remote branches to delete' .claude/rules/instruction-writing.md && grep -q 'deleting remote branches' .claude/skills/docket/modes/capture.md
---

**Problem.** Branch cleanup files no item and opens no pull request: deleting remote branches changes nothing in the repository, so the reply hands the owner the list and nothing is committed

**The decision** (project owner, 2026-09-26, ratified, over filing branch
cleanup as housekeeping with a pull request of its own, `PL-P99G`). The owner
asked a session to "clean up unused branches". Following the housekeeping rule,
it filed `PL-P99G`, claimed it, and opened draft `#1092` to carry the item. It
could not delete the branches itself (`docs/worker.md` § "Ref operations a
session cannot perform"). The owner closed it out with "Drop this. It was not
worth a pull request". Asked whether branch cleanup should skip the item and
the pull request from now on, since deleting branches changes nothing in the
repository and the item only ever records itself, they answered yes.

**Why it matters.** Three resident rules make a session file branch cleanup and
open a pull request for it:

- `CLAUDE.md`'s housekeeping bullet names clearing a stale ref among its
  examples.
- Rule 14 of `.claude/rules/instruction-writing.md` files any closing-block
  line that could outlive the sitting.
- `CLAUDE.md`'s commit-and-push bullet opens a pull request for a branch
  carrying only item files.

So the next cleanup repeats `#1092` exactly. The owner either merges a record
of work that changed nothing in the tree, or closes it as they did here.

**What to change: three sentences, the narrowest rule that removes it.** The
exemption covers deleting remote branches, together with clearing this clone's
tracking refs for them, and nothing else. Recovering a stranded item from a
branch stays filed housekeeping, because it changes the tree. A release tag
keeps its item, because `PL-H1JD` lost a tag request to an archived session.

1. `CLAUDE.md`, in the bullet that opens "**Housekeeping you are about to do
   yourself is filed before you do it.**": add one sentence beginning `Not for
   deleting remote branches`. It says the deletion changes nothing in the
   repository, so nothing is filed, claimed or committed, and no pull request
   opens. The reply hands the owner the list and the command. Stamp it with
   the decision's stamp above.
2. `.claude/rules/instruction-writing.md`, in rule 14's bullet "The block is a
   handover, not a store": after the sentence that files a line which "could
   reasonably outlive this sitting", add a clause carrying the words `remote
   branches to delete`. It says such a list stays in the reply, per
   `CLAUDE.md`'s housekeeping bullet.
3. `.claude/skills/docket/modes/capture.md`, in the paragraph "How small is too
   small to file ...": add a sentence carrying the words `deleting remote
   branches`. It says that work takes no commit at all, so there is nothing
   for an id to lead, and it is not filed.

The first two are resident. Their commit names what they replace, or says why
nothing can be cut (`CLAUDE.md` § "The queue", the resident-set bullet). The
likely answer is nothing: this is new behaviour, and no existing sentence
covers it.

**Falsifier.** Revisit this if a branch-deletion list the owner meant to act on
is lost with an archived session. Revisit it too if two sessions do the same
cleanup because neither could see the other's. Either would show that a reply
alone is not enough.

**Done when.** All three sentences are in place, `make check` passes, and the
pull request carrying them has merged.
