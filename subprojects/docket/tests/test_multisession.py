"""Several sessions and a forge working one store, end to end through the commands.

This ports the 2026-09-25 stress harness (`PL-P0FP`, `PL-VF3C`) into the suite.
A `World` is a bare `origin`, a clone that does GitHub's side of the work
(squash merges with `(#N)` subjects, branch deletion, closing a pull request),
and one clone per session. A fake forge script answers both forge commands
`docket.toml` names, from a JSON file the world writes, so a pull request can
be open, merged or closed, and the forge can be down. Every commit is dated
from the world's clock and every command gets `--now` from it, so no answer
depends on the wall clock.

The harness found eight violations, V1 to V8, and each was fixed under its own
item. Those items pinned each fix with a test of the one command it changed.
The tests here replay each scenario across every command a session reads, and
assert the invariant the violation broke: flight, show and next name the same
holder, a claim that exits 0 is one another session can see, and a branch
whose squash merge changed files holds none of its items. A regression in any
one reader fails here even where its own unit test still passes.

`test_random_interleavings` drives seeded random steps through the same world
and checks the invariants after every step. It is marked `slow` and is
deselected unless `-m slow` asks for it (`conftest.py`).
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from docket.claims import SESSION_VARIABLE
from docket.cli import main
from docket.store import ID_PATTERN

T0 = datetime(2026, 9, 25, 13, 0, tzinfo=UTC)
ATTRIBUTION = "Co-Authored-By: T <t@example.com>"
ID = re.compile(rf"\b{ID_PATTERN}")

#: The three ready items the seed holds, which `next` offers at the start.
X, Y, Z = "PL-X1X1", "PL-Y2Y2", "PL-Z3Z3"

#: The fake forge. It reads the world's JSON state and answers as
#: `tools/open_pull_requests.py` does: `BRANCH NUMBER` for each open pull
#: request, or with `--newest BRANCH BASE` one `NUMBER STATE HEAD` line for the
#: branch's newest pull request. It exits 1, printing nothing, when the forge
#: is down, which is the contract both commands owe (`docket.config`).
FORGE = """\
import json, sys
state = json.load(open(sys.argv[1]))
if state["down"]:
    sys.exit(1)
if "--newest" in sys.argv:
    pull = state["prs"].get(sys.argv[3])
    if pull:
        print(pull["number"], pull["state"], pull["head"])
else:
    for branch, pull in sorted(state["prs"].items()):
        if pull["state"] == "open":
            print(branch, pull["number"])
