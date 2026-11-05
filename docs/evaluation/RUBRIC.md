# Ryo Lu lens: 20-criterion, five-level rubric

A project-specific rubric inspired by the supplied card; not an official Ryo Lu rubric or endorsement.

Source: [supplied Ryo Lu card](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Design_Council/ryo_lu_design_hero.md). Priorities: simple entry, visible state, user control, reusable primitives, progressive disclosure and refinement in working software. Preserve original Enochian elements.

## Scoring contract

- Score each of 20 criteria with integer 1–5; sum is out of 100.
- Freeze anchors/weights before the loop. Do not omit difficult journeys or award points for test count alone.
- Every score needs a reason and evidence/method. Unverified requirements remain gaps, not assumed passes.
- Report observed UI separately from API/source/mock/format checks. Backend-only evidence cannot establish excellent interaction quality.
- Pass requires >=95 total, every criterion >=4, mandatory journeys passed and no unresolved critical/high defect.
- Self-evaluation is not independent expert review. Preserve unsuccessful runs and remaining limits.
- Repeat: evaluate → identify gaps → bounded fixes → build/test → drive relevant journeys → rescore unchanged rubric. Stop at the gate or a concrete validation blocker.

## Criteria

### 01. First launch and empty states

Identify both apps, start the first task and understand an empty queue.

| Points | Anchor |
| --- | --- |
| 1 | No usable entry point |
| 2 | Next action obscure |
| 3 | First task needs guidance |
| 4 | Clear actions and useful empty states |
| 5 | Entry, empty/loading and repeat launch verified |

### 02. Open local media

Open single/multiple files, spaces in names, append/drop and invalid media.

| Points | Anchor |
| --- | --- |
| 1 | Cannot open media |
| 2 | One fragile path |
| 3 | Single-file opening works |
| 4 | Single/multiple files and identity verified |
| 5 | Open, enqueue/drop, identity and invalid-file recovery verified |

### 03. Open streams and URLs

Play valid media URLs and recover from invalid or unreachable addresses.

| Points | Anchor |
| --- | --- |
| 1 | No URL path |
| 2 | Unreliable URL playback |
| 3 | Valid URL plays |
| 4 | Valid/invalid URL handling works |
| 5 | URL playback, range/seek, loading and failure recovery verified |

### 04. Playback transport and agency

Play/pause/resume/stop/previous/next act predictably with truthful state.

| Points | Anchor |
| --- | --- |
| 1 | Playback blocked |
| 2 | Some transport fails |
| 3 | Core transport with ambiguity |
| 4 | All transport states work |
| 5 | Actions, empty-queue boundaries and visible state verified |

### 05. Time, seeking and continuity

Time/duration/seek agree; boundary seeks do not strand playback.

| Points | Anchor |
| --- | --- |
| 1 | Time or seek broken |
| 2 | Unreliable seek |
| 3 | Normal seek works |
| 4 | Forward/backward seek and duration agree |
| 5 | Seek, pause/seek/resume and start/end boundaries verified |

### 06. Audio and media adjustments

Volume/mute and available track/speed/subtitle controls are discoverable and reversible.

| Points | Anchor |
| --- | --- |
| 1 | Essential adjustments absent |
| 2 | Settings frequently fail |
| 3 | Volume/mute works |
| 4 | Core and advanced routes work |
| 5 | Reversible adjustments, readbacks and absent-track cases verified |

### 07. Viewing and window modes

Fullscreen/exit and normal/compact layouts retain reachable controls and fitted video.

| Points | Anchor |
| --- | --- |
| 1 | Controls inaccessible |
| 2 | A mode traps the user |
| 3 | Main view works |
| 4 | Fullscreen/exit and both sizes work |
| 5 | Transitions, playback continuity and visible bounds verified |

### 08. Create a playlist

Add multiple items, inspect names and start the intended item without losing the queue.

| Points | Anchor |
| --- | --- |
| 1 | Cannot create queue |
| 2 | Items lost or misidentified |
| 3 | Multiple items play |
| 4 | Add/select works |
| 5 | Create/add/select/append and duplicate-name cases verified |

### 09. Edit and navigate playlists

Remove/reorder/navigate with clear selection and current item.

| Points | Anchor |
| --- | --- |
| 1 | Cannot edit |
| 2 | Wrong items changed |
| 3 | Basic remove/navigation |
| 4 | Remove/reorder/next/previous work |
| 5 | Edits, navigation and empty/boundary cases verified |

