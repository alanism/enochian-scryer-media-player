# Enochian Scryer — rqbit companion

The companion manages torrents and opens their media streams in **Enochian VLC**. Keeping the two processes separate lets downloads continue while you change videos or close the player. rqbit already prioritizes requested pieces and supports HTTP byte ranges; the bridge forwards those ranges for VLC seeking.

The Linux build uses rqbit's official 9.1.0 engine and its existing React interface, with the original Enochian controls. Omarchy opens the interface in a Chromium app window. This package does not replace rqbit's Rust engine or install its Tauri desktop wrapper.

## Use

Run `./install.sh` from this folder, then open **Enochian Rqbit** from the Omarchy launcher. Install the companion VLC package first to enable playback.

- **ADD LINK** accepts a magnet link or torrent URL; **ADD FILE** opens a torrent file.
- **Cards** is the initial view, with a visible **PLAY IN VLC** key and separate **RESUME TRANSFER / PAUSE TRANSFER** utility keys. **FILES & DETAILS** opens the existing detailed view. In **List**, select transfers to use the bulk transfer controls. The chosen view is remembered.
- **PLAY IN VLC** in Overview opens the first included media file. Files has a separate play key for each supported media file.
- In **CARDS** view, double-click a completed torrent to open its first included media file directly in Enochian VLC. Incomplete torrents do not launch. Completed paused torrents stay paused while the local file plays.
- Right-click a torrent card and choose **Show file** to reveal its first available included media file in the file manager. For non-media torrents, it reveals the first available included file. If file highlighting is unsupported, it opens the containing folder. Missing files produce an error on the card.
- Keyboard users can focus a completed card and press **Enter** to play, or **Shift+F10** to open its menu. **Escape** closes the menu.
- **IVORY / OBSIDIAN** changes the finish and remembers it. Both options stay visible with the selected state shown. VLC opens in the same finish as the companion.
- Downloads go to `~/Downloads/Enochian` by default; the add dialog can specify another folder.
- Closing the app window keeps transfers running. To stop the engine, use the launcher's **Stop transfers and service** action, or run `python3 ~/.local/share/enochian-rqbit/companion.py --stop`.
- The service starts when the app opens. It is not added to login startup, and it does not change magnet or torrent-file defaults.

## Components preserved

The CSS in `src/enochian/library.css` is copied from the Enochian Elements atlas. Tape Deck 05.07 supplies the original play/pause SVGs, key surfaces, lamps and down states. Drum Machine `sq-btn` supplies utility buttons. The original segmented ladder supplies progress. Obsidian and Ivory retain the original materials and colors. Labels, sizes and composition adapt these controls to transfer management; no new control artwork was drawn.

The interface keeps rqbit's transfer list, filters, file selection, limits, logs, and remove confirmation. Native file pickers remain system dialogs. Form text fields and rqbit's detailed data tables use the matching material palette and type; they are not copies of an atlas device screen.

## Build

From the rqbit repository root, `enochian/build.sh` installs the locked frontend dependencies and builds the web interface. If the engine is missing, it downloads the pinned official Linux x86_64 release and verifies its SHA-256. Use `enochian/build.sh --source-engine` with Rust installed to compile the checked-out engine instead. Node 20.19+ or 22.12+, npm, Python 3, Chromium and VLC are required; the installed app needs only Python 3, Chromium and the VLC bundle.

`provenance.json` records the source commit, release URL, checksum and control sources. rqbit retains its upstream Apache license; the bundled IBM Plex Mono font retains its OFL license.

## Verification and limits

Verified on this Omarchy desktop: TypeScript and production build; app loads without browser errors; transfer selection; Overview and Files; switching finishes; and Play in VLC. A private, tracker-free local MP4 fixture verified HTTP 206 byte ranges against the original bytes, pause/resume, the installed Obsidian VLC skin, Playing status and a five-second seek. No public torrent swarm was used for this test. Audible playback and live downloading from remote peers were not tested.

The card actions were checked with separate local completed and incomplete fixtures: completed playback opened the installed VLC with a local file, confirmed Playing and seeking, and preserved the torrent's paused state; incomplete-card double-click did not launch. Show file opened the fixture's download directory through the desktop file manager. The menu's keyboard opening, activation and dismissal were checked at 1280×720. From the rqbit root, `npm run test:enochian` runs 15 Python bridge/installer/launcher tests and three UI presentation regression cases. The [council review](../../docs/COUNCIL_REVIEW.md) records the scope and remaining limits.

The in-app browser comparison checked the original key silhouette and glyphs, key gradients and shadows, utility button edges, the two finish palettes, mono typography, and segmented progress. The compact table meter was adjusted to fit its column. New functional copy is limited to transfer labels and the VLC handoff. The 1280×720 desktop view was checked; narrow viewport overrides did not reliably apply to the background app tab, so mobile behavior remains unverified. This is a Linux desktop companion.

The HTTP interface binds to `127.0.0.1:19380`; the engine binds to `127.0.0.1:19381` with a new random credential per launch. The bridge restricts mutations to the app's origin and accepts only torrent/file identifiers for playback. Router port forwarding is disabled. Transfer state is stored under `~/.local/share/enochian-rqbit-state`, separately from any stock rqbit installation.
