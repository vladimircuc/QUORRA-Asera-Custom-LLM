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
    <div className="p-4 bg-[#1A1D23]">
      <div className="flex items-center gap-2">
        <input
          type="text"
          className="flex-1 p-2 rounded bg-gray-700 text-white placeholder-gray-400 outline-none"
          placeholder="Send a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <button
          onClick={handleSubmit}
          className="bg-[#2581C4] hover:bg-[#3AB3FF] text-white px-4 py-2 rounded">
          Send
        </button>
      </div>
    </div>
  );
}