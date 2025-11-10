import Navbar from "../components/Navbar"
   import { Link } from 'react-router-dom';

// src/pages/AccountPage.jsx

export default function LoginPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar/>
      <div className="flex justify-center items-center white-text grow bg-main">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl">Welcome to <span className="primary-text">Quorra</span></h1>
          
            <input className="bg-diff p-3" placeholder="Username" type="text" id="Username" />
            <input className="bg-diff p-3" placeholder="Password" type="text" id="Password" />
          
          <button className="bg-accent hover:bg-[#3AB3FF] text-white rounded px-14 py-2 m-auto text-xl mt-4">Login</button>
          <p className="text-center text-xs"href="">No Account? Sign Up <Link to="/Register" className="primary-text underline cursor-pointer">Here</Link></p>

        </div>
      </div>
    </div>
  )
}