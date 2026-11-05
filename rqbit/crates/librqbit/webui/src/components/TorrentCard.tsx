import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { TorrentListItem } from "../api-types";
import {
  desktopBridgeAvailable,
  playInVLC,
  showTorrentFile,
} from "../enochian/desktopBridge";
import { TorrentCardContent } from "./TorrentCardContent";

const interactiveTarget = (target: EventTarget | null) =>
  target instanceof Element &&
  !!target.closest(
    "button,a,input,select,textarea,[role=button],[role=menuitem]",
  );

export const TorrentCard: React.FC<{
  torrent: TorrentListItem;
  hidden?: boolean;
}> = ({ torrent, hidden }) => {
  const desktop = desktopBridgeAvailable();
  const completed = !!torrent.stats?.finished && !torrent.stats?.error;
  const card = useRef<HTMLElement>(null);
  const menu = useRef<HTMLDivElement>(null);
  const menuItem = useRef<HTMLButtonElement>(null);
  const busy = useRef(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [position, setPosition] = useState<{ x: number; y: number } | null>(
    null,
  );

  useEffect(() => {
    if (!position) return;
    menuItem.current?.focus();
    const dismiss = () => setPosition(null);
    const outside = (event: PointerEvent) => {
      if (!menu.current?.contains(event.target as Node)) dismiss();
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        dismiss();
        card.current?.focus();
      } else if (event.key === "Tab") dismiss();
    };
    document.addEventListener("pointerdown", outside, true);
    document.addEventListener("keydown", escape);
    document.addEventListener("scroll", dismiss, true);
    window.addEventListener("resize", dismiss);
    return () => {
      document.removeEventListener("pointerdown", outside, true);
      document.removeEventListener("keydown", escape);
      document.removeEventListener("scroll", dismiss, true);
      window.removeEventListener("resize", dismiss);
    };
  }, [position]);

  const run = async (action: () => Promise<void>, message: string) => {
    if (busy.current) return;
    busy.current = true;
    setError("");
    setFeedback(message);
    setPosition(null);
    try {
      await action();
      setFeedback(
        message === "Opening Enochian VLC…"
          ? "Opened in Enochian VLC"
          : "File shown in file manager",
      );
    } catch (e) {
      setFeedback("");
      setError(e instanceof Error ? e.message : "Desktop action failed");
    } finally {
      busy.current = false;
    }
  };

  const showMenu = (x: number, y: number) =>
    setPosition({
      x: Math.max(8, Math.min(x, window.innerWidth - 192)),
      y: Math.max(8, Math.min(y, window.innerHeight - 68)),
    });

  return (
    <article
      ref={card}
      aria-label={torrent.name ?? `Torrent ${torrent.id}`}
      className={hidden ? "hidden" : "en-torrent-card"}
      tabIndex={desktop ? 0 : undefined}
      title={
        desktop && completed
          ? "Double-click to open in Enochian VLC"
          : undefined
      }
      onDoubleClick={(event) => {
        if (desktop && completed && !interactiveTarget(event.target)) {
          event.preventDefault();
          void run(
            () => playInVLC(torrent.id, undefined, true),
            "Opening Enochian VLC…",
          );
        }
      }}
      onContextMenu={(event) => {
        if (!desktop || interactiveTarget(event.target)) return;
        event.preventDefault();
        showMenu(event.clientX, event.clientY);
      }}
      onKeyDown={(event) => {
        if (!desktop || event.target !== event.currentTarget) return;
        if (
          event.key === "ContextMenu" ||
          (event.shiftKey && event.key === "F10")
        ) {
          event.preventDefault();
          const bounds = event.currentTarget.getBoundingClientRect();
          showMenu(bounds.left + 16, bounds.top + 16);
        } else if (event.key === "Enter" && completed && !event.repeat) {
          event.preventDefault();
          void run(
            () => playInVLC(torrent.id, undefined, true),
            "Opening Enochian VLC…",
          );
        }
      }}
    >
      <TorrentCardContent torrent={torrent} />
      {feedback && (
        <p role="status" className="en-card-feedback">
          {feedback}
        </p>
      )}
      {error && (
        <p role="alert" className="en-card-error">
          {error}
        </p>
      )}
      {position &&
        createPortal(
          <div
            ref={menu}
            role="menu"
            aria-label="Torrent actions"
            className="en-torrent-menu"
            style={{ left: position.x, top: position.y }}
          >
            <button
              ref={menuItem}
              type="button"
              role="menuitem"
              className="en-button sq-btn"
              aria-label="Show file"
              onClick={() => {
                card.current?.focus();
                void run(() => showTorrentFile(torrent.id), "Showing file…");
              }}
              onKeyDown={(event) => {
                if (
                  ["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)
                ) {
                  event.preventDefault();
                  menuItem.current?.focus();
                }
              }}
            >
              Show file
            </button>
          </div>,
          document.body,
        )}
    </article>
  );
};
