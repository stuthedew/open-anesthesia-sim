---
id: PL-ZD8Y
title: docs/interface-provenance.md says Shift moves a border alone here, the reverse of Blender, only in the keyboard entry; the border-chain entry says nothing about Shift, and no divergence is recorded (copy editor structure read, 2026-11-05)
status: untriaged
feature: interface-provenance-structure
added: 2026-11-05
---

**Problem.** docs/interface-provenance.md says Shift moves a border alone here, the reverse of Blender, only in the keyboard entry; the border-chain entry says nothing about Shift, and no divergence is recorded (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on the Shift key:** rows 294-303 say that in Blender, Shift extends a border drag to every aligned border. Rows 1056-1069 say that here "Shift moves it alone, as in a drag", but the border-chain entry (rows 1013-1036) says nothing about Shift. The reader needs this project's Shift behaviour in rows 1013-1036. Does it reverse Blender's on purpose, as a recorded divergence?
