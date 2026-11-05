import { useContext, useState } from "react";
import { TorrentListItem, TorrentStats } from "../../api-types";
import { APIContext } from "../../context";
import { Button } from "./Button";
import { DeleteTorrentModal } from "../modal/DeleteTorrentModal";
import { useErrorStore } from "../../stores/errorStore";
import { useTorrentStore } from "../../stores/torrentStore";
import { useUIStore } from "../../stores/uiStore";
import { PlaylistCopyButton } from "./PlaylistButton";

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
      className="en-transfer-actions"
      role="group"
      aria-label="Transfer controls"
      data-enochian-finish
      data-finish={document.documentElement.dataset.finish}
    >
      {canUnpause && (
        <Button onClick={unpause} disabled={disabled}>
          Resume transfer
        </Button>
      )}
      {canPause && (
        <Button onClick={pause} disabled={disabled}>
          Pause transfer
        </Button>
      )}
      {canConfigure && (
        <Button onClick={() => openDetailsModal(id)} disabled={disabled}>
          Files &amp; details
        </Button>
      )}
      <Button onClick={startDeleting} disabled={disabled} variant="danger">
        Remove torrent
      </Button>
      <PlaylistCopyButton torrentId={id} disabled={disabled} />
      <DeleteTorrentModal
        show={deleting}
        onHide={cancelDeleting}
        torrents={[{ id, name }]}
      />
    </div>
  );
};
