#!/usr/bin/env python3
"""PreToolUse guard: block anything that could activate Meta ad spend or loosen the caps.

Exit code 2 blocks the tool call; stderr is shown to Claude.
"""
import json
import re
import sys

ACTIVATE = re.compile(r"""(status|effective_status|configured_status)["']?\s*[:=]\s*["']?ACTIVE""", re.I)
META = re.compile(r"graph\.facebook\.com|meta_ads\.py|/act_\d+|adsets|adcreatives|/ads\b", re.I)
PROTECTED = ("config/ads_guardrails.json", ".claude/hooks/ads_guard.py", ".claude/settings.json")


def block(msg):
    print(f"Blocked by ads_guard: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = event.get("tool_name", "")
    data = event.get("tool_input", {}) or {}

    if tool == "Bash":
        cmd = data.get("command", "")
        if META.search(cmd) and ACTIVATE.search(cmd):
            block("setting Meta ads to ACTIVE is not allowed. The owner activates campaigns in Ads Manager.")
        if re.search(r"curl[^|;&]*graph\.facebook\.com[^|;&]*(-X\s*POST|--data|-d\s|-F\s)", cmd, re.I):
            block("use tools/meta_ads.py (PAUSED-only, capped) instead of raw POSTs to the Graph API.")
        if any(p in cmd for p in PROTECTED) and re.search(r"(>|sed\s+-i|tee|mv|cp|rm|truncate|python3?\s+-c)", cmd):
            block("guardrail files can only be changed by the owner.")
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = (data.get("file_path") or data.get("notebook_path") or "").replace("\\", "/")
        if any(path.endswith(p) for p in PROTECTED):
            block(f"{path} is a guardrail file; only the owner may edit it.")
        text = json.dumps(data)
        if "data/ads/" in path and ACTIVATE.search(text):
            block("ad plans must not contain ACTIVE status.")


if __name__ == "__main__":
    main()
