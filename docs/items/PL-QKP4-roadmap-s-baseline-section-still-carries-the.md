---
id: PL-QKP4
title: ROADMAP's baseline section still carries the previous release's detail paragraphs under the current release's heading, with an orphaned 'v0.4.7.' line where a cut truncated a sentence
status: dropped
added: 2026-09-08
closed: 2026-09-12
reason: Already fixed. Verified 2026-09-12 against ROADMAP.md: the 'Current baseline: v0.4.13' section carries v0.4.13's own detail paragraphs, and no orphaned version line survives anywhere in the file (grep -nE '^v0\.4\.[0-9]+\.?\s*$' matches nothing). The residue this item describes was left by the v0.4.8 cut and cleared by one of the five cuts since. Filed 2026-09-08 and overtaken by ordinary release work, which is the argument for the release-time staleness list bin/docket release already prints rather than for a queue item.
---

**Problem.** ROADMAP's baseline section still carries the previous release's detail paragraphs under the current release's heading, with an orphaned 'v0.4.7.' line where a cut truncated a sentence
