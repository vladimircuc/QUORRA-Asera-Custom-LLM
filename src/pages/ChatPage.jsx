import { useEffect, useState} from "react";

// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Navbar from '../components/Navbar';

export default function ChatPage({mode, setMode}) {

  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState();
  const [allConversations, setAllConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [showClientPopup, setShowClientPopup] = useState(false);



  useEffect(() => {
    fetch("http://127.0.0.1:8000/clients")
    .then((response) => response.json())
    .then(setClients)
    .catch(console.error);
  }, []);

  useEffect(() => {
    const fetchAllConversations = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/conversations/11111111-2222-3333-4444-555555555555");
        console.log("we got here")
        const data = await res.json();
        setAllConversations(data.conversations);
      } catch (error) {
        console.error("Error fetching all conversations:", error);
      }
    };
    fetchAllConversations();
  }, []);

  const handleCreateNewChat = async (clientId) => {
    try{
      const response = await fetch("http://127.0.0.1:8000/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: clientId,
        }),
      });

      const data = await response.json();

      setAllConversations((prev) => [...prev, data]);
      setSelectedConversation(data);

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

  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex flex-1 w-full">
        <Sidebar clients={clients} 
        selectedClient={selectedClient} 
        setSelectedClient={setSelectedClient} 
        mode={mode} 
        setMode={setMode} 
        allConversations = {allConversations}
        onSelectedConversation = {handleConversationClick}
        onNewChatClick={handleNewChatClick}
        />
        <ChatWindow selectedConversation={selectedConversation}/>
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