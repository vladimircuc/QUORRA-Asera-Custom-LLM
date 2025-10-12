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
        />
        <ChatWindow selectedConversation={selectedConversation}/>
      </div>
      
    </div>
  );
}