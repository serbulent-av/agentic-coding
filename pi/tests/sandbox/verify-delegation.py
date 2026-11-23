#!/usr/bin/env python3
"""Verify the agentic-coding team actually delegates work to sub-agents.

Parses pi session files (JSONL) from a sandbox run and checks that the
conductor (patek) delegated implementation to philipe instead of doing the
file edits itself.

Session format (verified ground truth):
  - Files live at <sessions-dir>/<cwd-slug>/*.jsonl (nested one level; we
    glob recursively).
  - A sub-agent session has a header line:
    {"type":"session",...,"parentSession":"<path>"}. Top-level sessions lack it.
  - Tool calls are nested inside message lines:
    {"type":"message","message":{"role":"assistant","content":[
      {"type":"toolCall","id":...,"name":"bash","arguments":{...}}]}}
  - A delegation call has name == "Agent" and arguments.subagent_type.
  - The sub-agent system prompt contains the marker: active_agent name="patek"
    (plain quotes once the JSON is decoded). The marker is matched ONLY in
    messages with role == "system" so a quoted marker in user/tool text
    cannot mislabel a session.

PASS criteria (default): at least one sub-agent session whose system prompt
contains active_agent name="patek" AND that same session contains a toolCall
named "Agent" with arguments.subagent_type == "philipe".

Exit codes: 0 = PASS, 1 = FAIL (including "no session files found"),
2 = usage error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_SESSIONS_DIR = "/tmp/pi-sandbox/sessions"
AGENT_MARKER_RE = re.compile(r'active_agent name="([a-z0-9_-]+)"')


def iter_strings(obj):
    """Yield every string value in a decoded JSON structure (recursively)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from iter_strings(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_strings(item)


def parse_session(path):
    """Parse one session jsonl file.

    Returns a dict with:
      is_subagent : has a "session" header line containing "parentSession"
      agent_type  : agent name from the active_agent marker, or None
      tool_calls  : list of (name, arguments-dict) for every toolCall entry
    Lines that fail to parse are skipped (tolerates partial/truncated files).
    """
    is_subagent = False
    agent_type = None
    tool_calls = []

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("type") == "session" and "parentSession" in entry:
                is_subagent = True

            # Agent-type marker: scan only system-role messages so a marker
            # quoted in user/assistant/tool text cannot mislabel the session.
            # First match within those system messages wins.
            if agent_type is None and entry.get("type") == "message":
                message = entry.get("message")
                if not isinstance(message, dict):
                    message = entry
                if message.get("role") == "system":
                    # pi >= 1.6 stores the rendered system prompt in
                    # message.sections (e.g. sections.preamble) with content
                    # left empty; older versions put it in content. Scan both.
                    texts = list(iter_strings(message.get("content")))
                    sections = message.get("sections")
                    if isinstance(sections, dict):
                        for value in sections.values():
                            texts.extend(iter_strings(value))
                    for text in texts:
                        match = AGENT_MARKER_RE.search(text)
                        if match:
                            agent_type = match.group(1)
                            break

            if entry.get("type") == "message":
                msg = entry.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "toolCall":
                            arguments = block.get("arguments")
                            if not isinstance(arguments, dict):
                                arguments = {}
                            tool_calls.append((block.get("name"), arguments))

    return {"is_subagent": is_subagent, "agent_type": agent_type, "tool_calls": tool_calls}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog=(
            "--no-bash is independent of --strict so the harness works both "
            "before and after the conductor config fix lands; it is typically "
            "combined with --strict (patek should neither edit files nor run "
            "bash directly once delegation is fully enforced)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--sessions-dir",
        default=DEFAULT_SESSIONS_DIR,
        help="directory to glob recursively for session jsonl files "
             f"(default: {DEFAULT_SESSIONS_DIR})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="FAIL if any patek session contains a 'write' or 'edit' toolCall",
    )
    parser.add_argument(
        "--no-bash",
        action="store_true",
        help="FAIL if any patek session contains a 'bash' toolCall "
             "(typically combined with --strict)",
    )
    args = parser.parse_args()

    session_files = sorted(Path(args.sessions_dir).glob("**/*.jsonl"))
    if not session_files:
        print(f"FAIL: no session files found under {args.sessions_dir}")
        return 1

    sessions = []
    for path in session_files:
        info = parse_session(path)
        info["path"] = path
        sessions.append(info)

    # --- Report -------------------------------------------------------------
    subagent_counts = {}
    for s in sessions:
        if s["is_subagent"]:
            key = s["agent_type"] or "unknown"
            subagent_counts[key] = subagent_counts.get(key, 0) + 1

    print("Sub-agent sessions by agent type:")
    if subagent_counts:
        for agent, count in sorted(subagent_counts.items()):
            print(f"  {agent}: {count}")
    else:
        print("  (none)")

    print("Per-session toolCall counts:")
    for s in sessions:
        label = s["agent_type"] if s["is_subagent"] else "top-level"
        if s["is_subagent"] and s["agent_type"] is None:
            label = "unknown"
        print(f"  {s['path'].name}: {label}, {len(s['tool_calls'])} toolCall(s)")

    # --- Verdict ------------------------------------------------------------
    failures = []

    patek_sessions = [s for s in sessions if s["is_subagent"] and s["agent_type"] == "patek"]
    delegated = any(
        name == "Agent" and arguments.get("subagent_type") == "philipe"
        for s in patek_sessions
        for name, arguments in s["tool_calls"]
    )
    if not patek_sessions:
        failures.append("no sub-agent session with agent type 'patek' found")
    elif not delegated:
        failures.append(
            "no patek session contains an Agent toolCall with subagent_type 'philipe'"
        )

    if args.strict:
        for s in patek_sessions:
            offenders = sorted({n for n, _ in s["tool_calls"] if n in ("write", "edit")})
            if offenders:
                failures.append(
                    f"--strict: patek session {s['path'].name} used {', '.join(offenders)} directly"
                )

    if args.no_bash:
        for s in patek_sessions:
            if any(n == "bash" for n, _ in s["tool_calls"]):
                failures.append(
                    f"--no-bash: patek session {s['path'].name} used bash directly"
                )

    if failures:
        print("FAIL")
        for reason in failures:
            print(f"  - {reason}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
