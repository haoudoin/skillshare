# Rendering guidance

## Reproducible timing

Keep source-to-output mapping explicit. An edit item should contain `clip_id`, `source_path`, `source_in_seconds`, `source_out_seconds`, `speed`, `timeline_in_seconds`, and `reason`. Validate `0 <= in < out <= source duration` and positive speed. Before transitions, output duration is `(out - in) / speed`; overlaps shorten the timeline. Represent titles, audio, and transitions explicitly in the plan.

Generate FFmpeg commands with safe argument arrays when possible. Check local filters and encoders before relying on them. Capture failures and never silently omit failed clips.

## Media handling

- Mixed GoPro recordings can differ in resolution, frame rate, rotation, audio layout, and color transfer. Normalize canvas, output frame rate, pixel format, sample rate, and channel layout before concatenating. Preserve aspect ratio with an intentional crop or padding.
- HDR/HLG/PQ and log footage need appropriate color handling; changing color tags is not tone mapping. Avoid arbitrary LUTs when the camera profile is unknown.
- Use timestamps for variable-frame-rate inputs. Stream-copy cuts can land on keyframes; re-encode for precise boundaries. Reset trimmed segment timestamps before filter concatenation.
- Slow motion needs sufficient source frames for the target rate. Adjust video timestamps and handle audio explicitly: retime within supported ranges, mute, or replace. Do not promise smooth slow motion from low-frame-rate footage.
- Stabilization may already be baked into GoPro footage. Assess visible shake before adding stabilization, crop, lens correction, or sharpening.
- For review copies, H.264, yuv420p, AAC, and MP4 fast-start are reasonable defaults. Choose final resolution and quality for the user's delivery requirements. Preserve high-resolution originals.
- Handle silent clips explicitly when the timeline expects audio. Preserve useful natural sound; avoid abrupt audio cuts. Use supplied or appropriately licensed music. A music-free rough cut is acceptable when music is unavailable.
- For editor projects, target the user's actual editor and supported interchange format. Arbitrary JSON is not necessarily importable. Check frame rates, paths, and effect support; document unsupported transitions or titles.

## Verify the result

Use `ffprobe` to check duration, dimensions, codec, frame rate, and audio presence. Decode the export to a null sink with FFmpeg to catch corruption. Inspect frames around transitions, rotation, crops, titles, and color. Check levels with available audio tools; claim listening only if audio perception/playback tools actually supplied that evidence. A successful encode does not establish creative quality.

Keep the edit plan and render command/script beside the output so revisions do not require rescanning the footage.
