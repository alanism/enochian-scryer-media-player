import { ReactNode, useContext, useEffect, useState } from "react";
import {
  AddTorrentResponse,
  ErrorDetails as ApiErrorDetails,
} from "../../api-types";
import { APIContext } from "../../context";
import { ErrorWithLabel } from "../../rqbit-web";
import { FileSelectionModal } from "../modal/FileSelectionModal";
import { Button } from "./Button";

export const UploadButton: React.FC<{
  onClick: () => void;
  data: string | File | null;
  resetData: (completed?: boolean) => void;
  children: ReactNode;
  className?: string;
}> = ({ onClick, data, resetData, children, className }) => {
  const [loading, setLoading] = useState(false);
  const [listTorrentResponse, setListTorrentResponse] =
    useState<AddTorrentResponse | null>(null);
  const [listTorrentError, setListTorrentError] =
    useState<ErrorWithLabel | null>(null);
  const API = useContext(APIContext);

  // Get the torrent file list if there's data.
  useEffect(() => {
    if (data === null) {
      return;
    }

    let cancelled = false;
    let t = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await API.uploadTorrent(data, { list_only: true });
        if (!cancelled) setListTorrentResponse(response);
      } catch (e) {
        if (!cancelled)
          setListTorrentError({
            text: "Error listing torrent files",
            details: e as ApiErrorDetails,
          });
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 0);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [data]);

  const clear = (completed?: boolean) => {
    resetData(completed);
    setListTorrentError(null);
    setListTorrentResponse(null);
    setLoading(false);
  };

  return (
    <>
      <Button onClick={onClick} className={className}>
        {children}
      </Button>

      {data && (
        <FileSelectionModal
          onHide={clear}
          listTorrentError={listTorrentError}
          listTorrentResponse={listTorrentResponse}
          data={data}
          listTorrentLoading={loading}
        />
      )}
    </>
  );
};
