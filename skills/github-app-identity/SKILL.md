---
name: github-app-identity
description: Use a configured GitHub App role for GitHub CLI operations when the private App credentials live on the m2-mini host.
---

# GitHub App identity

Use `scripts/gh-app.sh <role> <owner/repo> -- gh <arguments...>` for GitHub CLI work that must be attributed to a GitHub App. On other hosts, the command runs on the credential-owning `m2-mini` through `hc`; tokens never return to the calling host. On m2-mini itself, it runs locally because that host has no self-address in `hc`.

The supported roles are `developer`, `reviewer`, `delivery-lead`, `tech-lead`, and `product-lead`. Use the least role that fits the requested action. For a repository change, the author uses `developer`; the designated reviewer/merger uses `tech-lead` when that role is the user's authority for the task. GitHub App roles identify actors; they do not replace repository review or merge rules. Follow the target repository's own required checks and approval rules.

Current App names are `tmc-developer`, `tmc-reviewer`, `tmc-delivery-lead`, `tmc-tech-lead`, and `tmc-product-lead`. The credential broker prefers `[tmc-<role>]` tables in `~/.config/wid/github-apps/apps.toml` and accepts `[wid-<role>]` tables as a migration fallback. Existing `WID_*` environment variables and `~/.cache/wid/` paths remain compatible.

Always name the full `owner/repo`. The remote broker requests a token scoped to that single repository and role, and caches it under both values. It uses an isolated temporary `gh` configuration and explicit token so a personal `gh` login cannot silently take over. The token remains on m2-mini and is never printed by the helper.

The `gh` process and filesystem arguments run on m2-mini, so file paths must exist there. Pipe local body text with `--body-file -`; the wrapper forwards stdin. Some commands such as `gh repo view` still require an explicit repository argument, for example `gh repo view owner/repo --json nameWithOwner`.

Use `scripts/git-app-push.sh <role> <owner/repo> <local-worktree> <branch>` to push one local branch through m2-mini. It sends a Git bundle to m2-mini; Git uses an ephemeral askpass credential there for the exact GitHub repository URL. Tokens stay on m2-mini and are not saved in Git configuration. The push is a normal fast-forward push. The wrapper does not impose merge guards from another repository: the repository's own policy governs.

The client wrapper expects the remote copy at `/Users/hao/.config/skillshare/skills/github-app-identity/scripts/gh-app-remote.py`. Set `WID_GH_REMOTE_SCRIPT` on the calling host if the m2-mini Skillshare source uses another path. The m2-mini must have `hc`, Python 3.11+, OpenSSL, Git, and GitHub CLI; App metadata and private keys stay in `~/.config/wid/github-apps/`, outside Skillshare.
