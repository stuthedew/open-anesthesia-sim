---
id: PL-8SDL
title: Identify Lowe and Ernst's references 9, 19, 20 and 26, the upstream the book itself cites for the reference patient's volumes and flows
status: untriaged
added: 2026-09-08
---

**Problem.** Identify Lowe and Ernst's references 9, 19, 20 and 26, the upstream the book itself cites for the reference patient's volumes and flows (`PL-7HDS`, 2026-09-08).

Page 56 of *The Quantitative Practice of Anesthesia* says of figure 4.1b, the
table the Gas Man Workbook credits for its volume and flow values: "The figure
models a 100-kg patient with normal physiologic organ volumes and blood flows
(9, 19, 20, 26)." The book therefore collects those figures rather than
measuring them, which is what makes it tier 2 - and the four references are the
next link in the only provenance chain the reference patient has.

Chapter 4's own narrative on page 55 names three of the four in passing, as
authors of compartmental or multiple-model uptake models: **9 Mapleson**, **19
Smith et al.**, **20 Zwart et al.** Reference **26 is named nowhere in the
pages supplied** (55-60 and 82-84), and chapter 4's reference list is outside
them, so none of the four has a full citation yet.

**Why it matters.** `docs/MODEL.md`'s source hierarchy places a value by what
its authority did, and every stored physiologic parameter in
`reference_adult.json` is currently tier 3 with no primary measurement adopted
for any of them. This is the shortest remaining route to finding out whether a
primary measurement exists at all: if one of these four measured the organ
volumes and flows, the reference patient has a tier-1 source it has never had;
if all four are models like the book, the chain is a compilation of
compilations and the `provenance_gap` should say so in those terms.

**What it needs.** Chapter 4's reference list - roughly pages 60-62 of the same
monograph, immediately after the pages already supplied - reached the same way
the rest was. Then each of the four resolved to a citation and read far enough
to say whether it measured these quantities.

**Not delegable in its first step**, for the same reason `PL-7HDS` was not: the
egress proxy refuses the Internet Archive, HathiTrust, Open Library and Google
Books, and PubMed does not index monographs. Once the four citations are in
hand, the papers themselves may well be reachable through the PubMed MCP
server, which is a different and cheaper problem.

