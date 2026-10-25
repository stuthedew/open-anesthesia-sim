"""Have Fable 5.1 read `docs/MODEL.md` against the stored data once, as one message batch.

`docs/MODEL.md` is the specification of the clinical model, and every value
under `src/anesthesia_sim/data/` is cited from it. A statement there that
contradicts a stored value, another statement or its own units could mislead a
learner, and no session has read the whole document against the data in one
pass, because it does not fit in one session's budget (`PL-5S71`). This tool
buys that reading on the owner's API credit.

**How the requests are built.** The document and the data files total about
215,000 tokens, which fits in Fable 5.1's 1M-token context. So each request
carries all of both, and asks the model to review the statements of one `##`
section against the whole. That finds a contradiction between two sections,
which a request carrying only its own section could not. The shared part comes
first and is marked for the prompt cache, so after the first request the rest
can read it at a fortieth of the input price. Inside a batch the cache is best
effort, so the cost bound this tool prints assumes no cache hits at all. The
model returns its findings as JSON against `FINDINGS_SCHEMA`.

**What it does not do.** It files nothing. A session reads the findings file,
checks each finding against the document, the data and the cited source, and
files each confirmed one as its own item, classed `science` or `safety`. A
model's reading is a lead to verify, never a finding to rely on.

It runs on the owner's machine, because the key and the credit are there, as
`tools/headless_worker.py` does (`PL-80R5`):

- `estimate` builds the requests, prints how many there are and the most they
  could cost, and sends nothing. `--write PATH` also saves the batch body for
  reading.
- `submit --credit-left USD` sends the batch, refusing when the cost bound is
  more than the credit left. It saves a manifest beside the results and prints
  the batch id.
- `fetch BATCH_ID` reports the batch's progress, and once it has ended,
  downloads the results and writes one findings file for a session to read.

The API's request shape, model and prices are from the Claude API reference
as read on 2026-10-25: Message Batches at `/v1/messages/batches`, the
`anthropic-version` `2026-10-21`, which refuses `temperature`, `top_p` and
`top_k`, and Fable 5.1's batch prices of $5 and $25 per million input and
output tokens. Fable 5.1 always thinks, so no `thinking` field is sent and
`output_config.effort` sets how hard it works.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from docket.lines import split_lines  # noqa: E402
from docket.vcs import tracked_under  # noqa: E402

from headless_worker import STATE_DIR, Refused, read_effort_level  # noqa: E402
from product_paths import DATA_DIR, MODEL_DOC  # noqa: E402

#: The strongest model, which the owner asked to do this reading (`PL-5S71`).
REVIEW_MODEL = "claude-fable-5-1"

ANTHROPIC_API = "https://api.anthropic.com"
BATCHES_PATH = "/v1/messages/batches"
ANTHROPIC_VERSION = "2026-10-21"

#: The most output, thinking included, that one section's request may use.
#: Fable 5.1 allows 128,000. This is large enough for a long section's
#: thinking and findings, and it bounds what a runaway request can cost.
MAX_OUTPUT_TOKENS = 48_000

#: Batch prices for Fable 5.1, in US dollars per million tokens.
BATCH_INPUT_USD_PER_MTOK = 5.0
BATCH_OUTPUT_USD_PER_MTOK = 25.0

#: Bytes per token assumed for the cost bound. English prose runs nearer four,
#: so three overstates the input on purpose.
BOUND_BYTES_PER_TOKEN = 3

#: How long one API call may take, in seconds.
API_TIMEOUT_S = 120

#: Where `submit` saves the manifest and `fetch` writes the findings.
REVIEW_DIR = STATE_DIR / "model-doc-review"

#: A batch request's `custom_id` must match this, per the API reference.
CUSTOM_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

KINDS = ("data", "internal", "unit")

FINDINGS_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": list(KINDS)},
                    "statement": {"type": "string"},
                    "conflicts_with": {"type": "string"},
                    "explanation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["kind", "statement", "conflicts_with", "explanation", "confidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["findings"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """\
