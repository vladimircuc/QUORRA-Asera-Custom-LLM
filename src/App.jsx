// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AccountPage from './pages/AccountPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/account" element={<AccountPage />} />
      <Route path="/settings" elemente={<SettingsPage />} />
    </Routes>
  );
}

export default App;