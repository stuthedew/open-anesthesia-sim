---
id: PL-KRGY
title: ROADMAP.md and docs/ARCHITECTURE.md's product placement in workflow_paths sets aside 90 and 40 items that pair them only with apparatus paths - 14 open - because both documents also carry apparatus facts, so the deliberate absence written when it cost four items now costs the crossing set most of its members
priority: P3
effort: M
status: done
classes: docs, infra
feature: parallel-sessions
milestone: v0.5.23
touches: docket.toml, docs/ARCHITECTURE.md, docs/apparatus.md, tools/doc_check.py, tests/unit/test_doc_check.py, tests/unit/test_inline_reference.py, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
closed: 2026-10-11
pr: 1400
payoff: the simulator's map stops carrying 625 lines of apparatus, which gets a map of its own on the workflow side, and the eight open apparatus items reaching it stop reading as both lanes' work
verify: grep -qF '"docs/apparatus.md"' docket.toml && grep -q '^## Developer tooling' docs/apparatus.md && ! grep -q '^## Developer tooling' docs/ARCHITECTURE.md
---

**Problem.** ROADMAP.md and docs/ARCHITECTURE.md's product placement in workflow_paths sets aside 90 and 40 items that pair them only with apparatus paths - 14 open - because both documents also carry apparatus facts, so the deliberate absence written when it cost four items now costs the crossing set most of its members

**Evidence, 2026-09-27, measured through `Item.lane` against the store as
`#1199` leaves the list** (the count `PL-8ZGY`'s design round ran; its script
is not in the tree). `docket.toml`'s `workflow_paths` records `ROADMAP.md`
and `docs/ARCHITECTURE.md` as deliberately absent, and the paragraph beside
them says four items reaching both a tool and the roadmap were set aside as a
result, "which is the right answer". The count today:

| Path | Items declaring it | Paired only with apparatus paths | Open among those |
| --- | --- | --- | --- |
| `ROADMAP.md` | 244 | 90 | `PL-B396`, `PL-DHJ7`, `PL-GL95`, `PL-KKRP`, `PL-YBFB`, `PL-YRLM` |
| `docs/ARCHITECTURE.md` | 120 | 40 | `PL-1RTM`, `PL-2H0K`, `PL-5N7T`, `PL-B5LB`, `PL-S5YM`, `PL-TPS7`, `PL-ZBBP` |

Every one of those reads `crossing`, so neither `docket next workflow` nor
`docket next product` offers it, and each would read `workflow` were the
document on the other side. The placement is not wrong on its own terms - both
documents are written for a reader of the simulator - but each also carries
apparatus facts: `docs/ARCHITECTURE.md` documents the `tools/` tree entry by
entry (`PL-93RN` is one such entry gone stale), and release scoping in
`ROADMAP.md` is queue work that touches `docs/items` in the same change.

**Two routes, and the second is the durable one.** Reopen the placement, which
moves the 130 the other way and misplaces the product items instead; or move
the apparatus facts out of the two documents - [superseded 2026-10-11: the
destination is a new `docs/apparatus.md`, decided below; neither document
named here fits] the `tools/` entries into `docs/worker.md` or
`subprojects/docket/README.md`, which are already on the workflow side - so
the documents stop being both. `PL-TPS7` (cut the prose in
`docs/ARCHITECTURE.md` and `docs/maintainer.md`) is adjacent to the second.
Not folded into `PL-8ZGY`, whose brief places only the paths no carrier has
placed; this is a placement a carrier made, with ordinary evidence against it.

**Why it matters.** The thirteen open items the table names read `crossing`,
so neither `bin/docket next workflow` nor `next product` offers them; only the
bare `next` does.

**Decision needed.** Which route, for each document. **Recommended: route 2
for `docs/ARCHITECTURE.md`, and no change for `ROADMAP.md`.**
`ARCHITECTURE.md`'s seven are all tool work (`PL-1RTM`, `PL-2H0K`, `PL-5N7T`,
`PL-B5LB`, `PL-S5YM`, `PL-TPS7`, `PL-ZBBP`) reaching it through its `tools/`
inventory, so moving that inventory to the apparatus side lets them read
`workflow`. `ROADMAP.md`'s six are mixed: `PL-B396` (agent amounts in litres of
vapour) and `PL-YRLM` (which release builds agent cost) are product decisions
route 1 would misplace, so the ratified placement stands and the other four stay
reachable through the bare `next`. Route 1 reopens a placement the owner
ratified under `PL-8ZGY`, so it would go back to him; route 2 reopens nothing.

