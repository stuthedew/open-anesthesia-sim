---
id: PL-KJXS
title: A QByteArray passed where Qt's C++ signature takes QByteArray *, at any of the six entry points PL-NDKC measured, is a use-after-free that segfaults or reads silently wrong zeros, and nothing fails make check when src/ writes one
status: untriaged
added: 2026-09-26
---

**Problem.** Six Qt entry points keep the `QByteArray *` they are given, and
PySide6 6.11.2 keeps no reference to the array at any of them, so an array
nothing else holds is freed while Qt still points at it. `PL-NDKC`'s thread in
`docs/WORKING_NOTES.md` measured the outcomes - segfaults, and zeros read back
with `status()` still `Ok` - and states the rule: never pass a `QByteArray`
where Qt's C++ signature takes `QByteArray *`. Nothing under `src/` or `tests/`
does it on 2026-09-26, and nothing would fail `make check` if something did.

The six, as the Python calls that bind them:

- `QBuffer(array)` and `buffer.setBuffer(array)`;
- `QDataStream(array, mode)`, with two arguments only - the one-argument
  `QDataStream(array)` binds `const QByteArray &` and copies;
- `QTextStream(array)` and `QTextStream(array, mode)` - both, because PySide6
  removes the copying overload Qt has;
- `QXmlStreamWriter(array)` and `QCborStreamWriter(array)`.

**The design question is types.** A call does not show its overload.
`QTextStream`, `QXmlStreamWriter` and `QCborStreamWriter` also take a
`QIODevice`, and `QBuffer` a parent `QObject`, which are the safe forms, and a
check reading the syntax tree cannot tell `QTextStream(device)` from
`QTextStream(array)` without inferring the argument's type. So it chooses
between flagging every such call with a way to mark the safe ones, and matching
only arguments it can see are `QByteArray`s. `QDataStream`'s split by argument
count and `setBuffer` are the decidable cases.

**Done when.** `make check` fails on each of the six Python call forms above
under `src/` and `tests/`, and passes on the safe forms the thread lists: the
one-argument `QDataStream`, `QBuffer()` with `setData`, and a `QIODevice`
argument.