You are reviewing the specification of an educational simulator of \
inhaled-anesthetic uptake and distribution. The specification is \
docs/MODEL.md. The parameter values the simulator stores are the JSON files \
under src/anesthesia_sim/data/. Both are given in full below.

A clinician could act on what the simulator displays, so a statement in the \
specification that is wrong or misleading is a safety problem. Your job is to \
find such statements in one section, which the request names.

Report only these three kinds of finding:

- "data": a statement in the section that contradicts a value, a unit or a \
field stored in one of the data files.
- "internal": a statement in the section that contradicts a statement \
elsewhere in the specification, in this section or another.
- "unit": a unit in the section that is wrong for its quantity, or an \
equation or conversion whose units do not balance.

Do not report style, wording, structure, missing material, or a disagreement \
with published literature that the text itself does not state. Each finding \
will be checked by a person against the files and the cited sources, so a \
finding that does not survive the check costs their time. Prefer a short list \
of findings you are sure of. An empty list is a good result for a sound \
section.

For each finding, give in "statement" the exact words from the named section, \
copied so they can be searched for. Give in "conflicts_with" either the exact \
words of the other statement, or the data file's path, the field and the \
stored value. Explain the conflict in one or two plain sentences.\
"""


@dataclass(frozen=True)
class Section:
    """One `##` section of the model document, with the request that reviews it."""

    custom_id: str
    heading: str
    text: str


def sections(document: str) -> list[Section]:
    """Each `##` section of `document`, in order, outside any fenced code block.

    The text before the first `##` heading is the document's title and is not a
    section. Each section's id leads with its position, so ids stay unique and
    sort in document order.
    """
    found: list[tuple[str, list[str]]] = []
    fenced = False
    for line in split_lines(document, keepends=True):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            found.append((line[3:].strip(), [line]))
        elif found:
            found[-1][1].append(line)
    out = []
    for index, (heading, lines) in enumerate(found, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        custom_id = f"s{index:02d}-{slug}"[:64].rstrip("-")
        out.append(Section(custom_id, heading, "".join(lines)))
    return out


def shared_prefix(document: str, data: Mapping[str, str]) -> list[dict[str, object]]:
    """The content every request shares: the document, then each data file by path.

    The last block carries the cache marker, so the whole of it is one cache
    entry. The one-hour lifetime is the one the API reference advises inside a
    batch, where requests can be processed more than five minutes apart.
    """
    blocks: list[dict[str, object]] = [
        {"type": "text", "text": f"<file path={MODEL_DOC!r}>\n{document}\n</file>"}
    ]
    for path, text in data.items():
        blocks.append({"type": "text", "text": f"<file path={path!r}>\n{text}\n</file>"})
    blocks[-1]["cache_control"] = {"type": "ephemeral", "ttl": "1h"}
    return blocks


def instruction(section: Section) -> str:
    """The part of a request that names the one section it reviews."""
    return (
        f"Review the section of docs/MODEL.md headed {section.heading!r}. Report "
        "findings only for statements inside that section, checked against the "
        "whole specification and every data file above."
    )


def build_requests(document: str, data: Mapping[str, str], effort: str) -> list[dict[str, object]]:
    """One batch request per section, each carrying the shared prefix."""
    prefix = shared_prefix(document, data)
    requests: list[dict[str, object]] = []
    for section in sections(document):
        if not CUSTOM_ID_RE.match(section.custom_id):
            raise Refused(f"section id {section.custom_id!r} is not one the API accepts")
        requests.append(
            {
                "custom_id": section.custom_id,
                "params": {
                    "model": REVIEW_MODEL,
                    "max_tokens": MAX_OUTPUT_TOKENS,
                    "system": SYSTEM_PROMPT,
                    "messages": [
                        {
                            "role": "user",
                            "content": [*prefix, {"type": "text", "text": instruction(section)}],
                        }
                    ],
                    "output_config": {
                        "effort": effort,
                        "format": {"type": "json_schema", "schema": FINDINGS_SCHEMA},
                    },
                },
            }
        )
    if len({r["custom_id"] for r in requests}) != len(requests):
        raise Refused("two sections share an id, so their results could not be told apart")
    return requests


def cost_bound_usd(requests: Sequence[Mapping[str, object]]) -> float:
    """The most the batch could cost, assuming no cache hit and every output at its cap."""
    input_bytes = sum(len(json.dumps(r["params"]).encode()) for r in requests)
    input_tokens = input_bytes / BOUND_BYTES_PER_TOKEN
    output_tokens = MAX_OUTPUT_TOKENS * len(requests)
    return (
        input_tokens * BATCH_INPUT_USD_PER_MTOK + output_tokens * BATCH_OUTPUT_USD_PER_MTOK
    ) / 1_000_000


def read_inputs(root: Path = ROOT) -> tuple[str, dict[str, str]]:
    """The model document, and each data file the repository tracks, by path."""
    document = (root / MODEL_DOC).read_text(encoding="utf-8")
    data = {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in tracked_under(root, DATA_DIR, ".json")
    }
    if not data:
        raise Refused(f"no data files are tracked under {DATA_DIR}")
    return document, data


def digest(document: str, data: Mapping[str, str]) -> str:
    """A hash of exactly what was reviewed, so findings can be matched to a tree."""
    h = hashlib.sha256(document.encode())
    for path, text in data.items():
        h.update(path.encode())
        h.update(text.encode())
    return h.hexdigest()


#: Sends one API call: the method, the path or full URL, and the JSON body or
#: `None`. Returns the response body as bytes.
Sender = Callable[[str, str, object], bytes]


def http_sender(key: str) -> Sender:
    """A `Sender` that calls the Anthropic API with `key`."""

    def send(method: str, target: str, body: object) -> bytes:
        url = target if target.startswith("https://") else ANTHROPIC_API + target
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "x-api-key": key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=API_TIMEOUT_S) as response:
                return bytes(response.read())
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:500]
            raise Refused(f"{method} {url} returned {error.code}: {detail}") from error

    return send


