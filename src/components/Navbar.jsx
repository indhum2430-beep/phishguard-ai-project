import React from "react";
import { ShieldCheck } from "lucide-react";

export default function Navbar({ darkMode, setDarkMode }) {
  return (
    <nav className="navbar">

      {/* LEFT - LOGO & BRAND */}
      <div className="brand">

        <div className="brand-logo">
          <ShieldCheck />
        </div>

        <div className="brand-info">
          <h2>PHISHGUARD <span>AI</span></h2>
          <p>INTELLIGENT PHISHING DETECTION</p>
        </div>

      </div>

      {/* CENTER - SYSTEM STATUS */}
      <div className="system-status">
        <span className="status-dot"></span>
        <span>AI ENGINE ONLINE</span>
      </div>

      {/* RIGHT - MODE BUTTON */}
      <button
        className="mode-btn"
        onClick={() => setDarkMode(!darkMode)}
      >
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>

    </nav>
  );
}