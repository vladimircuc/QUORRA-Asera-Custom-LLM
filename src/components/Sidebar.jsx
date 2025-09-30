import { useState } from "react";
import Folder from "./Folder";

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

  return (
    <aside className="sidebar w-64 bg-[#1A1D23] text-white flex flex-col p-4 border-r-4 border-[#3AB3FF] min-w-[100px] relative">
    
      {/* Inside of my navbar/ may make it expandable */}
      <button className="flex bg-gray-700 hover:bg-gray-600 py-2 px-3 rounded text-center text-sm my-5 justify-between">
        <p>Create a New Chat</p>
        <p>+</p>
      </button>
      <div className="primary-bg border-t-2 border-[#3AB3FF] mb-5"></div>

      {filler.map((folder) => (
        <Folder key={folder.id} folder={folder} />
      ))}

      {/* Add conversation list later */}
    </aside>
  );
}