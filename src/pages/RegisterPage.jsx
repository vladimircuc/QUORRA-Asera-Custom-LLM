import { useState } from "react";
import { supabase } from "../supabaseClient";
import Navbar from "../components/Navbar";
import { useNavigate } from "react-router-dom";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async () => {
    setError("");
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) {
      setError(error.message);
    } else {
      alert("Account created! Please check your email for confirmation.");
      navigate("/login");
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex justify-center items-center white-text grow bg-main">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl primary-text">Create Your Account</h1>

          <input
            className="bg-diff p-3"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className="bg-diff p-3"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            onClick={handleRegister}
            className="bg-accent hover:bg-[#3AB3FF] text-white rounded px-14 py-2 m-auto text-xl mt-4"
          >
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
}
