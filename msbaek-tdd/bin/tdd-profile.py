#!/usr/bin/env python3
"""tdd-profile — where does a msbaek-tdd session spend time and tokens?

Reads a Claude Code session transcript (JSONL) plus its subagents/ directory and
prints a per-phase breakdown. A "phase" is the most recent Skill invocation in
the main context (tdd-plan, tdd-rgb, ...); everything until the next Skill call
is attributed to it. Subagent runs are attributed to the phase active when they
were spawned.

Usage:
    tdd-profile.py                            # current cwd's transcript dir (most msbaek-tdd activity)
    tdd-profile.py <session.jsonl>            # one session
    tdd-profile.py <project-transcript-dir>   # picks the session with most msbaek-tdd activity
    tdd-profile.py ... --json                 # machine-readable
    tdd-profile.py ... --idle 600             # gap (s) treated as idle, excluded from wall-clock

Zero dependencies. Never modifies anything.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

IDLE_GAP_S = 600  # gaps longer than this are user think-time, not model time


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    pass


def pick_session(dir_path):
    best, best_n = None, -1
    for name in os.listdir(dir_path):
        if not name.endswith(".jsonl"):
            continue
        p = os.path.join(dir_path, name)
        n = 0
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "msbaek-tdd" in line and '"type":"assistant"' in line:
                    n += 1
        if n > best_n:
            best, best_n = p, n
    return best


class Bucket:
    def __init__(self):
        self.turns = 0
        self.inp = self.out = self.cache_read = self.cache_create = 0
        self.tools = defaultdict(int)
        self.wall_s = 0.0
        self.agents = []  # dicts
        self.first_ts = None
        self.last_ts = None
        self.models = defaultdict(int)   # "model/effort" -> turns

    def add_usage(self, u):
        self.turns += 1
        self.inp += u.get("input_tokens", 0)
        self.out += u.get("output_tokens", 0)
        self.cache_read += u.get("cache_read_input_tokens", 0)
        self.cache_create += u.get("cache_creation_input_tokens", 0)

    @property
    def total_in(self):
        return self.inp + self.cache_read + self.cache_create


def profile_subagent(path):
    b = Bucket()
    model = None
    prev = None
    seen = set()
    for rec in read_jsonl(path):
        ts = rec.get("timestamp")
        if ts:
            t = parse_ts(ts)
            if prev is not None:
                b.wall_s += min(t - prev, IDLE_GAP_S)
            prev = t
            b.first_ts = b.first_ts or t
            b.last_ts = t
        msg = rec.get("message") or {}
        if rec.get("type") == "assistant":
            model = msg.get("model") or model
            req = rec.get("requestId") or rec.get("uuid")
            if "usage" in msg and req not in seen:
                seen.add(req)
                b.add_usage(msg["usage"])
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    b.tools[c.get("name")] += 1
    return b, model


def profile(session_path, idle_gap):
    global IDLE_GAP_S
    IDLE_GAP_S = idle_gap
    sub_dir = os.path.join(os.path.splitext(session_path)[0], "subagents")
    phases = {}
    order = []
    phase = "(before first skill)"
    prev_t = None
    turn_rows = []  # (tokens_total_in, out, phase, ts, first tool)
    agent_spawn = {}  # toolUseId -> (phase, ts)
    seen_req = set()  # one API turn is written once per content block — count usage once

    def bucket(name):
        if name not in phases:
            phases[name] = Bucket()
            order.append(name)
        return phases[name]

    for rec in read_jsonl(session_path):
        if rec.get("isSidechain"):
            continue
        ts = rec.get("timestamp")
        t = parse_ts(ts) if ts else None
        msg = rec.get("message") or {}
        if rec.get("type") != "assistant":
            if t is not None:
                prev_t = t
            continue
        # phase switch on Skill call
        tools_here = []
        for c in msg.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                tools_here.append(c)
                if c.get("name") == "Skill":
                    phase = (c.get("input") or {}).get("skill") or phase
                if c.get("name") in ("Agent", "Task"):
                    agent_spawn[c.get("id")] = (phase, t)
        b = bucket(phase)
        if t is not None:
            if prev_t is not None:
                b.wall_s += min(t - prev_t, IDLE_GAP_S)
            prev_t = t
            b.first_ts = b.first_ts or t
            b.last_ts = t
        req = rec.get("requestId") or rec.get("uuid")
        if "usage" in msg and req not in seen_req:
            seen_req.add(req)
            u = msg["usage"]
            b.add_usage(u)
            b.models[f"{msg.get('model','?')}/{rec.get('effort','-')}"] += 1
            total_in = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                        + u.get("cache_creation_input_tokens", 0))
            turn_rows.append((u.get("cache_creation_input_tokens", 0), u.get("output_tokens", 0),
                              total_in, phase, ts, tools_here[0].get("name") if tools_here else "-"))
        for c in tools_here:
            b.tools[c.get("name")] += 1

    # subagents
    if os.path.isdir(sub_dir):
        for name in sorted(os.listdir(sub_dir)):
            if not name.endswith(".meta.json"):
                continue
            meta = json.load(open(os.path.join(sub_dir, name), encoding="utf-8"))
            jsonl = os.path.join(sub_dir, name.replace(".meta.json", ".jsonl"))
            if not os.path.exists(jsonl):
                continue
            sb, model = profile_subagent(jsonl)
            ph, spawn_t = agent_spawn.get(meta.get("toolUseId"), (None, None))
            if ph is None:
                # fall back: phase active at subagent start time
                ph = "(unattributed)"
                if sb.first_ts:
                    for p in order:
                        pb = phases[p]
                        if pb.first_ts and pb.last_ts and pb.first_ts <= sb.first_ts <= pb.last_ts + 1:
                            ph = p
            bucket(ph).agents.append({
                "type": meta.get("agentType"), "description": meta.get("description"),
                "model": model or meta.get("model"), "wall_s": round(sb.wall_s),
                "turns": sb.turns, "in": sb.total_in, "cache_create": sb.cache_create,
                "out": sb.out, "tools": dict(sb.tools),
            })
    return order, phases, turn_rows


def fmt_k(n):
    return f"{n/1000:,.0f}k" if n >= 1000 else str(n)


def fmt_dur(s):
    m = int(s // 60)
    return f"{m//60}h{m%60:02d}m" if m >= 60 else f"{m}m{int(s%60):02d}s"


def report(order, phases, turn_rows):
    W = 34
    print(f"{'phase':<{W}} {'wall':>7} {'turns':>5} {'in(total)':>10} {'cache+':>8} {'out':>7} {'tools':>5} {'agents':>6}")
    print("-" * (W + 62))
    tot = Bucket()
    for p in order:
        b = phases[p]
        a_in = sum(a["in"] for a in b.agents)
        a_out = sum(a["out"] for a in b.agents)
        a_wall = sum(a["wall_s"] for a in b.agents)
        print(f"{p[:W]:<{W}} {fmt_dur(b.wall_s):>7} {b.turns:>5} {fmt_k(b.total_in):>10} "
              f"{fmt_k(b.cache_create):>8} {fmt_k(b.out):>7} {sum(b.tools.values()):>5} {len(b.agents):>6}")
        if b.agents:
            print(f"{'  └ agents (own context)':<{W}} {fmt_dur(a_wall):>7} {'':>5} {fmt_k(a_in):>10} "
                  f"{fmt_k(sum(a['cache_create'] for a in b.agents)):>8} {fmt_k(a_out):>7}")
        tot.wall_s += b.wall_s
        tot.turns += b.turns
        tot.inp += b.inp; tot.out += b.out
        tot.cache_read += b.cache_read; tot.cache_create += b.cache_create
    print("-" * (W + 62))
    print(f"{'TOTAL (main context)':<{W}} {fmt_dur(tot.wall_s):>7} {tot.turns:>5} {fmt_k(tot.total_in):>10} "
          f"{fmt_k(tot.cache_create):>8} {fmt_k(tot.out):>7}")
    print("\n  in(total) = input + cache_read + cache_create per turn, summed (what the API billed as context)")
    print("  cache+    = cache_creation tokens: NEW context written this phase (files read, skill text loaded)")

    print("\n== Agents ==")
    rows = [(p, a) for p in order for a in phases[p].agents]
    rows.sort(key=lambda r: -r[1]["wall_s"])
    for p, a in rows[:15]:
        print(f"  {fmt_dur(a['wall_s']):>7}  in {fmt_k(a['in']):>7}  out {fmt_k(a['out']):>6}  "
              f"{a['model'] or '-':<26} {a['type']:<32} {a['description'] or ''}  [{p}]")

    print("\n== Heaviest single turns by cache_creation (context growth) ==")
    for cc, out, tin, p, ts, tool in sorted(turn_rows, key=lambda r: -r[0])[:10]:
        print(f"  cache+ {fmt_k(cc):>6}  in {fmt_k(tin):>7}  out {fmt_k(out):>6}  {ts[11:19]}  {tool:<14} [{p}]")

    print("\n== Model / effort actually used per phase (main context) ==")
    for p in order:
        b = phases[p]
        if b.models:
            print(f"  {p:<{W}} " + ", ".join(f"{k}×{v}" for k, v in sorted(b.models.items(), key=lambda kv: -kv[1])))

    print("\n== Recommendation (heuristic — verify against the numbers above) ==")
    print("  signal: out/turn = reasoning depth needed; tools/turn = mechanical work; agents = already delegated")
    for p in order:
        b = phases[p]
        if b.turns < 5:
            continue
        out_per_turn = b.out / b.turns
        tools_per_turn = sum(b.tools.values()) / b.turns
        edits = b.tools.get("Edit", 0) + b.tools.get("Write", 0)
        mechanical = tools_per_turn >= 0.5 and edits >= 10 and out_per_turn < 1500
        creative = out_per_turn >= 1500 or any(k in p for k in ("plan", "brainstorm", "reconstruct"))
        if mechanical and not creative:
            rec = "sonnet / medium  — high tool ratio, short outputs: execution, not design"
        elif creative:
            rec = "opus·fable / high — long outputs or design/history work"
        else:
            rec = "keep current — mixed signal"
        print(f"  {p:<{W}} out/turn {out_per_turn:>6.0f}  tools/turn {tools_per_turn:>4.2f}  edits {edits:>3}  → {rec}")
    ag = [(p, a) for p in order for a in phases[p].agents]
    if ag:
        by_type = defaultdict(lambda: [0, 0, 0])
        for p, a in ag:
            t = by_type[a["type"]]; t[0] += 1; t[1] += a["wall_s"]; t[2] += a["in"]
        print("  agents by type (count, wall, in-tokens) — candidates for haiku/low if outputs are small and tool-heavy:")
        for k, (n, w, i) in sorted(by_type.items(), key=lambda kv: -kv[1][1]):
            print(f"    {k:<32} ×{n:<3} {fmt_dur(w):>7}  in {fmt_k(i)}")

    print("\n== Tool calls per phase ==")
    for p in order:
        b = phases[p]
        if not b.tools:
            continue
        top = sorted(b.tools.items(), key=lambda kv: -kv[1])[:6]
        print(f"  {p:<{W}} " + ", ".join(f"{k}×{v}" for k, v in top))


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    idle = IDLE_GAP_S
    if "--idle" in argv:
        idle = int(argv[argv.index("--idle") + 1])
        args = [a for a in args if a != str(idle)]
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if args:
        path = os.path.expanduser(args[0])
    else:
        # no arg: transcript dir of the current working directory
        slug = os.path.abspath(os.getcwd()).replace("/", "-").replace("_", "-")
        path = os.path.expanduser(os.path.join("~/.claude/projects", slug))
        if not os.path.isdir(path):
            print(f"no transcript dir for cwd: {path}", file=sys.stderr)
            return 1
    if os.path.isdir(path):
        path = pick_session(path)
        if not path:
            print("no session jsonl found", file=sys.stderr)
            return 1
        print(f"# session: {path}\n")
    order, phases, turn_rows = profile(path, idle)
    if as_json:
        out = {p: {"wall_s": round(b.wall_s), "turns": b.turns, "in_total": b.total_in,
                   "cache_create": b.cache_create, "out": b.out, "tools": dict(b.tools),
                   "agents": b.agents} for p, b in phases.items()}
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        report(order, phases, turn_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
