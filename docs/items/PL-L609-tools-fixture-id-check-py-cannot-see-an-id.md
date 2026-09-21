---
id: PL-L609
title: tools/fixture_id_check.py cannot see an id spelled with underscores as a keyword argument, which is how PL-AAAA-open.md reached the doc_check fixtures
priority: P2
effort: S
status: done
classes: defect, infra
feature: one-id-grammar
milestone: v0.5.2
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md
added: 2026-09-21
closed: 2026-09-21
pr: 870
payoff: an id spelled as a keyword argument is judged by the same grammar as one spelled as a literal, so the form that kept four fixture ids out of the scan cannot hide a malformed one
verify: grep -q 'def test_an_id_spelled_as_a_keyword_argument_is_judged' tests/unit/test_fixture_id_check.py
---

**Problem.** `tools/fixture_id_check.py` matches `(?<![A-Za-z0-9])PL-[A-Za-z0-9]+`
and so cannot see an id written with an underscore separator. That form exists
because a fixture id has to be a keyword argument:
`tests/unit/test_doc_check.py`'s `_items(root, **briefs)` writes
`items / f"{name.replace('_', '-')}.md"`, so `PL_AAAA_open=` produced
`PL-AAAA-open.md` - an unmintable id reaching the tree in the one spelling the
check cannot read.

**Why it matters.** It is the same vacuous-assertion hazard as `PL-GXPP`, in a
form the new guard is blind to, in the one file that has the helper making it
convenient. Four instances existed; `PL-7922` renamed them to `PL_8888_open`
while adding the check, so nothing is currently wrong and nothing would say so
if it were.

**One correction to the framing above, verified 2026-09-21.** The filename is
not what made those four a hazard. `doc_check._live_item_briefs` globs
`docs/items/*.md` and reads the `status:` field, `store.read_items` takes the
id from the `id:` field and passes `path.name` only for reporting, and
`_brief()` writes `id: PL-T3ST` into every fixture - so no reader parsed
`PL-AAAA-open.md` as an id and no assertion rested on it. What the four
instances demonstrate is the *spelling*: an unmintable id can be written into a
tree this check scans and the check stays silent. The next helper keyed the
same way need not be as harmless.

**Why it was not simply widened.** Adding `PL_` to the candidate pattern would
reject ordinary module constants - `PL_PREFIX`, `PL_RE`, `PL_ITEMS` - for a
reason that has nothing to do with ids, which is the false-positive class
`CLAUDE.md` retires a check for. Measured 2026-09-21: 4 `PL_[A-Za-z0-9]{3,}`
tokens in the whole repository, all of them this one fixture, so the widening
would have been free *today* and the risk is entirely about what gets written
next.

**Decision, 2026-09-21: the third candidate *and* a narrowed first, because
they answer different halves.** The three candidates were: read the kwarg name
only where it is passed to a helper that converts it to a filename; have
`_items` itself refuse a name outside the alphabet; or change the helper to
take a mapping so the ids stay hyphenated literals the existing scan already
sees.

- The mapping removes the form from the tree. `_items(root, {"PL-8888-open":
  ...})` puts the id back into a string literal, which is the scan's main rule,
  and it also retires the `**{identifier: ...}` workaround the closed-brief test
  already needed because `PL-D0N3` is not an identifier.
- It does not close the hole, though, and the hole is what the item is about:
  the four instances were already benign. A guard with a documented blind spot
  in a convenient form is a guard that gets defeated again, so the checker
  reads keyword-argument names too.
- The guard is *not* the first candidate as written. Modelling "helpers that
  convert a kwarg to a filename" needs the checker to know which helpers those
  are, which is a heuristic with a blind spot of its own. Scoping to
  `ast.keyword.arg`, translating `_` to `-` and handing the result to the
  existing `malformed()` needs no such model, gives the form no second grammar,
  and stays quiet on a mintable id spelled that way.
- The second candidate was refused: after the mapping, `_items` is the one
  helper that no longer needs a guard, and a runtime check inside it reaches
  nothing else in the tree.

**The number that would have killed it, and the count.** A keyword-name scan is
wrong if the `PL_PREFIX` class the paragraph above names can occupy the keyword
position. Measured 2026-09-21 with `ast` over every `.py` file the tool walks,
under the 3.14 interpreter so nothing was skipped: **8,098 keyword arguments,
21 carrying any uppercase letter at all, and 17 of those are Qt's
`ignoreBounds`, `rateLimit` and `userData`** - none of which can produce a `PL-`
token. The remaining 4 are this fixture. No keyword argument in this repository
is SCREAMING_SNAKE, because a keyword argument is a *parameter* name and a
module constant is a name being bound; the collision the item warned about
needs a function declaring `PL_PREFIX` as a parameter, which is a defect
before it is a false positive. The class is empty in this position, and the
`not-an-id` marker covers it if it ever is not.

**What it still cannot see, stated rather than left to be found.** A helper
that does *not* put the hyphens back - one writing `f"{name}.md"` from
`PL_8888_open` - produces a filename no store could write, and this check stays
quiet on it because the token is mintable once translated. That is a filename
shape rather than an id grammar, and this tool judges ids.

**Done when.** `tools/fixture_id_check.py` reports an unmintable id spelled as
a keyword argument with the file and line it sits on, stays quiet on a mintable
one and on every ordinary keyword argument, and takes the `not-an-id` marker
there as it does elsewhere; `tests/unit/test_doc_check.py`'s `_items` takes a
mapping keyed by the filename, so no fixture id in the repository is spelled
with underscores; and the module docstring's "what it cannot see" paragraph
names the filename-shape residue above rather than this hole.
