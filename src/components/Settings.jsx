import { useState } from "react";
import { Link } from "react-router-dom";

export default function Settings({ mode, setMode }) {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const handleThemeToggle = () => {
    setMode(mode === "light" ? "dark" : "light");
  };

  return (
    <div className="w-full max-w-lg mx-auto mt-10 white-text shadow-lg">
      
      <div>
        <button
          onClick={() => toggleAccordion(0)}
          className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold highlight transition"
        >
          <span>Appearance</span>
          <span>{openIndex === 0 ? "-" : "+"}</span>
        </button>

        {openIndex === 0 && (
          <div className="px-6 py-4 bg-diff">
            <div className="flex items-center justify-between">
              <span>Theme: {mode === "light" ? "Light" : "Dark"}</span>
              <button
                onClick={handleThemeToggle}
                className="bg-sky-500 hover:bg-sky-600 text-white px-3 py-1 rounded-lg transition"
              >
                Toggle
              </button>
            </div>
          </div>
        )}
      </div>

      
      <div>
        <button
          onClick={() => toggleAccordion(1)}
          className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold highlight transition"
        >
          <span>Profile</span>
          <span>{openIndex === 1 ? "-" : "+"}</span>
        </button>

        {openIndex === 1 && (
          <div className="px-6 py-4 bg-diff">
            <Link to="/profile">
              <p>Profile Settings</p>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
