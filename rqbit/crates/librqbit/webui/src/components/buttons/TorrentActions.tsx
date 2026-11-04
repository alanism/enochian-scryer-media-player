import { TapeKey } from "../../enochian/TapeKey";
import { useContext, useState } from "react";
import { TorrentListItem, TorrentStats } from "../../api-types";
import { APIContext } from "../../context";
import { IconButton } from "./IconButton";
import { DeleteTorrentModal } from "../modal/DeleteTorrentModal";
import { FaCog, FaPause, FaPlay, FaTrash } from "react-icons/fa";
import { useErrorStore } from "../../stores/errorStore";
import { useTorrentStore } from "../../stores/torrentStore";
import { useUIStore } from "../../stores/uiStore";
import { PlaylistIconButton } from "./PlaylistButton";

export const TorrentActions: React.FC<{
  torrent: TorrentListItem & { stats: TorrentStats };
}> = ({ torrent }) => {
  const { id, name, stats } = torrent;
  const state = stats.state;

  let [disabled, setDisabled] = useState<boolean>(false);
  let [deleting, setDeleting] = useState<boolean>(false);

  const refreshTorrents = useTorrentStore((state) => state.refreshTorrents);
  const openDetailsModal = useUIStore((state) => state.openDetailsModal);

  const canPause = state == "live";
  const canUnpause = state == "paused" || state == "error";
  const canConfigure = state == "paused" || state == "live";

  const setCloseableError = useErrorStore((state) => state.setCloseableError);

  const API = useContext(APIContext);

  const unpause = () => {
    setDisabled(true);
    API.start(id)
      .then(
        () => {
          refreshTorrents();
        },
        (e) => {
          setCloseableError({
            text: `Error starting torrent id=${id}`,
            details: e,
          });
        },
      )
      .finally(() => setDisabled(false));
  };

  const pause = () => {
    setDisabled(true);
    API.pause(id)
      .then(
        () => {
          refreshTorrents();
        },
        (e) => {
          setCloseableError({
            text: `Error pausing torrent id=${id}`,
            details: e,
          });
        },
      )
      .finally(() => setDisabled(false));
  };

  const startDeleting = () => {
    setDisabled(true);
    setDeleting(true);
  };

  const cancelDeleting = () => {
    setDisabled(false);
    setDeleting(false);
  };

  return (
    <div
      className="en-row-actions tp flex w-full justify-center gap-1 sm:gap-2 dark:text-slate-300"
      data-enochian-finish
      data-finish={document.documentElement.dataset.finish}
    >
      {canUnpause && (
        <TapeKey
          kind="play"
          label="RESUME"
          onClick={unpause}
          disabled={disabled}
        />
      )}
      {canPause && (
        <TapeKey
          kind="pause"
          label="PAUSE"
          onClick={pause}
          disabled={disabled}
        />
      )}
      {canConfigure && (
        <IconButton
          onClick={() => openDetailsModal(id)}
          disabled={disabled}
          title="Files and details"
        >
          <FaCog className="hover:text-green-600" />
        </IconButton>
      )}
      <IconButton
        onClick={startDeleting}
        disabled={disabled}
        title="Remove torrent"
      >
        <FaTrash className="hover:text-red-500" />
      </IconButton>
      <PlaylistIconButton torrentId={id} disabled={disabled} />
      <DeleteTorrentModal
        show={deleting}
        onHide={cancelDeleting}
        torrents={[{ id, name }]}
      />
    </div>
  );
};
