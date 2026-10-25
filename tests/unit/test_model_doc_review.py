"""Tests for `tools/model_doc_review.py`, which has a strong model read the model document once.

The tool sends one batch request per section of `docs/MODEL.md`, each carrying
the whole document and every data file, and turns the batch's results into one
findings file for a session to check (`PL-5S71`). These tests cover how the
requests are built and how the results are read. No test calls the API.
"""

from __future__ import annotations

import json
from pathlib import Path

import model_doc_review as REVIEW
import pytest
from docket.model_choice import Choice

DOCUMENT = """\
# Title

Preamble text.

## First part

Body one.

```text
## Not a heading, because it is fenced
```

## Second: part (two)

Body two.
"""

#: A model the table could choose, priced at $10 and $50 per million tokens.
MODEL = REVIEW.ReviewModel(Choice("model-a", "high", None), 10.0, 50.0)

DATA = {
    "src/anesthesia_sim/data/agents/a.json": '{"x": 1}',
    "src/anesthesia_sim/data/patients/p.json": '{"y": 2}',
}


def test_sections_split_at_unfenced_level_two_headings() -> None:
    found = REVIEW.sections(DOCUMENT)
    assert [s.heading for s in found] == ["First part", "Second: part (two)"]
    assert [s.custom_id for s in found] == ["s01-first-part", "s02-second-part-two"]
    assert "## Not a heading" in found[0].text
    assert "Preamble" not in "".join(s.text for s in found)


def test_long_heading_id_is_cut_to_the_api_limit() -> None:
    (section,) = REVIEW.sections("## " + "word " * 40 + "\n")
    assert len(section.custom_id) <= 64
    assert REVIEW.CUSTOM_ID_RE.match(section.custom_id)
    assert not section.custom_id.endswith("-")


