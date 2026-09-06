---
id: PL-XYRN
title: Decide when the repository goes public, and run the human-facing pass immediately before it
priority: P2
effort: L
status: needs-decision
classes: docs, ux
feature: public-readiness
touches: README.md, docs, ROADMAP.md
added: 2026-09-05
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
months is not — which is the failure `.claude/rules/readme-hold.md` already
records for `README.md` alone.

**Decision needed.** *When does the repository go public?* Only the
project owner can answer it, and nothing here should start before they do. The
answer sets the pass running; until then this item stays `needs-decision` and
everything blocked on it stays out of `docket next`.

**Where.** `README.md`, `docs/`, `ROADMAP.md`, and the repository's own GitHub
settings.

**Blocked on this item.**

- `PL-N092` (rewrite README as a human-readable introduction) — `ready` in
  every other respect: `PL-RM83` settled its audience, its `docs/MODEL.md`
  boundary rule and its status treatment, and its brief is restated against
  them. It waits only for timing.

**Candidates, to be confirmed when the decision is made.** Named here so the
pass has a starting list rather than being reconstructed from memory; none is
blocked on this item yet, and each stays workable on its own until it is.

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

**Done when.** The project owner has set a date or a trigger for going public;
every item blocked on this one has been worked or explicitly released; and the
repository is public.

**The go-public half was answered by action on 2026-09-06.** The project owner
made the repository public (`"visibility": "public"` from the API, read the
same day), in the same message as unticking `main`'s up-to-date requirement.

**The pass did not run first, which is the outcome this item was written to
prevent.** Its whole shape - "run the human-facing pass *immediately before*
it" - assumed the decision would arrive as a decision, with the pass between
the answer and the switch. So the work is now remedial: the repository has been
publicly readable with no `README.md` and no GitHub description since that
moment. Nothing is wrong in the tree; what is missing is everything this item
was holding for a reader who can now arrive at any time.

`PL-N092` (rewrite README as a human-readable introduction) is unblocked as of
this note, and is the piece with a reader waiting. The rest of the candidate
list is unchanged and none of it was ever blocked on this item.

**What is still `needs-decision` here, restated.** Not the timing, which is
settled, but the shape: whether the remaining pass is scoped as a milestone in
`ROADMAP.md` - which is what the `docket` skill requires before an `L` item is
started - or dissolved into its parts now that the trigger has fired and each
part has a reader. That is the project owner's call and nothing here should
start before it, except `PL-N092`, which is `M` and stands on its own.
