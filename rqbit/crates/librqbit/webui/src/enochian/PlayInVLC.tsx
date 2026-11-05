import { useState } from "react";
import { TapeKey } from "./TapeKey";
import { desktopBridgeAvailable, playInVLC } from "./desktopBridge";
export function PlayInVLC({
  torrentId,
  fileId,
  disabled,
}: {
  torrentId: number;
  fileId?: number;
  disabled?: boolean;
}) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  // This capability is injected only by our local desktop bridge.
  if (!desktopBridgeAvailable()) return null;
  const play = async () => {
    setBusy(true);
    setError("");
    try {
      await playInVLC(torrentId, fileId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Playback failed");
    } finally {
      setBusy(false);
    }
  };
  return (
    <div
      className="en-vlc-action tp"
      data-enochian-finish
      data-finish={document.documentElement.dataset.finish}
    >
      <TapeKey
        kind="play"
        label={busy ? "OPENING" : "PLAY IN VLC"}
        onClick={play}
        disabled={disabled || busy}
      />
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
