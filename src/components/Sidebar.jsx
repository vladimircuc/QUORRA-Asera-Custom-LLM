import { useState, useEffect } from "react";
import Folder from "./Folder";
import Mode from "./mode";
import ClientDropdown from "./ClientDropdown";

export default function Sidebar() {

  const filler = [
    { id: 1, name: "pickleball", chats: ["question about company", "pickleball chat"] },
    { id: 2, name: "testing", chats: ["testing company chat", "testing chat"] },
    { id: 3, name: "Barney", chats: ["Barney chat"] },
    { id: 4, name: "fsc", chats: [] },
  ];

  const [selectedClient, setSelectedClient] = useState("");

    const [mode, setMode] = useState("light");

    useEffect(() => {
      document.documentElement.setAttribute("theme", mode);
    }, [mode]);

  return (
    <aside className="sidebar w-64 bg-main white-text flex flex-col p-4 border-r-4 border-[#3AB3FF] min-w-[100px] relative">
    <div className="circle">
      <Mode mode={mode} setMode={setMode}/>
    </div>
    <button className="flex bg-diff highlight py-4 px-3 rounded text-center text-sm my-5 justify-between">
      <p>Create a New Chat</p>
      <p>+</p>
    </button>
    <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

    <ClientDropdown onSelectClient={setSelectedClient}/>
      
    <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

    <Folder selectedClient={selectedClient} filler={filler} />

      {/* Add conversation list later */}
    </aside>
  );
}