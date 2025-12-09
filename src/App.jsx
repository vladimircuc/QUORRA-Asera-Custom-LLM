// src/App.jsx
import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AccountPage from './pages/AccountPage';
import SettingsPage from './pages/SettingsPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import { supabase } from './supabaseClient'; // Make sure you have this
import './App.css';

function App() {
  const [mode, setMode] = useState("light");
  const [user, setUser] = useState(null);
  const [showTimestamps, setShowTimestamps] = useState(true);
  const [compactMode, setCompactMode] = useState(false);
  async function refreshUser() {
  const { data } = await supabase.auth.getUser();
  setUser(data.user);
  }

  useEffect(() => {
    document.documentElement.setAttribute("theme", mode);
  }, [mode]);

  useEffect(() => {
    const getSession = async () => {
      const { data } = await supabase.auth.getSession();
      setUser(data.session?.user || null);
    };
    getSession();

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
    });

    return () => listener.subscription.unsubscribe();
  }, []);

  const userEmail = user?.email || null;

  return (
    <Routes>
      {user ? (
        <>
          <Route path="/" element={<ChatPage mode={mode} setMode={setMode} user={user} showTimestamps={showTimestamps} compactMode={compactMode}/>} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/settings" element={<SettingsPage mode={mode} setMode={setMode} user={user} setShowTimestamps={setShowTimestamps} showTimestamps={showTimestamps} compactMode={compactMode} setCompactMode={setCompactMode}/>} />
          <Route path="/profile" element={<ProfilePage user={user} refreshUser={refreshUser}/>}></Route>
          <Route path="*" element={<Navigate to="/" />} />
        </>
      ) : (
        <>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </>
      )}
    </Routes>
  );
}

export default App;