def api_key(environ: Mapping[str, str]) -> str:
    """The API key, or a refusal that says where to get one."""
    key = environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise Refused(
            "ANTHROPIC_API_KEY is not set. Create a key in the Console organization "
            "linked to the credit and export it first (docs/maintainer.md)."
        )
    return key


def message_text(message: Mapping[str, object]) -> str:
    """The text blocks of a returned message, joined; thinking blocks are left out."""
    content = message.get("content")
    if not isinstance(content, list):
        return ""
    return "".join(
        str(block.get("text", ""))
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def read_result(line: Mapping[str, object], headings: Mapping[str, str]) -> dict[str, object]:
    """One section's outcome from one line of the batch's results.

    A request that did not succeed, stopped for a reason other than finishing,
    or returned text that is not the findings JSON is kept with the reason, so
    the reading session knows which sections were not reviewed.
    """
    custom_id = str(line.get("custom_id", ""))
    out: dict[str, object] = {"custom_id": custom_id, "heading": headings.get(custom_id, "")}
    result = line.get("result")
    if not isinstance(result, dict) or result.get("type") != "succeeded":
        kind = result.get("type") if isinstance(result, dict) else None
        out["status"] = f"not reviewed: the request {kind or 'returned no result'}"
        out["error"] = result.get("error") if isinstance(result, dict) else None
        return out
    message = result.get("message")
    if not isinstance(message, dict):
        out["status"] = "not reviewed: the result carries no message"
        return out
    out["stop_reason"] = message.get("stop_reason")
    out["usage"] = message.get("usage")
    if message.get("stop_reason") != "end_turn":
        out["status"] = f"not reviewed: the model stopped with {message.get('stop_reason')!r}"
        return out
    try:
        findings = json.loads(message_text(message))["findings"]
    except (ValueError, KeyError, TypeError):
        out["status"] = "not reviewed: the reply was not the findings JSON"
        out["text"] = message_text(message)[:2000]
        return out
    out["status"] = "reviewed"
    out["findings"] = findings
    return out


def summarize(results: Sequence[Mapping[str, object]]) -> list[str]:
    """One line per section, then the totals, for the terminal."""
    lines = []
    for r in results:
        findings = r.get("findings")
        count = len(findings) if isinstance(findings, list) else 0
        lines.append(f"{r['custom_id']}: {r['status']}, {count} findings")
    reviewed = sum(1 for r in results if r.get("status") == "reviewed")
    total = sum(len(f) for r in results if isinstance(f := r.get("findings"), list))
    lines.append(f"{reviewed} of {len(results)} sections reviewed, {total} findings in all")
    return lines


def estimate(args: argparse.Namespace) -> int:
    document, data = read_inputs()
    requests = build_requests(document, data, read_effort_level())
    if args.write:
        args.write.write_text(json.dumps({"requests": requests}, indent=1), encoding="utf-8")
        print(f"wrote the batch body to {args.write}")
    print(f"{len(requests)} requests, one per section of {MODEL_DOC}, over {len(data)} data files")
    print(f"at most ${cost_bound_usd(requests):.2f}, with no cache hit and every output at its cap")
    return 0


def submit(args: argparse.Namespace, send: Sender | None = None) -> int:
    document, data = read_inputs()
    effort = read_effort_level()
    requests = build_requests(document, data, effort)
    bound = cost_bound_usd(requests)
    if not math.isfinite(args.credit_left) or bound > args.credit_left:
        raise Refused(
            f"the batch could cost up to ${bound:.2f}, more than the ${args.credit_left:.2f} "
            "of credit left"
        )
    send = send or http_sender(api_key(os.environ))
    batch = json.loads(send("POST", BATCHES_PATH, {"requests": requests}))
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "batch_id": batch["id"],
        "submitted_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "model": REVIEW_MODEL,
        "effort": effort,
        "inputs_sha256": digest(document, data),
        "data_files": list(data),
        "sections": {s.custom_id: s.heading for s in sections(document)},
        "cost_bound_usd": round(bound, 2),
    }
    path = REVIEW_DIR / f"{batch['id']}.manifest.json"
    path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"submitted {len(requests)} requests as batch {batch['id']}")
    print(f"saved {path}")
    print(f"check on it with: uv run python tools/model_doc_review.py fetch {batch['id']}")
    return 0