"""


def _item(identifier: str) -> str:
    return (
        f"---\nid: {identifier}\ntitle: The item {identifier}\npriority: P2\neffort: S\n"
        "status: ready\nadded: 2026-09-01\n---\n\n**Problem.** x\n"
    )


def _git(root: Path, *args: str, when: datetime, check: bool = True) -> str:
    env = {
        "GIT_AUTHOR_DATE": when.isoformat(),
        "GIT_COMMITTER_DATE": when.isoformat(),
        "GIT_AUTHOR_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "T",
        "GIT_COMMITTER_EMAIL": "t@example.com",
        "GIT_TERMINAL_PROMPT": "0",
    }
    done = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False, env=os.environ | env
    )
    if check and done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {root}: {done.stdout}{done.stderr}")
    return done.stdout


@dataclass
class Pull:
    number: int
    state: str  # open, merged or closed
    head: str
    #: Whether the squash changed any file. A squash of nothing but an empty
    #: claim commit proves nothing landed, so the branch's claims still apply
    #: (`docket.claims`, "An empty commit, the claim itself, ... proves no squash").
    landed: bool = False


@dataclass
class Session:
    root: Path
    branch: str = ""
    #: Each item this session was told it holds, by `claim` exiting 0, and the branch.
    believes: dict[str, str] = field(default_factory=dict)


class World:
    """A bare origin, GitHub's clone, and a clone per session, on one clock."""

    def __init__(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        sessions: int = 3,
    ) -> None:
        self.tmp = tmp_path
        self.monkeypatch = monkeypatch
        self.capsys = capsys
        self.t = T0
        self.prs: dict[str, Pull] = {}
        self.next_number = 1100
        self.down = False
        self.state = tmp_path / "forge.json"
        forge = tmp_path / "forge.py"
        forge.write_text(FORGE, encoding="utf-8")
        self._save()
        self.origin = tmp_path / "origin.git"
        _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(self.origin), when=self.t)
        seed = self._clone("seed")
        command = f"{sys.executable} {forge} {self.state}"
        files = {
            "docket.toml": (
                "[docket]\n"
                f"open_pull_requests_command = '{command}'\n"
                f"newest_pull_request_command = '{command} --newest'\n"
            ),
            f"docs/items/{X}-the-first.md": _item(X),
            f"docs/items/{Y}-the-second.md": _item(Y),
            f"docs/items/{Z}-the-third.md": _item(Z),
        }
        for path, text in files.items():
            target = seed / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        _git(seed, "add", "-A", when=self.t - timedelta(days=30))
        _git(seed, "commit", "-q", "-m", "base", when=self.t - timedelta(days=30))
        _git(seed, "push", "-q", "origin", "HEAD:refs/heads/main", when=self.t)
        self.gh = self._clone("gh")
        self.s = {f"s{i}": Session(self._clone(f"s{i}")) for i in range(1, sessions + 1)}

    # --- plumbing

    def _clone(self, name: str) -> Path:
        root = self.tmp / name
        _git(self.tmp, "clone", "-q", str(self.origin), str(root), when=self.t)
        for name_, value in (("user.email", "t@example.com"), ("user.name", "T")):
            _git(root, "config", name_, value, when=self.t)
        return root

    def _save(self) -> None:
        prs = {branch: pull.__dict__ for branch, pull in self.prs.items()}
        self.state.write_text(json.dumps({"down": self.down, "prs": prs}), encoding="utf-8")

    def tick(self, minutes: float = 1) -> None:
        self.t += timedelta(minutes=minutes)

    def git(self, who: str, *args: str, check: bool = True) -> str:
        root = self.gh if who == "gh" else self.s[who].root
        return _git(root, *args, when=self.t, check=check)

    def docket(self, who: str, *argv: str) -> tuple[int, str]:
        """Run one command in `who`'s clone as that session, and return its exit and output."""
        self.monkeypatch.setenv("GIT_AUTHOR_DATE", self.t.isoformat())
        self.monkeypatch.setenv("GIT_COMMITTER_DATE", self.t.isoformat())
        self.monkeypatch.setenv(SESSION_VARIABLE, f"cse_{who}")
        self.monkeypatch.chdir(self.s[who].root)
        self.capsys.readouterr()
        items = str(self.s[who].root / "docs" / "items")
        code = main([*argv, "--items", items, "--now", self.t.isoformat()])
        captured = self.capsys.readouterr()
        return code, captured.out + captured.err

    # --- what a session does

    def add_session(self, who: str) -> None:
        self.s[who] = Session(self._clone(who))

    def start(self, who: str, branch: str, *, track: bool = False) -> None:
        self.git(who, "fetch", "-q", "origin")
        how = ["--track"] if track else ["--no-track"]
        self.git(who, "checkout", "-q", *how, "-B", branch, "origin/main")
        self.s[who].branch = branch

    def fetch(self, who: str) -> None:
        self.git(who, "fetch", "-q", "origin")

    def claim(self, who: str, item: str, *extra: str) -> tuple[int, str]:
        code, out = self.docket(who, "claim", item, "--trailer", ATTRIBUTION, *extra)
        if code == 0:
            self.s[who].believes[item] = self.s[who].branch
        return code, out

    def capture(self, who: str, title: str) -> str:
        code, out = self.docket(who, "new", title)
        assert code == 0, out
        (identifier,) = dict.fromkeys(ID.findall(out))
        self.git(who, "add", "-A", "docs/items")
        self.git(who, "commit", "-q", "-m", f"{identifier}: capture")
        return identifier

    def work(self, who: str, item: str, name: str = "") -> None:
        path = self.s[who].root / "work" / (name or f"{self.s[who].branch.split('/')[-1]}.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{item} at {self.t.isoformat()}\n")
        self.git(who, "add", "-A", "work")
        self.git(who, "commit", "-q", "-m", f"{item}: work")

    def close(self, who: str, item: str) -> None:
        """Set `item` done in this branch's copy, as a close-out does."""
        (path,) = (self.s[who].root / "docs" / "items").glob(f"{item}-*.md")
        text = path.read_text(encoding="utf-8").replace(
            "status: ready", f"status: done\nclosed: {self.t.date()}"
        )
        path.write_text(text, encoding="utf-8")
        self.git(who, "add", "-A", "docs/items")
        self.git(who, "commit", "-q", "-m", f"{item}: close out")
        self.s[who].believes.pop(item, None)

    def push(self, who: str) -> None:
        self.git(who, "push", "-q", "-u", "origin", "HEAD")

    def unreachable(self, who: str, down: bool = True) -> None:
        url = str(self.tmp / "nowhere.git") if down else str(self.origin)
        self.git(who, "remote", "set-url", "origin", url)

    def open_pr(self, who: str) -> Pull:
        branch = self.s[who].branch
        pull = Pull(self.next_number, "open", self.git(who, "rev-parse", "HEAD").strip())
        self.next_number += 1
        self.prs[branch] = pull
        self._save()
        return pull

    # --- GitHub's side

    def squash_merge(self, branch: str) -> None:
        pull = self.prs[branch]
        self.git("gh", "fetch", "-q", "origin")
        self.git("gh", "checkout", "-q", "-B", "main", "origin/main")
        self.git("gh", "merge", "--squash", f"origin/{branch}")
        title = self.git("gh", "log", "-1", "--format=%s", f"origin/{branch}").strip()
        self.git("gh", "commit", "-q", "--allow-empty", "-m", f"{title} (#{pull.number})")
        self.git("gh", "push", "-q", "origin", "main")
        pull.landed = bool(self.git("gh", "diff", "--name-only", "HEAD~1", "HEAD").strip())
        pull.state = "merged"
        pull.head = self.git("gh", "rev-parse", f"origin/{branch}").strip()
        self._save()

    def close_pr(self, branch: str) -> None:
        self.prs[branch].state = "closed"
        self._save()

    def delete_branch(self, branch: str) -> None:
        self.git("gh", "push", "-q", "origin", "--delete", branch)

    def set_forge_down(self, down: bool) -> None:
        self.down = down
        self._save()

    # --- reads

    def flight_live(self, who: str) -> dict[str, list[str]]:
        """Each item `flight` lists as held by a live claim, and the refs holding it."""
        _, out = self.docket(who, "flight")
        held: dict[str, list[str]] = {}
        for line in out.splitlines():
            row = re.match(rf"^({ID_PATTERN})  (\S+)\s+live\b", line)
            if row:
                held.setdefault(row.group(1), []).append(row.group(2))
        return held

    def offered(self, who: str) -> list[str]:
        """The items `next` offers, in its order."""
        _, out = self.docket(who, "next", "--limit", "50")
        return [
            found.group(1) for found in re.finditer(rf"^\s+\d+\. P\d ({ID_PATTERN}) ", out, re.M)
        ]

    def holder(self, who: str, item: str) -> str:
        """The branch `show` names as holding `item`, or `""` where it names none."""
        _, out = self.docket(who, "show", item)
        found = re.search(r"^\s+holds it\s+(\S+)", out, re.M) or re.search(
            r"IN FLIGHT on (?:this branch \()?([^\s,)]+)", out
        )
        return found.group(1) if found else ""

    def agree(self, who: str, item: str, branch: str) -> None:
        """Flight, show and next in `who`'s clone all say `branch` holds `item`, and nobody else."""
        live = self.flight_live(who).get(item, [])
        assert len(live) == 1 and live[0].endswith(branch), f"flight: {live}"
        assert self.holder(who, item).endswith(branch), f"show: {self.holder(who, item)!r}"
        assert item not in self.offered(who), "next offers a held item"


