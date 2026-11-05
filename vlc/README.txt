ENOCHIAN VLC — OMARCHY EDITION

An actual VLC 3 Linux skin pack, with Obsidian and Ivory finishes.
Uses VLC's own Skins2 interface and playback engine. No browser wrapper,
custom media engine, VLC source rebuild, or replacement desktop theme.

START ON OMARCHY

1. Install the official Arch packages if missing:
   sudo pacman -S vlc vlc-gui-skins2 vlc-plugin-ffmpeg vlc-plugin-freetype xorg-xwayland python-gobject gtk3 nodejs

2. From this folder run:
   ./enochian-vlc

   Ivory finish:
   ./enochian-vlc --ivory

   Force smaller controls for a narrow tile:
   ./enochian-vlc --compact --ivory

   Open a file, preserving spaces in its name:
   ./enochian-vlc "/path/to/your movie.mkv"

3. To add a separate “Enochian VLC” entry to the Omarchy launcher:
   ./install.sh

The installer copies the launcher and skins to ~/.local/share/enochian-vlc
(or XDG_DATA_HOME), and adds its own desktop entry. It does not change file
associations, stock VLC defaults, Hyprland settings, or Omarchy themes.
The launcher's command line selects the skin for that VLC process.
Its own settings file is stored in ~/.config/enochian-vlc/vlcrc.

CONTROLS CHOSEN FROM YOUR ATLAS

Transport: Enochian Tape Deck (05.07), original tp-key markup and CSS.
  REW → previous playlist item; FF → next playlist item.
  PLAY → play/pause, PAUSE → pause/resume, STOP → stop.
  Caps, glyphs, lamps, pressed surfaces, shadows and labels retained.

Volume: Enochian Rotary Knob 01 (00.01), original bar marker and dial.
  101 rendered frames, uniformly resized from the original face.
  Obsidian outer trim is transparent at the user's request; geometry retained.
  Turn around the dial with the pointer; M mutes.

Seek and equalizer: Enochian Slider 01 (03.04), original ribbed cap.
  Seek by clicking or dragging along the line. EQ caps are uniformly
  reduced and rotated. These are live VLC sliders, not decorative images.

Utility keys: the Enochian Drum Machine's existing sq-btn component.
  Labels adapted to OPEN, PLAYLIST, EQ, MENU, FULL, CLOSE and other actions.

Finish colors are the atlas's existing Ivory and Obsidian definitions.
Control geometry was not redrawn. The surrounding player layout composes
these existing components. Source snapshots and the renderer are included.

ENGLISH SUBTITLES

SUBS uses an already enabled English track, a nearby English SRT, or an
embedded English track. Sidecar priority is Movie.en.srt, .eng.srt,
.english.srt, .en-us.srt, .en-gb.srt, then Movie.srt. A plain matching .srt
is treated as your default subtitle; its spoken language is not guessed.
VLC also prefers English language-tagged subtitle tracks when opening media.

When no suitable track/file is available, SUBS asks before any provider
request. DOWNLOAD searches OpenSubtitles for the best English match;
OPEN lets you select an SRT; CANCEL/Escape dismisses without downloading.
During download, Cancel stops this app's downloader. The filename, file size
and OpenSubtitles hash are used after consent. The video is not uploaded.
Matches may need timing adjustment in VLC's normal Subtitle menu.

The official opensubtitles-dev/opensubs-cli 0.1.1 client is included in the
installable Linux release. Provider availability, anonymous quotas and
account requirements are controlled by OpenSubtitles; the app reports a
failed request and offers the local-file route. No account is created.
A downloaded SRT is saved alongside the video without overwriting existing
files, or under ~/.cache/enochian-vlc/subtitles when the folder is read-only.
If playback changes during a download, it is saved without applying to the
new video. Completed rqbit local streams are resolved to their local file.
Other network streams can use an embedded English track or a manual SRT.

VLC's optional Arch vlc-plugin-freetype package is required for subtitle
text to appear. Node.js, Python GObject and GTK3 run the consent/downloader
helper. This helper uses an authenticated, random-port loopback VLC API;
its private connection file is removed when the player exits.

PLAYER FEATURES

Embedded video; drop files to play; elapsed time and duration; current
filename; playlist previous/next; play/pause/stop; seek; rotary volume;
mute; shuffle; loop queue; a skinned playlist window with add/remove/load/
save/sort and a Manage route to the native advanced playlist editor; a skinned 10-band equalizer with preamp and enable control; network
stream dialog; fullscreen; VLC context menu and standard keyboard hotkeys.

Space = play/pause    S = stop    N/P = next/previous    F = fullscreen
M = mute             Ctrl+O = open media

VLC's file picker, advanced settings, context menus and error dialogs use
VLC's standard Qt interface. They are outside Skins2's skinning API.
They have not been replaced with invented Enochian control designs.

LINUX / OMARCHY DETAILS

Skins2 requires X11, so this runs inside Omarchy's XWayland session.
It is not a native Wayland rewrite. The launcher uses xcb for Qt dialogs
and xcb_x11 for embedded video. Software video decoding is selected for
reliable output through this path; hardware-decoded 4K performance is not
claimed. You can explicitly test a different decoder via VLC arguments.
VLC's dbus plugin remains available for desktop media integration, but
physical media keys, audio output and suspend behavior have not been
manually verified on every Omarchy hardware configuration.

The initial window is half the active monitor's usable width and half its
usable height (one quarter of its area). On a 1920×1080 Omarchy monitor with
30 pixels reserved for the bar, that is 960×525. Standard controls resize
as a composition down to 820×360. Smaller monitors automatically use Compact
controls, with a 656×288 minimum. --standard or --compact overrides the
control size, while the initial window still follows the active monitor.

Drag the visible lower-right grip, the right edge or the bottom edge to
resize. FULL enters real window fullscreen even when no video is playing;
BACK or Escape restores the window. F keeps VLC's standard video-only
fullscreen behavior. The small X11 adapter covers only this player's FULL
and SUBS keys; the original bitmap controls still supply their feedback.
It listens only to this process's windows. No Hyprland settings are changed.

BUILD / EDIT

Requires Python 3, Pillow, Chromium and xmllint. No network is needed once
these tools are installed; the original control source and font are local.

  python source/build.py
  python source/make_compact.py
  python source/verify.py

build.py renders the original HTML/CSS into transparent PNGs, creates VLC
bindings and packages .vlt archives. make_compact.py scales all components
uniformly to 80%. verify.py validates XML against VLC's official DTD,
checks references and packaged files, unique IDs and dial frame geometry.
See VALIDATION.txt for the actual runtime checks and their limits.

SOURCES / NOTICES

User-supplied design library:
  https://uiux-nonhumanintelligence.web.app/UIUX
  Snapshots: source/reference/atlas.html and controls.css
  Retrieved 5 November 2026; original UI design ownership is unchanged.

VLC API and format:
  https://github.com/videolan/vlc
  source/reference/skin.dtd is the official VLC 3.0.21 Skins2 definition.
  https://www.videolan.org/vlc/skins2-create.html

IBM Plex Mono is bundled under the SIL Open Font License.
  See source/IBM-Plex-OFL.txt.

Arch package:
  https://archlinux.org/packages/extra/x86_64/vlc-gui-skins2/

REMOVE LAUNCHER INSTALLATION

Remove only ~/.local/share/enochian-vlc and
~/.local/share/applications/enochian-vlc.desktop (adjust for XDG_DATA_HOME).
Stock VLC and Omarchy are independent of this bundle.
