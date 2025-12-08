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

  // Format date nicely
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { 
      year: "numeric", 
      month: "long", 
      day: "numeric" 
    });
  };

  return (
    <div className="w-full h-full overflow-y-auto">
      <div className="flex flex-col max-w-3xl mx-auto my-10 px-6 py-8 rounded-lg white-text bg-diff highlight shadow-lg">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold primary-text mb-2">Profile Settings</h1>
          <p className="text-sm opacity-75">Manage your account information and preferences</p>
        </div>

        <div className="flex flex-col gap-6">

          {/* Display Name Section */}
          <div className="flex flex-col gap-3 p-5 rounded-lg bg-main highlight">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 primary-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <label className="text-lg font-medium">Display Name</label>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
              <input
                className="flex-1 px-4 py-2.5 rounded-lg bg-diff white-text highlight focus:outline-none focus:border-[#3AB3FF] transition-colors"
                placeholder="Enter your display name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
              />
              <button
                className="bg-[#3AB3FF] hover:bg-[#309bdd] cursor-pointer px-6 py-2.5 rounded-lg text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                onClick={handleUpdateName}
                disabled={loading || !newName.trim()}
              >
                {loading ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </div>

          {/* Email Section */}
          <div className="flex flex-col gap-3 p-5 rounded-lg bg-main highlight">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 primary-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <label className="text-lg font-medium">Email Address</label>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-base opacity-90">{user.email}</p>
              <span className="px-3 py-1 text-xs rounded-full bg-[#3AB3FF]/20 primary-text">Verified</span>
            </div>
          </div>

          {/* Account Created Section */}
          <div className="flex flex-col gap-3 p-5 rounded-lg bg-main highlight">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 primary-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <label className="text-lg font-medium">Account Created</label>
            </div>
            <p className="text-base opacity-90">{formatDate(user.created_at)}</p>
          </div>

          {/* Password Reset Section */}
          <div className="flex flex-col gap-3 p-5 rounded-lg bg-main highlight">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 primary-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <label className="text-lg font-medium">Password</label>
            </div>
            <p className="text-sm opacity-75 mb-3">Change your password by clicking the button below. You'll receive an email with instructions.</p>
            <button
              className="bg-[#3AB3FF] hover:bg-[#309bdd] cursor-pointer px-6 py-2.5 rounded-lg text-white font-medium transition-colors w-full sm:w-auto"
              onClick={handlePasswordReset}
            >
              Send Password Reset Email
            </button>
          </div>

          {/* Success/Error Message */}
          {message && (
            <div className={`p-4 rounded-lg ${
              message.includes("error") || message.includes("Error") 
                ? "bg-red-500/20 border border-red-500/50 text-red-300" 
                : "bg-green-500/20 border border-green-500/50 text-green-300"
            }`}>
              <p className="text-sm font-medium">{message}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
