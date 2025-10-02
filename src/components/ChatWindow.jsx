
import { useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'How can I help you today? fewf fwe fwe ewf  ewf we fw ef w e fw ef wef we fwe fw e ew wfe fwe f we f  ggggggggggggggggggggggggg' },
  ]);

  const handleSend = (input) => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', content: input }]);
  };

  return (
    <main className="flex flex-1 flex-col p-6 bg-main text-white">
      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4 flex flex-col">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} role={msg.role} content={msg.content} />
        ))}
      </div>

      {/* Input Bar */}
      <ChatInput onSend={handleSend}/>
    </main>
  );
}