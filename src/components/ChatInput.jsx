import { useRef, useState } from "react";

export default function ChatInput({ onSend, onSendFiles, conversationId, userId }) {
  const [input, setInput] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  const handleFileSelect = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append("conversation_id", conversationId);
    formData.append("user_id", userId);
    formData.append("content", input);

    for (let file of files) {
      formData.append("files", file);
    }

    await onSendFiles(formData);

    event.target.value = "";
    // setInput("");
  };

  return (
    <div className="flex m-auto mt-2 w-full max-w-4xl min-w-0 rounded bg-diff white-text">
      <button
        className="flex p-2 px-4 highlight text-xl rounded hover:cursor-pointer item-center"
        onClick={() => fileInputRef.current.click()}
      >
      {/* <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="white-text h-"> <path strokeLinecap="round" strokeLinejoin="round" d="m18.375 12.739-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.552 18.32m.009-.01-.01.01m5.699-9.941-7.81 7.81a1.5 1.5 0 0 0 2.112 2.13" /> </svg> */}
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

      <button onClick={handleSubmit} className="p-2 px-4 text-2xl white-text highlight">
        ↑
      </button>
    </div>
  );
}
