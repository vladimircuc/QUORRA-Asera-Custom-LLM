
import { useState, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatWindow({ selectedConversation }) {
  // const [messages, setMessages] = useState([
  //   { role: 'system', content: 'How can I help you today? fewf fwe fwe ewf  ewf we fw ef w e fw ef wef we fwe fw e ew wfe fwe f we f  ggggggggggggggggggggggggg' },
  // ]);
  const [messages, setMessages] = useState([]);


  useEffect (() => {
    if (!selectedConversation) return;

    console.log({selectedConversation});
    const fetchMessages = async () => {
      try {
      const response = await fetch(`http://127.0.0.1:8000/messages/${selectedConversation.id}`);
      const data = await response.json();
      console.log("Message", data);
      setMessages(Array.isArray(data.messages) ? data.messages : []);
      }catch (error) {
        console.error(error);
        setMessages([]);
      }
      };

    fetchMessages();
  },[selectedConversation]);

  const handleSend = (input) => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', content: input }]);
  };

  if (!selectedConversation){
    return <p className='bg-main flex-1 text-center pt-20 p-4 white-text'>Please select or create a conversation to view</p>
  }

  return (
    <main className="flex flex-1 flex-col p-6 bg-main text-white">
      {/* Message Feed */}
      <div className="h-142 overflow-y-auto p-4 space-y-4 flex flex-col">
        {messages.map((msg,index) => (
          <ChatMessage key={index} role={msg.role} content={msg.content} />
        ))}
      </div>

      {/* Input Bar */}
      <ChatInput onSend={handleSend}/>
    </main>
  );
}