import { useState } from "react";
import { supabase } from "../supabaseClient";
import Navbar from "../components/Navbar";
import { Link, useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError("");
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError(error.message);
    } else {
      navigate("/"); // redirect to home after login
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex justify-center items-center white-text grow bg-main">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl">
            Welcome to <span className="primary-text">Quorra</span>
          </h1>

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
            onClick={handleLogin}
            className="bg-accent hover:bg-[#3AB3FF] text-white rounded px-14 py-2 m-auto text-xl mt-4"
          >
            Login
          </button>

          <p className="text-center text-xs">
            No Account? Sign Up{" "}
            <Link
              to="/register"
              className="primary-text underline cursor-pointer"
            >
              Here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
