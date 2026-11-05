import { useContext, useRef, useState } from "react";
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
  const actionsRef = useRef<HTMLDivElement>(null);

  const restoreActionFocus = () => {
    if (document.activeElement === document.body) {
      actionsRef.current?.querySelector<HTMLButtonElement>("button")?.focus();
    }
  };

  const refreshTorrents = useTorrentStore((state) => state.refreshTorrents);
  const openDetailsModal = useUIStore((state) => state.openDetailsModal);

  const canPause = state == "live";
  const canUnpause = state == "paused" || state == "error";
  const canConfigure = state == "paused" || state == "live";

  const setCloseableError = useErrorStore((state) => state.setCloseableError);

  const API = useContext(APIContext);

  const unpause = () => {
    const hadFocus = actionsRef.current?.contains(document.activeElement);
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
      .finally(() => {
        setDisabled(false);
        if (hadFocus) requestAnimationFrame(restoreActionFocus);
      });
  };

  const pause = () => {
    const hadFocus = actionsRef.current?.contains(document.activeElement);
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
      .finally(() => {
        setDisabled(false);
        if (hadFocus) requestAnimationFrame(restoreActionFocus);
      });
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
      ref={actionsRef}
      className="en-transfer-actions"
      role="group"
      aria-label="Transfer controls"
      data-enochian-finish
      data-finish={document.documentElement.dataset.finish}
    >
      {(canUnpause || canPause) && (
        <Button onClick={canUnpause ? unpause : pause} disabled={disabled}>
          {canUnpause ? "Resume transfer" : "Pause transfer"}
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
