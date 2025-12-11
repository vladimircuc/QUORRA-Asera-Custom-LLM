import { useRef, useState } from "react";

export default function ChatInput({ onSend }) {
  const [input, setInput] = useState('');
  const [pendingFiles, setPendingFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const newFiles = [...e.target.files];
    setPendingFiles(prev => [...prev, ...newFiles]);

     e.target.value = null;
  };

  const removeFile = (index) => {
    setPendingFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    const hasText = input.trim().length > 0;
    const hasFiles = pendingFiles.length > 0;
    if (!hasText && !hasFiles) return;

    onSend(input, pendingFiles);
    setInput("");
    setPendingFiles([]);
  };

  return (
    <div className="flex flex-col w-full">

      {/* FILE PREVIEW */}
      {pendingFiles.length > 0 && (
        <div className="flex relative m-auto w-full max-w-4xl min-w-0 gap-2 wrap rounded white-text">
          {pendingFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-[#3AB3FF] px-2 py-1 rounded text-sm"
            >
              <span className="truncate max-w-40">{file.name}</span>
              <span className="opacity-70 text-xs">
                ({Math.round(file.size / 1024)} KB)
              </span>

              <button
                onClick={() => removeFile(index)}
                className="text-white hover:text-red-500 font-bold"
              >
                X
              </button>
            </div>
          ))}
        </div>
      )}

      {/* INPUT BAR */}
      <div className="flex m-auto w-full max-w-4xl min-w-0 rounded bg-diff white-text mt-2">
        <button
          className="flex p-2 px-4 highlight text-xl rounded hover:cursor-pointer"
          onClick={() => fileInputRef.current.click()}
        >
          +
        </button>

        <input
          type="file"
          ref={fileInputRef}
          multiple
          style={{ display: "none" }}
          onChange={handleFileSelect}
        />

        <input
          type="text"
          className="flex-1 pl-4 focus:outline-none"
          placeholder="Send a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />

        <button
          onClick={handleSubmit}
          className="p-2 px-4 text-2xl white-text highlight rounded"
        >
          ↑
        </button>
      </div>

    </div>
  );
}
