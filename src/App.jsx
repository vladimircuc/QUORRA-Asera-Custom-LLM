// src/App.jsx
import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AccountPage from './pages/AccountPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

function App() {

  const [mode, setMode] = useState("light");

    useEffect(() => {
      document.documentElement.setAttribute("theme", mode);
    }, [mode]);

  return (
    <Routes>
      <Route path="/" element={<ChatPage mode={mode} setMode={setMode}/>} />
      <Route path="/account" element={<AccountPage />} />
      <Route path="/settings" elemente={<SettingsPage />} />
    </Routes>
  );
}

export default App;