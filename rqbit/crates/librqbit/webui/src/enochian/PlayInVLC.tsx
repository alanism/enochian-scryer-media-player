import { useState } from "react";
import { TapeKey } from "./TapeKey";
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
  if (!document.querySelector('meta[name="enochian-bridge"]')) return null;
  const play = async () => {
    setBusy(true);
    setError("");
    try {
      const r = await fetch("/enochian/play", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          torrent_id: torrentId,
          file_id: fileId,
          finish: document.documentElement.dataset.finish,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error ?? "Could not open Enochian VLC");
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
