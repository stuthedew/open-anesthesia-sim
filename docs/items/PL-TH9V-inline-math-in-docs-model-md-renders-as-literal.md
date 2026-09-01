---
id: PL-TH9V
title: Inline math in docs/MODEL.md renders as literal parentheses on GitHub
status: untriaged
touches: docs/MODEL.md, docs/WORKING_NOTES.md, tools/doc_check.py
added: 2026-09-01
---

**Problem.** `docs/MODEL.md` writes inline math with LaTeX's `\(...\)`
delimiters, which GitHub's markdown does not recognise. `(` and `)` are ASCII
punctuation, so CommonMark consumes the backslashes as ordinary character
escapes before any math parser runs: `\(t\)` reaches the page as the literal
text `(t)`, and `\(\Delta t\)` as `(\Delta t)` — the `\D` survives only because
`D` is not escapable. The symbol table under "Symbols" is where it is most
visible; every row of it is affected. 97 occurrences in `docs/MODEL.md`, 1 in
`docs/WORKING_NOTES.md`.

Display math is unaffected: the 58 `$$` blocks render correctly. The second
half of the defect follows from the first — because inline math does not work,
single symbols have been set as display blocks mid-sentence. `docs/MODEL.md`
line 141 is the clearest case: "Let:", then `M_x` centred on its own line, then
"denote the equivalent gas volume of sevoflurane stored in compartment \(x\)."
One sentence broken across a centred equation, ending in an unrendered symbol.
Lines 115, 123, 129, 276, 282, 437 and 876 are the same shape. Once inline math
works, those collapse back into their sentences.

**Why it matters.** `docs/MODEL.md` is the authoritative specification for the
implemented model, and the symbol table is the key a reader uses to map a
displayed clinical value back to the equation and units that produced it. A key
whose left-hand column is unreadable is a traceability failure, not a cosmetic
one: `\lambda_{b:g}` shown raw does not tell a reader it is the blood:gas
partition coefficient, and the rows that do render — `(F_a)`, `(F_A)` — differ
only in a subscript's case, which is exactly the distinction the missing
formatting is supposed to carry.

**Where.** `docs/MODEL.md` (97 occurrences of `\(`, plus the short `$$` blocks
listed above), `docs/WORKING_NOTES.md` (1). Nine queue items also carry `\(`
copied out of `docs/MODEL.md`; they are internal and not part of this fix, but
whatever convention this item settles is the one they should follow when next
edited.

**Approach.** GitHub renders inline math from `$...$`, and from `` $`...` ``
for expressions that would otherwise be mangled by the surrounding markdown —
anything containing `$`, or a `_` pair that markdown would read as emphasis.
`F_D` and `\lambda_{b:g}` are in that second category, so `` $`...` `` is the
safer default here and is what the conversion should use unless a check of
GitHub's current syntax documentation says otherwise. That check was not
possible in the capturing session: `docs.github.com` is blocked by this
environment's egress proxy, so confirm the delimiters against the source before
converting 97 sites.

**Then make it decidable.** The conversion is worth nothing if the next edit
reintroduces `\(`. `tools/doc_check.py` should refuse a markdown file under
`docs/` containing `\(` or `\[`, which is a whole-file substring test with no
judgment in it, and it costs the session nothing once wired into `make check`.
Add that in the same change, not as a follow-up.

**Done when.** No `\(` or `\[` remains in `docs/MODEL.md` or
`docs/WORKING_NOTES.md`; every symbol-table row and inline symbol renders as
math on GitHub; the mid-sentence single-symbol `$$` blocks are inline again;
and `tools/doc_check.py` fails on a reintroduced `\(`.

**Verify.** `python3 tools/doc_check.py check && ! grep -rqF '\(' docs/MODEL.md
docs/WORKING_NOTES.md` — run it and watch it fail before writing it in.
Rendering itself is not machine-checkable here; confirm it by eye on the pushed
branch's GitHub view of `docs/MODEL.md`.
