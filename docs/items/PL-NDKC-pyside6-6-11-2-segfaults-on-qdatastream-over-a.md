---
id: PL-NDKC
title: PySide6 6.11.2 segfaults on QDataStream over a temporary QByteArray, which the layout persistence work will meet the first time it decodes a saved blob
priority: P3
effort: S
status: ready
classes: defect, infra
feature: interface-areas
touches: docs/WORKING_NOTES.md
added: 2026-09-16
verify: grep -qF 'QBuffer::readData' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
---

**Problem.** PySide6 6.11.2 segfaults on QDataStream over a temporary QByteArray, which the layout persistence work will meet the first time it decodes a saved blob

**Why it matters.** Found 2026-09-16 while re-measuring
`QSplitter.saveState()` for the v0.6.0 scoping. PySide6 6.11.2 segfaults on
`QDataStream(QByteArray(b"..."), QIODevice.ReadOnly)` when the `QByteArray` is a
temporary: the stream keeps a `QBuffer` over freed memory, and faulthandler
reports the crash inside `QBuffer::readData`. Binding the array to a name first
avoids it. `PL-SSQW`'s persistence work decodes saved blobs, so this is a crash
waiting at the first thing that reads one, and a segfault is the worst shape of
failure for a project whose standard prefers an obvious error to a wrong value.

**Done when.** The reproduction and the workaround are recorded in
`docs/WORKING_NOTES.md` where the persistence work will meet them, with the
PySide6 and Qt versions measured against.
