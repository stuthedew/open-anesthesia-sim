---
id: PL-PDBM
title: CLAUDE.md says a path-scoped rule loads when a session reads a matching file, but Claude Code's memory page now says it loads on a Read, Write or Edit of one and on a Bash read, so the resident reason for routing a rule rests on a stale fact (found by PL-124X)
priority: P3
effort: S
status: done
classes: docs
touches: CLAUDE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
closed: 2026-10-19
pr: 1640
payoff: the resident reason for routing a rule to a path scope matches what Claude Code documents about when such a rule loads
verify: ! grep -qF 'which loads when a session *reads* a matching file' CLAUDE.md
---

**Problem.** CLAUDE.md says a path-scoped rule loads when a session reads a matching file, but Claude Code's memory page now says it loads on a Read, Write or Edit of one and on a Bash read, so the resident reason for routing a rule rests on a stale fact (found by PL-124X)

**Why it matters.** `CLAUDE.md` § "A behavior change takes effect in the
session that asks for it" routes a rule to a path scope on the claim that such
a rule "loads when a session *reads* a matching file". Claude Code's memory
page, compared as markdown on 2026-10-19, says: "A path-scoped rule loads when
Claude uses the Read, Write, or Edit tool on a matching file". It also loads
when a Bash command such as `cat` reads one. The conclusion the bullet draws
still holds, because a rule that loads with a write arrives after that write's
content was composed. But a session reading the bullet is told something the
documentation no longer says, and `PL-124X` corrected the same claim in
`docs/resident-instructions.md` without touching the resident file.

**Done when.** The bullet says that a path-scoped rule loads on a read, a write
or an edit of a matching file, and keeps the reason it gives for refusing a
path scope to a rule that must apply before a first write. The edit names what
it replaces, as `CLAUDE.md` requires of every change to the resident set.

**Generator check.** One stale sentence, found by `PL-124X`'s comparison. Its
reader misread when a path-scoped rule loads, which no recorded head names, and
no other open item rests on it, so it is an ordinary item.

**Fixed 2026-10-19.** The bullet now says the rule "loads when a session reads,
writes or edits a matching file", and that a rule which must fire before a
first write reaches it only after that write. It replaces the old clause and
adds 31 characters to `CLAUDE.md`, for the two missing verbs. Nothing else can
be cut to pay for them, because the clause is the one place the bullet says
when such a rule loads.
