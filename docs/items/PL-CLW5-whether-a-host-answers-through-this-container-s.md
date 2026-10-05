---
id: PL-CLW5
title: Whether a host answers through this container's egress proxy is a dated probe, but the tree states it as a standing property of the environment - quality.yml (docs.github.com), docs/references/README.md (doi.org), qt_widgets.py and contrast_check.py (w3.org) - so each change to the allowed domains leaves sentences that send a session around a route that now works
priority: P1
effort: M
status: ready
classes: defect
feature: host-reachability
touches: .github/workflows/quality.yml, docs/references/README.md, src/anesthesia_sim/app/qt_widgets.py, tools/contrast_check.py, tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a session reading that a host is blocked sees when that was probed, so it tries a route that now works instead of working around it
verify: grep -q 'def test_a_host_block_claim_without_its_probe_date_is_refused' tests/unit/test_doc_check.py
root-cause-of: PL-M701, PL-P5NB, PL-B3MK
generator: live - present-tense block claims still stand at four sites on 2026-10-05, two of them already false, and each change to the allowed domains can falsify the rest
misread: Whether a host answers through this container's egress proxy: a dated probe, not a standing fact
---

**Problem.** Whether a host answers through this container's egress proxy is a
dated probe: the owner changes the allowed domains in settings no file reads.
The tree states it in the present tense, as a property of the environment, at
four sites still standing on 2026-10-05:

- `.github/workflows/quality.yml`, the comment above `concurrency:`:
  `docs.github.com` and `github.blog` "are both blocked by this container's
  egress proxy" (`PL-B3MK`);
- `docs/references/README.md`, the Jugel et al. entry: `www.vldb.org` and
  `doi.org` "are both blocked by the session egress proxy" (`PL-P5NB`);
- `src/anesthesia_sim/app/qt_widgets.py` and `tools/contrast_check.py`:
  `w3.org` "is"/"returns" `EGRESS_BLOCKED` from this container (`PL-JX0Z`).

**Reproduced 2026-10-05**, `curl -sS -o /dev/null -m 20 -w '%{http_code}'` from
the cloud container: `https://doi.org/` 301 and `https://docs.github.com/` 302,
past CONNECT, so two of the four sentences are already false;
`https://www.w3.org/TR/WCAG22/`, `https://github.blog/` and
`https://www.vldb.org/` 000, refused, so the other two are true today and
written as if they always will be.

**Why it matters.** A session reads the sentence, believes the route is closed
and works around a source it could have read - GitHub's own workflow prose for
`PL-B3MK`, a DOI registry for `PL-P5NB` - or rests a claim on memory instead.
`PL-M701` fixed the reader side (rule 14 of
`.claude/rules/instruction-writing.md`: probe before repeating a block, and
count only a refusal at CONNECT) and re-dated the `blender.org` sentences, but
swept no other file, so the writer side keeps producing members.

**Generator check.** This is the head. Misread fact: whether a host answers
through this container's egress proxy, which is a dated probe and not a
property of the environment. Members: `PL-M701` (closed 2026-09-26,
`blender.org`), `PL-P5NB` (`doi.org`) and `PL-B3MK` (`docs.github.com`, a
re-entry of `PL-M701` at a sibling site, filed nine days after it closed). No
head's `misread:` stated it (`bin/docket generators --misread`, 2026-10-05);
found by the 2026-10-05 triage pass reading `PL-B3MK`.

**Done when.** Every sentence in the tree saying a host is blocked or refused
carries the date it was probed, and the four above are re-dated or corrected
against a fresh probe (closing `PL-P5NB` and `PL-B3MK` with it, or leaving each
its own route fix); and the decidable half is in code, since a dated claim is a
pattern a script can hold: a check in `tools/doc_check.py` refuses a host-block
claim with no date beside it, pinned by
`test_a_host_block_claim_without_its_probe_date_is_refused` in
`tests/unit/test_doc_check.py`. Whether the claims instead move to one dated
record that the other sites cite is the implementing session's call. This fixes
a live generator, so the pause on new workflow mechanisms does not hold it
(`CLAUDE.md` § "What this project is").
