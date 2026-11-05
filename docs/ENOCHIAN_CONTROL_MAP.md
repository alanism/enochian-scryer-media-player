# Enochian controls → media functions

These are this project's design decisions after applying the council cards,
not endorsements or reviews by the named people. The user's existing elements
are the visual source of truth: [Enochian Elements](https://uiux-nonhumanintelligence.web.app/UIUX).

| Feature | Existing element | Function and state |
| --- | --- | --- |
| VLC play, pause, stop, previous and next | Tape Deck **05.07**, original transport keys | Familiar media transport; persistent playing/paused state keeps its key down and its lamp on. REW/FF artwork maps to previous/next playlist item and tooltips name that action. |
| Rqbit “Play in VLC” | Tape Deck **05.07**, original play key | A visible media handoff. The key is momentary because rqbit does not know VLC's ongoing playback state. Completed media opens from disk; incomplete media uses the existing stream action. |
| Pause/resume transfers; files; removal; copy playlist; Show file | Drum Machine **01.09**, original `sq-btn` utility caps | Labeled commands, separate from media playback. They retain their press travel and shadow. Removal still opens the existing confirmation. |
| Finish and Cards/List choice | Drum Machine **01.09**, original latched `sq-btn` state | Both choices stay visible; the active cap uses the original selected state. Layout choice is remembered. No new switch artwork is introduced. |
| Read-only download progress | LED Level Meter **06.03**, original 20-segment ladder | Reports actual byte completion with an exact numeric percentage. It is a progress indicator, not a draggable slider. Errors do not force it to 100%. |
| VLC volume | Rotary Knob **00.01**, original bar marker | A continuous scalar, with actual volume value and mute action. Existing 101-frame artwork and VLC angle mapping remain unchanged. |
| VLC seek and equalizer | Slider **03.04**, original ribbed grip | Continuous position and band gain. Seek exposes time/duration; EQ exposes frequency and gain. |

## Why these choices

The Tape Deck supplies an entire compatible media transport family and its
state language. Radio power, timer start, drum pattern play and the turntable's
motor control carry different meanings; borrowing their play icons would make
one suite use several visual vocabularies for the same action.

Transfer pause is a network task, so it uses a named utility key rather than
the same transport key as playback. Both states can be controlled independently.
A completed paused torrent can play without restarting its transfer.

The Segment Selector **03.03** is a suitable alternative when a larger set of
ordered choices needs one moving marker. Two named utility caps were retained
for the binary finish and layout choices to reuse the suite's existing toolbar
family. Knobs, faders and switch banks are not used for arbitrary commands or
simulated speeds. Advanced settings and logs remain accessible behind their
existing utility keys.

## Fidelity checks

The copied `library.css` and all four VLC skin archives are unchanged by this
review. In the live Ivory atlas and revised app, the Tape Deck gradient and
shadow matched exactly; the utility cap's white surface, 5px corners and shadow
also matched. Both finished app views were inspected at 1280×720. Card/header
controls measured at least 44px in both dimensions. No new control artwork was
drawn.
