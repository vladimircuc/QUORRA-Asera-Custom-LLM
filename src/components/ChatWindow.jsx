
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
    <main className="flex-1 flex flex-col bg-gray-800 text-white">
      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} role={msg.role} content={msg.content} />
        ))}
      </div>

      {/* Input Bar */}
      <ChatInput onSend={handleSend} />
    </main>
  );
}