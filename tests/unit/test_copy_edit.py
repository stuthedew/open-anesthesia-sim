"""Tests for `tools/copy_edit.py`, which runs the copy editor as its own `claude -p` process."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import copy_edit
import pytest

#: A stand-in for `claude` that records its arguments, its directory and what
#: that directory holds, then prints a reply in `claude -p`'s JSON form.
FAKE_CLAUDE = """\
#!/usr/bin/env python3
import json, os, sys
record = {"argv": sys.argv[1:], "cwd": os.getcwd(), "files": sorted(os.listdir("."))}
record["memory_off"] = os.environ.get("CLAUDE_CODE_DISABLE_AUTO_MEMORY")
record["prompt"] = open(sys.argv[sys.argv.index("--system-prompt-file") + 1]).read()
json.dump(record, open(os.environ["FAKE_RECORD"], "w"))
print(json.dumps({"result": "[1] keep", "is_error": False, "num_turns": 2,
                  "total_cost_usd": 0.1, "usage": {"input_tokens": 5,
                  "cache_creation_input_tokens": 100, "output_tokens": 7}}))
"""


@pytest.fixture
def fake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put the stand-in `claude` first on PATH, and return the file it records into."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    claude = bin_dir / "claude"
    claude.write_text(FAKE_CLAUDE, encoding="utf-8")
    claude.chmod(claude.stat().st_mode | stat.S_IEXEC)
    record = tmp_path / "record.json"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_RECORD", str(record))
    return record


def test_the_copy_editor_runs_alone_with_its_instructions_and_only_read(
    fake: Path, tmp_path: Path
) -> None:
    """No resident instruction can load: the directory holds the request and nothing else."""
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")

    reply, counts = copy_edit.run(request)

    seen = json.loads(fake.read_text(encoding="utf-8"))
    assert reply == "[1] keep"
    assert counts == "copy_edit: read 105 tokens, wrote 7, 2 turns, $0.10"
    assert seen["files"] == [copy_edit.REQUEST_NAME]
    assert seen["cwd"] != str(copy_edit.ROOT)
    assert seen["argv"][seen["argv"].index("--tools") + 1] == "Read"
    assert seen["argv"][seen["argv"].index("--setting-sources") + 1] == ""
    assert seen["memory_off"] == "1"
    assert seen["prompt"].startswith("You copy-edit prose that another session wrote.")
    assert "omitClaudeMd" not in seen["prompt"]


def test_the_model_is_the_one_the_models_table_chooses_for_the_copy_editor(
    fake: Path, tmp_path: Path
) -> None:
    """The run never falls to the account's default model."""
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")
    table = copy_edit.load_config(copy_edit.ROOT).models
    assert table is not None
    chosen = table.choose({"role": copy_edit.ROLE})

    copy_edit.run(request)

    argv = json.loads(fake.read_text(encoding="utf-8"))["argv"]
    assert argv[argv.index("--model") + 1] == chosen.model
    assert argv[argv.index("--effort") + 1] == chosen.effort


def test_an_error_result_is_refused_rather_than_printed_as_a_reply() -> None:
    output = json.dumps({"result": "Credit balance is too low", "is_error": True})

    with pytest.raises(copy_edit.Refused, match="Credit balance is too low"):
        copy_edit.reply_of(output)


def test_main_exits_1_with_the_reason_when_claude_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")

    assert copy_edit.main([str(request)]) == 1
    assert "copy_edit: no reply: no `claude` on PATH" in capsys.readouterr().err
