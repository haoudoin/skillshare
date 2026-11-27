#!/usr/bin/env bash
# Run GitHub CLI as an App on the credential-owning m2-mini host.
set -euo pipefail

usage() {
  echo "usage: gh-app.sh <role> <owner/repo> -- <gh arguments...>" >&2
  exit 2
}

[ "$#" -ge 4 ] || usage
role=$1; repo=$2; shift 2
[ "$1" = "--" ] || usage
shift
[ "$#" -ge 1 ] || usage
case "$role" in developer|reviewer|delivery-lead|tech-lead|product-lead) ;; *) echo "gh-app.sh: unknown role" >&2; exit 2 ;; esac
if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "gh-app.sh: expected a full owner/repo" >&2
  exit 2
fi
if [ "$1" != gh ]; then echo "gh-app.sh: command must start with gh" >&2; exit 2; fi
shift
if [ "${1:-}" = auth ]; then echo "gh-app.sh: gh auth is not available through this wrapper" >&2; exit 2; fi

remote_script=${WID_GH_REMOTE_SCRIPT:-/Users/hao/.config/skillshare/skills/github-app-identity/scripts/gh-app-remote.py}
local_apps=${WID_APPS_TOML:-${HOME}/.config/wid/github-apps/apps.toml}
if [ "$(uname -s)" = Darwin ] && [ -r "$local_apps" ]; then
  here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  exec python3 "$here/gh-app-remote.py" "$role" "$repo" -- "$@"
fi
exec hc exec --stdin --on m2-mini python3 "$remote_script" "$role" "$repo" -- "$@"
