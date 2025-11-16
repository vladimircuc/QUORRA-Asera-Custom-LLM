import React from "react";

export default function Folder({ conversation, onSelectedConversation }) {


  if (!conversation || conversation.length === 0) {
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


  return (
    <div className="mt-4">
        <div className="space-y-3">
          {conversation.map((chat) => (
            <div
              key={chat.id}
              onClick={() => onSelectedConversation(chat)}
              className="flex flex-col bg-diff highlight p-3 rounded text-sm my-2 justify-between cursor-pointer"
            >
              <div>
                <div className="flex flex-row gap-2">
                  <p className="tags bg-[#3AB3FF]">{chat.client_name}</p>
                  <p className={`tags ${statusColor(chat.client_status)}`}>{chat.client_status}</p>
                </div>
              </div>
              <p className="mt-1">{chat.title}</p>
            </div>
          ))}
        </div>
    </div>


  );
}
