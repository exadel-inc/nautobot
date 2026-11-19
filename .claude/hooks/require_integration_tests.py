#!/usr/bin/env python3
"""Stop hook: in the Colleague agent container, a session that changed web-UI code must run the
matching Selenium integration tests before it finishes. Anywhere else it does nothing.

Blocks at most once per stop (``stop_hook_active``), so it can never trap the agent in a loop.
"""
import json
import os
import re
import subprocess
import sys

UI_PATTERNS = (
    re.compile(r"(^|/)templates/.+\.html$"),
    re.compile(r"(^|/)static/.+\.(js|css|scss)$"),
    re.compile(r"(^|/)(views|forms|tables|filter_forms|navigation|template_content)\.py$"),
    re.compile(r"(^|/)(views|forms|tables|ui)/[^/]+\.py$"),
)
RAN_INTEGRATION = re.compile(r"--tag[= ]integration|\.tests\.integration\b|tests/integration/")


def in_agent_container() -> bool:
    return bool(os.environ.get("NAUTOBOT_SELENIUM_URL")) and os.path.exists(
        os.environ.get("EAE_TEST_ENV_STATUS_FILE", "/tmp/eae-test-env.status")
    )


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def changed_files() -> set[str]:
    base = git("merge-base", "HEAD", "origin/develop").strip()
    files = set(git("diff", "--name-only", base or "HEAD").split())
    files |= set(git("diff", "--name-only", "--cached").split())
    files |= set(git("ls-files", "--others", "--exclude-standard").split())
    return {f for f in files if f.startswith("nautobot/") and "/tests/" not in f}


def ran_integration(transcript_path: str) -> bool:
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"Bash"' in line and RAN_INTEGRATION.search(line):
                    return True
    except OSError:
        return True  # cannot tell: do not block
    return False


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active") or not in_agent_container():
        return
    ui = sorted(f for f in changed_files() if any(p.search(f) for p in UI_PATTERNS))
    if not ui or ran_integration(data.get("transcript_path", "")):
        return
    areas = sorted({f.split("/")[1] for f in ui if f.count("/") >= 2})
    labels = " ".join(f"nautobot.{a}.tests.integration" for a in areas) or "<label>"
    print(json.dumps({
        "decision": "block",
        "reason": (
            "This branch changes web-UI code (" + ", ".join(ui[:6]) + ("…" if len(ui) > 6 else "")
            + ") but no Selenium integration test ran in this session. Before finishing, run the "
            "integration tests for the affected area (see CLAUDE.md), e.g.\n"
            "  curl -fsS http://127.0.0.1:4444/status >/dev/null || (setsid nohup geckodriver --host 127.0.0.1 --port 4444 >/tmp/geckodriver.log 2>&1 &)\n"
            f"  nautobot-server --config=nautobot/core/tests/nautobot_config.py test --keepdb --no-input --tag integration {labels}\n"
            "Report the command and its result. If they cannot run, say why in your report."
        ),
    }))


if __name__ == "__main__":
    main()
