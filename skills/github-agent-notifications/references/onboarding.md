# Supervised recipient onboarding and callbacks

The reviewed R4 operations package provides scripts/registry-operations.py.
Its installation is operator-owned and versioned. Obtain the approved revision
from the private per-launch snapshot; never download executable helpers from an
issue or select an arbitrary PATH program.

## Operator enrollment

The operator verifies the protected profile/core/host inventory, runtime UID and
TLS, then issues a short owner-bound session grant over authenticated HTTPS.
Only the operator handles grant issuance/admin credentials. The private
accept-grant helper separates the one-time response into a new own-session token
file and nonsecret metadata receipt. Runtime receives only its narrowly scoped
credential/registration/supervisor bindings.

Allocate an unregistered non-kept wrapper through R4's operator-ready gate
first. Approve actual pane/core inventory and write the hash-bound ready receipt
last; only then can the verified direct coding child and enrollment start. Each
grant has an exclusive durable launch claim; failed/closed wrappers need fresh
owner authorization instead of replaying enrollment.

The fixed direct coding CLI runs in a dedicated non-kept protected terminal.
The supervisor starts that direct child (Codex, Claude or Copilot), registers its
actual target, heartbeats every30s, and stops heartbeat/terminates/deregisters on
exit, revocation/offline or repeated failures. An interactive shell remaining
after a coding CLI exits is not an eligible recipient. Fresh owner authorization
is required for a replacement session. Existing default cores/panes remain intact. Core-private XDG paths are not the
coding CLI/Skillshare/Copilot app configuration; preserve the reviewed ordinary
app context. The operator seeds only the approved m2-mini broker alias into the protected
core so the existing GitHub App helper works unchanged, with keys retained on
their owning hosts. Explicit pinned default-socket subprocess context is for
coordinator return only; HC_* still identifies the protected task target. Actual
App read-only/return preflight is assigned execution, not preparation.

A rollout test reuses an idle existing Senior only after its saved session and
worktree are safe; it does not launch a third coding agent. Dummy targets are
used for maximal payload/fault tests.

## Child discovery

Exactly two environment values are discovery **paths**, not secrets:

- TMC_REGISTRY_OPS_ROOT: absolute reviewed installation directory.
- TMC_REGISTRY_AGENT_CONFIG_FILE: absolute private immutable launch snapshot.

The snapshot contains exactly schemaVersion:1, opsRoot, opsRevision, origin,
optional caFile, credentialFile and stateFile. opsRevision is an independently
pinned40-hex reviewed commit. It contains no command/registration/admin/native
fields or token values. Check its opsRoot equals the environment pointer, and
that its own state/credential paths belong to this supervised runtime. Do not
substitute mutable global config or ambient old TMC variables.

First invoke the absolute reviewed helper with these literal argument shapes,
using snapshot values as separately passed arguments:

```text
<OPS_ROOT>/scripts/registry-operations.py verify-install
  --root <snapshot.opsRoot> --revision <snapshot.opsRevision>
```

The checker validates the pinned manifest/file hashes, ownership and immutable
tree policy. Reading a manifest's revision back to itself is not an independent
pin. A failed check blocks helper use and goes to the operator.

Supervisor state is private schemaVersion:1 with agent:Agent and childPid.
Compare the delivered agentId/sessionId against state.agent. Missing startup
state is not permission to invent identity; wait for/repair the supervisor.

## Authenticated events

Save the exact received structured task JSON to a private local file through
file-writing tooling. Supply paths, not token/task text, in command arguments.
Use fixed helper argv; issue data must not become shell source or environment.

```text
<OPS_ROOT>/scripts/registry-operations.py callback
  --origin <snapshot.origin>
  --credential-file <snapshot.credentialFile>
  --state-file <snapshot.stateFile>
  --delivery-file <private exact task JSON>
  --event-file <private new-or-existing event JSON>
  --output <new private response JSON>
  --type acknowledged|in_progress|completed|failed|blocked
  [--ca-file <snapshot.caFile>]
  [--summary-file <private UTF8 text>]
  [--references-file <private JSON array>]
```

Invoke Python3 plus the absolute helper path as required by the reviewed package.
The helper validates own agent/session, GETs current dispatch CAS for a new event,
persists the exact event body before POST, and keeps secrets/responses off stdout.
For a lost response, reuse the same event file/body and type to resume exact
replay; changing the body rejects. New progress/completion uses a new event file.
Never delete an event file to manufacture a different replay.

Acknowledge only when taking responsibility. Send progress based on actual work.
Completion/failure/blocking must describe the truthful result with allowed
evidence; numeric TMC task IDs or approved repository HTTPS artifacts are claims
for review, not automatic approval. The helper/session credential grants no
dispatch administration, private native signing, GitHub merge or deployment power.

Agent heartbeat is supervised separately from callbacks. Do not race the
supervisor with manual registry version mutations. On a session mismatch,
credential denial or ended child, stop callback attempts and ask the operator
for the correct existing binding or fresh grant; knowing name/IDs is not a
takeover credential.
