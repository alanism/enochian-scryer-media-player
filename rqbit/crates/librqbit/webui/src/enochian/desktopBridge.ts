export const desktopBridgeAvailable = () =>
  !!document.querySelector('meta[name="enochian-bridge"]');

async function desktopRequest(path: string, data: object) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error ?? "Desktop action failed");
}

export function playInVLC(
  torrentId: number,
  fileId?: number,
  completedOnly = false,
) {
  return desktopRequest("/enochian/play", {
    torrent_id: torrentId,
    file_id: fileId,
    finish: document.documentElement.dataset.finish,
    completed_only: completedOnly,
  });
}

export function showTorrentFile(torrentId: number) {
  return desktopRequest("/enochian/show-file", { torrent_id: torrentId });
}
