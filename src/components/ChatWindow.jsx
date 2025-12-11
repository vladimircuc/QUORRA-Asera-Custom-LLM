
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
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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


  async function refreshConversationTitle() {
  const { data: { user } } = await supabase.auth.getUser();
  const userId = user?.id;

  const convRes = await fetch(`http://127.0.0.1:8000/conversations/${userId}`);
  const convData = await convRes.json();

  const updated = convData.conversations.find(
    c => c.id === selectedConversation.id
  );

  if (updated) {
    updatedTitle(updated.id, updated.title);
  }
}


async function handleSend(input, pendingFiles) {
  if (!selectedConversation) return;

  const { data: { user } } = await supabase.auth.getUser();
  const userId = user?.id ?? "fallback-id";

  const hasText = input.trim().length > 0;
  const hasFiles = pendingFiles.length > 0;

  if (!hasText && !hasFiles) return;

  // UI update
  setMessages(prev => [
    ...prev,
    {
      role: "user",
      content: hasFiles
        ? `[files: ${pendingFiles.map(f => f.name).join(", ")}]` + (hasText ? ` - ${input}` : "")
        : input,
      created_at: new Date().toISOString(),
    }
  ]);

  setLoading(true);
  let res, data;

  if (hasFiles) {
    const form = new FormData();
    form.append("conversation_id", selectedConversation.id);
    form.append("user_id", userId);
    form.append("content", input.trim() || "[files only]");



    pendingFiles.forEach(file => form.append("files", file));

    res = await fetch("http://127.0.0.1:8000/messages/with-files", {
      method: "POST",
      body: form,
    });
  } else {
    res = await fetch("http://127.0.0.1:8000/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: selectedConversation.id,   // FIX
        user_id: userId,
        content: input,
      })
    });
  }

  data = await res.json();

  await refreshConversationTitle();

  const timestamp = data.message.created_at || new Date().toISOString();
  if (data?.message?.content) {
    setMessages(prev => [...prev, {
      role: "assistant",
      content: data.message.content,
      created_at: timestamp
    }]);
  }
  setLoading(false);
}


  if (!selectedConversation){
    return (
    <div className='bg-main flex flex-1 text-center justify-center items-center'>
      <div className='items-center bg-diff w-1/2 rounded py-8 px-4 white-text'>
          <p className='text-[#3AB3FF] text-3xl'>Welcome to QUORRA</p>
          <p className='text-xl'>Please select or create a conversation to view</p>
      </div>
      </div>);
  }

  return (
    <main className="flex flex-1 flex-col px-4 pt-6 pb-2 gap-2 bg-main text-white">
      {/* Message Feed */}
      <div className={`${compactMode ? "space-y-1" : "space-y-4"} h-138 overflow-y-auto p-4 flex flex-col`}>
        {messages.map((msg,index) => (
          <ChatMessage key={index} role={msg.role} content={msg.content} time={msg.created_at} showTimestamps={showTimestamps} compactMode={compactMode}/>
        ))}


        {loading && (
            <p className="loader m-auto my-2"></p>
        )}

        <div className='pb-4' ref={messagesEndRef} />
      </div>

      <div className={`
      w-full m-auto
      ${animateInput ? "transition-transform duration-500" : "" }
      ${messages.length === 0 ? "translate-y-[-40vh]" : "translate-y-0"}
    `}>
        {/* Input Bar */}
        <ChatInput 
        key={selectedConversation?.id} 
        onSend={handleSend}/>
      </div>
    </main>
  );
}