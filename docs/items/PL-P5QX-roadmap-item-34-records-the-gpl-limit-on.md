---
id: PL-P5QX
title: ROADMAP item 34 records the GPL limit on Blender's source but not that the Blender Manual and Developer Documentation are CC-BY-SA 4.0, which is the share-alike encumbrance that actually reaches this Apache-2.0 tree, and it names the Manual rather than the Developer Docs and Human Interface Guidelines where the design rationale it wants actually lives
status: untriaged
touches: ROADMAP.md
added: 2026-09-16
---

**Problem.** ROADMAP item 34 records the GPL limit on Blender's source but not that the Blender Manual and Developer Documentation are CC-BY-SA 4.0, which is the share-alike encumbrance that actually reaches this Apache-2.0 tree, and it names the Manual rather than the Developer Docs and Human Interface Guidelines where the design rationale it wants actually lives

**Why it matters.** Item 34's license paragraph is correct as far as it goes:
Blender's source files are `GPL-2.0-or-later` and the binary ships under
GPL-3.0-or-later, so code may not be ported into this Apache-2.0 tree. Verified
2026-09-16 against the SPDX header on
`source/blender/windowmanager/WM_api.hh` (`SPDX-FileCopyrightText: 2007 Blender
Authors` / `SPDX-License-Identifier: GPL-2.0-or-later`) and the repository
README ("Blender as a whole is licensed under the GNU General Public License,
Version 3. Individual files may have a different but compatible license").

But that is the constraint least likely to bite. Nobody here is porting C++.
The constraint that *is* live is the one the paragraph omits: **the Blender
Manual and the Blender Developer Documentation are both CC-BY-SA 4.0** — a
share-alike license — and item 34 already records that Manual § "Areas" and
§ "Workspaces" pages were "supplied directly". Copying prose into `ROADMAP.md`
or `docs/` *is* copying, where reading GPL source is not (GPLv2 § 0:
"Activities other than copying, distribution and modification are not covered
by this License; they are outside its scope."). So the weaker-sounding license
is the one that reaches this tree, and the stronger-sounding one does not.

Second gap: the paragraph sends a session to the Manual, which documents
*behaviour* for users. The **design rationale** the project actually wants —
why non-overlapping, why an area's type is a runtime property, how events
propagate window → screen → area → region — is in the Developer Documentation
and the Human Interface Guidelines, which item 34 never names.

- `developer.blender.org/docs/features/interface/` — window, screen, window manager
- `developer.blender.org/docs/features/interface/human_interface_guidelines/paradigms/`
- `developer.blender.org/docs/features/interface/human_interface_guidelines/editors/`
- `archive.blender.org/wiki/2015/index.php/Dev:2.5/Source/Architecture/Window_Manager/`
  — the 2.5 rewrite is when the current window manager was designed
- Doc license: `docs.blender.org/manual/en/latest/copyright.html`,
  `developer.blender.org/docs/license/`

**Not a violation today.** Checked 2026-09-16: item 34's prose is paraphrase
with citation, and its three-term glossary restates uncopyrightable facts about
how the interface behaves rather than reproducing the Manual's sentences. This
item records the rule so the practice survives a session that does not already
have it; there is nothing to remediate.

**Done when.** Item 34's license paragraph names the CC-BY-SA 4.0 constraint on
Blender's prose and the paraphrase-and-cite rule that follows from it, and
points at the Developer Docs and HIG rather than only the Manual.

**Note.** `PL-FTP5` proposes lifting this out of `ROADMAP.md` into a doc of its
own; if that is taken, this item is satisfied there instead.
