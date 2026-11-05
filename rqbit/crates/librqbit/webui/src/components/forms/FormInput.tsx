import { ChangeEventHandler } from "react";

export const FormInput: React.FC<{
  value: string;
  label?: string;
  autoFocus?: boolean;
  name: string;
  inputType?: string;
  min?: number;
  step?: number | string;
  onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>;
  placeholder?: string;
  help?: string;
  disabled?: boolean;
  onChange?: ChangeEventHandler<HTMLInputElement>;
}> = ({
  autoFocus,
  value,
  name,
  disabled,
  onChange,
  onKeyDown,
  label,
  help,
  inputType,
  min,
  step,
  placeholder,
}) => {
  return (
    <div className="flex flex-col gap-2 mb-2">
      <label htmlFor={name}>{label}</label>
      <input
        autoFocus={autoFocus}
        type={inputType}
        min={min}
        step={step}
        className="block border border-divider rounded bg-transparent py-1.5 pl-2 focus:ring-0 focus:border-primary sm:leading-6"
        id={name}
        name={name}
        aria-label={label || placeholder || name}
        aria-describedby={help ? `${name}-help` : undefined}
        disabled={disabled}
        placeholder={placeholder}
        value={value}
        onKeyDown={onKeyDown}
        onChange={onChange}
      />
      {help && (
        <div id={`${name}-help`} className="text-sm text-secondary">
          {help}
        </div>
      )}
    </div>
  );
};
