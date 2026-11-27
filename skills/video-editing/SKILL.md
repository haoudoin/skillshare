---
name: video-editing
model: sonnet
effort: medium
description: Coordinate footage reviewers and a creative producer for local video editing. Persist timestamped findings and a FOOTAGE.md overview so users can discuss individual videos across sessions, select highlights, develop creative direction, and produce edits.
---

# Video editing

Turn local footage into evidence-backed selections and playable edits. Use the source path and editing brief supplied by the user. Store generated media and project data in the user's project/output folder, never in this global skill directory.

## Team and durable project memory

Read [references/team-and-findings.md](references/team-and-findings.md) before reviewing footage or answering questions about an existing library. The main conversation coordinates the team, maintains shared indexes, and talks with the user. Delegate independent footage batches to the `footage-reviewer` Sonnet subagent and creative direction to the `creative-producer` Opus subagent when available. For a small focused question, answer from saved evidence or inspect directly without unnecessary delegation. If a configured agent/model is unavailable, disclose the fallback and follow the same persistence contract locally.

Findings are project files, not agent memory. Reviewers checkpoint each chunk; the coordinator maintains a top-level `FOOTAGE.md` that summarizes every discovered video, links to detailed findings, and clearly distinguishes reviewed, partial, stale, failed, and unreviewed footage. On a new session, read this overview and retrieve only the relevant detailed records before requesting fresh analysis.

## Model and token budget routing

Use Sonnet with medium effort for the coordinator, footage-reviewer, and video-editor; reserve Opus with high effort for creative-producer. These are quality/cost defaults, not measured guarantees. The skill model override applies to the invoking turn; for sustained chat recommend starting `claude --model sonnet` or selecting `/model sonnet`. Do not change global session settings. User-selected model preferences take precedence.

Invoke the named specialist types so their explicit models apply. Do not override them with the coordinator model or use an Opus general-purpose agent for routine work. Report a runtime model substitution if surfaced; configuration is not proof of the actual model used. Specialists read only the relevant references rather than preloading this entire orchestration skill.

- Run inventory, metadata aggregation, JSON validation, frame extraction, and rendering with reusable local scripts. Keep verbose logs on disk and return errors or concise summaries.
- Answer factual questions from saved findings in the coordinator. Do not invoke the producer for cataloging, retrieval, routine trimming, exports, or executing an existing plan. Invoke it for an initial creative proposal or a substantive change of story; minor mechanical revisions stay with Sonnet.
- Pass paths, assigned ranges, and a compact task brief to workers, not the full conversation or catalog. Batch enough footage per worker to amortize startup while keeping visual context manageable. Save full findings to disk; aim for handoff summaries under 300 words unless a material issue needs explanation.
- Give the producer shortlisted observations and selected visuals. Let it request specific missing evidence instead of rescanning the whole library. Reuse its saved decisions until the creative brief changes.
- Track completed ranges and evidence settings. Reuse valid artifacts, update only changed records, and load relevant excerpts instead of rereading all findings. Generate shared tables from structured records with scripts where practical.
- Record token usage and model from tool results when available; otherwise label usage unknown. Never infer exact cost from video file size or claim measured savings without a comparison.

## Task defaults

- Resolve the footage directory from the invocation or existing project catalog. If neither supplies it, ask for the directory before inventorying. Once resolved, proceed with the requested scope without asking again.
- Route by intent: catalog/review creates or refreshes findings and FOOTAGE.md; questions retrieve findings and inspect gaps; propose/plan adds creative direction and edit-plan.json; create/render/edit additionally delegates assembly to `video-editor` using the saved plan. Reuse valid catalog entries instead of reprocessing unchanged footage. Exclude the generated output directory from source discovery.
- The coordinator owns orchestration. Specialist subagents follow their assigned role and do not recursively launch the full team simply because this skill is preloaded.

- Match the requested deliverable: recommendations need a reviewable shortlist; a request to create a video includes rendering and checking the result. Do not expand advice-only requests into full-library renders.
- Infer creative defaults when unspecified: a 3–5 minute landscape YouTube vacation highlight with a strong opening, varied activities, personal moments, and a satisfying ending. State assumptions briefly; ask only for information that blocks useful work, such as a missing footage location.
- Check available `ffmpeg`, `ffprobe`, disk space, and optional transcription tools. Use installed tools first and disclose missing dependencies.
- Preserve originals. Keep proxies, frames, transcripts, catalogs, and exports in separate output paths. Account for existing outputs before overwriting. Treat filenames as data; use subprocess argument arrays or proper shell quoting.
- Local preprocessing does not imply local inference: images opened in Claude may be sent to its model service. External uploads of originals and separately billed APIs require authorization for that use. This skill does not authorize publishing to YouTube.

