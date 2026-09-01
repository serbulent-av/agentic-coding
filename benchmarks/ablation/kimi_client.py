"""Kimi-K3 client via the GitHub Copilot API (same mechanism that serves this
opencode session). OAuth token is reused from ~/.local/share/opencode/auth.json.

Ported from benchmarks/opus_client.py. Adds per-call usage capture + cumulative
token/cost accounting so the ablation can enforce a USD budget.
"""
import json, os, threading, time

AUTH = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://api.githubcopilot.com"
_HDR = {
    "Copilot-Integration-Id": "vscode-chat",
    "Editor-Version": "vscode/1.95.0",
    "Editor-Plugin-Version": "copilot-chat/0.22.0",
    "User-Agent": "GitHubCopilotChat/0.22.0",
}
_lock = threading.Lock()

# USD per token for kimi-k3 on this route. UNVERIFIED placeholder — Copilot API
# billing is subscription-based; override via env KIMI_USD_PER_TOKEN if you know it.
USD_PER_TOKEN = float(os.environ.get("KIMI_USD_PER_TOKEN", "0.0000005"))  # $0.50/M


def _token():
    return json.load(open(AUTH))["github-copilot"]["access"]


class Usage:
    """Cumulative token/cost tracker shared across the run."""
    def __init__(self):
        self.prompt = 0
        self.completion = 0
        self.total = 0

    def add(self, u):
        if not u:
            return
        self.prompt += u.get("prompt_tokens", 0)
        self.completion += u.get("completion_tokens", 0)
        self.total += u.get("total_tokens", 0)

    @property
    def cost_usd(self):
        return self.total * USD_PER_TOKEN

    def __repr__(self):
        return f"Usage(tokens={self.total}, cost=${self.cost_usd:.3f})"


def chat(messages, model="kimi-k3", temperature=0.0, max_tokens=4096,
         usage=None, retries=5, stream=False, timeout=120):
    """Send a chat request; return text. Accumulates usage into `usage` if given.

    Non-streaming by default (more reliable); set stream=True for long outputs.
    """
    import requests
    tok = _token()
    body = {"model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "stream": stream}
    last = None
    for i in range(retries):
        try:
            r = requests.post(f"{API}/chat/completions",
                              headers={"Authorization": f"Bearer {tok}",
                                       "Content-Type": "application/json", **_HDR},
                              json=body, timeout=timeout, stream=stream)
            if r.status_code != 200:
                last = f"HTTP {r.status_code}: {r.text[:200]}"
                if r.status_code in (401, 403):
                    tok = _token()
                if r.status_code == 429:
                    time.sleep(10 * (i + 1)); continue
                time.sleep(3 * (i + 1)); continue

            if not stream:
                obj = r.json()
                if usage is not None:
                    usage.add(obj.get("usage"))
                ch = obj.get("choices", [])
                msg = (ch[0].get("message", {}) or {}) if ch else {}
                # prefer final content; fall back to reasoning if content empty
                text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                text = _strip_markers(text)
                if text:
                    return text
                last = "empty body"
            else:
                buf, parts, u = "", [], None
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
                            obj = json.loads(p)
                        except Exception:
                            continue
                        if obj.get("usage"):
                            u = obj["usage"]
                        ch = obj.get("choices", [])
                        if ch:
                            d = ch[0].get("delta", {}) or {}
                            if d.get("content"):
                                parts.append(d["content"])
                if usage is not None:
                    usage.add(u)
                text = _strip_markers("".join(parts).strip())
                if text:
                    return text
                last = "empty stream"
        except Exception as e:
            last = repr(e)[:200]
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"kimi chat failed: {last}")


def _strip_markers(text):
    for marker in ("<|close|>response", "<|close|>"):
        if text.endswith(marker):
            text = text[: -len(marker)].rstrip()
    return text


if __name__ == "__main__":
    u = Usage()
    print(chat([{"role": "user", "content": "Reply with exactly: KIMI_OK"}],
               max_tokens=512, usage=u))
    print(u)
