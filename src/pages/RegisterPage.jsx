import Navbar from "../components/Navbar"
// src/pages/AccountPage.jsx

export default function RegisterPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar/>
      <div className="flex justify-center items-center white-text grow bg-main">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl primary-text">Create Your Account</h1>

            <input className="bg-diff p-3" placeholder="Email" type="text" id="Email" />
            <input className="bg-diff p-3" placeholder="Username" type="text" id="Username" />
            <input className="bg-diff p-3" placeholder="Password" type="text" id="Password" />
          
          <button className="bg-accent hover:bg-[#3AB3FF] text-white rounded px-14 py-2 m-auto text-xl mt-4">Sign Up</button>

        </div>
      </div>
    </div>
  )
}