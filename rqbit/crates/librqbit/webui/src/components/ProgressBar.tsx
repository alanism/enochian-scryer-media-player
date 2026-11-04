export const ProgressBar: React.FC<{
  now: number;
  label?: string | null;
  variant?: "warn" | "info" | "success" | "error";
  classNames?: string;
}> = ({ now, label, classNames }) => {
  const pct = Math.max(0, Math.min(100, Number.isFinite(now) ? now : 0));
  return (
    <div
      className={`en-progress ${classNames ?? ""}`}
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label ?? "Download progress"}
    >
      <span className="lad-segs" aria-hidden="true">
        {Array.from({ length: 20 }, (_, i) => (
          <i key={i} className={i < pct / 5 ? "on" : ""} />
        ))}
      </span>
      <span>{label ?? `${pct.toFixed(1)}%`}</span>
    </div>
  );
};
