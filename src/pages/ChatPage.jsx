// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Navbar from '../components/Navbar';

export default function ChatPage() {
  return (
    <div className="flex flex-col h-screen navy-bg">
      <Navbar />
      <div className="flex flex-1 w-screen bg-gray-900 text-white">
        <Sidebar />
        <ChatWindow />
      </div>
      
    </div>
  );
}