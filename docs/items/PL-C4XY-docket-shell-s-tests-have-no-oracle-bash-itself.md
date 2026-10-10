---
id: PL-C4XY
title: docket.shell's tests have no oracle: bash itself could check the lexer's reading of generated commands
status: untriaged
feature: reader-checks
added: 2026-10-10
---

**Problem.** `docket.shell` is the one shared reader with no reference in
its tests, since no shell library reads both views as bash does (`PL-JNYL`).
Bash itself can be the oracle: the review had `declare -f` print bash's parse
of `PL-0CJC`'s form. Generated commands, compared through that, would find a
lexer defect on the pull request that first writes the form, as the Markdown
and front-matter references do for theirs.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** A test compares `docket.shell`'s reading of generated commands
with bash's own, or the comparison is shown not to reach the forms the lexer
reads.
