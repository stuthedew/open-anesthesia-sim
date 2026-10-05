---
id: PL-WJF2
title: doc_check's four citation patterns pass over a closed quotation longer than their bound - 160 after a section mark or see/under, 200 after a quoted source or an item's mark - without a word, so a long cited title is neither checked nor reported unread; latent
status: untriaged
added: 2026-10-05
---

**Problem.** doc_check's four citation patterns pass over a closed quotation longer than their bound - 160 after a section mark or see/under, 200 after a quoted source or an item's mark - without a word, so a long cited title is neither checked nor reported unread; latent

**Found 2026-10-05 by `PL-T73L`** (`PL-R417`'s link 17, `#1382`), which
bounded the four patterns' quotations to the paragraph they open in and
refused one its paragraph never closes by name. The closed branch of each
kept the length bound it had: 160 in `CITATION_RE` and in
`UNMARKED_CITATION_RE`'s two branches, 200 in `QUOTED_SOURCE_RE` and
`ITEM_SECTION_RE`. A quotation its paragraph closes past the bound matches
neither branch - the closed one runs out, and `UNCLOSED_QUOTATION`'s
lookahead refuses a quotation that has its closing mark - so the citation is
passed over: neither compared nor reported unread. That is a partial reading
handed over as a complete one, which `.claude/rules/apparatus-standard.md`'s
floor refuses.

**Latent.** Measured 2026-10-05 on that branch, under the project
interpreter, over every quoting source with none declined, by lifting each
bound and counting the closed matches that appear: none in the documents
`check_citations` reads, and none in what `check_quoted_sources` reads. The
one in the tree is an `under` citation in `PL-6WYD`'s brief whose quotation
runs past 160, and `check_citations` does not read briefs.

**Why the bound is still there.** It stops a runaway match inside one
paragraph: a stray mark after `see` in a long paragraph would otherwise be
read on to that paragraph's next mark and compared as a title nobody wrote.
So lifting it trades a silent pass-over for a false error, and the choice is
between refusing the over-long form by name, an advisory, and a line in
`Report.declined`.

**Not a recurrence of `PL-T73L`.** `docket new` matched this capture to it
on the paths they share and recorded a recurrence there, which this capture
withdrew: `PL-T73L` was the paragraph end a quotation ran past, and this is
the length bound inside one paragraph, which `PL-T73L` left as it was.

**Generator check.** Not a member of `PL-R417`: the quotation is read within
its paragraph as CommonMark reads it, and dropped for its length rather than
for where its statement ends.

**Done when.** Each of the four readers reports a closed quotation longer
than its pattern's bound by name - unread, or as an advisory - rather than
passing over it, and a test per pattern gives the over-long form and gets
the report.
