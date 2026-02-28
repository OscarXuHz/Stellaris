"use client";

import {
  BookOpen, PenLine, TrendingUp, Award, Brain, Clock, Target,
  Zap, Bot, Cpu, ArrowRight, Sparkles, Shield,
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from "recharts";
import Link from "next/link";

/* ── Simulated data ──────────────────────────────────────────────────── */

const radarData = [
  { subject: "Algebra",      score: 78, fullMark: 100 },
  { subject: "Geometry",     score: 82, fullMark: 100 },
  { subject: "Trigonometry", score: 65, fullMark: 100 },
  { subject: "Calculus",     score: 71, fullMark: 100 },
  { subject: "Statistics",   score: 88, fullMark: 100 },
  { subject: "Logarithms",   score: 73, fullMark: 100 },
];

const masteryDistribution = [
  { name: "Mastered",      value: 2, color: "#10b981" },
  { name: "Progressing",   value: 3, color: "#f59e0b" },
  { name: "Needs Review",  value: 2, color: "#ef4444" },
  { name: "Not Started",   value: 9, color: "#d1d5db" },
];

const retentionForecast = [
  { day: "Today",  trigonometry: 65, calculus: 55, quadratic: 87, statistics: 92 },
  { day: "+1d",    trigonometry: 54, calculus: 44, quadratic: 83, statistics: 90 },
  { day: "+3d",    trigonometry: 38, calculus: 29, quadratic: 76, statistics: 85 },
  { day: "+7d",    trigonometry: 22, calculus: 15, quadratic: 64, statistics: 78 },
  { day: "+14d",   trigonometry: 12, calculus: 7,  quadratic: 48, statistics: 68 },
];

const recentActivity = [
  { date: "28 Feb",  activity: "Lesson: Quadratic Equations",  agent: "Teaching",   score: null },
  { date: "28 Feb",  activity: "Practice: Quadratic Equations", agent: "Assessment", score: "8/10" },
  { date: "27 Feb",  activity: "Lesson: Polynomials",           agent: "Teaching",   score: null },
  { date: "27 Feb",  activity: "Practice: Polynomials",         agent: "Assessment", score: "7/10" },
  { date: "26 Feb",  activity: "Spaced Review: Trigonometry",   agent: "Assessment", score: "6/10" },
];

/* ── Component ────────────────────────────────────────────────────────── */

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* ── Hero header with gradient ──────────────────────────────── */}
      <div className="relative bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 rounded-2xl p-6 text-white overflow-hidden animate-fade-in">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white rounded-full" />
          <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-white rounded-full" />
          <div className="absolute top-1/2 right-1/3 w-20 h-20 bg-white rounded-full" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-1">
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2">
              <Sparkles size={20} />
            </div>
            <h1 className="text-2xl font-bold">EduLoop DSE</h1>
          </div>
          <p className="text-blue-100 text-sm mt-1 max-w-xl">
            Your personalised AI-powered HKDSE Mathematics learning platform. Two specialised agents collaborate to teach and assess you in real time.
          </p>
        </div>
      </div>

      {/* ── Stat cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4 stagger-children">
        {[
          { label: "Lessons Completed", value: "12", delta: "+3 this week",         icon: BookOpen,   gradient: "from-blue-500 to-blue-600" },
          { label: "Average Score",     value: "74%", delta: "Up 8% from last week", icon: Award,     gradient: "from-emerald-500 to-emerald-600" },
          { label: "Study Streak",      value: "5 days", delta: "Personal best!",    icon: TrendingUp, gradient: "from-purple-500 to-purple-600" },
          { label: "Memory Retention",  value: "66%", delta: "3 topics need review", icon: Brain,     gradient: "from-amber-500 to-orange-500" },
        ].map(({ label, value, delta, icon: Icon, gradient }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5 animate-scale-in hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
            <div className={`inline-flex p-2.5 rounded-xl bg-gradient-to-br ${gradient} mb-3 shadow-sm group-hover:scale-110 transition-transform duration-300`}>
              <Icon size={16} className="text-white" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <p className="text-xs text-gray-400 mt-1">{delta}</p>
          </div>
        ))}
      </div>

      {/* ── Dual-Agent System Showcase ──────────────────────────────── */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white animate-fade-in overflow-hidden relative">
        {/* Background grid decoration */}
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-1">
            <Cpu size={16} className="text-blue-400" />
            <h2 className="font-bold text-lg">Dual-Agent AI Architecture</h2>
          </div>
          <p className="text-slate-400 text-xs mb-5">Two specialised AI agents powered by MiniMax-M2.5 work together, coordinated by an intelligent orchestrator.</p>

          <div className="grid grid-cols-3 gap-4">
            {/* Teaching Agent */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300 hover:border-green-500/30 group">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-gradient-to-br from-green-400 to-emerald-500 rounded-lg p-2 shadow-lg shadow-green-500/20 group-hover:scale-110 transition-transform duration-300">
                  <BookOpen size={14} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold text-white">Teaching Agent</p>
                  <p className="text-[10px] text-green-400 font-medium">ACTIVE</p>
                </div>
              </div>
              <ul className="space-y-1.5 text-xs text-slate-300">
                <li className="flex items-start gap-1.5"><span className="text-green-400 mt-0.5 shrink-0">&#x2022;</span>RAG-powered lesson generation</li>
                <li className="flex items-start gap-1.5"><span className="text-green-400 mt-0.5 shrink-0">&#x2022;</span>Personalised content adaptation</li>
                <li className="flex items-start gap-1.5"><span className="text-green-400 mt-0.5 shrink-0">&#x2022;</span>Active recall flashcards</li>
                <li className="flex items-start gap-1.5"><span className="text-green-400 mt-0.5 shrink-0">&#x2022;</span>Multimodal (audio + video)</li>
              </ul>
            </div>

            {/* Orchestrator */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300 hover:border-blue-500/30 group flex flex-col items-center justify-center text-center">
              <div className="bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full p-3 shadow-lg shadow-blue-500/20 mb-3 animate-pulse-ring group-hover:scale-110 transition-transform duration-300">
                <Bot size={20} className="text-white" />
              </div>
              <p className="text-sm font-bold text-white mb-1">Orchestrator</p>
              <p className="text-[10px] text-blue-400 font-medium mb-2">COORDINATOR</p>
              <div className="flex items-center gap-1 text-[10px] text-slate-400">
                <ArrowRight size={10} className="text-green-400 rotate-180" />
                <span>Routes</span>
                <ArrowRight size={10} className="text-purple-400" />
              </div>
              <p className="text-[10px] text-slate-500 mt-2">Intent detection &amp; intelligent routing between agents</p>
            </div>

            {/* Assessment Agent */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300 hover:border-purple-500/30 group">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-gradient-to-br from-purple-400 to-violet-500 rounded-lg p-2 shadow-lg shadow-purple-500/20 group-hover:scale-110 transition-transform duration-300">
                  <PenLine size={14} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold text-white">Assessment Agent</p>
                  <p className="text-[10px] text-purple-400 font-medium">ACTIVE</p>
                </div>
              </div>
              <ul className="space-y-1.5 text-xs text-slate-300">
                <li className="flex items-start gap-1.5"><span className="text-purple-400 mt-0.5 shrink-0">&#x2022;</span>DSE past-paper question bank</li>
                <li className="flex items-start gap-1.5"><span className="text-purple-400 mt-0.5 shrink-0">&#x2022;</span>AI-powered evaluation &amp; scoring</li>
                <li className="flex items-start gap-1.5"><span className="text-purple-400 mt-0.5 shrink-0">&#x2022;</span>Diagnostic misconception analysis</li>
                <li className="flex items-start gap-1.5"><span className="text-purple-400 mt-0.5 shrink-0">&#x2022;</span>Scaffolded hints system</li>
              </ul>
            </div>
          </div>

          {/* Tech stack bar */}
          <div className="mt-4 flex items-center justify-center gap-3 text-[10px] text-slate-500">
            {["MiniMax-M2.5 LLM", "ChromaDB RAG", "322 DSE Chunks", "Spaced Repetition", "TTS + Video Gen"].map((t) => (
              <span key={t} className="bg-white/5 border border-white/10 rounded-full px-2.5 py-1">{t}</span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Charts row: Mastery Radar + Pie + Retention Forecast ──── */}
      <div className="grid grid-cols-3 gap-5">
        {/* Radar */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-3">Mastery by Topic</h2>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="score" stroke="#2563eb" fill="#2563eb" fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Mastery Pie */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-scale-in hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-3">Topic Distribution</h2>
          <ResponsiveContainer width="100%" height={140}>
            <PieChart>
              <Pie data={masteryDistribution} cx="50%" cy="50%" innerRadius={38} outerRadius={60} paddingAngle={3} dataKey="value" stroke="none">
                {masteryDistribution.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip formatter={(v) => [`${v} topics`, ""]} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-3 gap-y-1 justify-center mt-1">
            {masteryDistribution.map(({ name, color }) => (
              <div key={name} className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-[10px] text-gray-500">{name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Retention forecast */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-1">Retention Forecast</h2>
          <p className="text-[10px] text-gray-400 mb-2">Predicted memory decay over the next 14 days</p>
          <ResponsiveContainer width="100%" height={170}>
            <AreaChart data={retentionForecast} margin={{ left: -25, right: 5, top: 5, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" tick={{ fontSize: 9 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 9 }} unit="%" />
              <Tooltip formatter={(v: number) => [`${v}%`]} />
              <Area type="monotone" dataKey="trigonometry" stroke="#ef4444" fill="#fee2e2" fillOpacity={0.4} strokeWidth={1.5} name="Trig" />
              <Area type="monotone" dataKey="calculus" stroke="#f59e0b" fill="#fef3c7" fillOpacity={0.4} strokeWidth={1.5} name="Calc" />
              <Area type="monotone" dataKey="statistics" stroke="#10b981" fill="#d1fae5" fillOpacity={0.4} strokeWidth={1.5} name="Stats" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Quick actions ──────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        <Link
          href="/learn"
          className="flex items-center gap-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 text-white rounded-xl p-5 animate-fade-in-left hover:shadow-lg hover:scale-[1.02] group"
        >
          <div className="bg-white/20 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
            <BookOpen size={20} />
          </div>
          <div>
            <p className="font-semibold">Start a Lesson</p>
            <p className="text-xs text-blue-200">Teaching Agent + RAG</p>
          </div>
        </Link>
        <Link
          href="/practice"
          className="flex items-center gap-4 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 transition-all duration-300 text-white rounded-xl p-5 animate-scale-in hover:shadow-lg hover:scale-[1.02] group"
        >
          <div className="bg-white/20 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
            <PenLine size={20} />
          </div>
          <div>
            <p className="font-semibold">Practice Assessment</p>
            <p className="text-xs text-purple-200">Assessment Agent + DSE</p>
          </div>
        </Link>
        <Link
          href="/evaluation"
          className="flex items-center gap-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 transition-all duration-300 text-white rounded-xl p-5 animate-fade-in-right hover:shadow-lg hover:scale-[1.02] group"
        >
          <div className="bg-white/20 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
            <Shield size={20} />
          </div>
          <div>
            <p className="font-semibold">Take Evaluation</p>
            <p className="text-xs text-emerald-200">Personalised + Report</p>
          </div>
        </Link>
      </div>

      {/* ── Personalised recommendation ────────────────────────────── */}
      <div className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 border border-amber-200 rounded-xl px-5 py-4 flex items-center gap-4 animate-fade-in hover:shadow-md transition-shadow duration-300">
        <div className="bg-gradient-to-br from-amber-400 to-orange-500 rounded-full p-2.5 shadow-sm">
          <Zap size={16} className="text-white" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-amber-900">Personalised Recommendation</p>
          <p className="text-xs text-amber-700 mt-0.5">Based on your forgetting curve, <strong>Trigonometry</strong> retention will drop below 50% tomorrow. We recommend a spaced review session now.</p>
        </div>
        <Link href="/evaluation" className="shrink-0 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors">
          Start Review
        </Link>
      </div>

      {/* ── Recent activity ────────────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-fade-in">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Recent Activity</h2>
          <Link href="/progress" className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors">View all</Link>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="px-5 py-3 text-left">Date</th>
              <th className="px-5 py-3 text-left">Activity</th>
              <th className="px-5 py-3 text-left">Agent</th>
              <th className="px-5 py-3 text-right">Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {recentActivity.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3 text-gray-500">{r.date}</td>
                <td className="px-5 py-3 text-gray-800">{r.activity}</td>
                <td className="px-5 py-3">
                  <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    r.agent === "Teaching" ? "bg-green-50 text-green-700" : "bg-purple-50 text-purple-700"
                  }`}>
                    {r.agent === "Teaching" ? <BookOpen size={9} /> : <PenLine size={9} />}
                    {r.agent}
                  </span>
                </td>
                <td className="px-5 py-3 text-right font-medium text-gray-700">{r.score ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
