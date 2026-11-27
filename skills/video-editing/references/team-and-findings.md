# Video team and persistent findings

## Project layout

Use `video-editing/` within the user's project unless they specify another output root. The top-level human entrypoint is `video-editing/FOOTAGE.md`. Store relative artifact links and source paths relative to an explicit source root when practical; support external media roots without copying originals.

```text
video-editing/
  FOOTAGE.md
  catalog.json
  videos/<clip-id>/
    summary.md
    events.json
    chunks/<chunk-id>.json
    transcript.json             # only when produced
  previews/<clip-id>/
  creative-brief.md             # when creative discussion starts
  edit-plan.json                # when an edit is proposed
```

## Ownership and orchestration

The coordinator inventories sources and assigns stable IDs before delegating. Do not use basenames alone: different directories may contain identical filenames. Keep IDs stable across runs using the catalog. Record source relative path, size, modification time, and optionally a content hash. Size/mtime is a change detector, not proof of content identity. Record fingerprint method. Mark changed sources and their derived observations stale; do not reuse them as current evidence.

Give each reviewer the output root, assigned clip IDs, exact source paths/time ranges, requested sampling settings, and user priorities. Prefer assigning a whole source video to one worker, which checkpoints chunks internally. For long clips, use bounded ranges with a small overlap, such as 2 seconds, and keep all timestamps relative to the original video. If multiple workers inspect one video, assign unique chunk files; the coordinator alone merges that video's summary/events. Deduplicate overlap findings without losing meaningful lead-in/aftermath.

Workers write only assigned video/chunk artifacts. Only the coordinator writes shared `catalog.json` and `FOOTAGE.md`; this prevents concurrent overwrites. Limit concurrent reviewers initially to two, adjusting for resources and requested scope. Media extraction/rendering is performed by local tools, not repeated model calls. Workers return concise completion reports with artifact paths, reviewed ranges, highlights, and gaps. Do not send every frame back to the coordinator.

Creative direction goes to `creative-producer` with the current brief, relevant summaries/events, shortlisted preview paths, and requested creative deliverable. It must visually inspect shortlisted evidence, and may request focused follow-up reviews. The coordinator integrates its proposal and user decisions; source observations and creative preferences remain distinct.

## Persistence contract

Use JSON with `schema_version: 1`, UTC update time, reviewer/model when known, source fingerprint, and review settings. Save after every completed chunk, using a temporary sibling file followed by atomic replacement. A failed chunk remains failed/pending; never mark the whole video complete because one chunk succeeded. On resume, check fingerprint and settings and process only missing/stale ranges unless the user requests a new review style.

Catalog entries include clip ID, source path, duration/stream metadata, review status, reviewed ranges, evidence methods, links to findings/previews, and failures. Coverage refers to sampled source ranges, not a claim that every frame was watched. Save sampling interval, actual inspected frame timestamps or their manifest path, and transcript coverage separately.

Each chunk record includes source start/end seconds, inspected evidence paths, sampling method, observations, candidate highlights, technical issues, uncertainties, completion status, and any failure. Each event includes:

- Stable event ID, clip ID, source start/end seconds.
- What is visible or said, activity/scene tags, and optional user-supplied location/person labels.
- Evidence method (sampled frames, dense frames, transcript, actual playback), supporting artifact references, confidence, and limitations.
- Highlight suitability and reason, separately from factual observations.

Use explicit approximate event boundaries when only sparse samples support them; tighten them before precise editing. Do not infer identities, exact locations, or dialogue from appearance. Preserve user corrections and preferences separately with their provenance; do not overwrite them on automated refresh.

The per-video `summary.md` includes source identity and metadata, a readable synopsis, chronological timestamped events, best moments with reasons, technical/audio notes, links to previews and structured findings, coverage/gaps, and user notes. `events.json` is the merged timestamped event list, not just the highlights: preserve ordinary observed events so later questions about the video are answerable. A transcript is optional; missing transcription is explicitly recorded, not fabricated.

## Required top-level FOOTAGE.md

Maintain this as a browsable summary of the entire library, including videos not yet reviewed. Update after integrating each completed batch and before returning to the user. Include:

1. Source root, last update, total files and duration, review coverage, failures and stale sources. Avoid double-counting overlapping ranges.
2. One row per source video: clip ID, source filename/path, duration, concise content synopsis, review status/evidence level, best candidate timestamps, and relative links to summary and previews. Unknown content is labeled unreviewed, not guessed.
3. Activities/themes index linking to relevant videos and timestamped findings, based only on observed or user-supplied information.
4. Cross-library highlights and possible narrative threads, labeled as creative suggestions.
5. Remaining review work and links to catalog, creative brief, and edit plan when they exist.

The overview should let the user understand the files and footage without reading JSON. Link out for detailed events rather than duplicating the entire catalog. Use readable `HH:MM:SS` times in Markdown and numeric source-relative seconds in JSON. Verify artifact links, JSON parsing, range bounds, unique IDs, and status consistency after integration.

## Chat across sessions

Read FOOTAGE.md, then the relevant video records. Answer questions with source filenames and timestamps, linking to evidence or previews. If findings lack the requested detail, inspect that source range and persist the new evidence. Do not re-review the entire library to answer a question about one clip. Do not rely on a previous subagent conversation being available.
