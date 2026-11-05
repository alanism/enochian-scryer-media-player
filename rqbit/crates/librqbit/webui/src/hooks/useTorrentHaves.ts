import { useContext, useEffect, useState } from "react";
import { APIContext } from "../context";
import { customSetInterval } from "../helper/customSetInterval";
import type { TorrentStats } from "../api-types";

export function useTorrentHaves(
  torrentId: number | undefined,
  totalPieces: number,
  stats: TorrentStats | null,
) {
  const API = useContext(APIContext);
  const [result, setResult] = useState<{
    id: number;
    total: number;
    bitmap: Uint8Array | null;
  } | null>(null);
  const state = stats?.state;
  const finished = stats?.finished;
  const selectedBytes = stats?.total_bytes;

  useEffect(() => {
    if (torrentId === undefined || totalPieces <= 0) return;
    let cancelled = false;
    const stop = customSetInterval(async () => {
      try {
        const bitmap = await API.getTorrentHaves(torrentId);
        if (!cancelled)
          setResult({ id: torrentId, total: totalPieces, bitmap });
      } catch {
        if (!cancelled)
          setResult({ id: torrentId, total: totalPieces, bitmap: null });
      }
      return (state === "live" || state === "initializing") && !finished
        ? 2000
        : 30000;
    }, 0);
    return () => {
      cancelled = true;
      stop();
    };
  }, [API, torrentId, totalPieces, state, finished, selectedBytes]);

  return result && result.id === torrentId && result.total === totalPieces
    ? result.bitmap
    : null;
}
