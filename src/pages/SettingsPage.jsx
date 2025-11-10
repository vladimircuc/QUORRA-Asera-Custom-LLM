// src/pages/SettingsPage.jsx
import Navbar from "../components/Navbar"
import Settings from "../components/settings"
// Just made this for a future light mode button
// and potentially profile settings changes?

export default function SettingsPage({mode, setMode}) {
    
  return (
    <div className="flex flex-col h-screen">
      <Navbar/>
      <div className="flex flex-col grow bg-main">
        <Settings  mode={mode} setMode={setMode}/>
        {/* <div className="flex flex-col h-full border-1 border-sky-500 m-10 gap-4 p-10 text-center">
          <p className="text-white highlight p-2 ">Account Settings</p>
          <p className="text-white highlight p-2">Lighting Settings</p>

        </div> */}
      </div>
    </div>
  )
}