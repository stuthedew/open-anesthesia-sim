---
id: PL-YTDN
title: Rename the nine item files whose slug no longer matches their title, now that docket check names them
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.29
touches: docs/items/
added: 2026-09-13
closed: 2026-09-19
pr: 712
verify: uv run pytest -q subprojects/docket/tests/test_store.py && python3 -c "import sys, pathlib; sys.path.insert(0, 'subprojects/docket/src'); from docket.store import read_items, filename_for; items = read_items(pathlib.Path('docs/items')); raise SystemExit(1 if [i for i in items if i.path and i.identifier and i.path != filename_for(i)] else 0)"
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

**Why it matters.** The advisory has no owner, so it fires on every `make
check` in every session and none of them is the session whose job it is.
`CLAUDE.md` calls an advisory nobody acts on a candidate for retirement rather
than promotion - so the choice is to discharge it once or to admit it is not
earning its place, and discharging it is cheap. A slug is also what a later
session greps `docs/items/` by when tracing why something was done, which is
why the closed files are renamed too.

**Triaged 2026-09-13, and `PL-D4GS` is dropped into this item** - the same
finding, filed independently by the session that cut v0.4.15. Three things it
carried that this brief did not, kept here:

- **The count is eight, not nine, and the list has moved.** `PL-DZFJ` was
  renamed on 2026-09-08 by `bin/docket record` as a side effect of writing a
  `pr:` number, which is `PL-LBR6`. Now: `PL-0VFF`, `PL-5N7T`, `PL-6194`,
  `PL-68XK`, `PL-K9HV`, `PL-TTMF`, `PL-XQRK`, `PL-ZX12`. Re-read the advisory
  rather than either list.
- **Check `PL-LBR6` first.** Until it lands, any `record` run renames drifted
  files underneath this pass, so the set changes without anyone deciding it.
- **This is not a sweep to run start to finish.** A rename conflicts against
  any branch editing the file. `git mv` only the files no live branch holds,
  then re-run `make check` and name the rest in the close-out for the next
  pass. `PL-ZX12` is the worked example: it was held by the stale-name batch of
  Gate 1 while `PL-D4GS` was being written.

**Done when.** `bin/docket check` no longer reports a filename-drift advisory,
or reports only files a live branch holds and the close-out names them; the
`verify:` command's own re-check (below) is clean; and nothing that referenced
a renamed file by path is broken.

**`verify:` rewritten 2026-09-13 before it was ever relied on.** The first
version ran `bin/docket check` and piped its output into `grep`, and
`docket check --verify` refused it with the reason: a nested run is told not to
replay the open items' commands, so it never prints the landed advisory - a
`grep` for that answer matches nothing whether the work is done or not, and the
inverted form passes on the strength of it. It exited 1 when it was run, for
the wrong reason, which is exactly the failure the "watch it fail for the right
reason" rule names.

It now asks the store directly, through the same `filename_for` comparison
`docket check` uses and this brief's own one-liner already carried: zero drifted
files is exit 0, any drift is exit 1. No nesting, no output parsing, and it is
the condition the work actually has to reach.

## Done, 2026-09-19: seven files, and the count in the title is historical

**The set had moved again, as the brief said it would.** Nine at the 2026-09-13
measurement, eight in `PL-D4GS`'s recount, **seven** on the tree that closed
`PL-5QLP` (`record` no longer renaming a drifted file while writing `pr:`):
`PL-0VFF`, `PL-5N7T`, `PL-68XK`, `PL-H4N8`, `PL-K9HV`, `PL-TFWR`, `PL-TTMF`.
Four of the original nine had been renamed under other work in the meantime and
two had drifted in since. The title's "nine" is left as the record of what was
asked rather than corrected, since correcting it would drift this file's own
slug.

**All seven were renamed, not six.** No branch held any of them: the one
candidate, `origin/claude/optimistic-brahmagupta-63pa72` against `PL-H4N8`,
turned out to be behind `main` on that file rather than carrying an edit of its
own - `git log origin/main..<branch> -- <path>` reports the merge commit, so the
test that decides this is `git diff $(git merge-base origin/main <branch>)..<branch> -- <path>`,
which was empty.

**`PL-TFWR` was the one the brief expected to hold back, and holding it back was
the weaker option** (project owner, 2026-09-19, ratified, over leaving it
drifted behind `PL-Y5JX`'s recorded skip). `PL-Y5JX` had deliberately skipped it on 2026-09-19 because
two items name its file by full path in `touches:`, and a rename leaves those
declarations pointing at nothing - silently, since a `touches` entry naming a
missing path is not yet an error. That hazard is *a declaration broken without
anybody noticing*, not the rename itself, so it is removed by repairing the
declarations rather than by deferring the rename forever:
`PL-3V6C` (closed) and `PL-77SV` (open, and the one that matters, since a live
item's `touches` is read by `concurrent`, the lane split and `verify`) were
updated in the same commit. Leaving it would also have failed this item's own
`verify:`, which demands zero drift, and left the advisory firing on one file in
every session indefinitely.

**The brief's own re-check one-liner under-reports, and that is worth knowing
before the next pass.** It scans `verify` and the body and **not** `touches`,
which is where both real couplings lived - so it returned "0 of the 9" here too,
while the true answer was two live declarations. Recorded on `PL-Y5JX`, whose
guard is still owed.

**Not promoted to an error.** The brief asks whether the advisory should become
a hard failure now that the count is zero; it should not, yet. Nothing warns a
session that the file it is about to rename is named by another item's
`touches`, so a hard error would compel exactly the rename that breaks a
declaration. `PL-Y5JX` builds that warning; the promotion is filed behind it.
