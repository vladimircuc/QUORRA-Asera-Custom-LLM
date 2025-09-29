export default function Sidebar() {
  return (
    <aside className="w-64 bg-[#202123] text-white flex flex-col p-4 border-r border-gray-700">
      <h1 className="text-xl font-bold mb-4">QUORRA</h1>
      <button className="bg-gray-700 hover:bg-gray-600 py-2 px-3 rounded text-left mb-4">
        + New Chat
      </button>
      <div className="text-sm text-gray-400">Previous Conversations</div>
      {/* Add conversation list later */}
    </aside>
  );
}