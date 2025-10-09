import React from "react";

export default function Folder({ selectedClient, filler }) {

  const client = filler.find((c) => c.name.toLowerCase() === selectedClient.name?.toLowerCase());

  if (!client) {
    return <p>Select a client to view chats.</p>
  }

  const statusColor = () => {
    if (!selectedClient) return '';
    switch (selectedClient.status.toLowerCase()) {
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
      {client.chats.length === 0 && (
        <p className="text-gray-400">No chats yet for {selectedClient.name}.</p>
      )}

      {client.chats.length > 0 && (
        <div className="space-y-3">
          {client.chats.map((chat, index) => (
            <div
              key={index}
              className="flex flex-col bg-diff highlight p-3 rounded text-sm my-2 justify-between"
            >
              <div>
                <div className="flex flex-row gap-2">
                  <p className="tags bg-[#3AB3FF]">{selectedClient.name}</p>
                  <p className={`tags ${statusColor()}`}>{selectedClient.status}</p>
                </div>
              </div>
              <p>{chat}</p>
            </div>
          ))}
        </div>
      )}
    </div>


  );
}
