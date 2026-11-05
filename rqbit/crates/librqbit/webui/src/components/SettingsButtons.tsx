import { JSX, useState } from "react";
import { DarkMode } from "../helper/darkMode";
import { ConfigModal } from "./config/ConfigModal";
import { useUIStore } from "../stores/uiStore";
export const SettingsButtons: React.FC<{
  onLogsClick: () => void;
  menuButtons?: JSX.Element[];
}> = ({ onLogsClick, menuButtons }) => {
  const [isDark, setIsDark] = useState(DarkMode.isDark());
  const [configOpen, setConfigOpen] = useState(false);
  const viewMode = useUIStore((s) => s.viewMode),
    setViewMode = useUIStore((s) => s.setViewMode);
  return (
    <div className="en-settings">
      {menuButtons?.map((b, i) => (
        <span key={i}>{b}</span>
      ))}
      {!menuButtons?.length && (
        <button
          className="sq-btn"
          onClick={() => setConfigOpen(true)}
          title="Settings"
        >
          SETUP
        </button>
      )}
      <button className="sq-btn" onClick={onLogsClick} title="View logs">
        LOGS
      </button>
      <div role="group" aria-label="Finish" className="en-choice-group">
        {([false, true] as const).map((dark) => (
          <button
            key={String(dark)}
            type="button"
            className="sq-btn"
            aria-pressed={isDark === dark}
            onClick={() => {
              if (isDark !== dark) DarkMode.toggle();
              setIsDark(DarkMode.isDark());
            }}
          >
            {dark ? "OBSIDIAN" : "IVORY"}
          </button>
        ))}
      </div>
      <div role="group" aria-label="View" className="en-choice-group">
        <button
          type="button"
          className="sq-btn"
          aria-pressed={viewMode === "full"}
          onClick={() => setViewMode("full")}
        >
          CARDS
        </button>
        <button
          type="button"
          className="sq-btn"
          aria-pressed={viewMode === "compact"}
          onClick={() => setViewMode("compact")}
        >
          LIST
        </button>
      </div>
      <ConfigModal isOpen={configOpen} onClose={() => setConfigOpen(false)} />
    </div>
  );
};
