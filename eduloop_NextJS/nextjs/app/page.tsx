"use client";

import { BookOpen, PenLine, BarChart2, TrendingUp, Award } from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import Link from "next/link";

const radarData = [
  { subject: "Algebra",      score: 78 },
  { subject: "Geometry",     score: 82 },
  { subject: "Trigonometry", score: 65 },
  { subject: "Calculus",     score: 71 },
  { subject: "Statistics",   score: 88 },
];

const recentActivity = [
  { date: "28 Feb 2026", activity: "Lesson: Quadratic Equations", score: "—" },
  { date: "27 Feb 2026", activity: "Assessment: Polynomials",     score: "7/10" },
  { date: "26 Feb 2026", activity: "Lesson: Functions",           score: "—" },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">📚 EduLoop DSE</h1>
        <p className="text-gray-500 mt-1">Your AI-powered HKDSE Mathematics tutor</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Lessons Completed", value: "0", delta: "Start learning!", icon: BookOpen, color: "blue" },
          { label: "Average Score",     value: "—",  delta: "No assessments yet", icon: Award, color: "green" },
          { label: "Study Streak",      value: "1",  delta: "Keep going!",        icon: TrendingUp, color: "purple" },
        ].map(({ label, value, delta, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className={`inline-flex p-2 rounded-lg bg-${color}-50 mb-3`}>
              <Icon size={18} className={`text-${color}-600`} />
            </div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <p className="text-xs text-gray-400 mt-1">{delta}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-800 mb-4">📊 Mastery by Topic</h2>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
              <Radar dataKey="score" stroke="#2563eb" fill="#2563eb" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-800 mb-4">📈 Performance by Topic</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={radarData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="subject" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="score" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          href="/learn"
          className="flex items-center gap-4 bg-blue-600 hover:bg-blue-700 transition-colors text-white rounded-xl p-5"
        >
          <BookOpen size={24} />
          <div>
            <p className="font-semibold">Start a Lesson</p>
            <p className="text-sm text-blue-200">AI-generated from DSE syllabus</p>
          </div>
        </Link>
        <Link
          href="/practice"
          className="flex items-center gap-4 bg-white hover:bg-gray-50 transition-colors border border-gray-200 rounded-xl p-5"
        >
          <PenLine size={24} className="text-gray-600" />
          <div>
            <p className="font-semibold text-gray-900">Practice Assessment</p>
            <p className="text-sm text-gray-500">Real DSE past-paper questions</p>
          </div>
        </Link>
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">📅 Recent Activity</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="px-5 py-3 text-left">Date</th>
              <th className="px-5 py-3 text-left">Activity</th>
              <th className="px-5 py-3 text-right">Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {recentActivity.map((r) => (
              <tr key={r.date} className="hover:bg-gray-50">
                <td className="px-5 py-3 text-gray-500">{r.date}</td>
                <td className="px-5 py-3 text-gray-800">{r.activity}</td>
                <td className="px-5 py-3 text-right font-medium">{r.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
