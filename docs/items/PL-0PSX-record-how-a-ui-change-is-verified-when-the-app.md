---
id: PL-0PSX
title: Record how a UI change is verified when the app cannot be rendered in a remote session
status: needs-decision
added: 2026-09-04
priority: P2
effort: M
classes: docs, infra
feature: worker-instructions
touches: docs/worker.md
---

**Problem.** The app cannot be rendered, driven or screenshotted from a
Claude Code web session. Flet's Flutter web client fetches its CanvasKit and
`skwasm` renderer from `www.gstatic.com`, which the remote environment's
network egress policy refuses (measured 2026-09-04: the agent proxy answers
403 to `CONNECT www.gstatic.com:443`, and the browser stops at the Flutter
splash). A local run works; a remote one cannot.

**Why it matters.** Several interface items are queued behind this one -
`PL-CC23` (fit the chart's vertical axis to the run), `PL-SSBP` (the chart
time-base selector), `PL-F52R` (the MAC-awake reference band), `PL-DR1Z` (the
control-input timeline) - and each carries a claim that only a rendered
frame settles: whether a row reflows, whether an axis crowds, whether a
label wraps. Several existing comments in `app/simulation_view.py` record
measurements "by rendering the running app at each step", so the project
already relies on that check. A remote session cannot repeat it and today
nothing says so, which means the next session either burns time discovering
the block or quietly skips the verification.

**Where.** `docs/worker.md`, and possibly the session-start digest.

**Decision needed.** Remove the limitation, or document it? Allowing
`www.gstatic.com` through the remote environment's egress policy, or serving
CanvasKit locally, would let a remote session render the app - and only the
owner can change that policy. Documenting the block instead is cheap and
certain but leaves four queued interface items unable to verify what they
claim. Answer that first; the work below assumes the documenting branch.

**Approach.** Write down what a remote session can and cannot establish, and
what it should do instead: assert the assembled control tree (sizes, ordering,
the shared baseline, `col` spans) in `tests/unit/test_simulation_view.py`,
which is Flet-real and catches structure but not pixels, and say plainly in
the reply that layout was not visually confirmed so the owner knows to look.
Check first whether the environment's egress policy can simply allow
`www.gstatic.com`, or whether Flet can be pointed at a locally served
CanvasKit - either would remove the limitation rather than document it, and is
the better outcome if it is available.

**Done when.** A session that needs to see the interface knows, before trying,
whether it can - and knows what to do instead when it cannot.
