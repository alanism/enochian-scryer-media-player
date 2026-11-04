import { ReactNode } from "react";
export const IconButton: React.FC<{
  onClick: () => void;
  disabled?: boolean;
  className?: string;
  color?: string;
  children: ReactNode;
  href?: string;
  title?: string;
}> = ({ onClick, disabled, children, title, className }) => (
  <button
    type="button"
    className={`sq-btn en-icon ${className ?? ""}`}
    disabled={disabled}
    title={title}
    aria-label={title}
    onClick={(e) => {
      e.stopPropagation();
      e.preventDefault();
      onClick();
    }}
  >
    {children}
  </button>
);
