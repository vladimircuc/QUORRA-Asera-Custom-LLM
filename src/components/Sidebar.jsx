import { useState, useEffect } from "react";
import Folder from "./Folder";
import Mode from "./mode";
import ClientDropdown from "./ClientDropdown";

export default function Sidebar({clients, selectedClient, setSelectedClient, mode, setMode, allConversations, onSelectedConversation}) {

  // Conversation is either allConversations or filtered
  // based on whether a client has been chosen or not
  const [conversation, setConversation] = useState([]);
  

  useEffect(() => {
    
    if (allConversations.length === 0 || clients.length === 0) return;

    const addedFields = allConversations.map(chat => {
      const client = clients.find(c => c.id === chat.client_id);
      return {
        ...chat,
        client_name: client?.name || "Unknown Client",
        client_status: client?.status || "Unknown",
      };
    });

    const filteredConvos = selectedClient
      ? addedFields.filter(c => c.client_id === selectedClient.id)
      : addedFields;

    setConversation(filteredConvos);
  }, [selectedClient, allConversations, clients]);



  return (
    <aside className="sidebar w-64 bg-main white-text flex flex-col p-4 border-r-4 border-[#3AB3FF] min-w-[100px] relative">
    <div className="circle">
      <Mode mode={mode} setMode={setMode}/>
    </div>
    <ClientDropdown setSelectedClient={setSelectedClient} clients = {clients}/>
      
    <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

    <div className="h-125 overflow-y-auto">
      <Folder conversation={conversation} onSelectedConversation={onSelectedConversation}/>
    </div>
      {/* Add conversation list later */}
    </aside>
  );
}