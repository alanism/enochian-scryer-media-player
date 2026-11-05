import { RefObject, useRef, useState } from "react";
import { UploadButton } from "./UploadButton";
import { CgFileAdd } from "react-icons/cg";

export const FileInput = ({ className }: { className?: string }) => {
  const inputRef = useRef<HTMLInputElement>(
    null,
  ) as RefObject<HTMLInputElement>;
  const [file, setFile] = useState<File | null>(null);
  const [remaining, setRemaining] = useState<File[]>([]);

  const onFileChange = async () => {
    if (!inputRef?.current?.files) {
      return;
    }
    const files = Array.from(inputRef.current.files);
    setFile(files[0] ?? null);
    setRemaining(files.slice(1));
  };

  const reset = (completed?: boolean) => {
    if (!inputRef?.current) {
      return;
    }
    inputRef.current.value = "";
    if (completed && remaining.length) {
      setFile(remaining[0]);
      setRemaining(remaining.slice(1));
    } else {
      setFile(null);
      setRemaining([]);
    }
  };

  const onClick = () => {
    if (!inputRef?.current) {
      return;
    }
    inputRef.current.click();
  };

  return (
    <>
      <input
        type="file"
        ref={inputRef}
        multiple={true}
        accept=".torrent"
        onChange={onFileChange}
        hidden
      />
      <UploadButton
        onClick={onClick}
        data={file}
        resetData={reset}
        className={`group ${className}`}
      >
        <CgFileAdd className="text-blue-500 group-hover:text-white dark:text-white" />
        <div>ADD FILE</div>
      </UploadButton>
    </>
  );
};
