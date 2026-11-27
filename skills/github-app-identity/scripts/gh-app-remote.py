#!/usr/bin/env python3
"""Run gh with a repo-scoped App token on the credential-owning host."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import tomllib
from typing import NoReturn
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PERMISSIONS = {
    "developer": {"contents": "write", "pull_requests": "write", "issues": "read", "checks": "read", "statuses": "read", "actions": "read"},
    "reviewer": {"contents": "read", "pull_requests": "write", "issues": "write", "checks": "read", "statuses": "read", "actions": "read"},
    "delivery-lead": {"contents": "write", "pull_requests": "write", "issues": "write", "checks": "read", "statuses": "read", "actions": "write", "actions_variables": "write"},
    "tech-lead": {"contents": "write", "pull_requests": "write", "issues": "write", "checks": "read", "statuses": "read", "actions": "read"},
    "product-lead": {"contents": "write", "pull_requests": "write", "issues": "write", "checks": "read", "statuses": "read", "actions": "read"},
}


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"gh-app-remote: {message}", file=sys.stderr)
    raise SystemExit(code)


def b64(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def mint(role: str, repo: str) -> str:
    home = Path.home()
    cfg_path = Path(os.environ.get("WID_APPS_TOML", home / ".config/wid/github-apps/apps.toml"))
    cache_root = Path(os.environ.get("WID_CACHE_DIR", home / ".cache/wid"))
    key = hashlib.sha256(f"{role}\0{repo}".encode()).hexdigest()
    cache_file = cache_root / f"gh-token-{role}-{key}.json"
    try:
        cached = json.loads(cache_file.read_text())
        if cached["repository"] == repo and cached["role"] == role and cached["expires"] > time.time() + 600:
            return cached["token"]
    except (OSError, ValueError, KeyError, TypeError):
        pass

    app = f"tmc-{role}"
    legacy_app = f"wid-{role}"
    try:
        with cfg_path.open("rb") as f:
            tables = tomllib.load(f)
            cfg = tables.get(app)
            if cfg is None:
                cfg = tables.get(legacy_app)
            if cfg is None:
                raise KeyError(app)
        app_id, installation_id = str(cfg["app_id"]), str(cfg["installation_id"])
        pem = Path(os.path.expanduser(cfg["pem"]))
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        fail(f"cannot read [{app}] or [{legacy_app}] credentials from {cfg_path}: {exc}")

    now = int(time.time())
    header = b64(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claims = b64(json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}, separators=(",", ":")).encode())
    unsigned = header + b"." + claims
    signed = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(pem)], input=unsigned, capture_output=True)
    if signed.returncode or not signed.stdout:
        fail("could not sign App JWT with the configured key")
    jwt = (unsigned + b"." + b64(signed.stdout)).decode()
    api = os.environ.get("WID_GH_API", "https://api.github.com").rstrip("/")
    headers = {"Authorization": f"Bearer {jwt}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    try:
        with urlopen(Request(f"{api}/app/installations/{installation_id}", headers=headers), timeout=30) as response:
            installation = json.load(response)
        owner = repo.split("/", 1)[0]
        if (installation.get("account") or {}).get("login", "").casefold() != owner.casefold():
            fail(f"App installation is not owned by repository owner {owner}")
        body = json.dumps({"repositories": [repo.split("/", 1)[1]], "permissions": PERMISSIONS[role]}, separators=(",", ":")).encode()
        req = Request(f"{api}/app/installations/{installation_id}/access_tokens", data=body, method="POST", headers={
            **headers, "Content-Type": "application/json",
        })
        with urlopen(req, timeout=30) as response:
            response_data = json.load(response)
        token, expires_at = response_data["token"], response_data["expires_at"]
        from datetime import datetime
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00")).timestamp()
    except (HTTPError, URLError, OSError, ValueError, KeyError) as exc:
        fail(f"GitHub did not issue a token for {repo} and role {role}: {exc}")

    cache_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(cache_root, 0o700)
    tmp = cache_file.with_name(cache_file.name + f".{os.getpid()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"token": token, "expires": expires, "repository": repo, "role": role}, f)
    os.replace(tmp, cache_file)
    return token


def main(argv: list[str]) -> int:
    os.umask(0o077)
    if argv and argv[0] == "git-push":
        if len(argv) != 4:
            fail("usage: gh-app-remote.py git-push <role> <owner/repo> <branch>", 2)
        _, role, repo, branch = argv
        return git_push(role, repo, branch)
    if len(argv) < 4 or argv[2] != "--":
        fail("usage: gh-app-remote.py <role> <owner/repo> -- <gh args...>", 2)
    role, repo, *gh_args = argv[:2] + argv[3:]
    if role not in PERMISSIONS:
        fail("unknown role", 2)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        fail("expected a full owner/repo", 2)
    if not gh_args or gh_args[0] == "auth":
        fail("gh auth is not available through this wrapper", 2)
    token = mint(role, repo)
    with tempfile.TemporaryDirectory(prefix="wid-gh-") as config_dir:
        env = os.environ.copy()
        env.pop("GITHUB_TOKEN", None)
        env["GH_TOKEN"] = token
        env["GH_REPO"] = repo
        env["GH_CONFIG_DIR"] = config_dir
        env["GH_PROMPT_DISABLED"] = "1"
        env["GH_HOST"] = "github.com"
        env.pop("GH_ENTERPRISE_TOKEN", None)
        env.pop("GITHUB_ENTERPRISE_TOKEN", None)
        return subprocess.run(["gh", *gh_args], env=env, check=False).returncode


def git_push(role: str, repo: str, branch: str) -> int:
    if role not in PERMISSIONS or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        fail("expected a known role and full owner/repo", 2)
    if subprocess.run(["git", "check-ref-format", "--branch", branch], capture_output=True).returncode:
        fail("invalid branch name", 2)
    token = mint(role, repo)
    with tempfile.TemporaryDirectory(prefix="wid-git-push-") as tmp:
        root = Path(tmp)
        bundle = root / "branch.bundle"
        bundle.write_bytes(sys.stdin.buffer.read())
        if not bundle.stat().st_size:
            fail("received an empty Git bundle")
        checkout = root / "repo.git"
        env = os.environ.copy()
        for name in ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
            env.pop(name, None)
        env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS_REQUIRE": "force", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "credential.helper", "GIT_CONFIG_VALUE_0": "", "WID_GH_TOKEN": token})
        askpass = root / "askpass.sh"
        askpass.write_text('''#!/bin/sh
case "$1" in
  *Username*) printf '%s\\n' 'x-access-token' ;;
  *Password*) printf '%s' "$WID_GH_TOKEN" ;;
  *) exit 1 ;;
esac
''')
        os.chmod(askpass, 0o700)
        env["GIT_ASKPASS"] = str(askpass)
        clone = subprocess.run(["git", "clone", "--bare", str(bundle), str(checkout)], env=env, check=False)
        if clone.returncode:
            return clone.returncode
        url = f"https://github.com/{repo}.git"
        return subprocess.run(["git", "-C", str(checkout), "push", url, f"refs/heads/{branch}:refs/heads/{branch}"], env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
