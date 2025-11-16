// src/pages/SettingsPage.jsx
import Navbar from "../components/Navbar";
import Profile from "../components/profile";
// Just made this for a future light mode button
// and potentially profile settings changes?

export default function ProfilePage({userEmail}) {
    
  return (
    <div className="flex flex-col h-screen">
      <Navbar userEmail= {userEmail}/>
      <div className="flex flex-col grow bg-main">
        <Profile/>
      </div>
    </div>
  )
}