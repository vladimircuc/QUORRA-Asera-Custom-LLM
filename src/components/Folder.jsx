import React, { useState, useEffect, useRef } from "react";

export default function Folder({ conversation, onSelectedConversation, APILoading, selectedConversation, onRename, onDelete }) {

  const [openMenuId, setOpenMenuId] = useState(null);
  const menuRef = useRef(null);

    useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpenMenuId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (APILoading) {
    return <p className="loader m-auto my-2"></p> 
  }
  if (!APILoading && conversation === null) {
    return <p className="text-center">Start having coversations by creating a new chat</p>
  }

  const statusColor = (status) => {
    switch (status?.toLowerCase()) {
      case ('active'):
        console.log('1');
        return 'bg-green-500';
      case ('at risk'):
        return 'bg-red-500';
      case ('pending renewal'):
        return 'bg-blue-500'
      case ('on hold'):
        return 'bg-yellow-500'
      default:
        return 'bg-white';
      }
    };


  return (<div className="mt-4">
      <div className="space-y-3">
        {conversation.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onSelectedConversation(chat)}
            className={`flex flex-row bg-diff highlight p-3 rounded text-sm my-2 justify-between cursor-pointer 
              ${selectedConversation?.id === chat.id ? "selected" : ""}`}
          >
          
            <div className="flex flex-col">
              <div className="flex flex-row gap-2">
                <p className="tags bg-[#3AB3FF]">{chat.client_name}</p>
                <p className={`tags ${statusColor(chat.client_status)}`}>{chat.client_status}</p>
              </div>
              <p className="mt-1">{chat.title}</p>
            </div>

          
            <div className="relative" onClick={(e) => e.stopPropagation()}>
  <button
    className="white-text rounded-full hover:bg-[#3AB3FF] p-1 ml-1 text-xs"
    onClick={() => setOpenMenuId(openMenuId === chat.id ? null : chat.id)}
  >
    •••
  </button>

  {openMenuId === chat.id && (
    <div
      ref={menuRef} 
      className="absolute right-0 mt-2 w-32 selected border border-sky-500 white-text rounded shadow-lg text-sm z-50"
    >
      <button
        className="block w-full text-left px-4 py-2 hover:bg-sky-500"
        onClick={() => {
          setOpenMenuId(null);
          onRename(chat);
        }}
      >
        Rename
      </button>

      <button
        className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-red-500"
        onClick={() => {
          setOpenMenuId(null);
          onDelete(chat);
        }}
      >
        Delete
      </button>
    </div>
  )}
</div>
          </div>
        ))}
      </div>
    </div>
  );
}
