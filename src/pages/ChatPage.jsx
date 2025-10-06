// File: src/pages/ChatPage.jsx
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Navbar from '../components/Navbar';

export default function ChatPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex flex-1 w-full">
        <Sidebar />
        <ChatWindow />
      </div>
      
    </div>
  );
}