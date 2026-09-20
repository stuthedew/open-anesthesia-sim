---
id: PL-LT77
title: git fetch --tags does not prune, so a tag deleted on origin keeps failing doc_check in every checkout that already fetched it, and nothing distinguishes stale local state from a real repository fault
priority: P2
effort: S
status: ready
classes: defect, infra
feature: tag-error-names-its-cause
touches: tools/doc_check.py, .claude/hooks
added: 2026-09-07
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_stale_local_tag_names_its_own_remedy' tests/unit/test_doc_check.py
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

**Triage note, 2026-09-07.** Left at `needs-decision` rather than `ready`
because the item's three shapes are a live choice and it declines a `verify:`
command for that reason - any command written now would presume one of them.
The open question, for whoever answers it: widen the error message (the item's
own recommendation, one string and no new mechanism), prune tags in the
session-start hook, or give `doc_check` a network read. The condition is not
firing in this checkout today - `python3 tools/doc_check.py check` reports
`0 errors, 0 advisories` - so the decision can be taken unhurried.

**Decision needed.** Which of the three shapes above closes this: (1) widen
`doc_check`'s release-tag error to name stale local state and the
`git fetch --prune-tags origin` that clears it - the item's own recommendation,
one string and no new mechanism; (2) prune tags in the session-start hook,
which fixes it before anything reads it but makes every session pay a network
round-trip for a rare condition and silently discards a locally created tag; or
(3) have `doc_check` verify the tag against `origin`, which trades the tool's
stated offline property and the item rejects unless the other two fail. Answer
this and the item is `ready`; a `verify:` command cannot be written before it,
because each shape asserts something different.

**Answered 2026-09-19 under `PL-4Q9B`** (record clone trust and the permitted ref
operations): **shape 1, widen the error message** - this item's own
recommendation (project owner, 2026-09-19, ratified), chosen over pruning tags in the session-start hook and
over giving `doc_check` a network read.

The reasoning is the one the item already made, and the head confirmed it
generalises: there is no single point at which this checkout gets reconciled
against the remote, so each staleness condition is repaired where it surfaces.
This one surfaces in `doc_check`'s own output, which is where the reader is
standing when they need to know.

The message is at `tools/doc_check.py:2320`. It should name the possibility -
that the tag may have been withdrawn on origin and survive locally - and the
one command that clears it, `git tag -d v<version>` by name. Not
`--prune-tags`, which implies `--prune` and is refused by
`.claude/hooks/no-prune-guard.sh`, and not `--tags --force`, which updates a
tag and cannot remove one the remote has dropped (`PL-KFWL` records both).

**The `verify:` command was run 2026-09-19 and fails for the right reason**: the
240-test `doc_check` suite passes and the `grep` half exits 1, so the pair exits
1 today and the test it names is what the work owes.

**Grouped as `feature: tag-error-names-its-cause`** (`PL-JKML`'s duplicate
sweep, 2026-09-20, confirmed on independent refutation). `PL-KFWL` and
`PL-LT77` are two causes of one symptom: `doc_check` erroring on `main` in
every session over a release tag, with nothing in the message saying which
cause it is. `PL-KFWL` is a tag pushed onto a commit where the release was
never cut - a real fault in the remote. `PL-LT77` is a tag deleted on the
remote that a warm checkout keeps, because `git fetch --tags` does not prune -
a fault in local state only. The two demand opposite actions from the reader,
and today the error cannot tell them apart. The group closes when it can.
