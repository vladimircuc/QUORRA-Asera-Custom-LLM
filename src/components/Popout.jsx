import { useState } from "react";
import { Link } from "react-router-dom";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      {/* Hamburger Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="w-10 h-10 bg-sky-500 cursor-pointer rounded-4xl mr-4"
      >
      </button>

      {/* Overlay (click to close) */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 z-40 bg-black/40"
        ></div>
      )}

      {/* Sidebar Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-64 primary-bg shadow-lg p-5 z-50 transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >

        <div className="flex flex-col gap-4">
          <nav className="flex flex-col gap-2 text-lg py-4">
            <Link className="text-white hover:bg-sky-500 shadow p-2" to="/login">Login</Link>

            <Link className="text-white hover:bg-sky-500 shadow p-2" to="/">Home</Link>

            <Link className="text-white hover:bg-sky-500 shadow p-2 " to="/settings">Settings</Link>
          </nav>
        </div>
      </div>
    </div>
  );
}
