import { useEffect, useState} from "react";

// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Navbar from '../components/Navbar';
import {supabase} from "../supabaseClient";
import Rename from "../components/Rename";

export default function ChatPage({mode, setMode, user, showTimestamps, compactMode}) {

  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState();
  const [allConversations, setAllConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [showClientPopup, setShowClientPopup] = useState(false);
  const [APILoading, setAPILoading] = useState(true);
  const [isRenameOpen, setIsRenameOpen] = useState(false);
  const [renameTarget, setRenameTarget] = useState(null);



const handleDeleteConversation = async (conversation) => {
  try {
    await fetch(`http://127.0.0.1:8000/conversations/${conversation.id}`, {
      method: "DELETE",
    });

    setAllConversations(prev =>
      prev.filter(c => c.id !== conversation.id)
    );

    if (selectedConversation?.id === conversation.id) {
      setSelectedConversation(null);
    }

  } catch (err) {
    console.error("Error deleting conversation:", err);
  }
};


const handleRenameConversation = async (conversation, newTitle) => {
  try {
    await fetch(`http://127.0.0.1:8000/conversations/${conversation.id}/title`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle })
    });

    // Update state WITHOUT re-fetch (chat suggested)
    setAllConversations(prev =>
      prev.map(c =>
        c.id === conversation.id ? { ...c, title: newTitle } : c
      )
    );

    if (selectedConversation?.id === conversation.id) {
      setSelectedConversation(prev => ({
        ...prev,
        title: newTitle
      }));
    }

  } catch (err) {
    console.error("Rename failed:", err);
  }
};

const openRenameModal = (conversation) => {
  setRenameTarget(conversation);
  setIsRenameOpen(true);
};

  useEffect(() => {
    fetch("http://127.0.0.1:8000/clients")
    .then((response) => response.json())
    .then(setClients)
    .catch(console.error);
  }, []);

useEffect(() => {
  const fetchAllConversations = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || "11111111-2222-3333-4444-555555555555"; // fallback to dummy

      console.log("Fetching conversations for user:", userId);

      const res = await fetch(`http://127.0.0.1:8000/conversations/${userId}`);
      const data = await res.json();
      setAllConversations(data.conversations);
      setAPILoading(false);
    } catch (error) {
      console.error("Error fetching all conversations:", error);
      setAPILoading(false);
    }
  };

  fetchAllConversations();
}, []);


const handleCreateNewChat = async (clientId) => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id || "11111111-2222-3333-4444-555555555555";

    const response = await fetch("http://127.0.0.1:8000/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: clientId,
        user_id: userId,
      }),
    });

    const data = await response.json();

    setAllConversations((prev) => [...prev, data.conversation]);
    setSelectedConversation(data.conversation);
  } catch (error) {
    console.error("Error creating conversation:", error);
  }
};


    const handleNewChatClick = () => {
    if (!selectedClient) {
      setShowClientPopup(true);
    } else {
      handleCreateNewChat(selectedClient.id);
    }
  };

  const handleClientConfirm = (clientId) => {
    setShowClientPopup(false);
    handleCreateNewChat(clientId);
  };

  const handleConversationClick = (conversation) => {
    console.log("This is the conversation being sent");
    console.log({conversation})
    setSelectedConversation(conversation);
  }

  const updatedTitle = (id, newTitle) => {
    setAllConversations(prev =>
      prev.map(conv => conv.id === id ? {...conv, title: newTitle}:conv)
      );
  }

  return (
    <div className="flex flex-col h-screen">
      <Navbar user = {user}/>
      <div className="flex flex-1 w-full">
        <Sidebar clients={clients} 
        selectedClient={selectedClient} 
        setSelectedClient={setSelectedClient} 
        mode={mode} 
        setMode={setMode} 
        allConversations = {allConversations}
        onSelectedConversation = {handleConversationClick}
        onNewChatClick={handleNewChatClick}
        APILoading={APILoading}
        onRenameConversation={openRenameModal} 
        onDeleteConversation={handleDeleteConversation} 
        selectedConversation={selectedConversation}  
        />
        <Rename
        isOpen={isRenameOpen}
        onClose={() => setIsRenameOpen(false)}
        conversation={renameTarget}
        onRename={(newTitle) => handleRenameConversation(renameTarget, newTitle)}
      />
        <ChatWindow selectedConversation={selectedConversation} updatedTitle={updatedTitle} user={user} showTimestamps={showTimestamps} compactMode={compactMode}/>
      </div>
 {showClientPopup && (
        <div className="fixed inset-0 bg-black/80 flex justify-center items-center">
          <div className="bg-main white-text border-2 border-[#3AB3FF] p-6 rounded w-80">
            <h2 className="text-lg text-[#3AB3FF] text-center mb-4">Select a client for the new chat</h2>
            <select 
              onChange={(e) => handleClientConfirm(e.target.value)}
              className="w-full border p-2 rounded bg-main"
              defaultValue=""
            >
              <option value="" disabled>Select a client</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <button
              onClick={() => setShowClientPopup(false)}
              className="mt-4 w-full bg-prim text-white rounded py-2"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}