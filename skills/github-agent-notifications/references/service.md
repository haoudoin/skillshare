# Registry notification service operations

This source contains the N5 label-routing correction. Read the operator's
[verified live report](https://github.com/pro-max-ultra/tmc-infrastructure/blob/main/docs/agent-registry/live-service-report.md)
for the actual active/paused scope, endpoints and current identities. Source or
skill presence alone does not establish deployment. The legacy workflow remains
separate from the registry workflow and excluded for the selected repositories.

## Runtime authority

The n8n custom node uses native GitHub/TMC HTTPS credential references and
Node24 SQLite cursor/lease metadata. Cron remains every5min; separate pending
intake and dispatch observation run every60s. Repository/issue discovery is
polling; no new webhook subscription is implied. Java alone owns durable tasks,
dispatches, protected execution, retries/deadlines and administrative recovery.
Contact is inspection data, never a command or send capability.

Use the [workflow package](https://github.com/pro-max-ultra/tmc-infrastructure/tree/main/n8n_registry)
and [N4 operator checklist](https://github.com/pro-max-ultra/tmc-infrastructure/blob/main/docs/agent-registry/n4-rollout-checklist.md)
for exact reviewed installation/configuration. The shared
[contract](https://github.com/pro-max-ultra/tmc-infrastructure/blob/main/docs/agent-registry/contract.md)
governs API/MCP semantics.

## Before scoped activation

The coordinator assigns a concrete execution slice after R4/N4 review. Preserve
current default cores, user panes, n8n encryption/database/volumes, unrelated
workflows/subscriptions and deployed legacy UI/HTTP/MCP behavior. Build/install
only the reviewed custom package/protected profiles with verified public CA and
runtime UID/private socket routes. H3 Linux and Darwin pins establish those
platform paths; other platforms fail closed.

Back up DB, n8n state/workflows, cursor SQLite/WAL coherently, mutable runtime
config and guarded images immediately before execution. Disable legacy routing
for the exact selected repository scope before enabling label routing. Record
actual endpoints, server-issued IDs, core pins, workflow/execution IDs and
authenticated ACK/progress/completion. Expand only after coordinator review.

## Credential rotation

Dispatcher credentials last24h. A new UUID must be provisioned privately; a
restart with the same file does not renew expiry. The authorized n8n operator
updates the existing HTTP credential reference on its owning host, verifies API
scope/TLS and preserves workflow/worker enabled/disabled state. Retire the old
credential only after the approved overlap and validated receipt.

The nonsecret rotation ACK binds oldCredentialId/newCredentialId,
credentialRefValidated:true, validatedAt UTC and matching workflowStateBefore/
After plus workerStateBefore/After booleans. Minimum overlap is30s. Tokens remain
in private files/n8n credentials and never enter shared skills, contact, issue
payload, logs, argv or environment. R4 owns provision/retire semantics; ordinary
agents cannot rotate service/admin credentials.

## Pause and rollback

Stopping n8n stops new intake, not armed Java jobs. Pause the selected intake and
disable/quiesce the backend executor, stop possible writers and retain uncertain
fences until authorized evidence-backed reconciliation. Preserve jobs/receipts,
completed history and the guarded API. Once managed rows exist, restoring an
old unguarded API or deleting audit/schema is not rollback.

Restore selected routing only through the reviewed coordinator decision after
fences/ownership are resolved. Preserve unrelated repository subscriptions and
operator-disabled states. Skill distribution or package presence alone never
authorizes production changes.

## Skill distribution

The reviewed repository copy of this skill is the source change. Later authorized
distribution uses each host's existing Skillshare source/targets, previews/audits,
then syncs. Verify Codex, Claude and Copilot on the NUC and every currently
hc-reachable host (including m2-mini/nv5mo2g); record commit and content hashes.
Mac Codex may discover the universal ~/.agents/skills target rather than a
separately named codex target. Recheck actual configuration instead of guessing.

Preserve target-local skills and unrelated resource selections. Global
sync --all would also touch extras/MCP/hooks and is not implied by this change.
Review conflicts/audit blocks; do not use force/skip-audit to hide them. Keep
credentials and host-specific private snapshots outside the shared source.

Inspect same-name legacy Codex copies at ~/.codex/skills/github-agent-notifications
on every selected host as well as configured targets. Back up an owned real copy
before updating its four files to canonical content; a symlink may already resolve
to canonical. Verify exact paths/hashes so stale duplicate instructions do not
remain discoverable. Preserve unrelated skills/configuration; do not delete the
legacy directory or change global discovery settings.