def fetch(args: argparse.Namespace, send: Sender | None = None) -> int:
    manifest_path = REVIEW_DIR / f"{args.batch_id}.manifest.json"
    if not manifest_path.exists():
        raise Refused(f"no manifest at {manifest_path}; was the batch submitted from here?")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    send = send or http_sender(api_key(os.environ))
    batch = json.loads(send("GET", f"{BATCHES_PATH}/{args.batch_id}", None))
    if batch.get("processing_status") != "ended":
        progress = batch.get("processing_status")
        print(f"batch {args.batch_id} is {progress}: {batch.get('request_counts')}")
        print("run fetch again later; most batches end within an hour, and all within 24")
        return 2
    raw = send("GET", str(batch["results_url"]), None).decode()
    headings = manifest["sections"]
    results = sorted(
        (read_result(json.loads(line), headings) for line in split_lines(raw) if line.strip()),
        key=lambda r: str(r["custom_id"]),
    )
    out = REVIEW_DIR / f"{args.batch_id}.findings.json"
    out.write_text(
        json.dumps({"manifest": manifest, "results": results}, indent=1), encoding="utf-8"
    )
    print("\n".join(summarize(results)))
    print(f"wrote {out}; attach this file to the project thread for a session to check")
    return 0


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    est = commands.add_parser("estimate", help="build the requests and print the cost bound")
    est.add_argument("--write", type=Path, help="also save the batch body here")
    sub = commands.add_parser("submit", help="send the batch")
    sub.add_argument("--credit-left", type=float, required=True, help="US dollars of credit left")
    got = commands.add_parser("fetch", help="report progress, and write the findings once ended")
    got.add_argument("batch_id")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    command = {"estimate": estimate, "submit": submit, "fetch": fetch}[args.command]
    try:
        return command(args)
    except Refused as refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
