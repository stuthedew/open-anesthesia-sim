---
id: PL-92MY
title: Three readings of where a fenced block is disagree: docket checks._without_fences follows CommonMark (a backtick opener's info string holds no backtick, and only a closed block is blanked), docket instructions.FENCE_RE toggles on any line opening with three backticks or tildes, and doc_check._without_fences toggles on backtick lines and blanks everything after one left open
status: untriaged
added: 2026-09-26
---

**Problem.** Three readings of where a fenced block is disagree: docket checks._without_fences follows CommonMark (a backtick opener's info string holds no backtick, and only a closed block is blanked), docket instructions.FENCE_RE toggles on any line opening with three backticks or tildes, and doc_check._without_fences toggles on backtick lines and blanks everything after one left open

Found 2026-09-26 building `PL-NQ3X` under `PL-GPJ7`'s step 3, which needed a fence reader for item briefs and could reuse neither: `instructions.FENCE_RE` reads `PL-6SRZ`'s wrapped triple-backtick code span (its line 39) as an opening fence, so a later real fence would close it and blank the headings between. The three disagree on exactly that line, on tildes, and on a fence left open. doc_check's reading is live: it opens a fence at that line and nothing closes it, so the rest of `PL-6SRZ`'s brief is never read for line citations. A shared reader in `docket`, which `tools/doc_check.py` already imports from, would give one answer; which of the three behaviours it keeps for an unclosed fence is the open part, since doc_check's blanking of everything after one is CommonMark's rendering and checks' reading-as-written avoids reporting a visible section as missing. Possibly a member of `PL-PVW2`'s fact (a predicate spelled again wherever it is needed); for triage to decide.
