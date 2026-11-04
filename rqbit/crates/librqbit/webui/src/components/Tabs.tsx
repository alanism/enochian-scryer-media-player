import React from "react";

export interface TabButtonProps {
  id: string;
  label: string;
  active: boolean;
  onClick: () => void;
}

export const TabButton: React.FC<TabButtonProps> = ({
  label,
  active,
  onClick,
}) => (
  <button onClick={onClick} aria-pressed={active} className="sq-btn en-tab">
    {label}
  </button>
);

export interface TabListProps {
  children: React.ReactNode;
  className?: string;
}

export const TabList: React.FC<TabListProps> = ({ children, className }) => (
  <div className={`en-tabs flex border-b border-divider ${className ?? ""}`}>
    {children}
  </div>
);
