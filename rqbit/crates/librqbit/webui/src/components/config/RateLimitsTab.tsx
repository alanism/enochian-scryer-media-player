import React from "react";
import { Fieldset } from "../forms/Fieldset";
import { FormInput } from "../forms/FormInput";

export interface RateLimitsTabProps {
  downloadBps: number | null | undefined;
  uploadBps: number | null | undefined;
  onDownloadBpsChange: (value: number | null) => void;
  onUploadBpsChange: (value: number | null) => void;
}

export const RateLimitsTab: React.FC<RateLimitsTabProps> = ({
  downloadBps,
  uploadBps,
  onDownloadBpsChange,
  onUploadBpsChange,
}) => {
  return (
    <Fieldset>
      <FormInput
        label="Download limit (MB/s)"
        name="download_bps"
        inputType="number"
        min={0}
        step="any"
        value={downloadBps ? String(downloadBps / 1_000_000) : ""}
        placeholder="Unlimited"
        onChange={(e) => {
          const val = e.target.valueAsNumber;
          onDownloadBpsChange(
            !Number.isFinite(val) || val <= 0
              ? null
              : Math.round(val * 1_000_000),
          );
        }}
        help="Leave blank for unlimited download speed."
      />
      <FormInput
        label="Upload limit (MB/s)"
        name="upload_bps"
        inputType="number"
        min={0}
        step="any"
        value={uploadBps ? String(uploadBps / 1_000_000) : ""}
        placeholder="Unlimited"
        onChange={(e) => {
          const val = e.target.valueAsNumber;
          onUploadBpsChange(
            !Number.isFinite(val) || val <= 0
              ? null
              : Math.round(val * 1_000_000),
          );
        }}
        help="Leave blank for unlimited upload speed."
      />
    </Fieldset>
  );
};
