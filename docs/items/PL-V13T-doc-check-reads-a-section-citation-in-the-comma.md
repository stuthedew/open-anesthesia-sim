---
id: PL-V13T
title: doc_check reads a section citation in the comma form but not the section-mark form, so 285 of the 324 citations in the tree are unchecked while the run reports they all resolve
priority: P2
effort: S
status: done
closed: 2026-09-13
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items/, ROADMAP.md
added: 2026-09-13
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_section_mark_citation_is_checked_like_a_comma_one' tests/unit/test_doc_check.py
---

**Problem.** `doc_check`'s `QUOTED_SOURCE_RE` - the pattern that checks a
citation naming its own document, and the only one that runs over the queue and
the source docstrings - allowed `,` or `:` between the document and the
quotation and nothing else:

```python
r"`(?P<document>[\w./-]+\.md)`[ \n]*[,:]?[ \n]*"
```

This repository writes its citations with a section mark: ``docs/MODEL.md` §
"Supported input ranges"`. That form matched nothing, and matching nothing is
silent - so every one of them was skipped while the run printed that "the
citations in the documentation, the queue and the source docstrings all
resolve".

**Measured 2026-09-13**, across `*.py` and `*.md` outside `.git`:

```text
  `<document>.md` § "Section"   285 occurrences   unchecked
  `<document>.md`, "Section"     39 occurrences   checked
```

88% of the tree's document-section citations were unchecked. The A/B that
settles it, run against `core/exceptions.py` with a section name no file has:
the `§` form gave **0 errors**, the comma form gave **1**.

**Why it matters.** `CLAUDE.md` names this failure exactly - a check that
"gives a wrong answer silently, so a check passes while the guarantee it stands
for is void" is the first of its three tests for friction that must be raised
rather than filed. It is also upstream of a queue item: `PL-VZL0` exists to
cite `docs/MODEL.md` from every `core/` function implementing a governing
equation, in the `§` form, *specifically* so the citations are enforced - its
brief says that without enforcement "these citations are unenforced prose, and
a section rename would silently orphan every one of them, which is the failure
mode the citation is being added to prevent". `PL-X2XX` was believed to have
delivered that check and had not, for the form the project writes.

**A second defect was hiding behind the first.** With `§` recognised, 18 errors
surfaced; 11 were one false positive. A quotation inside a `>` blockquote
carries the marker of every line it wraps onto, so

```markdown
> `ROADMAP.md` § "v0.5.1 -
> the interface moves to Qt"
```

compared as `v0.5.1 - > the interface moves to Qt` and failed against a heading
that is present at `ROADMAP.md:2255`. All eleven were the Qt-port deferral note
the project owner added to six item files on 2026-09-10. `_normalized` now
strips a blockquote or list marker that *opens a continued line* before joining;
a marker inside the text is untouched.

**Seven of the remaining eight were genuinely stale, and had been invisible.**
All are historical pointers in closed items, repaired by what actually happened
to each target rather than by re-pointing them all:

```text
renamed in place   docs/WORKING_NOTES.md, the UI structure/form mockups
                   section, now headed "Shelved, then resumed" where it was
                   headed "Shelved". Same section, so the pointer moves.
                   Two sites, one of them ROADMAP.md:3427, a live document.

deleted outright   README.md's Current status section went with the root
                   README in #366 and the rewritten README has no
                   equivalent. A pointer cannot be repaired, so those three
                   stop being quotations and become descriptions, which is
                   honest about a section that no longer exists and is not
                   read as a citation.

version-stamped    ROADMAP.md's current-baseline heading carries the version,
                   so it moved from v0.4.10 to v0.4.14. PL-WSDY was about the
                   v0.4.10 baseline specifically, so re-pointing it would make
                   a closed item cite a section it never read. De-quoted for
                   the same reason. This is the recurring case: every citation
                   of that heading goes stale at every release.
```

**Done when.** `doc_check` reads the `§` form, a wrapped blockquote citation is
not reported stale, both are pinned by tests that fail without the fix
(mutation-checked, separately, 2026-09-13), and the tree is at 0 errors with
the check now actually looking.

**Not done here.** Nothing was converted between the two forms. 285 `§` and 39
comma citations both work and both are now checked; picking one is a
readability question, not a correctness one, and would be a large mechanical
diff for no change in what is enforced.

**Writing this item up tripped the fix, which is the limitation worth
recording.** The five examples above were reported as citations, because
nothing distinguishes *making* a citation from *discussing* one - a check
reading prose cannot see the difference, and should not try to. They are in
fenced blocks instead, which `doc_check` already skips for this reason
(`test_a_quoted_source_inside_a_fence_is_not_a_citation`). Any future item
about a stale citation has to do the same.
