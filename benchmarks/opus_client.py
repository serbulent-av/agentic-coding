"""Programmatic Opus 4.8 via the GitHub Copilot API (token reused from OpenCode auth.json).
The OAuth token works directly as a Bearer against api.githubcopilot.com (no exchange).
Used as 'planner' and 'reviewer' for the agentic experiments.
"""
import json, time, requests, threading

AUTH = "/home/serbulentunsal/.local/share/opencode/auth.json"
API = "https://api.githubcopilot.com"
_HDR = {
    "Copilot-Integration-Id": "vscode-chat",
    "Editor-Version": "vscode/1.95.0",
    "Editor-Plugin-Version": "copilot-chat/0.22.0",
    "User-Agent": "GitHubCopilotChat/0.22.0",
}
_lock = threading.Lock()

def _token():
    return json.load(open(AUTH))["github-copilot"]["access"]

def chat(messages, model="claude-opus-4.8", temperature=0.0, max_tokens=3000, reasoning_effort="low", retries=5):
    # Claude via Copilot: content only via SSE; always-on thinking -> use low effort + buffered parse.
    tok = _token()
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "stream": True}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    last = None
    for i in range(retries):
        try:
            r = requests.post(f"{API}/chat/completions",
                              headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json", **_HDR},
                              json=body, timeout=300, stream=True)
            if r.status_code == 200:
                buf, parts = "", []
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    buf += chunk
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        p = line[5:].strip()
                        if p == "[DONE]":
                            continue
                        try:
                            ch = json.loads(p).get("choices", [])
                        except Exception:
                            continue
                        if ch:
                            d = ch[0].get("delta", {}) or {}
                            if d.get("content"):
                                parts.append(d["content"])
                text = "".join(parts).strip()
                if text:
                    return text
                last = "empty stream"
            else:
                last = f"HTTP {r.status_code}: {r.text[:200]}"
                if r.status_code in (401, 403):
                    tok = _token()
                if r.status_code == 429:
                    time.sleep(10 * (i + 1)); continue
        except Exception as e:
            last = repr(e)[:200]
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"opus chat failed: {last}")

if __name__ == "__main__":
    print(chat([{"role": "user", "content": "Reply with exactly: OPUS_OK"}], max_tokens=10))
