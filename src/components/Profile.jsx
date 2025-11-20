import { useState } from "react";
import { supabase } from "../supabaseClient";

export default function Profile({ user, refreshUser }) {
  const [newName, setNewName] = useState(user.user_metadata?.display_name || "");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleUpdateName() {
    setLoading(true);
    setMessage("");

    const { error } = await supabase.auth.updateUser({
      data: { display_name: newName }
    });

    if (error) {
      setMessage(error.message);
    } else {
      setMessage("Display name updated!");
      await refreshUser(); // pulls the new user into App.jsx
    }

    setLoading(false);
  }

  async function handlePasswordReset() {
    const { error } = await supabase.auth.resetPasswordForEmail(user.email);
    setMessage(error ? error.message : "Password reset email sent.");
  }

  return (
    <div className="w-full h-full">
      <div className="flex flex-col m-10 p-10 rounded white-text shadow bg-diff">
        <h1 className="text-center relative text-2xl">Profile Settings</h1>

        <div className="flex flex-col gap-4 mt-10">

          {/* Display Name */}
          <div className="flex flex-row justify-between items-center">
            <p className="text-xl">Display Name:</p>

            <input
              className="border p-1 rounded bg-diff white-text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>

          <button
            className="bg-[#3AB3FF] hover:bg-[#309bdd] cursor-pointer p-2 rounded text-lg m-auto text-white mt-1"
            onClick={handleUpdateName}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save Display Name"}
          </button>

          <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

          {/* Email */}
          <div className="flex flex-row justify-between">
            <p className="text-xl">Email:</p>
            <p>{user.email}</p>
          </div>

          <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

          {/* Account Created */}
          <div className="flex flex-row justify-between">
            <p className="text-xl">Account Created:</p>
            <p>{user.created_at}</p>
          </div>

          <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

          {/* Password reset */}
          <button
            className="bg-[#3AB3FF] hover:bg-[#309bdd] cursor-pointer m-auto p-2 rounded text-lg text-white"
            onClick={handlePasswordReset}
          >
            Change Password
          </button>

          {message && (
            <p className="text-center text-sm text-green-300 mt-3">{message}</p>
          )}
        </div>
      </div>
    </div>
  );
}
