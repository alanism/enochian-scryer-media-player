# Council review — 5 November 2026

Reviewed baseline: `0fd5083679739846160bc8ee194073b953cc5ab7` (v0.1.1).
Scope: authored Linux launch/install scripts, the VLC skin definitions and
validation, the rqbit bridge, and the modified React interface. This is not a
full audit of the imported upstream VLC/rqbit engines.

## Sources and application

The [shared router](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/how-to-use.md)
and cards were loaded from `alan-coding-dark-factory` at the revision above.
They were used as advisory review lenses by the implementer; there were no
independent reviewers, council votes, or consultations with their namesakes.
This task follows the media project's existing authorization, not ACDF release
gates. The user authorized inspection and design fixes while preserving the
existing Enochian elements.

| Review role / lens | Applied concern |
| --- | --- |
| Code review / [Ryan Lopopolo](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Engineering_Council/ryan_lopopolo_coding_hero.md) | Reproducible checks, truthful UI state, a short repository map and focused regression tests. |
| Runtime review / [Mitchell Hashimoto](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Engineering_Council/mitchell_hashimoto_coding_hero.md) | Process failure behavior, isolated integration fixtures, reinstall behavior and persisted state. |
| Implementation / [John Carmack](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Engineering_Council/john_carmack_coding_hero.md) | Direct control flow, typed presentation helpers, measured behavior rather than a rewrite. |
| Interaction review / [Andy Allen](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Design_Council/andy_allen_design_hero.md) | Preserve tactile key materials and travel; usable targets; conventional media functions. |
| Clarity review / [Ryo Lu](https://github.com/alanism/alan-coding-dark-factory/blob/ba629d91156d0a549e79b7f96852be4c03b93cea/heroes/Design_Council/ryo_lu_design_hero.md) | Visible actions and outcomes, clear playback/transfer separation, simple default with advanced list/settings preserved. |

Willison and Carlini cards were also read for context. Their agent-specific
security architecture was not imposed on this deterministic media app, and no
full adversarial security certification is claimed. No NotebookLM query was
needed to resolve a material design or implementation question.

## Findings and fixes

| Priority | Evidence at the baseline | Result |
| --- | --- | --- |
| P2 | `TorrentTableRow.tsx` and `OverviewTab.tsx` forced any error's progress to 100%; zero-byte metadata could also appear complete. | Shared `torrentProgress` derives the value from bytes, clamps invalid counters, and leaves checking at zero. Regression case: 250/1000 bytes plus a disk error stays 25%. |
| P2 | `OverviewTab.tsx` used a session download counter as total piece inventory; completed paused fixtures displayed 0/26. | Completed fixture displays 26/26. An unavailable partial inventory uses a dash rather than a fabricated zero. |
| P2 | `.en-row-actions .tp-key` used `zoom:.5`, shrinking labels to roughly 4.5px; utility targets shrank below 30px. | Full-size playback key, labeled transfer utilities and card/header targets measuring at least 44×44px. |
| P2 | Cards had no visible media action; play-shaped transfer keys blurred download and playback meaning. | Visible Tape Deck “Play in VLC”; distinct utility commands for pause/resume transfer; double-click and Show file retained. |
| P2 | View mode reset on reload and toolbar choices showed only the alternative action. | Cards are the initial view; the chosen view persists; both choices and selected state remain visible. |
| P2 | `/enochian/play` accepted JSON scalars/arrays and then raised `AttributeError`, dropping the request. | Desktop action bodies must be objects and return HTTP 400 otherwise. Four malformed shapes reproduced the old failure before the fix. |
| P2 | Engine connection loss escaped the health handler and the proxy closed requests without a useful error. | Health returns 503 and the proxy returns a readable 502 JSON error before streaming starts. Regression tests reproduced both old failures. |
| P3 | `--ivory --compact` left `--compact` for VLC instead of choosing the compact skin. | Leading Enochian flags work in either order; shell argument boundaries are preserved. |
| P3 | Rqbit desktop Exec failed to escape literal `%` in a custom installation path. | Percent field-code escaping now matches the VLC installer; a path containing spaces and `%` validates. |

A suspected running-executable replacement problem was **not confirmed**:
the existing GNU `install` successfully replaced the fixture executable while
its old process stayed alive. No unnecessary replacement mechanism was added.

## Evidence and limits

- `npm run test:enochian`: 15 Python bridge/installer/launcher tests and 3
  TypeScript presentation cases pass. The frontend tests transpile with the
  existing TypeScript dependency to avoid requiring experimental TypeScript
  execution flags. This run used Node 26; Node 20/22 were not separately run.
- `npm run build -w rqbit-webui`: TypeScript and Vite production build pass.
- The four VLC skins passed DTD, asset and dial-frame verification using the
  existing workspace Python environment with Pillow. System Python lacked
  Pillow; no new system package was installed for this check.
- Live isolated rqbit 9.1.0 fixtures on ports 19390/19391: completed media
  opened in the installed VLC, reported Playing and accepted a five-second
  seek; the completed transfer stayed paused. Resume/Pause changed real
  transfer state independently. Show file opened the fixture location.
- Browser: both finishes at 1280×720; visible media action, Files/details,
  26/26 completed pieces, persisted List selection, Cards selection, card
  context menu and feedback; no app console errors or framework overlay.
  DOM measurements found no undersized card/header control or horizontal
  overflow. The live atlas materials matched the revised Ivory controls.
- [Control/function map](ENOCHIAN_CONTROL_MAP.md) records retained choices and
  alternatives. Original component CSS and VLC skin artwork are unchanged.
- The installed bridge, frontend and VLC launcher were updated and compared
  with the delivered files. Both desktop entries validate; the companion
  restarted with the same existing transfer identifiers and hashes.

Desktop was the target. Narrow/mobile layouts, audible output, remote public
torrent swarms, every VLC auxiliary control and failure during an active
stream were not exhaustively exercised. Engine-loss response behavior was
verified with focused failure-injection tests, not by crashing the user's
running engine. The first attempted disk-error fixture was rejected by the
engine at add time, so error-progress presentation was verified with explicit
regression inputs instead of claiming a live disk-error torrent test.

Native file pickers and advanced VLC dialogs remain system/Qt dialogs. Those
limits are unchanged; the council review does not imply a full native Wayland
VLC fork or independent human security sign-off.
