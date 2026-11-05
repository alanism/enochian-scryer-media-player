import type { TorrentStats } from "../api-types";

export function torrentProgress(stats?: TorrentStats | null): number {
  if (!stats) return 0;
  if (stats.total_bytes <= 0) return stats.finished ? 100 : 0;
  const percent = (stats.progress_bytes / stats.total_bytes) * 100;
  return Number.isFinite(percent) ? Math.max(0, Math.min(100, percent)) : 0;
}

export function torrentStatus(stats?: TorrentStats | null): string {
  if (!stats) return "Loading";
  if (stats.error || stats.state === "error") return "Error";
  if (stats.state === "initializing") return "Checking files";
  if (stats.state === "paused")
    return stats.finished ? "Complete · paused" : "Paused";
  return stats.finished ? "Seeding" : "Downloading";
}

export function pieceCount(bitmap: Uint8Array | null, total: number): string {
  if (!Number.isSafeInteger(total) || total < 0) return "—";
  if (!bitmap || bitmap.length < Math.ceil(total / 8))
    return `—/${total.toLocaleString()}`;
  // The engine's MSB0 inventory includes on-disk pieces; selection completion
  // and per-session network counters cannot establish this count.
  let count = 0;
  for (let index = 0; index < Math.ceil(total / 8); index++) {
    const remaining = total - index * 8;
    let bits = bitmap[index] & (remaining < 8 ? 0xff << (8 - remaining) : 0xff);
    while (bits) {
      bits &= bits - 1;
      count++;
    }
  }
  return `${count.toLocaleString()}/${total.toLocaleString()}`;
}