## Index and inspect

1. Inventory footage recursively with `ffprobe`. Record stable clip IDs, source paths, duration, video/audio streams, resolution, frame rate, rotation, and color metadata. Record unreadable files explicitly. Do not infer chronology solely from filenames or assume camera clocks are accurate. Keep GoPro chapter files traceable to their originals.
2. Generate readable JPEG contact sheets labeled with source IDs and source-relative timestamps. Start near one frame every 15 seconds for a cost-conscious overview of long vacation clips, including beginning/end samples. Use approximately 5 seconds or denser for short clips, action, and user-prioritized moments. State that a coarse scan can miss brief events; increase coverage when the requested review requires it. Start with frames around 640 pixels wide, enlarging only when evidence is unreadable; contact sheets do not make image tokens free. Paginate long clips and retain a machine-readable frame-to-time mapping. Use media timestamps rather than frame count divided by nominal FPS.
3. Actually open the images with Claude's image-capable file tool. Process manageable batches and persist observations per clip. Generating sheets or reading filenames does not count as visual inspection.
4. Inspect promising or ambiguous sections with larger frames and denser sequences, typically 2–4 FPS or more for brief action. Include lead-in and aftermath. Sparse sampling can miss the best moment; scene detection alone misses events within continuous recordings.
5. When speech matters, use an available transcription tool for source-timestamped text. Preserve offsets when chunking audio. Label uncertain words. Transcripts do not establish music quality, sound quality, or emotional delivery.
6. Track coverage as metadata-only, sampled visually, densely sampled, transcribed, or playback-reviewed. Do not claim to have watched or heard footage without tools that supply that evidence. Flag motion/audio uncertainties for playback review.

For large libraries, start with a representative batch to calibrate selection style, then continue through the requested scope. Cache observations and reuse valid previews. A pilot does not complete a whole-library request. Report coverage and failures.

## Recommend a story

Favor memorable action, clear reactions, distinctive settings, and moments meaningful to the traveler. Balance people, scenery, activities, transitions, and quieter beats. Avoid redundant scenery, long setup, and accidental recordings unless they serve the story. Distinguish technical quality from personal significance; user favorites override generic scoring.

Deliver a ranked shortlist and ordered edit proposal with source filename, clip ID, source in/out times, intended timeline duration, selection reason, evidence level, and uncertainty. Include an opening hook, coherent sequence, natural-audio opportunities, and ending. Do not invent events, dialogue, identities, locations, or music rights.

Persist the catalog and edit plan as JSON with times in seconds and explicit source versus output timing; provide a readable Markdown summary. When useful, create a local HTML review page with thumbnails and playable candidate excerpts. Browser-incompatible originals may need lightweight H.264/AAC proxies. Escape text and filenames in HTML; use portable relative links within the output folder.

## Render and verify

For requested renders, delegate to the `video-editor` Sonnet subagent when available. Give it the exact edit-plan.json path and revision, source root, creative-brief.md, output directory, and delivery requirements. The coordinator saves a concrete plan before dispatch: ordered source ranges, speed, timeline placement, transitions, titles, audio choices, and output settings. If creative direction has not been developed, obtain the producer's proposal and integrate it first. An existing user-supplied plan can be used directly.

The editor creates a reproducible local render script, assembles the selected original ranges with FFmpeg, and produces a versioned MP4 plus a verification report under `video-editing/exports/`. It may create proxies for previews but uses originals for the final render. It reports missing inputs and unsupported choices instead of silently replacing the producer's selections. The coordinator integrates output links into FOOTAGE.md. For subsequent feedback, revise the brief/plan as needed and render a new version without recataloging unchanged sources.

Read [references/rendering.md](references/rendering.md) when rendering, changing speed, mixing audio, or exporting an editor timeline.

A direct request to create an edit authorizes a reversible rough cut; do not add an extra approval gate. Render a short representative preview before a costly full export when technical choices are uncertain.

Check selected ranges, output decoding, duration, and expected streams. Inspect rendered frames around cuts and at the beginning/end. Distinguish automated verification from playback/audio checks actually performed. Report output paths, creative choices, source coverage, and remaining review needs.