@pytest.fixture
def world(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> World:
    return World(tmp_path, monkeypatch, capsys)


def test_v1_a_claim_confirmed_first_is_not_displaced_by_a_retry(world: World) -> None:
    """V1 (`PL-ZLJ9`): a claim written first but published last took the item.

    s2 writes its claim while its push fails, so nobody can see it. s1 then
    claims, is told it holds the item, and its claim is the one every clone
    sees. When s2 retries, its older claim used to order first and take the
    item from a session already told it held it.
    """
    world.start("s1", "claude/alpha-a3a3a3")
    world.start("s2", "claude/beta-b4b4b4")
    world.tick()
    world.unreachable("s2")
    code, out = world.claim("s2", X, "--no-fetch")
    assert code == 4, out
    world.unreachable("s2", down=False)
    world.tick()
    code, out = world.claim("s1", X)
    assert code == 0, out
    world.tick()
    code, out = world.claim("s2", X)
    assert code == 3, out
    for who in ("s1", "s2", "s3"):
        world.fetch(who)
        world.agree(who, X, "claude/alpha-a3a3a3")


def test_v2_a_claim_only_this_clone_holds_does_not_exit_0(world: World) -> None:
    """V2 (`PL-1X56`): a claim on a branch with a pull request open exited 0 unpushed.

    A captures-only push had opened the pull request first, so `claim` may not
    push: the pull request may be armed and would merge the claim away. It
    used to commit, say "not pushed", and exit 0, while another session's
    `next` still offered the item. Exit 4 says the claim is local, and
    `claim --push` then publishes it.
    """
    world.start("s1", "claude/alpha-iiii01")
    world.capture("s1", "A capture pushed before the claim")
    world.push("s1")
    world.open_pr("s1")
    world.tick()
    code, out = world.claim("s1", X)
    assert code == 4, out
    assert X in world.offered("s2")
    code, out = world.claim("s1", X, "--push")
    assert code == 0, out
    world.agree("s2", X, "claude/alpha-iiii01")


def test_v3_a_clone_behind_origin_main_does_not_offer_what_main_closed(world: World) -> None:
    """V3 (`PL-Y48N`): a fetched clone whose branch predates a merge offered the closed item.

    s2 forked before s1's pull request closed the item and squash-merged.
    s2's fetch then brings that merge into origin/main, but its own working
    tree still reads the item ready. `next` used to offer it and `show` said
    it was ready, with nothing to say origin/main had closed it.
    """
    world.start("s2", "claude/beta-cccc02")
    world.start("s1", "claude/alpha-cccc01")
    world.claim("s1", X)
    world.work("s1", X)
    world.close("s1", X)
    world.push("s1")
    world.open_pr("s1")
    world.tick(5)
    world.squash_merge("claude/alpha-cccc01")
    world.tick(2)
    for who in ("s2", "s3"):
        assert X not in world.offered(who), who
        assert X not in world.flight_live(who), who
        _, out = world.docket(who, "show", X)
        assert "done" in out.splitlines()[1] or "origin/main" in out, out


def test_v4_a_failed_fetch_is_said_by_every_read(world: World) -> None:
    """V4 (`PL-8Z1T`): after a fetch that failed, the reads answered as if it had worked.

    s2 fetched s1's branch, and s1's pull request then merged while s2's
    origin was unreachable. `branch` said "current with origin/main" and
    `stranded` printed recovery commands for an item that had already merged,
    with no word that the refs were older than the answer.
    """
    world.start("s1", "claude/alpha-kkkk01")
    world.capture("s1", "A capture that merges while s2 is offline")
    world.claim("s1", X)
    world.work("s1", X)
    world.push("s1")
    world.open_pr("s1")
    world.start("s2", "claude/beta-kkkk02")
    world.tick()
    world.squash_merge("claude/alpha-kkkk01")
    world.tick()
    world.unreachable("s2")
    for argv in (("branch",), ("stranded",), ("flight",), ("next",), ("show", X)):
        _, out = world.docket("s2", *argv)
        assert "`git fetch origin` failed, so nothing refreshed the refs" in out, argv[0]
    code, out = world.docket("s2", "arm")
    assert out.startswith("unknown"), out


def test_v5_a_merged_captures_only_branch_is_told_it_merged(world: World) -> None:
    """V5 (`PL-8BR0`): a squash leaves no commit of a captures-only branch on main.

    So `branch` read the merged branch as one behind and one ahead, and told
    the session to merge origin/main in and push, and `arm` answered `behind`.
    The next capture on the branch then landed nowhere. The forge's word that
    the pull request merged is now the evidence both read.
    """
    world.start("s1", "claude/capture-ffff01")
    world.capture("s1", "A capture that rides a captures-only branch")
    world.push("s1")
    world.open_pr("s1")
    world.tick()
    _, out = world.docket("s1", "arm")
    assert out.startswith("arm"), out
    world.tick(3)
    world.squash_merge("claude/capture-ffff01")
    world.tick()
    _, out = world.docket("s1", "branch")
    assert "#1100" in out and "merged" in out, out
    assert "git merge origin/main" not in out, out
    _, out = world.docket("s1", "arm")
    assert not out.startswith(("arm", "behind")), out


def test_v6_an_item_a_pull_request_carries_is_not_left_behind(world: World) -> None:
    """V6 (`PL-X3NY`): `stranded` could not tell work in flight from work abandoned.

    A capture on a branch with its pull request open was listed as only on a
    branch, with a `recover:` line, as if its session had gone. Now the open
    pull request is named as carrying it. Once the pull request closes
    unmerged, the capture is left behind, and the `recover:` line returns.
    """
    world.start("s1", "claude/capture-eeee01")
    capture = world.capture("s1", "A capture on a branch whose pull request is open")
    world.push("s1")
    pull = world.open_pr("s1")
    world.tick(30)
    _, out = world.docket("s2", "stranded")
    entry = out.split(capture, 1)[1].split("\n\n", 1)[0]
    assert f"carried: pull request #{pull.number} is open" in entry, out
    assert "recover:" not in entry, out
    world.close_pr("claude/capture-eeee01")
    world.tick(30)
    _, out = world.docket("s2", "stranded")
    entry = out.split(capture, 1)[1].split("\n\n", 1)[0]
    assert "recover: git checkout origin/claude/capture-eeee01" in entry, out
    assert f"#{pull.number}" not in entry, out


def test_v7_a_down_forge_is_said_and_never_read_as_none_open(world: World) -> None:
    """V7 (`PL-D1P5`, extending `PL-QSGX`): a read that could not ask said nothing of it.

    `flight` names the pull request open on each branch. With the forge down
    it must say it could not ask, rather than print the row the way it prints
    a branch with no pull request.
    """
    world.start("s1", "claude/alpha-l2l2l2")
    world.claim("s1", X)
    world.work("s1", X)
    world.close("s1", X)
    world.push("s1")
    world.open_pr("s1")
    world.tick()
    _, out = world.docket("s2", "flight")
    assert "#1100" in out, out
    world.set_forge_down(True)
    _, out = world.docket("s2", "flight")
    assert "could not be read" in out or "could not ask" in out, out
    assert "no pull request open" not in out, out


def test_v8_a_branch_tracking_origin_main_can_claim(world: World) -> None:
    """V8 (`PL-KX73`): the web harness starts a branch whose upstream is origin/main.

    The claim refused it as pushing to a second branch. Every claim the harness
    started that way had to be renamed by hand first.
    """
    world.start("s1", "claude/web-uuuu01", track=True)
    code, out = world.claim("s1", X)
    assert code == 0, out
    world.fetch("s2")
    world.agree("s2", X, "claude/web-uuuu01")


#: The items a random run claims from: the seed's three and one that does not exist.
POOL = (X, Y, Z, "PL-Q9Q9")


class RandomRun:
    """Seeded random steps by three sessions, with the invariants checked after each one.

    An oracle clone, fetched before every check and detached at origin/main,
    plays a session arriving fresh. Each violation is recorded with its step,
    and the run's trace is what a finding is filed with.
    """

    def __init__(self, world: World, seed: int) -> None:
        self.w = world
        self.rng = random.Random(seed)
        self.seed = seed
        self.w.add_session("oracle")
        self.trace: list[str] = []
        self.violations: list[str] = []
        self.n = 0

    def step(self) -> tuple[str, str]:
        w, rng = self.w, self.rng
        who = rng.choice(["s1", "s2", "s3"])
        session = w.s[who]
        pull = w.prs.get(session.branch)
        if not session.branch or (pull and pull.state != "open" and rng.random() < 0.7):
            self.n += 1
            w.start(who, f"claude/r{self.seed}-{who}-{self.n:02d}")
            return who, "start"
        ops = {
            "capture": 6, "claim": 10, "claim_nf": 4, "work": 8, "close": 4, "push": 10,
            "open_pr": 6, "merge_main": 3, "squash": 7, "close_pr": 2, "delete": 3,
            "fetch": 8, "tick": 8, "days": 1, "yield": 2,
        }  # fmt: skip
        op = rng.choices(list(ops), weights=list(ops.values()))[0]
        mine = [item for item, branch in session.believes.items() if branch == session.branch]
        if op == "capture":
            self.n += 1
            w.capture(who, f"A random capture {self.n} by {who}")
        elif op in ("claim", "claim_nf"):
            item = rng.choice(POOL)
            code, _ = w.claim(who, item, *(["--no-fetch"] if op == "claim_nf" else []))
            op = f"{op} {item} -> {code}"
        elif op == "work":
            w.work(who, rng.choice(mine or list(POOL)))
        elif op == "close" and mine:
            item = rng.choice(mine)
            w.close(who, item)
            op = f"close {item}"
        elif op == "push":
            w.git(who, "push", "-q", "-u", "origin", "HEAD", check=False)
        elif op == "open_pr" and (pull is None or pull.state != "open"):
            if w.git(who, "ls-remote", "--heads", "origin", session.branch).strip():
                w.open_pr(who)
        elif op == "merge_main":
            w.fetch(who)
            try:
                w.git(who, "merge", "-q", "--no-edit", "origin/main")
            except RuntimeError:
                w.git(who, "merge", "--abort", check=False)
        elif op == "squash":
            branches = [branch for branch, pull_ in w.prs.items() if pull_.state == "open"]
            if branches:
                branch = rng.choice(branches)
                try:
                    w.squash_merge(branch)
                    op = f"squash {branch}"
                except RuntimeError:
                    w.git("gh", "reset", "-q", "--hard", "origin/main")
        elif op == "close_pr":
            branches = [branch for branch, pull_ in w.prs.items() if pull_.state == "open"]
            if branches:
                w.close_pr(rng.choice(branches))
        elif op == "delete":
            heads = w.git("gh", "ls-remote", "--heads", "origin")
            done = [b for b, p in w.prs.items() if p.state != "open" and f"refs/heads/{b}" in heads]
            if done:
                w.delete_branch(rng.choice(done))
        elif op == "fetch":
            w.fetch(who)
        elif op == "tick":
            w.tick(rng.choice([1, 5, 30, 120]))
        elif op == "days":
            w.t += timedelta(days=rng.choice([3, 8]))
        elif op == "yield" and mine:
            item = rng.choice(mine)
            code, _ = w.docket(who, "yield", item, "--trailer", ATTRIBUTION)
            # Exit 4 wrote the yield and left it for the next push to publish.
            if code in (0, 4):
                session.believes.pop(item, None)
            op = f"yield {item} -> {code}"
        return who, op

    def violate(self, step: int, text: str) -> None:
        self.violations.append(f"step {step}: {text}")

    def check(self, step: int, actor: str) -> None:
        w = self.w
        w.git("oracle", "fetch", "-q", "--prune", "origin")
        w.git("oracle", "checkout", "-q", "--detach", "origin/main")
        live = w.flight_live("oracle")
        offered = w.offered("oracle")
        heads = w.git("gh", "ls-remote", "--heads", "origin")
        for item in POOL:
            done = w.git(
                "oracle",
                "grep",
                "-l",
                "^status: done",
                "HEAD",
                "--",
                f"docs/items/{item}-*",
                check=False,
            )
            holders = live.get(item, [])
            holder = w.holder("oracle", item)
            if len(holders) > 1:
                self.violate(step, f"flight lists {item} live on {holders}")
            if holders and not done:
                if item in offered:
                    self.violate(step, f"next offers {item}, which flight says {holders} holds")
                if not any(ref.endswith(holder.split("/")[-1]) for ref in holders) or not holder:
                    self.violate(step, f"flight says {holders} hold {item}, show says {holder!r}")
            for who in ("s1", "s2", "s3"):
                branch = w.s[who].believes.get(item)
                pull = w.prs.get(branch or "")
                if (
                    branch is None
                    or done
                    or branch != w.s[who].branch
                    or f"refs/heads/{branch}" not in heads
                    or (pull is not None and pull.state != "open")
                    # Past seven days a claim may have lapsed, which this does not model.
                    or w.t - T0 > timedelta(days=7)
                ):
                    continue
                if not holder.endswith(branch):
                    self.violate(
                        step, f"{who} was told it holds {item} on {branch}; show names {holder!r}"
                    )
        for branch, pull in w.prs.items():
            tip = w.git(
                "oracle", "rev-parse", "--verify", "--quiet", f"origin/{branch}", check=False
            ).strip()
            if pull.state == "merged" and pull.landed and tip == pull.head:
                for item, refs in live.items():
                    if any(ref.endswith(branch) for ref in refs):
                        self.violate(step, f"{item} is live on {branch}, whose pull request merged")
        if actor not in w.s or not w.s[actor].branch:
            return
        _, said = w.docket(actor, "arm", "--no-fetch")
        behind = int(w.git(actor, "rev-list", "--count", "HEAD..origin/main").strip())
        counted = re.match(r"behind (\d+)", said)
        if counted and int(counted.group(1)) != behind:
            self.violate(step, f"{actor}'s arm says behind {counted.group(1)}; git counts {behind}")
        if said.startswith("arm") and behind:
            self.violate(step, f"{actor}'s arm says arm while {behind} behind")
        pull = w.prs.get(w.s[actor].branch)
        if pull and pull.state == "merged" and said.startswith(("arm", "behind")):
            self.violate(step, f"{actor}'s arm answers {said.split()[0]} on merged #{pull.number}")
        for item in w.offered(actor):
            closed = w.git(
                actor,
                "grep",
                "-l",
                "^status: done",
                "origin/main",
                "--",
                f"docs/items/{item}-*",
                check=False,
            )
            if closed:
                self.violate(step, f"{actor}'s next offers {item}, which its origin/main closed")

    def run(self, steps: int) -> None:
        for step in range(1, steps + 1):
            before = self.w.t
            actor, op = self.step()
            self.trace.append(f"{step:02d} [{before:%m-%d %H:%M}] {actor} {op}")
            self.check(step, actor)


@pytest.mark.slow
@pytest.mark.parametrize("seed", range(1, 21))
def test_random_interleavings(world: World, seed: int) -> None:
    """Thirty seeded random steps hold every invariant the eight scenarios above assert.

    Run against the claim code before `#1026` (`PL-1X56`), 14 of these 20 seeds
    fail, each on a session told it holds an item that no other clone can see.
    A violation here is a finding: file it with the trace this prints.
    """
    run = RandomRun(world, seed)
    run.run(30)
    assert not run.violations, "\n".join([*run.violations, "", "trace:", *run.trace])
