import { useState } from 'react';

export default function ChatInput({ onSend }) {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  return (
      <div className="flex gap-2 m-auto pt-2 w-full max-w-4xl">
        <input
          type="text"
          className="flex-1 min-w-0 p-3 rounded bg-diff white-text placeholder-gray-400 outline-none"
          placeholder="Send a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <button
          onClick={handleSubmit}
          className="bg-accent hover:bg-[#3AB3FF] text-white px-6 sm:px-11 py-3 rounded shrink-0"
        >
          Send
        </button>
      </div>
  );
}