"use client";

import { useState } from "react";
import { Save, CheckCircle2 } from "lucide-react";

interface Profile {
  name: string;
  level: "foundation" | "standard" | "extended";
  learningStyle: "visual" | "analytical" | "practice-heavy";
  language: "en" | "zh-hk";
  dailyGoal: number;
}

const defaultProfile: Profile = {
  name: "",
  level: "standard",
  learningStyle: "practice-heavy",
  language: "en",
  dailyGoal: 30,
};

function loadProfile(): Profile {
  if (typeof window === "undefined") return defaultProfile;
  try {
    const raw = localStorage.getItem("eduloop_profile");
    return raw ? { ...defaultProfile, ...JSON.parse(raw) } : defaultProfile;
  } catch {
    return defaultProfile;
  }
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile>(loadProfile);
  const [saved, setSaved] = useState(false);

  function save() {
    localStorage.setItem("eduloop_profile", JSON.stringify(profile));
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  return (
    <div className="space-y-6 max-w-lg">
      <h1 className="text-2xl font-bold text-gray-900">⚙️ Settings</h1>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <h2 className="font-semibold text-gray-700">Student Profile</h2>

        {/* Name */}
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Display Name</label>
          <input
            type="text"
            placeholder="Your name"
            value={profile.name}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Level */}
        <div className="space-y-1">
          <label className="text-xs text-gray-500">DSE Curriculum Level</label>
          <select
            value={profile.level}
            onChange={(e) => setProfile({ ...profile, level: e.target.value as Profile["level"] })}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="foundation">Foundation (Compulsory Part)</option>
            <option value="standard">Standard (Compulsory Part)</option>
            <option value="extended">Extended (Module 1 or Module 2)</option>
          </select>
        </div>

        {/* Learning style */}
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Learning Style</label>
          <select
            value={profile.learningStyle}
            onChange={(e) => setProfile({ ...profile, learningStyle: e.target.value as Profile["learningStyle"] })}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="visual">Visual — Diagrams & visual examples</option>
            <option value="analytical">Analytical — Step-by-step proofs</option>
            <option value="practice-heavy">Practice-Heavy — Many worked examples</option>
          </select>
        </div>

        {/* Language */}
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Interface Language</label>
          <select
            value={profile.language}
            onChange={(e) => setProfile({ ...profile, language: e.target.value as Profile["language"] })}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="en">English</option>
            <option value="zh-hk">繁體中文 (Traditional Chinese)</option>
          </select>
        </div>

        {/* Daily goal */}
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Daily Study Goal: {profile.dailyGoal} minutes</label>
          <input
            type="range" min={10} max={120} step={5} value={profile.dailyGoal}
            onChange={(e) => setProfile({ ...profile, dailyGoal: Number(e.target.value) })}
            className="w-full accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>10 min</span><span>120 min</span>
          </div>
        </div>

        <button
          onClick={save}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-5 py-2.5 text-sm font-semibold transition-colors"
        >
          {saved ? <CheckCircle2 size={15} /> : <Save size={15} />}
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>

      {/* AI / Backend */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold text-gray-700">AI Model</h2>
        <div className="text-sm text-gray-500 space-y-2">
          <div className="flex justify-between">
            <span>LLM</span>
            <span className="font-medium text-gray-800">MiniMax-M2.5</span>
          </div>
          <div className="flex justify-between">
            <span>Vector DB</span>
            <span className="font-medium text-gray-800">ChromaDB (322 chunks)</span>
          </div>
          <div className="flex justify-between">
            <span>Embeddings</span>
            <span className="font-medium text-gray-800">all-MiniLM-L6-v2</span>
          </div>
          <div className="flex justify-between">
            <span>Backend</span>
            <span className="font-medium text-gray-800">FastAPI @ localhost:8000</span>
          </div>
        </div>
      </div>
    </div>
  );
}
