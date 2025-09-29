// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';

export default function ChatPage() {
  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white">
      <Sidebar />
      <ChatWindow />
    </div>
  );
}