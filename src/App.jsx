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
          <Route path="/" element={<ChatPage mode={mode} setMode={setMode} userEmail={userEmail} />} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/settings" element={<SettingsPage mode={mode} setMode={setMode} userEmail={userEmail}/>} />
          <Route path="/profile" element={<ProfilePage userEmail={userEmail}/>}></Route>
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
