---
id: PL-79DP
title: doc_check's undated host-claim check reads block as a refusal in its Markdown sense too, so a sentence holding a project's URL and 'its block reading' or 'a code block' is refused as an undated claim that the host was blocked; found writing PL-0C2S's test docstring
status: untriaged
feature: host-reachability
added: 2026-10-10
---

**Problem.** doc_check's undated host-claim check reads block as a refusal in its Markdown sense too, so a sentence holding a project's URL and 'its block reading' or 'a code block' is refused as an undated claim that the host was blocked; found writing PL-0C2S's test docstring

**Reproduced 2026-10-10**, writing `PL-0C2S`'s test. A docstring sentence
naming markdown-it-py's repository URL and "the reference its block reading is
held to" failed `python3 tools/doc_check.py check` with "names `github.com`
beside a refusal in a sentence that carries no date". `HOST_REFUSAL_RE` reads
`block`, `blocks` and `blocked` at a word boundary, and in this tree the word
is also the Markdown noun, a fenced or code block. The sentence was reworded to
drop the URL, so nothing in the tree fails on it now.
