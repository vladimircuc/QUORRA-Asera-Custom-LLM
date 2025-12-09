import { useState } from "react";
import { Link } from "react-router-dom";

// Toggle Component
function Toggle({ enabled, onChange, label, description, icon}) {
  return (
    <div className="flex items-start justify-between p-4 rounded-lg bg-main highlight hover:border-[#3AB3FF]/50 transition-colors">
      <div className="flex items-start gap-3 flex-1">
        {icon && (
          <div className="mt-0.5 primary-text">
            {icon}
          </div>
        )}
        <div className="flex-1">
          <label className="text-base font-medium cursor-pointer block mb-1">
            {label}
          </label>
          {description && (
            <p className="text-sm opacity-70">{description}</p>
          )}
        </div>
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#3AB3FF] focus:ring-offset-2 focus:ring-offset-main ml-4 ${
          enabled ? "bg-[#3AB3FF]" : "bg-gray-600"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            enabled ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}

export default function Settings({ mode, setMode, setShowTimestamps, showTimestamps , compactMode, setCompactMode}) {
  const [openIndex, setOpenIndex] = useState(null);
  
  // Notification settings state
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [weeklySummary, setWeeklySummary] = useState(false);
  const [productUpdates, setProductUpdates] = useState(true);
  
  // Chat experience settings state
  // const [compactMode, setCompactMode] = useState(false);
  // const [showTimestamps, setShowTimestamps] = useState(true);
  const [highlightCode, setHighlightCode] = useState(true);

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const handleThemeToggle = () => {
    setMode(mode === "light" ? "dark" : "light");
  };

  // Icons
  const BellIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
  );

  const MailIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );

  const ChatIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );

  const CodeIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  );

  const ClockIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );

  const PaletteIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  );

  const UserIcon = (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );

  return (
    <div className="w-full max-w-3xl mx-auto my-10 px-6 white-text">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold primary-text mb-2">Settings</h1>
        <p className="text-sm opacity-75">Customize your experience and preferences</p>
      </div>

      <div className="space-y-3">
        {/* Appearance Section */}
        <div className="bg-diff highlight rounded-lg overflow-hidden">
          <button
            onClick={() => toggleAccordion(0)}
            className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold hover:bg-main/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {PaletteIcon}
              <span>Appearance</span>
            </div>
            <svg 
              className={`w-5 h-5 transition-transform ${openIndex === 0 ? "rotate-180" : ""}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openIndex === 0 && (
            <div className="px-6 py-4 border-t highlight">
              <div className="flex items-center justify-between p-4 rounded-lg bg-main">
                <div className="flex items-center gap-3">
                  <span className="text-base font-medium">Theme: {mode === "light" ? "Light" : "Dark"}</span>
                </div>
                <button
                  onClick={handleThemeToggle}
                  className="bg-[#3AB3FF] hover:bg-[#309bdd] text-white px-4 py-2 rounded-lg transition-colors font-medium"
                >
                  Switch to {mode === "light" ? "Dark" : "Light"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Profile Section */}
        <div className="bg-diff highlight rounded-lg overflow-hidden">
          <button
            onClick={() => toggleAccordion(1)}
            className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold hover:bg-main/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {UserIcon}
              <span>Profile</span>
            </div>
            <svg 
              className={`w-5 h-5 transition-transform ${openIndex === 1 ? "rotate-180" : ""}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openIndex === 1 && (
            <div className="px-6 py-4 border-t highlight">
              <Link to="/profile">
                <div className="p-4 rounded-lg bg-main highlight hover:border-[#3AB3FF]/50 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-base font-medium">Manage Profile Settings</span>
                    </div>
                    <svg className="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  <p className="text-sm opacity-70 mt-1">Update your display name, email, and password</p>
                </div>
              </Link>
            </div>
          )}
        </div>

        {/* Notifications Section */}
        <div className="bg-diff highlight rounded-lg overflow-hidden">
          <button
            onClick={() => toggleAccordion(2)}
            className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold hover:bg-main/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {BellIcon}
              <span>Notifications</span>
            </div>
            <svg 
              className={`w-5 h-5 transition-transform ${openIndex === 2 ? "rotate-180" : ""}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openIndex === 2 && (
            <div className="px-6 py-4 border-t highlight space-y-3">
              <Toggle
                enabled={emailAlerts}
                onChange={setEmailAlerts}
                label="Email alerts for new messages"
                description="Receive email notifications when you receive new messages"
                icon={MailIcon}
              />
              <Toggle
                enabled={weeklySummary}
                onChange={setWeeklySummary}
                label="Weekly activity summary"
                description="Get a weekly digest of your account activity"
                icon={BellIcon}
              />
              <Toggle
                enabled={productUpdates}
                onChange={setProductUpdates}
                label="Product updates"
                description="Stay informed about new features and improvements"
                icon={BellIcon}
              />
            </div>
          )}
        </div>

        {/* Chat Experience Section */}
        <div className="bg-diff highlight rounded-lg overflow-hidden">
          <button
            onClick={() => toggleAccordion(3)}
            className="w-full flex justify-between items-center px-6 py-4 text-left font-semibold hover:bg-main/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {ChatIcon}
              <span>Chat Experience</span>
            </div>
            <svg 
              className={`w-5 h-5 transition-transform ${openIndex === 3 ? "rotate-180" : ""}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {openIndex === 3 && (
            <div className="px-6 py-4 border-t highlight space-y-4">
              <Toggle
                enabled={compactMode}
                onChange={setCompactMode}
                label="Compact mode"
                description="Reduce spacing between chat messages for a denser view"
                icon={ChatIcon}
              />
              <Toggle
                enabled={showTimestamps}
                onChange={setShowTimestamps}
                label="Show timestamps in chat"
                description="Display time information for each message"
                icon={ClockIcon}
              />
              <Toggle
                enabled={highlightCode}
                onChange={setHighlightCode}
                label="Highlight code blocks"
                description="Apply syntax highlighting to code snippets in messages"
                icon={CodeIcon}
              />

              {/* Preview Box */}
              <div className="mt-6 p-4 rounded-lg bg-main highlight">
                <p className="text-sm font-medium mb-3 opacity-75">Preview:</p>
                <div className={`space-y-2 ${compactMode ? "space-y-1" : "space-y-3"}`}>
                  <div className={`rounded-lg p-3 bg-[#3AB3FF] white-text max-w-[80%] ml-auto ${compactMode ? "py-2 px-3 text-sm" : "py-3 px-4"}`}>
                    <p className="text-sm">User message example</p>
                    {showTimestamps && (
                      <p className="text-xs opacity-70 mt-1">2:30 PM</p>
                    )}
                  </div>
                  <div className={`rounded-lg p-3 bg-diff white-text max-w-[80%] ${compactMode ? "py-2 px-3 text-sm" : "py-3 px-4"}`}>
                    <p className="text-sm">Assistant response</p>
                    {highlightCode && (
                      <pre className="mt-2 p-2 rounded bg-main text-xs overflow-x-auto">
                        <code>const example = "code block";</code>
                      </pre>
                    )}
                    {showTimestamps && (
                      <p className="text-xs opacity-70 mt-1">2:31 PM</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
