import { FileInput } from "./buttons/FileInput";
import { MagnetInput } from "./buttons/MagnetInput";
export const Header = ({
  version,
  settingsSlot,
}: {
  title: string;
  version: string;
  settingsSlot?: React.ReactNode;
}) => (
  <header className="en-header">
    <div className="en-brand">
      <h1>
        ENOCHIAN <span>RQBIT</span>
      </h1>
      <span className="en-version">
        {version ? `v${version}` : "Connecting…"}
      </span>
    </div>
    <div className="en-header-controls">
      <MagnetInput />
      <FileInput />
      {settingsSlot}
    </div>
  </header>
);
