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
    toggleViewMode = useUIStore((s) => s.toggleViewMode);
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
      <button
        className="sq-btn"
        onClick={() => {
          DarkMode.toggle();
          setIsDark(DarkMode.isDark());
        }}
        title="Change finish"
      >
        {isDark ? "IVORY" : "OBSIDIAN"}
      </button>
      <button
        className="sq-btn"
        onClick={toggleViewMode}
        title="Change list layout"
      >
        {viewMode === "compact" ? "CARDS" : "LIST"}
      </button>
      <ConfigModal isOpen={configOpen} onClose={() => setConfigOpen(false)} />
    </div>
  );
};
