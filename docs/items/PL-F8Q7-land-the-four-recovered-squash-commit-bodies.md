---
id: PL-F8Q7
title: Land the four recovered squash-commit bodies (818, 820, 821, 822) that PL-BXNH's session wrote to claude/festive-allen-nj1x98 and never merged, before the archived session's branch is deleted
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/pr-bodies, docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 837
payoff: the reasoning behind four merged pull requests stops existing only on GitHub and on an archived session's branch, and the digest line that has reported it lost in every session goes quiet
verify: test -f docs/pr-bodies/818.md && test -f docs/pr-bodies/820.md && test -f docs/pr-bodies/821.md && test -f docs/pr-bodies/822.md
---

**Problem.** Land the four recovered squash-commit bodies (818, 820, 821, 822) that PL-BXNH's session wrote to claude/festive-allen-nj1x98 and never merged, before the archived session's branch is deleted

**Decided: land them now** (project owner, 2026-09-21, ratified). Chosen over
leaving them on `claude/festive-allen-nj1x98` for a later pass or for that
session to finish - which it cannot, being archived. The branch was still on the
remote, so nothing was at immediate risk; the ground for not waiting is that the
three sibling branches in this same sweep
(`claude/amazing-thompson-3hwksq`, `claude/funny-turing-bul2ux`,
`claude/nifty-gauss-rgoya2`) were deleted from the remote within hours of their
sessions ending, and one of them held a ratified decision that survived only in
one container's unpruned tracking ref.

**Recovered through the tool rather than off the branch, and cross-checked
against it.** `python3 tools/pr_body_check.py --recover` fetches each body from
GitHub, which is the authority; the branch copy is one session's output of that
same command. Both routes were run and compared: all four files are
**byte-identical** to `claude/festive-allen-nj1x98`'s copies (`git show ... |
diff -`, four for four), and `python3 tools/pr_body_check.py` now prints
nothing where it had reported "4 squash commit(s) on origin/main lost their
body, newest #822" in every session digest since the loss.

Two independent routes agreeing on the bytes is what makes this safe to land
without reading 16 KB of prose for fidelity: the question a reader would ask -
"is this really what #818 said?" - is answered by GitHub having served it, not
by the branch having stored it.

**`#832` recovered this item's neighbour but not this work.** That pull request
restored `PL-BXNH`'s *item file* - the record that four bodies were lost - while
the bodies themselves stayed on the branch. That split is why `PL-B78T` is
filed: `bin/docket stranded` reads only `docs/items`, so work product sitting
anywhere else is invisible to the one command whose job is finding it.
