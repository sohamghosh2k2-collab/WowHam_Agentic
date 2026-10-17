"""Minimal Meta Graph API client (stdlib only). Token comes from META_ACCESS_TOKEN."""
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUARDRAILS = ROOT / "config" / "ads_guardrails.json"


def api_version():
    try:
        return json.loads(GUARDRAILS.read_text()).get("graph_api_version", "v23.0")
    except FileNotFoundError:
        return "v23.0"


def env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing environment variable {name} (see .env.example)")
    return value


def _redact(text):
    token = os.environ.get("META_ACCESS_TOKEN")
    return text.replace(token, "***") if token else text


def request(method, path, params=None, timeout=30):
    params = dict(params or {})
    params["access_token"] = env("META_ACCESS_TOKEN")
    url = f"https://graph.facebook.com/{api_version()}/{path.lstrip('/')}"
    encoded = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in params.items()}
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(encoded)
    else:
        data = urllib.parse.urlencode(encoded).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"Graph API error {e.code} on {method} {path}: {_redact(body)}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error calling Graph API ({path}): {e.reason}")
