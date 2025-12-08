// src/pages/ProfilePage.jsx
import Navbar from "../components/Navbar";
import Profile from "../components/Profile";
// Just made this for a future light mode button
// and potentially profile settings changes?

export default function ProfilePage({user, refreshUser}) {
    
  return (
    <div className="flex flex-col h-screen">
      <Navbar user= {user}/>
      <div className="flex flex-col grow bg-main">
        <Profile user={user} refreshUser={refreshUser}/>
      </div>
    </div>
  )
}