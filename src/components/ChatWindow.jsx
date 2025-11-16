
import { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { supabase } from "../supabaseClient";

export default function ChatWindow({ selectedConversation }) {
  // const [messages, setMessages] = useState([
  //   { role: 'system', content: 'How can I help you today? fewf fwe fwe ewf  ewf we fw ef w e fw ef wef we fwe fw e ew wfe fwe f we f  ggggggggggggggggggggggggg' },
  // ]);
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  }
  }, [messages]);

  useEffect (() => {
    if (!selectedConversation) return;

    console.log({selectedConversation});
    const fetchMessages = async () => {
      try {
      const response = await fetch(`http://127.0.0.1:8000/messages/${selectedConversation.id}`);
      const data = await response.json();
      console.log("Message", data);
      setMessages(Array.isArray(data.messages) ? data.messages : []);
      console.log("Fetched Messages:", data.messages);
      }catch (error) {
        console.error(error);
        setMessages([]);
      }
      };

    fetchMessages();
  },[selectedConversation]);

const handleSend = async (input) => {
  if (!input.trim() || !selectedConversation) return;

  setMessages((prev) => [
    ...prev,
    { role: "user", content: { text: input } },
  ]);

  try {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id || "11111111-2222-3333-4444-555555555555";

    const res = await fetch("http://127.0.0.1:8000/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: selectedConversation.id,
        user_id: userId,
        content: input,
      }),
    });

    const data = await res.json();

    if (data?.message?.content) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: { text: data.message.content } },
      ]);
    }
  } catch (err) {
    console.error("Error sending message:", err);
  }
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

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <ChatInput onSend={handleSend}/>
    </main>
  );
}