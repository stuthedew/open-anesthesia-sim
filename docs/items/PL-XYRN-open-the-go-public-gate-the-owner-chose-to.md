---
id: PL-XYRN
title: Open the go-public gate: the owner chose to publish now and run the human-facing pass afterwards
priority: P2
effort: S
status: done
classes: docs, ux
feature: public-readiness
touches: docs/items, ROADMAP.md
added: 2026-09-05
closed: 2026-09-06
pr: 370
verify: bin/docket check && ! grep -q '^blocked-by: PL-XYRN' docs/items/PL-N092-rewrite-readme-as-a-human-readable-introduction.md && ! grep -q 'immediately before it is made public' ROADMAP.md
---

**Problem.** Several pieces of work only pay off when a stranger arrives, and
each one drifts if it is done months early. There is no point in the plan that
collects them, so they are either done too soon or forgotten. This item is that
point.

**Why it matters.** The project owner deferred `PL-N092` (rewrite README as a
human-readable introduction) here on 2026-09-05 rather than running it once
`PL-RM83` (decide what README.md is for) settled its audience and scope, and
said there would be "a number of things like that" — human-facing work due
before going public. Deferring is right and it needs somewhere to defer *to*:
`ROADMAP.md`'s "Planned milestones" item 32 carries the intent, and this item is
what `blocked-by:` can name, so a deferred item leaves `docket next` instead of
being handed to the next session that asks for work.

Doing them as one pass is the point rather than an efficiency. Human-facing
prose is judged against a reader, and a set of documents written to one reader
over one week is coherent in a way the same documents written singly over
months is not — which is the failure the README freeze was written to record for
`README.md` alone. (That freeze was `.claude/rules/readme-hold.md`; `PL-3V4N`
retired the path-scoped rule for `tools/readme_hold_check.py` in #366, so the
file no longer exists and the reasoning now lives in `PL-WB5K`.)

**Decided, 2026-09-05 (project owner): "public today. Will do human facing pass
in the nearish future."** The two halves of this item were designed to move
together — the gate holds the date, and the pass runs immediately before it —
and the owner has deliberately separated them. The repository goes public now;
the human-facing work follows when it follows.

So the coupling this item was built on no longer holds, and the item is
rewritten rather than kept as a gate that gates nothing. What it costs is
stated above and stands: a first-time visitor arriving before the pass meets a
repository with no `README.md` at all — deleted deliberately under `PL-WB5K`,
with `tools/readme_hold_check.py` now enforcing the absence. That was raised
before the decision and answered; it is recorded here as a known state rather
than as an objection.

**Where.** `docs/items/PL-N092-*` (release it), `ROADMAP.md` item 32 (reword,
since it says the pass runs "immediately before" the flip and it no longer
does), and the repository's own GitHub settings, which only the owner can
reach.

**Released by this decision.**

- `PL-N092` (rewrite README as a human-readable introduction) — was `blocked-by`
  this item and waiting only on timing. Now `ready`. Its `verify:` was silently
  broken by `PL-WB5K`'s README deletion (#366): `! grep -q '…' README.md` on a
  file that does not exist returns 0, so the command passed on a tree with none
  of the work done. Corrected here, having been run, to require the file back.

**The pass itself keeps its starting list.** Named so it is not reconstructed
from memory when the owner returns to it; none is blocked on this item, and each
stays workable on its own.

- `PL-3VKZ` (rewrite over-verbose and poorly worded prose in the human-facing
  markdown documents) — the same reader, the same week, and the document set
  overlaps.
- `PL-8DDG` (add `CITATION.cff`) — the `CONTRIBUTING.md` half of it, which
  `PL-RM83`'s standards research ties to a contributor audience that does not
  exist until the repository is public. The `CITATION.cff` half is done and did
  not wait.
- Roadmap item 20 (accessibility) and item 23 (packaging, signing and
  distribution). Item 23 is the harder dependency: `PL-RM83` established that
  the README's second audience — a clinician who wants to run the simulator and
  has no interest in the code — cannot be served at all until something is
  distributable. Going public without it means the README tells that reader
  the honest "not yet packaged", which is a defensible state to launch in but
  should be a choice rather than a discovery.

**Done when.** `PL-N092` is released and carries a `verify:` that fails on a
tree without the work; `ROADMAP.md` item 32 no longer says the pass runs
immediately before the flip, and says instead that the pass is owed and the
repository is already public; and the repository is public.

**Done. The repository is public as of 2026-09-06 (00:09 UTC / 2026-09-05
evening US Central), confirmed against the GitHub API rather than assumed:**
`GET /repos/stuthedew/open-anesthesia-sim` returns `visibility: public`. The
owner flipped it themselves; visibility is an owner-only setting and no session
here can reach it. That was the last clause of the **Done when** above, and it
closes this item and with it the `public-readiness` feature, which held only
this one.

**Two consequences that outlive the item.** Neither is work for this item; both
are recorded so they are not rediscovered.

- **Standard GitHub Actions runners are free on a public repository**, which is
  the premise `PL-SSQX` (quality.yml's concurrency comment says the repository
  is public and standard runners are free, closed in #369) was filed against
  while the repository was still private. Several `ci-cost` items were scoped to
  save billed minutes that are no longer billed. What survives the change is
  wall-clock latency, which is a real cost to a session waiting on a merge and a
  different argument from the one those items make. Re-read on their own merits
  rather than assumed still-valid; the owner should confirm against the
  repository's own Actions billing page rather than against this sentence.
- **The pre-publication sweep is a matter of record.** `LICENSE` and
  `CITATION.cff` present, no tracked `.env`/key/credential files, and no
  credential-shaped strings in any of the 733 commits then in history. Nine
  commits dated 2026-08-31 carry a personal email address rather than the GitHub
  noreply one; the owner was told before the flip and it stands, since a history
  rewrite would break every `pr:` link `PL-ZQ9C`, `PL-99Y4` and `PL-XCYB` exist
  to preserve.

**The pass has no gate now, which is the risk this item was built to prevent.**
Item 32 is where it lives, and `ROADMAP.md` "Planned milestones" is deliberately
unscoped, so nothing will surface it on its own — the next thing that raises it
is a session offering to scope milestone 32, or the owner asking. That is the
accepted cost of the decision rather than a defect to route around, and it is
written here so the next reader does not rediscover it as a surprise.
