---
id: PL-6VZF
title: Reopen the session network setting: weigh the allowlist's recorded reasons against what it cost in the 2026-11-10 design round
priority: P2
effort: S
status: done
classes: docs, infra
milestone: v0.6.18
touches: .claude/rules/citing-sources.md, CLAUDE.md, .claude/rules/instruction-writing.md, docs/resident-instructions.md, docs/worker.md, docs/items/PL-HS9M-the-interface-pass-has-no-agreed-order-of-work.md
added: 2026-11-11
closed: 2026-11-11
pr: 2111
payoff: a session can read any primary source before it cites it, and no citation reaches the owner from memory
verify: grep -qF 'Never cite a source from memory' CLAUDE.md && grep -qF 'Direct HTTP reaches any host' .claude/rules/citing-sources.md && ! grep -qF 'allowed domains where no session can read them' .claude/rules/instruction-writing.md
---

**Problem.** Reopen the session network setting: weigh the allowlist's recorded reasons against what it cost in the 2026-11-10 design round


**The decision being reopened.** `.claude/rules/citing-sources.md` records
that the session environment's network access is on `Custom`, an allowlist
(project owner, 2026-09-19, ratified, over `Full`), "chosen because this
repository is public, its copyright exposure is not yet closed, and an
allowlist is a record of what a session could reach where `Full` is not". A
ratified decision reopens on ordinary evidence. On 2026-11-10 the owner asked:
"I feel like you just back door everything when you can by search or pubmed or
whatever and we cite our sources so is not having an open policy to the web
really beneficial?"

**What happened in the 2026-11-10 design round** (`PL-HS9M`).

- No session evaded the allowlist. The routes used were the PubMed connector,
  hosts already on the list, and two hosts the owner approved one at a time:
  `www.ncsa.illinois.edu` and `www.nngroup.com`.
- Seven hosts were refused before that: `www.w3.org`, `www.nngroup.com`,
  `en.wikipedia.org`, `rsms.me`, `m3.material.io`, `carbondesignsystem.com`
  and `www.ncsa.illinois.edu`. `publish.illinois.edu`, `www.usability.gov` and
  `www.edwardtufte.com` were refused later.
- Five claims reached the owner marked "from memory" because their sources were
  on refused hosts. Four were confirmed once a host was approved, and one,
  a quotation from Tufte, is still unconfirmed.
- Part of that cost was the session's own order of work. It could have asked
  for the hosts before citing from memory, as `.claude/rules/citing-sources.md`
  says a refused host is no reason to fall back on memory.
- A session with no owner present cannot get a host approved at all.

**The three reasons, against that evidence.**

1. Copyright. The allowlist already permits the publishers whose full text
   carries the most copyright risk: `onlinelibrary.wiley.com`,
   `link.springer.com` and `*.sciencedirect.com`. It refuses W3C and Wikipedia.
   What a session commits to a public repository creates the exposure, and
   the list does not control that.
2. A record of what a session could reach. The list records reach. A citation
   records what was read, and that is the record a reviewer of a stored value
   uses.
3. Not in the recorded reasons, but real: a narrower network means less
   untrusted text for a session to read, and fewer places it could send data.
   Package registries are already open, sessions already push to a public
   repository, and a simulator change already waits for the owner's review
   before it merges, so the list adds little here.

**Recommendation (session, 2026-11-10, not yet answered by the owner).** Move
the environment to `Full`, on two conditions that put the control where it
works:

1. Every citation keeps saying how its source was read: the full text, an
   abstract, a secondary source, or memory. `.claude/rules/citing-sources.md`
   already asks for the route to be recorded.
2. No fetched full text, figure or screenshot from a third party is committed.
   Check whether a rule or a check already enforces that, and add one if not.

The cost of `Full` is that the stored list is discarded, and that sessions will
read pages nobody chose in advance.

**The alternative.** Keep `Custom` and add the primary-source hosts the
project keeps meeting. Each new field then costs more approvals, and sessions
with no owner present still fall back on weaker sources.

**If the owner chooses `Full`.** `.claude/rules/citing-sources.md` states the
`Custom` setting and its reasons, so it is edited in the same change.

**Decided 2026-11-10: `Full`, and no citation from memory.** The owner
answered: "Agree with rec for 1. Except you should never cite anything from
memory. Should always look it up". So the decision is `Full` (project owner,
2026-11-10, ratified, over keeping `Custom` and adding hosts), and condition 1
above is stricter than the session recommended: memory is not a route at all
(project owner, 2026-11-10, specified).

**What changed.**

- The environment. The session sent the change to the Default environment and
  the owner approved it. Four hosts that had been refused then answered a
  probe: `www.w3.org`, `en.wikipedia.org`, `www.usability.gov` and
  `www.edwardtufte.com`. The Default environment is the owner's personal one,
  so every session of theirs that uses it has the open setting.
- `CLAUDE.md` § "Proactive expert review and domain best practices" now says
  never to cite a source from memory: read it in the session, say what was
  read, and do not cite a source that cannot be read. It is resident because a
  citation is given in a reply.
- `.claude/rules/instruction-writing.md` rule 14 lost its sentence about the
  allowed domains, which pays for the new one. `docs/resident-instructions.md`
  records both.
- `.claude/rules/citing-sources.md` § "Direct HTTP reaches any host, and a
  publisher can still refuse" replaces the allowlist section.
  `docs/worker.md` § "Reaching a source" says the same to a worker.

**Condition 2 needed no new rule.** `docs/references/README.md` §
"Redistribution" already says which files this public repository may hold, and
the citing rule now points at it. `git ls-files` shows no tracked PDF. A check
that refuses a tracked full text is filed separately.

**The list that `Full` discarded**, to restore `Custom` from: `doi.org`,
`api.crossref.org`, `api.openalex.org`, `pubmed.ncbi.nlm.nih.gov`,
`eutils.ncbi.nlm.nih.gov`, `pmc.ncbi.nlm.nih.gov`, `www.ncbi.nlm.nih.gov`,
`onlinelibrary.wiley.com`, `link.springer.com`, `*.sciencedirect.com`,
`arxiv.org`, `search.worldcat.org`, `creativecommons.org`, `anthropic.com`,
`*.anthropic.com`, `claude.com`, `*.claude.com`, `blender.org`,
`*.blender.org`, `blenderartists.org`, `*.blenderartists.org`,
`docs.github.com`, `releases.astral.sh`, `*.qt.io`,
`qt-project.atlassian.net`, `www.ncsa.illinois.edu` and `www.nngroup.com`.
Package registries and the hosts of connected MCP servers were also allowed.

**Generator check.** One-off, and work the owner asked for. It reopens one
ratified decision on the owner's own question, and no reader misread a fact
the repository holds.
