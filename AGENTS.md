# Enochian Scryer contributor map

This is a Linux/Omarchy media suite: system VLC 3 plus skins, and rqbit with a
custom frontend and a local Python desktop bridge. Upstream rqbit's engine is
imported source; it is not a new media engine.

## Find the integration

- `vlc/enochian-vlc`: installed VLC launcher. `vlc/source/`: skin generator and verifier.
- `rqbit/enochian/companion.py`: local HTTP bridge and engine lifecycle.
- `rqbit/crates/librqbit/webui/src/enochian/`: copied control rules and React adapters.
- `rqbit/crates/librqbit/webui/src/helper/torrentPresentation.ts`: truthful progress/status presentation.
- [Control/function decisions](docs/ENOCHIAN_CONTROL_MAP.md).
- [Council review and evidence](docs/COUNCIL_REVIEW.md).

## Preserve the user's design

Reuse the existing Enochian elements. Resize, relabel and compose them; preserve
their surfaces, glyphs, shadows and corner geometry. The copied rules are in
`library.css`; app layout belongs in `app.css`. Keep Ivory and Obsidian matched.
Tape Deck keys operate media. Utility keys operate transfers and files.
Do not add decorative knobs or meters that are not connected to real values.

## Check a change

From `rqbit/`, run `npm run test:enochian` and `npm run build -w rqbit-webui`.
From the suite root, `python3 vlc/source/verify.py` verifies all four skins
(requires Pillow and xmllint; see `vlc/README.txt`).
Drive the rendered UI when changing interaction or layout; compilation alone
does not verify a user journey. Keep any test media synthetic and separate from
the installed app's transfer state.

The bridge supports `ENOCHIAN_RQBIT_TEST=1` with separate UI/engine ports,
`ENOCHIAN_RQBIT_STATE`, and `ENOCHIAN_RQBIT_DOWNLOADS` for isolated checks.
Use those rather than the user's live download records for testing.

Engine binaries, built web files, caches and dependencies are ignored by Git;
include the verified engine and built frontend in the installable release ZIP.
The root installer changes the MP4 association only with `--make-default`.
