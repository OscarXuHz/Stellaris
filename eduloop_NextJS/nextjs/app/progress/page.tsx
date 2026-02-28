"use client";

import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const topicData = [
  { topic: "Quadratic",     score: 82, attempts: 5 },
  { topic: "Trigonometry",  score: 68, attempts: 4 },
  { topic: "Polynomials",   score: 75, attempts: 6 },
  { topic: "Statistics",    score: 90, attempts: 3 },
  { topic: "Calculus",      score: 55, attempts: 2 },
  { topic: "Logarithms",    score: 71, attempts: 4 },
  { topic: "Sequences",     score: 63, attempts: 3 },
];

const timelineData = [
  { date: "Mon", minutes: 25 },
  { date: "Tue", minutes: 40 },
  { date: "Wed", minutes: 15 },
  { date: "Thu", minutes: 55 },
  { date: "Fri", minutes: 35 },
  { date: "Sat", minutes: 60 },
  { date: "Sun", minutes: 30 },
];

const gaps = [
  { topic: "Calculus",     gap: "Differentiation rules need reinforcement" },
  { topic: "Sequences",   gap: "AP/GP general term formula confusion" },
  { topic: "Trigonometry", gap: "Solving equations in stated range" },
];

export default function ProgressPage() {
  const avg = Math.round(topicData.reduce((s, d) => s + d.score, 0) / topicData.length);
  const total = topicData.reduce((s, d) => s + d.attempts, 0);
  const totalTime = timelineData.reduce((s, d) => s + d.minutes, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">📊 My Progress</h1>

      {/* ── Stat cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Average Score",    value: `${avg}%`,   color: "text-blue-600"  },
          { label: "Total Questions",  value: total,        color: "text-green-600" },
          { label: "Study Time (wk)",  value: `${totalTime}m`, color: "text-purple-600" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
            <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* ── Topic score bar chart ───────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-700 mb-4">Score by Topic</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topicData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="topic" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={50} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => [`${v}%`, "Score"]} />
              <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* ── Study time line chart ────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-700 mb-4">Daily Study Time (this week)</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={timelineData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} unit="m" />
              <Tooltip formatter={(v) => [`${v} min`, "Study Time"]} />
              <Legend />
              <Line type="monotone" dataKey="minutes" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} name="Minutes" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Knowledge gaps ──────────────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-700 mb-3">⚠️ Identified Knowledge Gaps</h2>
        <div className="divide-y divide-gray-100">
          {gaps.map(({ topic, gap }) => (
            <div key={topic} className="flex items-start gap-4 py-3">
              <span className="bg-amber-100 text-amber-700 text-xs font-semibold px-2 py-1 rounded-md whitespace-nowrap">
                {topic}
              </span>
              <p className="text-sm text-gray-700">{gap}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Attempts table ──────────────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-700 mb-3">Attempt Summary</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
              <th className="pb-2">Topic</th>
              <th className="pb-2 text-center">Attempts</th>
              <th className="pb-2 text-center">Score</th>
              <th className="pb-2">Mastery</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {topicData.map(({ topic, attempts, score }) => (
              <tr key={topic}>
                <td className="py-2.5 font-medium text-gray-800">{topic}</td>
                <td className="py-2.5 text-center text-gray-500">{attempts}</td>
                <td className={`py-2.5 text-center font-semibold ${score >= 80 ? "text-green-600" : score >= 60 ? "text-amber-600" : "text-red-500"}`}>
                  {score}%
                </td>
                <td className="py-2.5">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5 w-32">
                    <div
                      className={`h-1.5 rounded-full ${score >= 80 ? "bg-green-500" : score >= 60 ? "bg-amber-500" : "bg-red-400"}`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
