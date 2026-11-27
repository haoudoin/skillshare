# Label routing and outcomes

The [shared contract](https://github.com/pro-max-ultra/tmc-infrastructure/blob/main/docs/agent-registry/contract.md)
is normative. Use the operator's verified active scope before expecting delivery.

## Grammar and identity

Exactly one GitHub label must be `agent:canonical-name` and one must be
`agent-id:canonical-server-GUID`. These are label names, not body lines; no literal
brackets are used. The slug matches [a-z0-9][a-z0-9-]{0,43}; the GUID is the actual
canonical lowercase server value. GitHub labels allow 50 characters, so routable
names allow 44; the registry/API still permits63. Do not shorten, alias, truncate,
trim or case-fold a route. Ask a repository maintainer/authorized automation to
correct labels unless the author is already permitted to do so.

For rejection, classify ASCII-case-insensitive agent-id or agent after leading
ASCII whitespace, followed by colon/ASCII whitespace/end. Every candidate must
then match the full exact lowercase label grammar. Thus bare agent/agent-id,
AGENT:foo, leading whitespace, agent :foo, agent foo, bracketed values and uppercase
GUIDs invalidate intake even beside a valid pair. Identical duplicates also fail.
Unrelated labels, including agent-machine: and agent-pane:, are ignored.

GitHub REST label strings and objects with string names are normalized once to
immutable names, preserving duplicates. Missing labels are empty. Null/non-array
labels or non-string/nameless entries reject the upstream snapshot/page and leave
its checkpoint unacknowledged; they are not silently dropped. Body text, including
valid or conflicting former body pairs/fences, never participates in routing.

First registration allocates a permanent server GUID. An unknown name can remain
pending; registering it later does not make a previously guessed/foreign GUID
correct. The unchanged pair becomes a held mismatch. Copy the actual new server
identity when correcting a not-yet-created work item. Existing offline identities
retain their GUID: an owner-authorized new session can recover eligible pending
work without a cosmetic issue edit.

Supported input is a title of at most256 and body of at most65536 Unicode code
points. Oversized data is held as revision_observed/payload_too_large before a
task/attempt; it is never truncated. Issue pages are bounded to25 rows, retain
state=all/sort=updated/direction=desc, and must complete before checkpoint.

## Work identity

One work item exists per repository/issue. Label edits/removal/replacement, body edits and reopens are context/audit after
creation; they do not create a second task, change assignment, reopen completed
work or authorize a resend. An authorized operator handles an explicit handoff
through the existing reconcile protocol. New work after completion uses a new
issue.

## Results

| Result | Meaning and action |
| --- | --- |
| eligible / queued | Intake/work is durable; first admission or delivery may still be blocked |
| delivered | Backend verified transport acceptance; wait for authenticated acknowledgement |
| acknowledged / in_progress | Agent accepted responsibility; inspect its progress/evidence |
| completed | Agent explicitly completed with evidence; review/merge remains separate |
| no_agent_found | No task; verify canonical name and actual server identity |
| agent_id_mismatch | Held; requester verifies identity and asks a permitted maintainer/automation to correct initial labels |
| agent_unavailable | Pending; operator restores a genuine eligible session with the same permanent identity |
| invalid_routing / unsupported_transport | Held for correction or reviewed adapter/policy change |
| source_unavailable | GitHub404/410 remains pending; operator restores visibility or inspects transfer/deletion |
| blocked / failed | Inspect reason and dependency; an acknowledged task is not automatically replayed |
| delivery_uncertain | Possible send; preserve fence and require authorized stopped-writer reconciliation |

Source404/410 is not proof that an issue closed. Other pending items continue;
global auth/rate/API outages may stop the scan. Org discovery reports visible,
selected, excluded and expected-but-missing repositories. A credential's visible
list alone cannot prove full organization coverage.

The acknowledgement deadline is5min after original transport acceptance; accepted
acknowledgement initializes the30min progress deadline. Registry heartbeat is
separate and does not extend task progress. Backend retries only durable not_sent
outcomes within the approved five-attempt budget; n8n does not invent retry clocks.

For uncertainty the operator may choose retry_not_executed, confirm_completed or
cancel only with the contract's matching evidence and stop/revoke requirements.
Already completed work can receive matching physical-fence cleanup without
reopening. Offline recovery may need the exact staged reconcile request replayed
after owner-authorized registration; preserve its request/body and original
uncertain history. Ordinary recipients/skills have no administrative authority.
