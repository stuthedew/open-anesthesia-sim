---
id: PL-YMKV
title: "Recover PL-SYG4 and PL-DL4M, which exist only on the branch refs of two archived sessions: no pull request is open for either, so nothing will carry them to main"
priority: P3
effort: S
status: done
classes: infra
feature: queue-hygiene
milestone: v0.4.26
touches: docs/items
added: 2026-09-15
closed: 2026-09-15
pr: 594
verify: test -e docs/items/PL-SYG4-the-digest-s-reserved-verdict-suppresses-the.md && test -e docs/items/PL-DL4M-docs-working-notes-md-still-heads-two-resolved.md
---

**Problem.** `PL-SYG4` and `PL-DL4M` exist only on the branch refs of two
sessions that are gone. No pull request is open for either, so nothing will
carry them to `main`.

**Established 2026-09-15, not assumed.** `bin/docket stranded` reports five
items on branches, and its own closing line says a branch on live work is
expected there — the hole is a branch nobody will merge. Separating the two
took three readings:

| item | branch | holder | verdict |
| --- | --- | --- | --- |
| `PL-1RTM`, `PL-WBLM` | `gifted-johnson-2cqhll` | session "PL-MXSL", running | live |
| `PL-7G5M` | `busy-pasteur-stq3by` | session "Next gate/goal", idle, blocked on the owner | live |
| `PL-SYG4` | `fervent-knuth-pr9ex7` | session "New version release decision", **archived** | stranded |
| `PL-DL4M` | `blissful-cerf-e0d1s3` | session "Repository development plan overview", **archived** | stranded |

The repository had **zero open pull requests** at the time, so no branch was
one merge away from landing its item either. `blissful-cerf-e0d1s3`'s archived
session names `PL-DL4M` in its own closing summary — "captured PL-DL4M stale
headers" — which is what turned that one from probable to certain.

**Why it matters.** An item on an abandoned branch ref is worse than a lost
one, because nothing reads as missing: the finding was made, written up and
then made invisible to every command that reads the store. `docs/dead-ends.md`
records that this project refuses `git fetch --prune` for exactly this reason —
a stale `origin/<branch>` ref can be the only surviving copy, and `PL-HKF4`
came within one prune of losing one. The refusal buys time; it does not
recover anything, and nothing else does either until a session looks.

Both recovered items are live findings rather than stale ones. `PL-SYG4`
describes behaviour the owner meets on every session start: the digest's
RESERVED verdict suppresses the release offer entirely instead of naming the
next free patch number, on a tree carrying 32 finished items unreleased since
`v0.4.25`. `PL-DL4M` is the cold-read hazard in `docs/WORKING_NOTES.md`, whose
headings still present two resolved threads as open.

**Done when.** Both files are on the default branch, which the `verify:` above
reads. They arrive `untriaged`, faithful to how they were captured, and the
next `bin/docket triage` folds them in; triaging them was deliberately not
bundled into this recovery, which is a different mode of work.
