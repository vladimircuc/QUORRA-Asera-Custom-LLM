import React from "react";

export default function Folder({ selectedClient, filler }) {

  const client = filler.find((c) => c.name.toLowerCase() === selectedClient.toLowerCase());
  
  if (!client) {
    return <p>Select a client to view chats.</p>
  }


  return (
    <div className="mt-4">
      {client.chats.length === 0 && (
        <p className="text-gray-400">No chats yet for {selectedClient}.</p>
      )}

      {client.chats.length > 0 && (
        <div className="space-y-3">
          {client.chats.map((chat, index) => (
            <div
              key={index}
              className="flex flex-col bg-diff highlight p-3 rounded text-sm my-2 justify-between"
            >
              <div>
                <p className="tags">{selectedClient}</p>
              </div>
              <p>{chat}</p>
            </div>
          ))}
        </div>
      )}
    </div>


  );
}
