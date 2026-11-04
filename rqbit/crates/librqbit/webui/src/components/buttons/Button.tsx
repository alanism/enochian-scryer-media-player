import { ReactNode } from "react";
export const Button: React.FC<{
  onClick: () => void;
  variant?: "cancel" | "primary" | "secondary" | "danger" | "none";
  size?: "sm" | "default";
  className?: string;
  disabled?: boolean;
  children: ReactNode;
}> = ({ onClick, children, className, disabled, variant }) => (
  <button
    type="button"
    disabled={disabled}
    data-variant={variant}
    onClick={(e) => {
      e.preventDefault();
      onClick();
    }}
    className={`sq-btn en-button ${className ?? ""}`}
  >
    {children}
  </button>
);
