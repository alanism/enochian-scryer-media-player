import { CSSProperties, useState } from "react";

export function TapeKey({
  kind,
  label,
  active,
  disabled,
  onClick,
}: {
  kind: "play" | "pause";
  label: string;
  active?: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  const [pressed, setPressed] = useState(false);
  const down = !!active || pressed;
  return (
    <button
      type="button"
      className="tp-key"
      title={label}
      aria-label={label}
      data-down={down ? "true" : "false"}
      aria-pressed={active === undefined ? undefined : !!active}
      disabled={disabled}
      onClick={onClick}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        setPressed(true);
      }}
      onPointerUp={() => setPressed(false)}
      onPointerCancel={() => setPressed(false)}
      onKeyDown={(e) => {
        if (e.key === " " || e.key === "Enter") setPressed(true);
      }}
      onKeyUp={() => setPressed(false)}
      onBlur={() => setPressed(false)}
    >
      <span
        className={`tp-led ${down ? "on" : ""}`}
        style={
          {
            "--lc": kind === "play" ? "var(--go)" : "var(--amber)",
          } as CSSProperties
        }
      />
      <svg viewBox="0 0 20 20" aria-hidden="true">
        {kind === "play" ? (
          <path d="M6 4v12l10-6z" />
        ) : (
          <>
            <rect x="5" y="4" width="3.5" height="12" rx="1" />
            <rect x="11.5" y="4" width="3.5" height="12" rx="1" />
          </>
        )}
      </svg>
      <span className="tp-name">{label}</span>
    </button>
  );
}