**Recount, 2026-10-11, in the design round** (store at `1ee4e78e`: 2,172
items, 357 open, every item's `touches` read through `Item.lane` against
`workflow_paths`' 68 entries; the script ran in the round's session and is not
in the tree, as the first count's was not). "Only with apparatus" below means
every other declared path is under `workflow_paths`; "alone" means the document
is the item's only path.

| Path | Declared (open) | Alone (open) | Only with apparatus (open) | Only with product (open) | Mixed (open) |
| --- | --- | --- | --- | --- | --- |
| `ROADMAP.md` | 259 (25) | 49 (11) | 96 (8) | 39 (5) | 75 (1) |
| `docs/ARCHITECTURE.md` | 155 (19) | 12 (6) | 59 (8) | 30 (5) | 54 (0) |

Of the 37 open items that read `crossing`, 16 cross through one of these two
documents and nothing else, eight each, and no other single product-side path
crosses more than five (`tests/unit`, by the import rule, on purpose). The open
items, by document:

- `ROADMAP.md`, only with apparatus: `PL-B396` and `PL-YRLM` (each `ROADMAP.md`
  and `docs/items`; both product decisions, a readout's unit and a release's
  scope), `PL-D388`, `PL-DHJ7` and `PL-Z64T` (each a `tools/doc_check.py` rule
  reading the roadmap), `PL-JV5Q` and `PL-KKRP` (each the docket skill and the
  roadmap's gate), `PL-GL95` (attribution markers, with `docs/WORKING_NOTES.md`
  and `docs/items`). Only with product, so route 1 would turn them `crossing`:
  `PL-HJPY`, `PL-QR6Q`, `PL-VJZK`, `PL-W54S`, `PL-WV9K`. Alone, so route 1
  would send them to the workflow side: eleven, among them `PL-DWHV` (display
  patient uptake), `PL-M3X6` (a Required-scope entry) and `PL-K7N7` (cut the
  roadmap's prose for a human reader), the other eight drift fixes to roadmap
  sentences.
- `docs/ARCHITECTURE.md`, only with apparatus: `PL-124X`, `PL-2H0K`, `PL-5N7T`,
  `PL-B5LB`, `PL-S5YM`, `PL-TPS7`, `PL-ZBBP` and this item. Six of the seven
  reach the document through § "Developer tooling (`tools/`)" or § "Wired
  hooks (`.claude/hooks/`)": a tool's inventory entry, a hook's description,
  the quotations of Claude Code's documentation, the enumeration of
  `quality.yml`'s commands, the sentence on a directory drawn bare in a tree.
  `PL-ZBBP` reaches § "Where new code belongs", the simulator's half, beside a
  `.claude/rules/` file, and `PL-TPS7` is the cut of the whole document and
  `docs/maintainer.md`. Only with product: `PL-8XMV`, `PL-HJPY`, `PL-TH35`,
  `PL-WV9K`, `PL-ZW0J`, every one a blocked interface item editing the package
  map or § "Where new code belongs" beside `src/`, `docs/MODEL.md` or
  `ROADMAP.md`. Alone: `PL-GTSL`, `PL-MXLV` and `PL-WQT0`, each a wrong
  sentence in the `tools/` inventory, so apparatus documentation offered today
  to a product session; and `PL-R1WQ`, `PL-SSQW` and `PL-W4M9`, the
  simulator's.

Of the first count's thirteen open items, `PL-1RTM` and `PL-YBFB` have closed
(`#1300`, `#1309`); `PL-124X`, `PL-D388`, `PL-JV5Q` and `PL-Z64T` have joined.

**Decided 2026-10-11, in the design round: `ROADMAP.md` stays where `PL-8ZGY`
placed it.** A session's call under rule 14's obvious-call clause, so it
reopens on ordinary evidence. Route 1's arithmetic refutes it on the count
alone: it frees eight open items, two of which (`PL-B396`, `PL-YRLM`) are
product decisions it would then hand to an apparatus session, while crossing
five open items that pair the roadmap with `src/` or `docs/MODEL.md` and
moving eleven roadmap-only items, product direction and drift fixes to it,
onto the workflow side; and it reopens a placement the owner ratified on
2026-09-27. A route 2 for the roadmap would move the debt-gate sections out of
it, and those are where the roadmap meets the queue by design: `bin/docket
wave` and `gate` compute from them, and the owner reads release direction and
its gate as one document. Six lane labels do not buy that. The six apparatus
items left `crossing` are each a check or a skill reading or editing the
roadmap's gate, which is the honest reading the placement's own comment gives
them, and they reach a session through the bare `bin/docket next` or by name,
as this feature's own chain hands items.

**Decided 2026-10-11, in the design round: route 2 for `docs/ARCHITECTURE.md`,
into a new `docs/apparatus.md`**, the apparatus's own map, on the workflow
side. The same kind of call, reopenable the same way. Two measurements decide
it and point the same way, and route 1 is refuted by the count that refutes it
for the roadmap: it would cross the five blocked interface items, send
`PL-R1WQ`, `PL-SSQW` and `PL-W4M9` to the workflow side, and call the package
map apparatus, which it is not.

- *The lanes.* After the move, seven of the document's eight apparatus-paired
  open items read `workflow`, and the three apparatus sentences filed alone
  (`PL-GTSL`, `PL-MXLV`, `PL-WQT0`) stop being offered to a product session;
  the five product-paired items stay `product`. `PL-TPS7` and `PL-ZBBP` keep
  reading `crossing`, honestly: a cut spanning both documents and
  `docs/maintainer.md`, and a rule beside the simulator's map.
- *The document.* `docs/ARCHITECTURE.md` opens as "a map for contributors" and
  `CLAUDE.md` holds it to the specialist standard, yet § "Developer tooling
  (`tools/`)" and § "Wired hooks (`.claude/hooks/`)" are 625 of its 1,465 lines
  and 67,246 of its 124,540 characters, measured 2026-10-11: apparatus that
  `CLAUDE.md` says "nobody evaluating this project will read", held to
  `.claude/rules/apparatus-standard.md`'s different bar, whose `paths:` cannot
  reach prose inside a product document (`PL-6SBB` is what a bar read in the
  wrong place costs). Of the file's 31 lines over 300 characters, 27 are
  there; the longest, a `tools/` tree entry, is 3,853. The owner found the
  document too verbose on 2026-09-05 (`PL-TPS7`), when it was 576 lines, and
  the inventory is most of what has grown since. Separating the halves is the
  first half of that cut, and puts the apparatus half under the bar that says
  "streamlined".

Neither of the brief's two destinations fits, which is why the superseded
clause above names a third: `docs/worker.md` is instructions to a session, as
its own first heading says, and `subprojects/docket/README.md` is docket's,
where most `tools/` scripts are not docket's. The 625 lines are a map, so they
get a map's file. The name follows the apparatus side's own documents
(`docs/worker.md`, `docs/maintainer.md`, `docs/resident-instructions.md`) and
the standard that governs it; the simulator's capitalised `ARCHITECTURE.md`
and `MODEL.md` stay the only two of that kind.

**What the build carries**, one pull request in its own thread, the item
claimed afresh:

1. `docs/apparatus.md`, opening with what it is - the map of the workflow
   apparatus, held to `.claude/rules/apparatus-standard.md` - and holding
   § "Developer tooling (`tools/`)" and § "Wired hooks (`.claude/hooks/`)"
   moved whole from `docs/ARCHITECTURE.md`, the tree fence as it stands so
   `tools/doc_check.py` parses it, plus § "Tests (`tests/`)"'s paragraph on the
   vendored Markdown specifications, which describes `doc_check`'s corpus.
   Moved, not cut: the cut is `PL-TPS7`'s. `docs/ARCHITECTURE.md` keeps one
   paragraph pointing at the new file where the sections stood; its § "Tests
   (`tests/`)" stays, since `.claude/rules/where-new-code-goes.md` routes a new
   test through it.
2. `tools/doc_check.py`: `check_package_maps` reads `docs/ARCHITECTURE.md`
   alone, through its `ARCHITECTURE` constant, so the `tools/` tree would go
   unchecked the moment it moved. It reads both documents' trees, each held to
   the disk both ways, with the "no package-map tree found" guard firing per
   document. `tests/unit/test_doc_check.py` pins the second document, and its
   fixture heading `## Developer tooling` follows the move.
3. `docket.toml`: `workflow_paths` gains `docs/apparatus.md` -
   `tools/workflow_paths_check.py` refuses an unplaced tracked path, so the
   build cannot forget it - and the `product_paths` comments on `ROADMAP.md`
   and `docs/ARCHITECTURE.md` record this decision in place of "`PL-KRGY`
   weighs" and "`PL-KRGY` again".
4. The standard's carriers - `.claude/rules/apparatus-standard.md`'s `paths:`,
   and the enumerations in `CLAUDE.md` and `.claude/rules/expert-review.md` -
   gain the file as a row in `PL-21RC`'s table, as `PL-8ZGY`'s build handed
   that item its six rows. This item edits none of the three, which also keeps
   its pull request off the owner's read list.
5. Open items re-pointed in `touches`, `docs/ARCHITECTURE.md` to
   `docs/apparatus.md`, declared through `docs/items`: `PL-124X`, `PL-2H0K`,
   `PL-5N7T`, `PL-B5LB`, `PL-GTSL`, `PL-MXLV`, `PL-S5YM`, `PL-WQT0`. `PL-TPS7`
   gains the new path and keeps the old; `PL-ZBBP` is untouched. Their briefs'
   citations of the moved headings follow - `PL-S5YM`'s is the one open brief
   citing them - as `make check`'s citation check requires.
6. `README.md` is unchanged: its pointer at `docs/ARCHITECTURE.md` as "the map
   of where new code belongs" stays true, and its reading list is for a reader
   of the simulator.

This item's own lane after the build is `crossing`, honestly: it moves text
out of a product document into an apparatus one.

**Done when.** `docs/apparatus.md` is in the tree and in `workflow_paths`,
holding § "Developer tooling (`tools/`)" and § "Wired hooks
(`.claude/hooks/`)", which `docs/ARCHITECTURE.md` no longer holds; `make check`
passes with both documents' trees checked; and the open items step 5 names
have the lanes this round expects - `workflow` for the eight re-pointed,
`crossing` for `PL-TPS7` and `PL-ZBBP` - read through `Item.lane` after the
build and recorded here, with any that differ.

**Generator check.** `PL-8ZGY`'s fact (which lane each tracked path is in),
filed in the commit that closed `PL-8ZGY` as the question its table deferred
here; not a post-close instance.

**Built 2026-10-11, `#1400`.** `docs/apparatus.md` holds
§ "Developer tooling (`tools/`)" and § "Wired hooks (`.claude/hooks/`)", and the
vendored specifications' paragraph as
§ "Third-party text (`tests/unit/markdown-specs/`)";
`docs/ARCHITECTURE.md` keeps § "The workflow apparatus", one paragraph pointing
at it where the two stood. The text moved as it stood but for three references
the move made wrong, each now naming `docs/ARCHITECTURE.md`: the `doc_check.py`
tree entry's "this map", the paragraph saying the trees "above" are checked,
and a § "Layering" "above". `tools/doc_check.py`'s `check_package_maps` reads
both documents through `PACKAGE_MAPS`, each held to the disk both ways and each
refusing a missing file or a lost tree on its own;
`test_the_apparatus_map_is_held_to_the_tree_too` and
`test_each_map_document_answers_for_its_own_tree` pin the second document.

Lanes read through `Item.lane` on the branch, against `origin/main` before it:

| Item | Before | After |
| --- | --- | --- |
| `PL-124X`, `PL-2H0K`, `PL-5N7T`, `PL-B5LB`, `PL-S5YM` | crossing | workflow |
| `PL-GTSL`, `PL-MXLV`, `PL-WQT0` | product | workflow |
| `PL-TPS7`, `PL-ZBBP` | crossing | crossing |
| `PL-KRGY` | crossing | crossing |

None differs from what this round expected. Five of the re-pointed items'
`verify:` commands grepped `docs/ARCHITECTURE.md` for text that moved, and
`PL-MXLV`'s, a `! grep`, would have passed on the moved tree with none of its
work done; each now greps `docs/apparatus.md`, and all five were run on the
branch and fail, as an open item's must. Two lost a clause in the move,
`PL-GTSL`'s `python3 tools/doc_check.py check` and `PL-S5YM`'s
`uv run pytest tests/unit/test_doc_check.py`, which `bin/docket set` refuses
beside a grep in a command written since 2026-09-24; each brief says so.
`tests/unit/test_inline_reference.py` joined `touches` for its docstring, which
cited the licence paragraph's old place.
