ENOCHIAN VLC — OMARCHY EDITION

An actual VLC 3 Linux skin pack, with Obsidian and Ivory finishes.
Uses VLC's own Skins2 interface and playback engine. No browser wrapper,
custom media engine, VLC source rebuild, or replacement desktop theme.

START ON OMARCHY

1. Install the official Arch packages if missing:
   sudo pacman -S vlc vlc-gui-skins2 vlc-plugin-ffmpeg xorg-xwayland

2. From this folder run:
   ./enochian-vlc

   Ivory finish:
   ./enochian-vlc --ivory

   Smaller window for a split-screen tile (832 x 650):
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
  Turn around the dial with the pointer; M mutes.

Seek and equalizer: Enochian Slider 01 (03.04), original ribbed cap.
  Seek by clicking or dragging along the line. EQ caps are uniformly
  reduced and rotated. These are live VLC sliders, not decorative images.

Utility keys: the Enochian Drum Machine's existing sq-btn component.
  Labels adapted to OPEN, PLAYLIST, EQ, MENU, FULL, CLOSE and other actions.

Finish colors are the atlas's existing Ivory and Obsidian definitions.
Control geometry was not redrawn. The surrounding player layout composes
these existing components. Source snapshots and the renderer are included.

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

Normal size: 1040 x 812 minimum. Compact: 832 x 650 minimum.
Use Omarchy's usual window move/resize actions; video expands with the
window while the controls retain their sizes. The skin does not install
window rules or force floating mode. For a narrower tile, use Compact.

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
