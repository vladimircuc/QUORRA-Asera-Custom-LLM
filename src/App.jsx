// src/App.jsx
import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AccountPage from './pages/AccountPage';
import SettingsPage from './pages/SettingsPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
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
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/settings" element={<SettingsPage mode={mode} setMode={setMode}/>} />
    </Routes>
  );
}

export default App;