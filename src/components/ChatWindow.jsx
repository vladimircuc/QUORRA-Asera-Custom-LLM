
import { useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'How can I help you today?' },
  ]);

  const handleSend = (input) => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', content: input }]);
  };

  return (
    <main className="flex-1 flex flex-col bg-[#1A1D23] text-white">
      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-6 m-auto space-y-4 text-center">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} role={msg.role} content={msg.content} />
        ))}
      </div>

      {/* Input Bar */}
      <ChatInput onSend={handleSend} />
    </main>
  );
}