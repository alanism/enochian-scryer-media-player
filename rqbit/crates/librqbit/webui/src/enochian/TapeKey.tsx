import { CSSProperties } from "react";

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
  return (
    <button
      type="button"
      className="tp-key"
      title={label}
      aria-label={label}
      data-down={active ? "true" : "false"}
      aria-pressed={!!active}
      disabled={disabled}
      onClick={onClick}
    >
      <span
        className={`tp-led ${active ? "on" : ""}`}
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
