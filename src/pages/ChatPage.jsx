import { useEffect, useState} from "react";

// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Navbar from '../components/Navbar';

export default function ChatPage({mode, setMode}) {

  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState();

      useEffect(() => {
        fetch("http://127.0.0.1:8000/clients")
        .then((response) => response.json())
        .then(setClients)
        .catch(console.error);
    }, []);

  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex flex-1 w-full">
        <Sidebar clients={clients} selectedClient={selectedClient} setSelectedClient={setSelectedClient} mode={mode} setMode={setMode}/>
        <ChatWindow selectedClient={selectedClient}/>
      </div>
      
    </div>
  );
}