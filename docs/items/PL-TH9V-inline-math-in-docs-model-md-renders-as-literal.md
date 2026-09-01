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

**Approach — verified against GitHub's "Writing mathematical expressions",
2026-09-01.** GitHub renders LaTeX through MathJax and documents exactly two
inline delimiters: `$...$`, and `` $`...` `` — "useful when the expression you
are writing contains characters that overlap with markdown syntax". `\(...\)`
appears nowhere in the page; it is not a supported delimiter, which is the
defect above.

**Convert to `` $`...` ``, not to `$...$`.** The subscripts are the reason. The
symbol-table row for `F_a` (`docs/MODEL.md` line 156) already carries two
expressions on one line — the symbol itself and the parenthetical
`F_a \equiv F_A` — so under bare `$` that row would hold four delimiters and
three `_` characters, and the text between the middle pair is precisely what
markdown reads as emphasis. That is the overlap case the documentation names.
The backtick form costs two characters per site and takes the ambiguity out.

**One site is already on the other syntax and is also wrong.**
`docs/MODEL.md` lines 1327-1328 read `$F_a \equiv\nF_A$` — correct delimiters,
but wrapped across a source line break by the paragraph reflow. Inline math is
parsed within a line, so this does not render either. Any conversion must keep
each expression on one source line, which constrains how the file may be
rewrapped; a `` $`...` `` span split by a future `fmt` pass fails the same way.

**Display math needs no change, but note the alternative.** The 58 `$$` blocks
are correct as written. The documentation also offers a ```` ```math ````
fenced block as an equivalent, which is worth preferring for any *new* block
because a fence cannot be silently broken by rewrapping. Converting the
existing 58 is not part of this item.

**No stray dollar signs to escape.** Every `$` in `docs/MODEL.md` today is
either a `$$` fence or part of the line-1327 expression, so introducing `$`-
delimited inline math cannot collide with prose. The documentation's `\$` and
`<span>$</span>` escapes are therefore not needed here — but the doc_check rule
below should be the thing that keeps that true.

**Then make it decidable.** The conversion is worth nothing if the next edit
reintroduces `\(`. `tools/doc_check.py` should refuse a markdown file under
`docs/` containing `\(` or `\[`, which is a whole-file substring test with no
judgment in it, and it costs the session nothing once wired into `make check`.
Add that in the same change, not as a follow-up. A second rule is worth the
same few lines: an odd count of unescaped `` ` ``-delimited math spans on a
line, or a `$`/`` $` `` span left unclosed at end of line, catches the
line-1327 wrap defect and any future reflow that reintroduces it.

**Done when.** No `\(` or `\[` remains in `docs/MODEL.md` or
`docs/WORKING_NOTES.md`; every inline expression sits on one source line,
including the currently-wrapped one at lines 1327-1328; every symbol-table row
and inline symbol renders as math on GitHub; the mid-sentence single-symbol
`$$` blocks are inline again; and `tools/doc_check.py` fails on both a
reintroduced `\(` and a math span split across a line break.

**Verify.** `python3 tools/doc_check.py check && ! grep -rqF '\(' docs/MODEL.md
docs/WORKING_NOTES.md` — run it and watch it fail before writing it in.
Rendering itself is not machine-checkable here; confirm it by eye on the pushed
branch's GitHub view of `docs/MODEL.md`.
