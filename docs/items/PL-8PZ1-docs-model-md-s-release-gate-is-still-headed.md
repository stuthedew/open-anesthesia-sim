---
id: PL-8PZ1
title: docs/MODEL.md's release gate is still headed 'Version v0.1.0 is complete only when', but entries are being added to it for v0.3.0
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-02
closed: 2026-09-13
pr: 507
verify: python3 tools/doc_check.py check && ! grep -q 'Version v0.1.0 is complete only when' docs/MODEL.md
---

**Problem.** `docs/MODEL.md`'s `## Release gate` section opens `Version v0.1.0
is complete only when:` and lists fifteen criteria beneath it. Those criteria
are the standing gate every release passes, not v0.1.0's: entries have been
added to the list since, most recently "the published wash-in validation passes
for every agent and cohort", which arrived with `PL-9Y42` in the v0.3.0 window
— four releases after v0.1.0 shipped. Several criteria could not have been
v0.1.0's at all, since they name agents and cohorts that did not exist until
v0.2.0.

**Why it matters.** `docs/MODEL.md` is the authoritative model specification,
so a scope statement it gets wrong is not cosmetic. A reader checking whether
the current release satisfies the gate has first to decide whether the section
applies to it, and the honest reading of the heading is that it does not — so
the gate is either ignored or applied at a v0.1.0-era bar. It is the same
failure as `PL-C1KK` (MODEL.md still names v0.2.3 as the current baseline) one
section over, and the pair of them is the argument for making these statements
version-generic rather than repairing each as it goes stale.

**Where.** `docs/MODEL.md`, the `## Release gate` section: the lead-in line,
and any criterion whose wording assumes one agent or one milestone.

**Approach.** Two candidates. Make the lead-in version-generic — "A release is
complete only when:" — or keep a version in it and state which release it
currently governs. The first is preferred: the criteria beneath are already
generic, and a heading naming a version is a second thing to keep true, which
is exactly what failed here and in `PL-C1KK`.

**Found.** 2026-09-02, captured during a queue review and triaged in the
v0.2.9 release pass.

**Done when.** No heading or lead-in in `docs/MODEL.md` scopes the release gate
to a version it no longer governs, and the section reads as what it is: the
standing gate every release passes.


**Closed 2026-09-13.** The lead-in is now "A release is complete only when:",
the version-generic option the brief preferred, with a paragraph above it saying
that this is the standing gate, why the v0.1.0 lead-in survived four releases,
and why a heading naming a version is a second thing to keep true (`PL-C1KK`).
No criterion beneath needed rewording: the one version any of them names is
v0.0.2's circuit reference set, which is the identity of a test set rather than
a scope claim.
