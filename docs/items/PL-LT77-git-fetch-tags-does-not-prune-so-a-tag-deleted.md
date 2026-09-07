---
id: PL-LT77
title: git fetch --tags does not prune, so a tag deleted on origin keeps failing doc_check in every checkout that already fetched it, and nothing distinguishes stale local state from a real repository fault
status: untriaged
feature: dev-tooling
touches: tools/doc_check.py, .claude/hooks
added: 2026-09-07
---

**Problem.** `doc_check`'s release-tag rule reads **local** tags. `git fetch
--tags` fetches new tags but does not delete ones the remote has dropped, and
neither `git fetch origin main --tags` nor `git pull` will prune them. So a tag
deleted on `origin` stays in every checkout that already fetched it, and
`doc_check` goes on failing on it indefinitely — reporting a fault the
repository does not have, in wording that reads as though it does:

```
ROADMAP.md: git holds v0.4.8, but no row of the version table marks v0.4.8
completed; a release that shipped is one this table has to name
```

"git holds v0.4.8" is true of *this checkout* and false of the repository. The
message offers nothing that would let a reader tell those apart.

**Measured 2026-09-07.** `v0.4.8` was pushed onto `b03a7d03` — a commit whose
`pyproject.toml` reads `version = "0.4.7"`, with no ROADMAP row and no release
notes — and `doc_check` went red for every session. The tag was then **deleted
from origin**. This checkout then ran `git fetch origin main --tags`, which left
the tag in place, and `doc_check` stayed red:

| Action | `doc_check` |
| --- | --- |
| after `git fetch origin main --tags` | `exit=1`, still naming v0.4.8 |
| `git ls-remote origin refs/tags/v0.4.8` | empty — gone on origin |
| after `git tag -d v0.4.8`, nothing else changed | `0 errors, 0 advisories` |

**Why it matters, concretely.** This session reported `main` as red to the
project owner on the strength of that message, after the tag had already been
deleted on `origin`. The reading was wrong and the message invited it. Three
other sessions captured the same tag condition independently — `PL-6YYR`,
`PL-BKDP` and `PL-KFWL`, each stranded on a different unmerged branch — so the
cost of a misread here is paid by every session at once, which is what a shared
gate does.

The blast radius is narrower than it first looks, and asymmetric in the
unhelpful direction. A container that clones fresh is unaffected, so most remote
sessions self-heal. What persists is a **warm checkout** — a long-running
session, and the project owner's own machine, which is the one place nobody
re-clones and the one reader who cannot escalate to anybody else.

**Where.** The release-tag rule in `tools/doc_check.py`; `.claude/hooks/` if the
prune is done at session start instead.

**Done when.** A session that hits this can tell in one read that the tag is
stale locally rather than wrong in the repository. Three shapes, and the
recommendation is the cheapest:

1. **Widen the error message** to name the possibility and the command —
   *"…if this tag was deleted on origin, `git fetch --prune-tags origin` will
   clear it."* **Recommended.** One string, no new mechanism, and it converts a
   misdiagnosis into a five-second fix.
2. **Prune tags in the session-start hook.** Fixes it before anything reads it,
   but makes every session pay a network round-trip for a rare condition, and
   silently discards a tag a session might have created locally.
3. **Have `doc_check` verify the tag against `origin`.** Rejected unless the
   other two fail: `CLAUDE.md` requires new tools to use the standard library
   so *"a hook or a bare checkout can run them"*, and this one is deliberately
   offline. Adding network to it to catch a stale tag trades a stated design
   property for a narrow win.

**Not a duplicate of the three stranded captures.** `PL-6YYR`, `PL-BKDP` and
`PL-KFWL` all record the *forward* direction — a tag pushed for a version that
was never cut. This is the reverse: what happens after that tag is withdrawn.
The forward direction was in fact detected, loudly, by `doc_check`; it is the
withdrawal that nothing detects. Worth triaging alongside them.

**No `verify:` command is recorded**, deliberately. Every candidate presumes one
of the three shapes above — a `grep` for the new message assumes shape 1 — and
would report the wrong answer if triage picks another. `PL-0ZGK` carries none
for the same reason: an item still deciding its shape has nothing stable to
assert.

**Found.** 2026-09-07, refreshing `main` while closing out `PL-SR8F` and
`PL-0GTC`, when a fetch that reported no changes left `doc_check` red on a tag
`origin` no longer had.
