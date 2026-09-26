---
id: PL-M701
title: Sessions repeat ROADMAP.md's and docs/interface-provenance.md's claim that blender.org is blocked without probing it, though every blender.org host answers through the proxy on 2026-09-26 and the owner has it on the allowed domains
priority: P2
effort: S
status: ready
classes: docs
touches: .claude/rules/instruction-writing.md, ROADMAP.md, docs/interface-provenance.md, docs/items/PL-PV5Q-docs-interface-provenance-md-s-stated-rationale.md
added: 2026-09-26
payoff: a session probes a host before calling it blocked, so work that needs blender.org or any other allowed host is attempted rather than skipped on a dated note
verify: grep -qi 'reachab' .claude/rules/instruction-writing.md && ! grep -qE '(is|are) refused by this environment' docs/interface-provenance.md && ! grep -qF 'is blocked by the session egress proxy' ROADMAP.md
---

**Problem.** Sessions repeat ROADMAP.md's and docs/interface-provenance.md's claim that blender.org is blocked without probing it, though every blender.org host answers through the proxy on 2026-09-26 and the owner has it on the allowed domains

**Found 2026-09-26.** A session asked what v0.6.0 holds told the project owner
`blender.org` was blocked. It was repeating `ROADMAP.md` and never probed. The
owner corrected it and said: "This is an issue if you assume things are blocked
when they aren't" (project owner, 2026-09-26). Probed the same day through the
proxy, reading curl's `%{http_connect}` so that an origin refusal is not taken
for a proxy denial: `docs.blender.org`, `developer.blender.org`,
`www.blender.org`, `archive.blender.org` and `projects.blender.org` all
returned 200 at CONNECT, and `web.archive.org` returned 403. The owner
confirmed that `blender.org` and `*.blender.org` are on the environment's
allowed domains.

**The stale statements**, each written in the present tense on or about
2026-09-16:

- `ROADMAP.md`, the `PL-PV5Q` bullet under "Explicitly out of scope for
  v0.6.0": "`blender.org` is egress-blocked from this project's sessions".
- `ROADMAP.md`, planned-milestone item 34: "`docs.blender.org` is blocked by
  the session egress proxy".
- `docs/interface-provenance.md` § "How this study was conducted, and where it
  could not reach", and the opening of § "What the code cannot answer".
- `PL-PV5Q`'s premise, that the pages it re-reads against cannot be reached.

**Why it matters.** Whether a host is reachable is a fact about the environment
on the day it was measured, and the owner changes the allowed domains in the
environment's settings, which no session can read -
`$HTTPS_PROXY/__agentproxy/status` reports the proxy's state, not its policy.
Written in the present tense, a block reads as permanent, and a session skips
work it could do: `PL-PV5Q` has waited since 2026-09-16 for "a session that can
reach those pages".

**Done when.** Each stale statement says when the block was seen and that it no
longer holds. Rule 14's re-verification bullet in
`.claude/rules/instruction-writing.md` names reachability as external state, to
be probed before it is repeated. `PL-PV5Q` records that its pages can be read.

**Generator check.** One-off, and work the owner asked for. The misread fact is
that a reachability statement records the environment on the day it was
measured; no head's `misread:` states it, and no check encodes it.

**The allowed domains, as the owner listed them on 2026-09-26** - a dated
snapshot for whoever works this, not a standing list, since the owner edits it
in the environment's settings: `doi.org`, `api.crossref.org`,
`api.openalex.org`, `pubmed.ncbi.nlm.nih.gov`, `eutils.ncbi.nlm.nih.gov`,
`pmc.ncbi.nlm.nih.gov`, `www.ncbi.nlm.nih.gov`, `onlinelibrary.wiley.com`,
`link.springer.com`, `*.sciencedirect.com`, `arxiv.org`,
`search.worldcat.org`, `creativecommons.org`, `anthropic.com`,
`*.anthropic.com`, `claude.com`, `*.claude.com`, `blender.org`,
`*.blender.org`, `blenderartists.org`, `*.blenderartists.org`,
`docs.github.com`, `releases.astral.sh`. The same day's probes agreed with it:
`github.com` and `raw.githubusercontent.com` also answered without being
listed, and `doc.qt.io`, `docs.python.org`, `web.archive.org`,
`journals.lww.com`, `pubs.asahq.org`, `academic.oup.com`,
`www.bjanaesthesia.org`, `www.nature.com`, `www.gasmanweb.com` and
`www.wikipedia.org` returned 403 at CONNECT.
