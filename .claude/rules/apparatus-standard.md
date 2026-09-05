---
paths:
  - "subprojects/docket/**"
  - "tools/**"
  - ".claude/**"
  - "docs/worker.md"
---

# The bar for the workflow apparatus

`CLAUDE.md` § "Proactive expert review and domain best practices" splits this
repository into two standards and names the paths on each side. This is the
apparatus half, and it loads only on those paths.

That scoping is the point rather than a convenience. Applied to `src/`,
`tests/`, `docs/MODEL.md` or `README.md`, every sentence below is wrong — they
are held to the opposite standard, and one that argues for *more* investment,
not less. While this text was resident a session quoted it as the bar for
comment quality in `src/` and reached the wrong answer confidently, citing the
right file (`PL-6SBB`). A session that never opens an apparatus path now never
loads it.

The apparatus is held to **working reliably and staying streamlined**.
Reliability and the functionality it actually needs are the outcome;
"streamlined" describes how that gets built, never a ceiling on it. What to cut
is bloat — duplicated logic, an option nobody sets, prose restating what a
command already prints, a mechanism larger than its job because it was written
badly — and never function or robustness, which is the trade a size target
invites and this one refuses.

It is scaffolding, not product; nobody evaluating this project will read it.
Polishing it past sufficient is the most common way this project wastes a
session. Where the two standards compete for a session, the simulator wins.
