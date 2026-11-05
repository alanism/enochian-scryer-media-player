// Modal.tsx
import React, { type ReactNode, useId } from "react";
import RestartModal from "@restart/ui/Modal";

interface ModalProps {
  isOpen: boolean;
  onClose?: () => void;
  title: string;
  children: ReactNode;
  className?: string;
}

const ModalHeader: React.FC<{
  onClose?: () => void;
  title: string;
  titleId: string;
}> = ({ onClose, title, titleId }) => {
  return (
    <div className="flex p-3 justify-between items-center border-b border-divider gap-2">
      <h2 id={titleId} className="text-xl font-semibold truncate min-w-0">
        {title}
      </h2>
      {onClose && (
        <button
          className="sq-btn en-modal-close"
          onClick={onClose}
          aria-label="Close modal"
        >
          Close
        </button>
      )}
    </div>
  );
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  className,
}) => {
  const titleId = useId();
  const renderBackdrop = () => {
    return (
      <div className="fixed inset-0 bg-black/30 z-300 dark:bg-black/60 backdrop-blur"></div>
    );
  };
  return (
    <RestartModal
      show={isOpen}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      onHide={onClose}
      onClick={(event: React.MouseEvent<HTMLDivElement>) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
      onKeyDown={(event: React.KeyboardEvent<HTMLDivElement>) => {
        if (event.key !== "Tab") return;
        const dialog = event.currentTarget;
        const controls = Array.from(
          dialog.querySelectorAll<HTMLElement>(
            'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [tabindex]:not([tabindex="-1"])',
          ),
        ).filter(
          (control) =>
            control.getClientRects().length > 0 && control.tabIndex >= 0,
        );
        const first = controls[0];
        const last = controls[controls.length - 1];
        const active = document.activeElement;
        if (!first) {
          event.preventDefault();
          dialog.focus();
        } else if (event.shiftKey && (active === first || active === dialog)) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && active === last) {
          event.preventDefault();
          first.focus();
        }
      }}
      renderBackdrop={renderBackdrop}
      className="fixed z-301 top-0 left-0 w-full h-full block overflow-x-hidden overflow-y-auto"
    >
      <div
        className={`bg-surface-raised shadow-lg my-4 mx-4 sm:my-8 sm:mx-auto sm:max-w-2xl rounded ${className}`}
      >
        <ModalHeader onClose={onClose} title={title} titleId={titleId} />
        {children}
      </div>
    </RestartModal>
  );
};
