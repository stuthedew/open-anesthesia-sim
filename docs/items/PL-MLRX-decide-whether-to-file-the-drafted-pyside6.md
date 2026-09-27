---
id: PL-MLRX
title: Decide whether to file the drafted PySide6 report that six Qt entry points keep a QByteArray * PySide6 does not keep alive, and link it from PL-NDKC's thread once filed
status: untriaged
feature: qbytearray-pointer-trap
touches: docs/WORKING_NOTES.md
added: 2026-09-27
---

**The question.** Whether to file the report drafted below with the Qt
tracker's Qt for Python project (key `PYSIDE`, https://qt-project.atlassian.net),
from the project owner's Qt Account. A session cannot file it: the tracker
takes a new issue only from a signed-in account, and the report is public and
under the owner's name. `PL-NDKC`'s thread in `docs/WORKING_NOTES.md` holds the
measurements it rests on, and ends "A report was recommended to the project
owner on 2026-09-26 and is not filed."

**Recommendation: file it.** Nothing here waits on a fix: the thread's rule -
never pass a `QByteArray` where Qt's C++ signature takes `QByteArray *` -
protects this project with or without one, at no cost. The report is about the
gap itself. Idiomatic Python reaches a segfault or silently wrong data through
signatures that advertise `bytes`, the kind of defect a binding exists to close,
and nobody has reported it. Upstream has twice held a pointer's lifetime to be
the caller's business (PYSIDE-1807, PYSIDE-237), so the draft argues what
differs here rather than asserting a bug, and offers a documentation fallback so
that "by design" still ends in a change. Declining is defensible too, and then
the thread's sentence records that instead.

**Filing it**, from Qt's own guide (https://wiki.qt.io/Reporting_Bugs, read
2026-09-27). The project, issue type, component and version names were read
from the tracker's public REST API the same day. The form's button labels could
not be seen without signing in.

1. Sign in at https://qt-project.atlassian.net with a Qt Account, creating one
   first if needed.
2. Create an issue in the project **Qt for Python**, type **Bug**.
3. Fill in the fields from the draft: Summary, Component/s **PySide**, Affects
   Version/s **6.11.2**, Environment, Description. Leave Platform/s blank and
   the priority as offered.
4. Save the script at the end of the draft as `repro.py` and attach it.
5. Create the issue, and note its key (`PYSIDE-` and a number).

**Done when.** The report is filed and the thread's sentence names its key and
link - or the owner declines, and the sentence says so, with the date. If
upstream fixes it, the thread already says how to re-measure: its `refcount`
form, run first on the upgraded wheel.

**The draft.** Its claims were re-run on 2026-09-27 against PySide6 6.11.2 / Qt
6.11.2 / CPython 3.14.7 with the draft's own reproduction:

- refcount 2 -> 2 at all six entry points, and 2 -> 3 for the control;
- the `datastream` form segfaulted 25 runs of 25, in `QBuffer::readData`;
- the `qbuffer` form printed `0 '' Status.Ok` 25 runs of 25;
- `bytes`, `bytearray` and `memoryview` were refused with `ValueError` at all
  six, whose stub parameters read `PySide6.QtCore.QByteArray | bytes |
  bytearray | memoryview`;
- the Qt for Python pages for `QDataStream`, `QTextStream`, `QXmlStreamWriter`
  and `QCborStreamWriter` do not carry the caller-responsible sentence, and the
  `QBuffer` page does.

````text
Summary:
QByteArray passed to QBuffer, QDataStream, QTextStream, QXmlStreamWriter or QCborStreamWriter is not kept alive: a temporary is freed while Qt still holds its pointer

Project: Qt for Python (PYSIDE)
Issue type: Bug
Component/s: PySide
Affects Version/s: 6.11.2
Environment: Ubuntu 24.04.4 LTS, x86-64; CPython 3.14.7; PySide6 6.11.2 wheel from PyPI (Qt 6.11.2)

Description:

Six Qt entry points keep the QByteArray pointer they are given:

- QBuffer(QByteArray *, QObject *) and QBuffer::setBuffer(QByteArray *)
- QDataStream(QByteArray *, QIODevice::OpenMode)
- QTextStream(QByteArray *, QIODevice::OpenMode)
- QXmlStreamWriter(QByteArray *)
- QCborStreamWriter(QByteArray *)

PySide6 keeps no reference to the Python QByteArray at any of them. When nothing else references the array - typically QDataStream(QByteArray(data), QIODevice.ReadOnly) - it is freed when the call returns, while Qt still points at it. sys.getrefcount() on the array is unchanged by each of the six calls, where QReadLocker(lock), whose argument the typesystem marks <reference-count action="set"/>, raises the lock's count by one.

Steps: run the attached repro.py as python -X faulthandler repro.py <form>.

- refcount: prints n -> n for each of the six, and n -> n + 1 for the QReadLocker control.
- datastream: QDataStream(QByteArray(blob), ReadOnly), then readInt32().
  Expected: 42 'hello, workspace' Status.Ok
  Actual: segmentation fault, 25 runs of 25, in QBuffer::readData <- QIODevicePrivate::read <- QDataStream::readBlock <- QDataStream::operator>>(int&).
