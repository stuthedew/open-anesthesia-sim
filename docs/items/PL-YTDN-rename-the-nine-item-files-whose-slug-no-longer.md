---
id: PL-YTDN
title: Rename the nine item files whose slug no longer matches their title, now that docket check names them
status: untriaged
added: 2026-09-13
---

**Problem.** Rename the nine item files whose slug no longer matches their title, now that docket check names them

Measured 2026-09-13, on the tree that closed `PL-3833`: nine of 810 item
files carry a slug their title no longer generates — `PL-0VFF`, `PL-5N7T`,
`PL-6194`, `PL-68XK`, `PL-DZFJ`, `PL-K9HV`, `PL-TTMF`, `PL-XQRK`, `PL-ZX12`.
`bin/docket check` now names all nine on one advisory line; this item is the
pass that discharges it.

**Why it is a separate item.** `PL-3833` deliberately stopped at reporting.
Its own 2026-09-08 addendum records why: a rename arriving as a side effect
of an unrelated command made `PL-36R4` a rename-against-edit conflict for
whoever merged second, so the safe split is to report the drift and leave the
rename to a session that has checked who else holds the file. Four of the
nine (`PL-0VFF`, `PL-6194`, `PL-DZFJ`, `PL-ZX12`) are open Gate 1 entries, so
this wants a moment when no gate session is running.

**Done when.** The nine files are renamed with `git mv` to the name
`docket.store.filename_for` writes, the advisory is silent, and `make check`
passes. Worth asking at that point whether the check should be promoted from
an advisory to an error, which is only safe once the count is zero.

**Checked 2026-09-13, after `PL-3833` landed: the rename is safe today, and
the reason it is safe will not hold forever.**

The hazard is that an item's `verify:` command can hardcode another item's
file path, and a rename then breaks a command nobody was looking at.
`PL-JRPP` is the shape — a closed item whose command greps
`docs/items/PL-MGF9-the-process-work-grooming-advisory-only.md` by full path.

Measured against the store on `origin/main` at `de6baee`:

- **0 of the 9 drifted files** are referenced by path in any other item's
  `verify:` command or brief. So this pass can rename all nine without
  breaking anything.
- **34 items do hardcode some item file path in their `verify:` command.**
  None of those targets has drifted yet. The coupling is latent, not
  theoretical: the next title edited in place on one of those 34 targets
  creates exactly the breakage this bullet rules out today.

So re-run the first check before renaming rather than trusting this note —
the store moves. The one-liner:

```
python3 - <<'PY'
import sys, pathlib
sys.path.insert(0, "subprojects/docket/src")
from docket.store import read_items, filename_for
items = read_items(pathlib.Path("docs/items"))
drift = {i.identifier: i.path for i in items
         if i.path and i.identifier and i.path != filename_for(i)}
for i in items:
    text = (i.verify or "") + "\n" + (i.body or "")
    for d, path in drift.items():
        if path in text and i.identifier != d:
            print(f"{i.identifier} references {d}'s path - renaming {d} breaks it")
PY
```

**The split, for scoping.** Of the nine, **6 are open** (`PL-0VFF`, `PL-5N7T`,
`PL-6194`, `PL-TTMF`, `PL-XQRK`, `PL-ZX12`) and **3 are closed** (`PL-68XK`
dropped, `PL-DZFJ` done, `PL-K9HV` dropped). Rename all nine rather than the
open six: findability by `ls docs/items/ | grep` is the whole point of the
slug, and a closed item is precisely what a later session looks up by name
when tracing why something was done. The check reports closed items
deliberately for the same reason.
