import React, { useState } from "react";

export default function Rename({ isOpen, onClose, conversation, onRename }) {
  const [newTitle, setNewTitle] = useState(conversation?.title || "");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
      <div className="bg-main white-text border border-4 border-[#3AB3FF] rounded-lg p-6 w-80 shadow-xl">
        <h2 className="text-xl text-center mb-4">Rename Conversation</h2>

        <input
          className="w-full p-2 rounded bg-gray-100 bg-diff"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          autoFocus
        />

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-3 py-1 bg-diff rounded border border-1 border-[#3AB3FF] bg-gray-200 hover:bg-gray-300"
          >
            Cancel
          </button>

          <button
            onClick={() => {
              onRename(newTitle);
              onClose();
            }}
            className="px-3 py-1 rounded bg-[#3AB3FF] text-white hover:bg-sky-500"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
