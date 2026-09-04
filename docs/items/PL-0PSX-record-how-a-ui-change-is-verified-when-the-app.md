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

**Appended 2026-09-04 (PL-F52R) — the Problem statement's conclusion is false,
and this item's own Approach is what disproved it.** The Approach above says to
"check first whether the environment's egress policy can simply allow
`www.gstatic.com`, or whether Flet can be pointed at a locally served
CanvasKit — either would remove the limitation rather than document it". That
check has now been run, and the second branch is available, free, and needs no
policy change from the owner.

**What is true and what is not.** The measurement is right: the agent proxy
does refuse `www.gstatic.com`, and without a flag the browser stops at the
Flutter splash with no error anywhere — which is why the wrong conclusion is an
easy one to reach. What does not follow is "a remote one cannot". `flet_web`
already ships the renderer locally, at
`.venv/lib/python3.14/site-packages/flet_web/web/canvaskit/`, and
`FLET_WEB_NO_CDN=true` is the flag that makes Flutter's bootstrap use it
instead of the CDN. Nothing is fetched from `gstatic` when it is set.

**Rendered here on 2026-09-04, with the run driven and the chart read.**

```
FLET_FORCE_WEB_SERVER=true FLET_WEB_NO_CDN=true \
  FLET_SERVER_PORT=8551 FLET_SERVER_IP=127.0.0.1 uv run python <entry>.py
```

Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, headless,
with `--no-sandbox --no-proxy-server --remote-debugging-port=9222`, driven over
the DevTools protocol with the `websockets` package the project venv already
carries — `Page.navigate`, `Emulation.setDeviceMetricsOverride`,
`Input.dispatchMouseEvent` to press Start by coordinate (Flutter draws to a
canvas, so there is no DOM to click), and `Page.captureScreenshot` with a
`clip` for a zoomed region. Playwright is not required and is not installed.
The run reached 31.5 s of simulated time with all six traces drawn.

**So the "Why it matters" is inverted too.** `PL-F52R` is named there as an
item carrying a claim only a rendered frame settles. That frame was rendered,
it settled the claim, and it also found what no unit test would have: the
MAC-awake band spans 2.5 % of the plot height and reads as a thick line rather
than a band. That finding went to `PL-CC23`. The remaining three interface
items are not blocked either.

**What is left of this item.** The want is still real — a session should know
how to see the interface without deriving it — but that is `PL-CQRL` (record
how to drive this app in a browser from a container session), captured
2026-09-02, which already holds the recipe and proposes a skill as its home.
`PL-CQRL` predates this capture and says in terms that a live client *is*
available; this item was written without it. Two dispositions, both the
owner's: retitle and re-scope this one around what a remote session genuinely
cannot do (there is still no way to judge a rendered frame automatically), or
drop it as a duplicate of `PL-CQRL` with the recipe above folded in. Either
way the `Decision needed.` as posed no longer has a question in it, and the
title and Problem statement must not stand as they are — a session reading
them will believe something false and skip a check it could have run.

**The block is wider than rendering, and there is a working route (measured
2026-09-04).** This brief frames the limitation as Flet's client failing to
fetch CanvasKit from `www.gstatic.com`. The same egress policy also refuses
**primary literature**: `CONNECT` was rejected for ScienceDirect, Springer,
`doi.org`, Crossref, OpenAlex, Semantic Scholar and arXiv, and `curl` is blocked
on the same policy.

That matters beyond layout. `PL-F52R` (the MAC-awake band) required MAC-awake
values sourced from the primary literature and said explicitly that they "must
not be taken from memory" - and a citation recorded from a search-result snippet
is indistinguishable, in the data file, from one read at the source. The same
applies to every remaining `model-spec-accuracy` item, `PL-6Q8N` above all.

**The PubMed MCP server works and is the route to record here.** Verified
end-to-end in the same session: search returns hits (`"MAC-awake" AND
sevoflurane`, 23 results) and metadata retrieval returns abstract, journal,
volume/issue/pages and DOI. So the honest instruction is not "you cannot reach
the literature" - it is "direct HTTP to publishers is refused; use the PubMed
MCP server, and say in the reply which route a citation came from and whether
full text or only the abstract was read".

Recording both halves is the point. A session told only that the environment is
restricted concludes the literature is unreachable and falls back to memory,
which is the specific failure the safety-critical standard forbids.
