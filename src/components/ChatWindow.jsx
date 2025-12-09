
import { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { supabase } from "../supabaseClient";

export default function ChatWindow({ selectedConversation, updatedTitle, user, showTimestamps, compactMode}) {
  // const [messages, setMessages] = useState([
  //   { role: 'system', content: 'How can I help you today? fewf fwe fwe ewf  ewf we fw ef w e fw ef wef we fwe fw e ew wfe fwe f we f  ggggggggggggggggggggggggg' },
  // ]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [animateInput, setAnimateInput] = useState(false);
  const messagesEndRef = useRef(null);
  const userId = user?.id;

  useEffect(() => {
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  }
  }, [messages, loading]);

  useEffect (() => {
    if (!selectedConversation) return;

    console.log({selectedConversation});
    const fetchMessages = async () => {
      try {
      const response = await fetch(`http://127.0.0.1:8000/messages/${selectedConversation.id}`);
      const data = await response.json();
      console.log("Message", data);
      setMessages(Array.isArray(data.messages) ? data.messages : []);
      if (data.messages?.length === 0){
        setAnimateInput(true);
      }
      else{
        setAnimateInput(false);
      }
      console.log("Fetched Messages:", data.messages);
      }catch (error) {
        console.error(error);
        setMessages([]);
      }
      };

    fetchMessages();
  },[selectedConversation]);

async function handleSendFiles(formData) {

  if (messages.length === 0) {
    setAnimateInput(true);
  }

 if (!formData.get("content")) {
    formData.append("content", "[file upload]");
  }

  const fileNames = [...formData.getAll("files")].map(f => f.name);
  const displayText = fileNames.length ? fileNames.join(", ") : "(uploaded file)";

  setMessages(prev => [
    ...prev,
    { role: "user", content: displayText }
  ]);

  const res = await fetch("http://127.0.0.1:8000/messages/with-files", {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  console.log("Upload response:", data);

  if (data?.message?.content) {
    setMessages(prev => [
      ...prev,
      { role: "assistant", content: data.message.content }
    ]);
  }
}


const handleSendMessage = async (input) => {
  if (!input.trim() || !selectedConversation) return;

  if (messages.length === 0) {
    setAnimateInput(true);
  }

  setMessages(prev => [
    ...prev,
    { role: "user", content: input, created_at: new Date().toISOString() }
  ]);

  try {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id || "11111111-2222-3333-4444-555555555555";

    setLoading(true);
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
  console.log("Normal Response mehehe",data);
  
    if (data?.message?.content) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: data.message.content, created_at: data.message.created_at || new Date().toISOString() }
      ]);
      setLoading(false);
    }

    const convRes = await fetch(`http://127.0.0.1:8000/conversations/${userId}`);
    const convData = await convRes.json();

    const updated = convData.conversations.find(
      c => c.id === selectedConversation.id
    );

    if (updated) {
      
      updatedTitle(updated.id, updated.title);
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
      <div className={`${compactMode ? "space-y-2" : "space-y-4"} h-142 overflow-y-auto p-4 flex flex-col`}>
        {messages.map((msg,index) => (
          <ChatMessage key={index} role={msg.role} content={msg.content} time={msg.created_at} showTimestamps={showTimestamps} compactMode={compactMode}/>
        ))}


        {loading && (
            <p className="loader m-auto my-2"></p>
        )}

        <div className='pb-4' ref={messagesEndRef} />
      </div>

      <div className={`
      w-full
      ${animateInput ? "transition-transform duration-500" : "" }
      ${messages.length === 0 ? "translate-y-[-40vh]" : "translate-y-0"}
    `}>
        {/* Input Bar */}
        <ChatInput onSend={handleSendMessage} onSendFiles={handleSendFiles}  conversationId={selectedConversation.id}
  userId={userId}/>
      </div>
    </main>
  );
}