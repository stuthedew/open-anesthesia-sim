---
id: PL-XG77
title: Five closed briefs wrap a code span across the start of a list item, a block quote or an HTML block, so GitHub renders each with stray backticks; live, in closed items only
status: untriaged
touches: docs/items
added: 2026-10-04
---

**Problem.** Five closed briefs wrap a code span across the start of a list item, a block quote or an HTML block, so GitHub renders each with stray backticks; live, in closed items only

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Each pairs two backticks across a block start, which CommonMark § 6.1 does not, so GitHub shows the delimiters literally: `PL-D2GW`:127-129 (a list item), `PL-DL4M`:23-24 (a list item), `PL-KQHN`:109-110 (a block quote), `PL-Q2BJ`:49-50 (a list item) and `PL-RLTK`:61-62 (a `<base>` HTML block). The `prose-renders-as-written` shape (`PL-N7LK`), in briefs nobody reads for a verdict; the reader half is the sweep's paragraph-end member.
