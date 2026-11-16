---
id: PL-41CR
title: docs/interface-provenance.md says the blender.org hosts answered a probe on 2026-09-26, then says wm_window.cc was read through the GitHub mirror on 2026-09-27 because the Manual page was not reachable; which is right? (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-05
closed: 2026-11-14
pr: 2162
payoff: no later session skips a reachable Blender page because this document says it could not be reached
verify: ! grep -qF 'page was not reachable from the container' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md says the blender.org hosts answered a probe on 2026-09-26, then says wm_window.cc was read through the GitHub mirror on 2026-09-27 because the Manual page was not reachable; which is right? (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on when the Blender hosts could be reached:** rows 134-146 say "The hosts answered a probe on 2026-09-26 (`PL-M701`)". Rows 931-941 say `wm_window.cc` was read on 2026-09-27 "through the GitHub mirror, because the Manual page was not reachable from the container". Which is right?

**Checked 2026-11-09:** `grep -n 'answered a probe\|not reachable' docs/interface-provenance.md` finds both sentences. § "What the code cannot answer: Blender's stated reasoning" says the `blender.org` hosts answered a probe on 2026-09-26 (`PL-M701`). The Adopted entry on the maximized window says `wm_window.cc` was read through the GitHub mirror on 2026-09-27, "because the Manual's page was not reachable from the container". `PL-M701` probed `docs.blender.org`, `developer.blender.org`, `www.blender.org`, `archive.blender.org` and `projects.blender.org` on 2026-09-26, and all of them answered. It also confirmed that the owner had `blender.org` and `*.blender.org` on the allowed domains. The second sentence was written a day later by `PL-Z4K6` (#1182), and no probe is recorded for it. So the reason it gives is the claim `PL-M701` had just found false. Reading the C++ source through the GitHub mirror is a fair route in any case, because the Manual does not hold the source.

**Why it matters.** A later session reading "not reachable from the container" may skip a reachable Blender page and work from memory or a mirror, which is the failure `PL-M701` recorded.

**Done when.** The `wm_window.cc` sentence says that the file was read through the GitHub mirror on 2026-09-27, and gives no reachability claim that no probe supports.

**Generator check.** Belongs to `PL-CLW5`'s fact, "Whether a host answers through this container's egress proxy: a dated probe, not a standing fact". The sentence carries its date, which is what `PL-CLW5`'s check asks, and was written on 2026-09-27, before `PL-CLW5` closed on 2026-10-06. So it is not a post-close instance: it is a one-off from the `docs/interface-provenance.md` structure read.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already says `wm_window.cc` was read through the GitHub mirror "since the Manual's page was not reachable" (row 801). `PL-M701` had recorded the hosts as reachable on 2026-09-26. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

**Built 2026-11-14.** The `wm_window.cc` sentence now says only that the file was read through the GitHub mirror on 2026-09-27, and adds that the Manual does not hold the source, which is why a source file is read from a mirror at all. It makes no reachability claim. Docs swept: `docs/interface-provenance.md` (`grep -n 'reachable\|probe'` finds only § "What the code cannot answer"'s dated 2026-09-26 probe, which `PL-M701` records).