- qbuffer: QBuffer(QByteArray(blob)), opened ReadOnly and read through QDataStream(buffer).
  Expected: 42 'hello, workspace' Status.Ok
  Actual: 0 '' Status.Ok, 25 runs of 25 - wrong data, and no error.

In other scripts on the same versions, QTextStream(QByteArray(...)) segfaulted in readAll(), and QXmlStreamWriter(QByteArray()) and QCborStreamWriter(QByteArray()) segfaulted while writing - though one script saw QXmlStreamWriter return normally every run. It is a use-after-free, so the symptom depends on what reuses the memory.

Why I think the binding should close this, knowing the position taken on PYSIDE-1807 and PYSIDE-237 that a pointer argument is the caller's to keep alive:

1. QByteArray is a value type, and the Python signatures present it as one. QtCore.pyi types all six parameters as "PySide6.QtCore.QByteArray | bytes | bytearray | memoryview", but bytes, bytearray and memoryview are each refused at all six with ValueError "... called with wrong argument values". The natural next step, wrapping the data inline in QByteArray(data), is exactly the temporary that gets freed.

2. For four of the six, the pointer is held by an object the caller never sees: the QDataStream, QTextStream, QXmlStreamWriter and QCborStreamWriter constructors wrap it in a new QBuffer and open it before returning. Qt for Python's QBuffer page carries Qt's "The caller is responsible for ensuring that byteArray remains valid until the QBuffer is destroyed, or until setBuffer() is called to change the buffer." The QDataStream, QTextStream, QXmlStreamWriter and QCborStreamWriter pages do not.

3. Two calls that read alike behave differently. One-argument QDataStream(array) binds QDataStream(const QByteArray &), which copies, and is safe. Qt gives QTextStream the same copying overload, but typesystem_core_common.xml removes it (signature="QTextStream(const QByteArray&,QFlags<QIODeviceBase::OpenModeFlag>)" remove="all"), so one-argument QTextStream(array) binds the pointer.

In C++ the same mistake does not compile (g++: "taking address of rvalue"). In Python it is idiomatic code, and the outcome is a segfault or silently wrong data rather than an exception.

Suggested fix: keep the array alive from the object that holds the pointer, as the typesystem already does for QReadLocker(QReadWriteLock*) - a <reference-count action="set"/> on the QByteArray * argument of the six, with QBuffer's constructor and setBuffer() sharing one reference so that setBuffer() releases the previous array. If the current behaviour is kept by design, please say so on the QDataStream, QTextStream, QXmlStreamWriter and QCborStreamWriter pages, and stop the stubs advertising bytes | bytearray | memoryview for these parameters.

A search of PYSIDE for QBuffer, setBuffer, QDataStream, QTextStream, QXmlStreamWriter and QCborStreamWriter found no existing report. PYSIDE-232 is a different bug, fixed in 2018.

repro.py:

```python
import sys

from PySide6.QtCore import (
    QBuffer,
    QByteArray,
    QCborStreamWriter,
    QDataStream,
    QIODevice,
    QReadLocker,
    QReadWriteLock,
    QTextStream,
    QXmlStreamWriter,
)

READ = QIODevice.OpenModeFlag.ReadOnly

# Bytes that Qt itself wrote: an int32 and a QString.
written = QByteArray()
out = QDataStream(written, QIODevice.OpenModeFlag.WriteOnly)
out.writeInt32(42)
out.writeQString("hello, workspace")
del out
blob = bytes(written.data())


def set_buffer(array):
    buffer = QBuffer()
    buffer.setBuffer(array)
    return buffer


if sys.argv[1] == "refcount":
    # Control: QReadLocker's argument has <reference-count action="set"/>.
    lock = QReadWriteLock()
    before = sys.getrefcount(lock)
    locker = QReadLocker(lock)
    print("QReadLocker(lock)", before, "->", sys.getrefcount(lock))
    locker.unlock()
    for name, keep in [
        ("QBuffer(array)", QBuffer),
        ("QBuffer().setBuffer(array)", set_buffer),
        ("QDataStream(array, READ)", lambda array: QDataStream(array, READ)),
        ("QTextStream(array)", QTextStream),
        ("QXmlStreamWriter(array)", QXmlStreamWriter),
        ("QCborStreamWriter(array)", QCborStreamWriter),
    ]:
        array = QByteArray(blob)
        before = sys.getrefcount(array)
        kept = keep(array)
        print(name, before, "->", sys.getrefcount(array))
        del kept
elif sys.argv[1] == "datastream":  # expected: 42 'hello, workspace' Status.Ok
    stream = QDataStream(QByteArray(blob), READ)
    print(stream.readInt32(), repr(stream.readQString()), stream.status())
elif sys.argv[1] == "qbuffer":  # expected: 42 'hello, workspace' Status.Ok
    buffer = QBuffer(QByteArray(blob))
    buffer.open(READ)
    stream = QDataStream(buffer)
    print(stream.readInt32(), repr(stream.readQString()), stream.status())
```
````
