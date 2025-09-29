// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AccountPage from './pages/AccountPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/account" element={<AccountPage />} />
    </Routes>
  );
}

export default App;