### 10. Save and reopen playlists

Named playlist round-trip preserves order and identity; missing files have recovery.

| Points | Anchor |
| --- | --- |
| 1 | Cannot save/reload |
| 2 | Saved data incomplete |
| 3 | Basic save/load |
| 4 | Order and identities survive |
| 5 | Named round-trip, spaces/Unicode and missing-file recovery verified |

### 11. Add torrents and links

Import file/link, inspect inclusion/destination, cancel and recover from invalid input.

| Points | Anchor |
| --- | --- |
| 1 | Cannot add |
| 2 | One partial add path |
| 3 | Main add path works |
| 4 | File/link, selection and cancel work |
| 5 | Both paths, invalid input, destination and cancel verified |

### 12. Control transfers and selected files

Pause/resume/inclusion/limits/removal affect the intended record.

| Points | Anchor |
| --- | --- |
| 1 | Controls fail |
| 2 | Wrong target or state |
| 3 | Pause/resume works |
| 4 | Selection and controls independent |
| 5 | Pause/resume/inclusion/limits/removal verified against real state |

### 13. Torrent-to-player handoff

Completed/per-file actions select the right media/player; incomplete double-click does not launch.

| Points | Anchor |
| --- | --- |
| 1 | No handoff |
| 2 | Wrong media/player |
| 3 | Main handoff works |
| 4 | Completed/per-file behavior works |
| 5 | Completed/partial/per-file handoff and finish/state preservation verified |

### 14. Show files and destinations

Reveal the correct item; missing files and custom destinations have clear outcomes.

| Points | Anchor |
| --- | --- |
| 1 | No location access |
| 2 | Wrong location |
| 3 | Main reveal works |
| 4 | Reveal/missing/custom paths work |
| 5 | Reveal, fallback, missing/custom paths and feedback verified |

### 15. Progress and status truth

Percentages, pieces and pending/success/error signals agree with actual state.

| Points | Anchor |
| --- | --- |
| 1 | Absent or false state |
| 2 | Misleading completion |
| 3 | Mostly correct |
| 4 | Success/error/paused/checking truthful |
| 5 | Relevant states and zero/invalid counters verified; no misleading success |

### 16. Settings and progressive disclosure

Common preferences are simple; advanced paths remain; save/cancel/reopen are predictable.

| Points | Anchor |
| --- | --- |
| 1 | Settings inaccessible |
| 2 | Save/cancel unreliable |
| 3 | Common settings work |
| 4 | Common/advanced and persistence work |
| 5 | Save/cancel/reopen/error and preference persistence verified |

### 17. Keyboard, focus and labels

Core tasks have keyboard routes, visible focus, labels and usable targets without traps.

| Points | Anchor |
| --- | --- |
| 1 | Core tasks inaccessible |
| 2 | Unlabeled/trapped controls |
| 3 | Main keyboard routes |
| 4 | Core focus/label/target checks pass |
| 5 | Core journeys and modal/menu focus restoration verified; native input limits stated |

### 18. Errors, cancellation and destructive safety

Explain next steps; cancel commits nothing; destructive choices reset before reuse.

| Points | Anchor |
| --- | --- |
| 1 | Loss or no recovery |
| 2 | Unsafe cancel/destructive state |
| 3 | Basic confirmation/errors |
| 4 | Cancel/reset/error recovery works |
| 5 | Failure/retry/cancel/backdrop/Escape and destructive-state reset verified |

### 19. Enochian fidelity and hierarchy

Original elements match functions; both finishes are legible without clipping/material drift.

| Points | Anchor |
| --- | --- |
| 1 | Elements replaced/broken |
| 2 | Major mismatch |
| 3 | Recognizable with gaps |
| 4 | Correct mapping and readable finishes |
| 5 | Reference plus real-view sizing, contrast, focus and overflow checks pass |

### 20. Install, defaults and continuity

Install/update/default/restart/background behavior preserve records with a recovery route.

| Points | Anchor |
| --- | --- |
| 1 | Cannot install/launch |
| 2 | Updates lose data/defaults |
| 3 | Main install works |
| 4 | Install/default/restart preserve data |
| 5 | Upgrade/restart/default/background/failure recovery verified in isolation |

## Mandatory journeys

Open local files; playback transport; create/add/edit/reorder playlist; save/reopen playlist; torrent add/control; torrent playback/Show file; settings save/cancel; error/cancellation recovery. Each evidence item records the surface, fixture, action, result, method and uncertainty.
