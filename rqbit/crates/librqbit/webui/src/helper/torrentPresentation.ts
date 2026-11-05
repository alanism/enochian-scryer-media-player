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

export function pieceCount(stats: TorrentStats, total: number): string {
  if (stats.finished)
    return `${total.toLocaleString()}/${total.toLocaleString()}`;
  // A per-session network-download counter is not the on-disk piece inventory.
  return `—/${total.toLocaleString()}`;
}