def test_one_request_per_section_sharing_one_cached_prefix() -> None:
    requests = REVIEW.build_requests(DOCUMENT, DATA, MODEL.choice)
    assert [r["custom_id"] for r in requests] == ["s01-first-part", "s02-second-part-two"]
    contents = [r["params"]["messages"][0]["content"] for r in requests]
    # Everything but the last block is the shared prefix, identical in every request.
    assert contents[0][:-1] == contents[1][:-1]
    prefix = contents[0][:-1]
    assert len(prefix) == 1 + len(DATA)
    assert "docs/MODEL.md" in prefix[0]["text"] and "Body two." in prefix[0]["text"]
    assert [("cache_control" in b) for b in prefix] == [False, False, True]
    assert prefix[-1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert "'Second: part (two)'" in contents[1][-1]["text"]
    assert "cache_control" not in contents[1][-1]


def test_request_params_fit_the_2026_10_21_api() -> None:
    choice = Choice("model-b", "max", 1)
    (params,) = (r["params"] for r in REVIEW.build_requests("## Only\n\nx\n", DATA, choice))
    assert params["model"] == "model-b"
    assert params["max_tokens"] == 48_000
    # Version 2026-10-21 refuses the sampling fields, and thinking is left at its default.
    for refused in ("temperature", "top_p", "top_k", "thinking"):
        assert refused not in params
    assert params["output_config"]["effort"] == "max"
    assert params["output_config"]["format"]["type"] == "json_schema"
    assert params["output_config"]["format"]["schema"]["required"] == ["findings"]


def test_repeated_heading_gets_a_distinct_id() -> None:
    requests = REVIEW.build_requests("## Same\n\na\n\n## Same\n\nb\n", DATA, MODEL.choice)
    assert [r["custom_id"] for r in requests] == ["s01-same", "s02-same"]


def test_cost_bound_assumes_no_cache_and_full_output() -> None:
    request = {"params": {"k": "v" * 2_999_991}}  # 3,000,000 bytes as JSON
    assert len(json.dumps(request["params"]).encode()) == 3_000_000
    # 1,000,000 input tokens at half of $10, and 48,000 output tokens at half of
    # $50 per million.
    assert REVIEW.cost_bound_usd([request], MODEL) == pytest.approx(5.0 + 1.2)


def _project(tmp_path: Path, models: str) -> Path:
    (tmp_path / "docs" / "items").mkdir(parents=True)
    (tmp_path / "docket.toml").write_text(models, encoding="utf-8")
    return tmp_path


def test_the_reading_takes_the_table_s_review_model_and_its_price(tmp_path: Path) -> None:
    """The model, effort and price come from `[models]` (`PL-0XDM`)."""
    root = _project(
        tmp_path,
        '[models]\ndefault = { model = "model-a", effort = "high" }\n'
        '[[models.rule]]\nmatch = { role = "review" }\nmodel = "model-b"\neffort = "max"\n'
        "[models.prices]\nmodel-a = { input = 1, output = 2 }\n"
        "model-b = { input = 10, output = 50 }\n",
    )
    assert REVIEW.review_model(root) == REVIEW.ReviewModel(Choice("model-b", "max", 1), 10.0, 50.0)


def test_a_model_with_no_price_is_refused(tmp_path: Path) -> None:
    root = _project(tmp_path, '[models]\ndefault = { model = "model-a", effort = "high" }\n')
    with pytest.raises(REVIEW.Refused, match="no price for model-a"):
        REVIEW.review_model(root)


def test_the_project_table_prices_the_model_it_chooses() -> None:
    """The real table prices the model it chooses for a review."""
    model = REVIEW.review_model()
    assert model.input_usd_per_mtok > 0 and model.output_usd_per_mtok > 0


def test_real_document_builds_valid_requests() -> None:
    document, data = REVIEW.read_inputs()
    found = REVIEW.sections(document)
    assert found
    assert all(REVIEW.CUSTOM_ID_RE.match(s.custom_id) for s in found)
    assert all(path.startswith("src/anesthesia_sim/data/") for path in data)


def _line(custom_id: str, **result: object) -> dict[str, object]:
    return {"custom_id": custom_id, "result": result}


def _message(text: str, stop: str = "end_turn") -> dict[str, object]:
    return {
        "type": "succeeded",
        "message": {
            "stop_reason": stop,
            "usage": {"input_tokens": 10, "output_tokens": 5},
            "content": [{"type": "thinking", "thinking": "..."}, {"type": "text", "text": text}],
        },
    }


FINDING = {
    "kind": "data",
    "statement": "the blood:gas coefficient is 0.65",
    "conflicts_with": "src/anesthesia_sim/data/agents/a.json, x, 1",
    "explanation": "The stored value differs.",
    "confidence": "high",
}


def test_read_result_keeps_the_findings_of_a_finished_request() -> None:
    line = _line("s01-a", **_message(json.dumps({"findings": [FINDING]})))
    result = REVIEW.read_result(line, {"s01-a": "A"})
    assert result["status"] == "reviewed"
    assert result["heading"] == "A"
    assert result["findings"] == [FINDING]


@pytest.mark.parametrize(
    ("line", "status"),
    [
        (_line("s01-a", type="errored", error={"type": "overloaded"}), "the request errored"),
        (_line("s01-a", type="expired"), "the request expired"),
        (_line("s01-a", **_message('{"findings": []}', stop="max_tokens")), "'max_tokens'"),
        (_line("s01-a", **_message('{"findings": []}', stop="refusal")), "'refusal'"),
        (_line("s01-a", **_message("not json")), "not the findings JSON"),
        (_line("s01-a", **_message('{"other": []}')), "not the findings JSON"),
    ],
)
def test_read_result_marks_a_section_not_reviewed(line: dict[str, object], status: str) -> None:
    result = REVIEW.read_result(line, {"s01-a": "A"})
    assert result["status"].startswith("not reviewed")
    assert status in result["status"]
    assert "findings" not in result


@pytest.fixture
def small_tree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setattr(REVIEW, "read_inputs", lambda: (DOCUMENT, DATA))
    monkeypatch.setattr(REVIEW, "review_model", lambda: MODEL)
    monkeypatch.setattr(REVIEW, "REVIEW_DIR", tmp_path)
    return tmp_path


def _args(**fields: object) -> object:
    return type("Args", (), fields)()


def test_submit_refuses_a_bound_above_the_credit_left(small_tree: Path) -> None:
    def never(method: str, target: str, body: object) -> bytes:
        raise AssertionError("submit sent a batch it should have refused")

    with pytest.raises(REVIEW.Refused, match="more than the \\$0.01"):
        REVIEW.submit(_args(credit_left=0.01), send=never)


def test_submit_then_fetch_writes_the_findings_file(small_tree: Path) -> None:
    sent: list[tuple[str, str]] = []
    status = {"value": "in_progress"}

    def send(method: str, target: str, body: object) -> bytes:
        sent.append((method, target))
        if method == "POST":
            assert isinstance(body, dict) and len(body["requests"]) == 2
            return json.dumps({"id": "msgbatch_1"}).encode()
        if target.endswith("/msgbatch_1"):
            return json.dumps(
                {"processing_status": status["value"], "results_url": "https://r/x"}
            ).encode()
        lines = [
            _line("s02-second-part-two", **_message('{"findings": []}')),
            _line("s01-first-part", **_message(json.dumps({"findings": [FINDING]}))),
        ]
        return "\n".join(json.dumps(x) for x in lines).encode()

    assert REVIEW.submit(_args(credit_left=1000.0), send=send) == 0
    manifest = json.loads((small_tree / "msgbatch_1.manifest.json").read_text())
    assert manifest["sections"] == {
        "s01-first-part": "First part",
        "s02-second-part-two": "Second: part (two)",
    }
    assert manifest["inputs_sha256"] == REVIEW.digest(DOCUMENT, DATA)

    assert REVIEW.fetch(_args(batch_id="msgbatch_1"), send=send) == 2
    assert not (small_tree / "msgbatch_1.findings.json").exists()

    status["value"] = "ended"
    assert REVIEW.fetch(_args(batch_id="msgbatch_1"), send=send) == 0
    written = json.loads((small_tree / "msgbatch_1.findings.json").read_text())
    assert [r["custom_id"] for r in written["results"]] == ["s01-first-part", "s02-second-part-two"]
    assert written["results"][0]["findings"] == [FINDING]
    assert sent[0] == ("POST", "/v1/messages/batches")
    assert sent[-1] == ("GET", "https://r/x")


def test_fetch_refuses_without_the_manifest(small_tree: Path) -> None:
    with pytest.raises(REVIEW.Refused, match="no manifest"):
        REVIEW.fetch(_args(batch_id="msgbatch_missing"), send=lambda *a: b"")


def test_api_key_is_required() -> None:
    with pytest.raises(REVIEW.Refused, match="ANTHROPIC_API_KEY"):
        REVIEW.api_key({"ANTHROPIC_API_KEY": "  "})
