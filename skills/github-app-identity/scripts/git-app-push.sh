#!/usr/bin/env bash
# Transfer a single branch bundle to m2-mini and push it there with scoped credentials.
set -euo pipefail

[ "$#" -eq 4 ] || { echo "usage: git-app-push.sh <role> <owner/repo> <local-worktree> <branch>" >&2; exit 2; }
role=$1; repo=$2; worktree=$3; branch=$4
case "$role" in developer|reviewer|delivery-lead|tech-lead|product-lead) ;; *) echo "git-app-push.sh: unknown role" >&2; exit 2 ;; esac
if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then echo "git-app-push.sh: expected a full owner/repo" >&2; exit 2; fi
git -C "$worktree" check-ref-format --branch "$branch" >/dev/null
git -C "$worktree" show-ref --verify --quiet "refs/heads/$branch" || { echo "git-app-push.sh: local branch not found" >&2; exit 2; }
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
local_apps=${WID_APPS_TOML:-${HOME}/.config/wid/github-apps/apps.toml}
if [ "$(uname -s)" = Darwin ] && [ -r "$local_apps" ]; then
  remote=(python3 "$here/gh-app-remote.py" git-push "$role" "$repo" "$branch")
else
  remote=(hc exec --stdin --on m2-mini python3 "${WID_GH_REMOTE_SCRIPT:-/Users/hao/.config/skillshare/skills/github-app-identity/scripts/gh-app-remote.py}" git-push "$role" "$repo" "$branch")
fi
git -C "$worktree" bundle create - "refs/heads/$branch" |
  "${remote[@]}"
