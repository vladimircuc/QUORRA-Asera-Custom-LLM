import { useState, useEffect } from "react";
import Folder from "./Folder";
import Mode from "./mode";

export default function Sidebar() {

  const filler = [
    {
      id: 1,
      name: "Asera Stuff Folder",
      children: [
        { id: 2, name: "Question about website", children: [] },
        {
          id: 3,
          name: "Business Things",
          children: [
            { id: 4, name: "Drafting up a contract", children: [] },
            { id: 5, name: "I am a cool client", children: [
              { id: 9, name: "I am a cool client blah", children: [] },
            ] },
          ],
        },
      ],
    },
    { id: 6, name: "Asera Doc Question", children: [] },
    { id: 7, name: "Asera's very serious rules", children: [] },
    { id: 8, name: "Filler Conversations that tests if it breaks when longer text", children: [] },
  ];

    const [mode, setMode] = useState("light");

    useEffect(() => {
      document.documentElement.setAttribute("theme", mode);
    }, [mode]);

  return (
    <aside className="sidebar w-64 bg-main white-text flex flex-col p-4 border-r-4 border-[#3AB3FF] min-w-[100px] relative">
    <div className="circle">
      <Mode mode={mode} setMode={setMode}/>
    </div>
      {/* Inside of my navbar/ may make it expandable */}
      <button className="flex bg-diff highlight py-4 px-3 rounded text-center text-sm my-5 justify-between">
        <p>Create a New Chat</p>
        <p>+</p>
      </button>
      <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

      {filler.map((folder) => (
        <Folder key={folder.id} folder={folder} />
      ))}

      {/* Add conversation list later */}
    </aside>
  );
}