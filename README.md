# Enochian Scryer Media Player

A matching media suite for Omarchy: **Enochian VLC** for playback and **Enochian Rqbit** for torrent transfers, connected by a **Play in VLC** key.

The suite reuses the original controls from [Enochian Elements](https://uiux-nonhumanintelligence.web.app/UIUX). Tape Deck transport keys, Drum Machine utility buttons, rotary volume and ribbed sliders retain their original artwork, materials and states. The two apps offer matching Obsidian and Ivory finishes.

## Install on Omarchy

Install the system playback components with:

```sh
omarchy pkg add vlc vlc-gui-skins2 vlc-plugin-ffmpeg xorg-xwayland
```

Python 3 and Chromium are also needed for the transfer companion. For a checkout from GitHub, build its interface and fetch the verified engine first:

```sh
cd rqbit
enochian/build.sh
cd ..
```

The ready-to-install Linux bundle already contains that engine and interface. Install both apps, with the player as the MP4 default:

```sh
./install.sh --make-default
```

Open **Enochian VLC** or **Enochian Rqbit** from the Omarchy launcher. The companion sends torrent media directly to VLC; the torrent engine continues running when the player closes. See [companion controls and background-service behavior](rqbit/enochian/README.md) and [VLC controls](vlc/README.txt).

## Why two apps

rqbit already streams files through range-enabled HTTP and prioritizes pieces requested by a player. Keeping transfers in a companion avoids tying download lifetime to a VLC window. The local bridge accepts a torrent/file choice and launches the installed Enochian VLC with the stream URL and matching finish. No public server or browser extension is needed.

## Implementation

- `vlc/`: four VLC 3 Skins2 packages (Obsidian/Ivory, standard/compact), launcher, user installer and original component snapshots/build sources. VLC itself comes from the system packages; this is a skin integration, not a VLC engine fork.
- `rqbit/`: the upstream rqbit source at `f23bacdddcc5318caa813418b8eb1b1d7307faaa`, with the shared React interface reskinned and a Linux companion in `rqbit/enochian/`.
- `rqbit/enochian/provenance.json`: official rqbit 9.1.0 release URL and verified SHA-256. The standard Linux bundle uses this release engine; Rust compilation is optional.

The VLC interface uses XWayland on Omarchy. Its main player, playlist and equalizer are skinned. File pickers and advanced VLC dialogs remain system/Qt dialogs. The transfer companion uses a Chromium app window, rqbit's existing data views, and the original Enochian controls; its native file picker remains a system dialog.

## Checked on this machine

The MP4 desktop association opened the installed Obsidian VLC skin and reported Playing. rqbit's production frontend build passed. A private local MP4 torrent verified byte-for-byte HTTP 206 ranges, pause/resume, opening the installed VLC, Playing status and a five-second seek. Browser checks covered transfer selection, Overview/Files, the VLC action and both finishes without app console errors. See the component READMEs for the tested scope and remaining limits. No remote public torrent swarm or audible playback was tested.

## Sources and notices

[VLC](https://github.com/videolan/vlc), [rqbit](https://github.com/ikatson/rqbit), and [Enochian Elements](https://uiux-nonhumanintelligence.web.app/UIUX). Upstream code and bundled fonts retain their included licenses and notices. The Enochian artwork is not relicensed by rqbit's upstream license.
