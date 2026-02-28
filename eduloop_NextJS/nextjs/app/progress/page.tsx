"use client";

import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell, AreaChart, Area,
} from "recharts";
import {
  TrendingUp, Brain, Clock, Target, CalendarClock, AlertTriangle,
  CheckCircle2, ArrowRight, Zap, BarChart2, RefreshCw,
} from "lucide-react";
import clsx from "clsx";

/* ── Simulated student data ──────────────────────────────────────────── */

const topicData = [
  { topic: "Quadratic",     score: 82, attempts: 5, retention: 87, lastReview: "Feb 28", stability: 4.2 },
  { topic: "Trigonometry",  score: 68, attempts: 4, retention: 52, lastReview: "Feb 25", stability: 2.1 },
  { topic: "Polynomials",   score: 75, attempts: 6, retention: 78, lastReview: "Feb 27", stability: 3.5 },
  { topic: "Statistics",    score: 90, attempts: 3, retention: 92, lastReview: "Feb 26", stability: 5.8 },
  { topic: "Calculus",      score: 55, attempts: 2, retention: 38, lastReview: "Feb 20", stability: 1.4 },
  { topic: "Logarithms",    score: 71, attempts: 4, retention: 65, lastReview: "Feb 24", stability: 2.8 },
  { topic: "Sequences",     score: 63, attempts: 3, retention: 48, lastReview: "Feb 22", stability: 1.9 },
];

const timelineData = [
  { date: "Mon",  minutes: 25, questions: 8  },
  { date: "Tue",  minutes: 40, questions: 14 },
  { date: "Wed",  minutes: 15, questions: 5  },
  { date: "Thu",  minutes: 55, questions: 18 },
  { date: "Fri",  minutes: 35, questions: 12 },
  { date: "Sat",  minutes: 60, questions: 20 },
  { date: "Sun",  minutes: 30, questions: 10 },
];

const masteryDistribution = [
  { name: "Mastered",      value: 2, color: "#10b981" },
  { name: "Progressing",   value: 3, color: "#f59e0b" },
  { name: "Needs Review",  value: 2, color: "#ef4444" },
  { name: "Not Started",   value: 9, color: "#d1d5db" },
];

/* ── Ebbinghaus Forgetting Curve data ─────────────────────────────────
   R(t) = e^(-t/S)  where S = memory stability
   Without review: rapid decay (S≈3)
   With spaced repetition: stability increases after each review ─────── */

function buildForgettingCurve() {
  const reviewDays = [0, 1, 3, 7, 14, 30];
  const data = [];
  for (let day = 0; day <= 30; day++) {
    const withoutReview = Math.round(100 * Math.exp(-day / 3));

    // With spaced repetition — stability grows with each review
    let lastReview = 0;
    let stability = 3;
    for (const rd of reviewDays) {
      if (day >= rd) { lastReview = rd; stability *= 1.5; }
    }
    const elapsed = day - lastReview;
    const withSpacedRep = Math.round(100 * Math.exp(-elapsed / stability));

    data.push({ day, withoutReview, withSpacedRep });
  }
  return data;
}
const forgettingCurveData = buildForgettingCurve();

/* ── Spaced repetition review schedule (simulated) ────────────────── */
const reviewSchedule = [
  { topic: "Trigonometry", nextReview: "Today",  retention: 52, interval: "4d", urgency: "overdue" as const },
  { topic: "Calculus",     nextReview: "Today",  retention: 38, interval: "7d", urgency: "overdue" as const },
  { topic: "Sequences",    nextReview: "Today",  retention: 48, interval: "7d", urgency: "overdue" as const },
  { topic: "Logarithms",   nextReview: "Mar 3",  retention: 65, interval: "7d", urgency: "soon" as const },
  { topic: "Polynomials",  nextReview: "Mar 6",  retention: 78, interval: "7d", urgency: "ok" as const },
  { topic: "Quadratic",    nextReview: "Mar 7",  retention: 87, interval: "7d", urgency: "ok" as const },
  { topic: "Statistics",   nextReview: "Mar 12", retention: 92, interval: "14d", urgency: "ok" as const },
];

/* ── Knowledge gap analysis ──────────────────────────────────────────── */
const gaps = [
  { topic: "Calculus",     gap: "Differentiation rules need reinforcement",      priority: "high" as const },
  { topic: "Sequences",    gap: "AP/GP general term formula confusion",          priority: "high" as const },
  { topic: "Trigonometry", gap: "Solving equations in stated range",             priority: "medium" as const },
  { topic: "Logarithms",   gap: "Log laws application in compound expressions",  priority: "medium" as const },
];

/* ── Learning method effectiveness (simulated) ──────────────────────── */
const methodEffectiveness = [
  { method: "Active Recall",       effectiveness: 92 },
  { method: "Spaced Repetition",   effectiveness: 88 },
  { method: "Interleaved Practice", effectiveness: 76 },
  { method: "Elaborative Interrogation", effectiveness: 72 },
  { method: "Passive Re-reading",  effectiveness: 35 },
];

/* ── Component ────────────────────────────────────────────────────────── */

export default function ProgressPage() {
  const [curveView, setCurveView] = useState<"both" | "noReview" | "spaced">("both");

  const avg = Math.round(topicData.reduce((s, d) => s + d.score, 0) / topicData.length);
  const avgRetention = Math.round(topicData.reduce((s, d) => s + d.retention, 0) / topicData.length);
  const totalAttempts = topicData.reduce((s, d) => s + d.attempts, 0);
  const totalTime = timelineData.reduce((s, d) => s + d.minutes, 0);
  const overdueCount = reviewSchedule.filter((r) => r.urgency === "overdue").length;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 animate-fade-in">My Progress</h1>

      {/* ── Stat cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4 stagger-children">
        {[
          { label: "Average Score",      value: `${avg}%`,      icon: Target,        color: "blue",   delta: "+8% vs last week" },
          { label: "Memory Retention",   value: `${avgRetention}%`, icon: Brain,     color: "purple", delta: `${overdueCount} topics need review` },
          { label: "Total Questions",    value: `${totalAttempts}`, icon: BarChart2,  color: "green",  delta: "+12 this week" },
          { label: "Study Time (week)",  value: `${totalTime}m`,   icon: Clock,      color: "amber",  delta: "37m avg / day" },
        ].map(({ label, value, icon: Icon, color, delta }) => (
          <div key={label} className={`bg-white rounded-xl border border-gray-200 p-5 animate-scale-in hover:shadow-lg hover:-translate-y-1 transition-all duration-300`}>
            <div className={`inline-flex p-2 rounded-lg bg-${color}-50 mb-3`}>
              <Icon size={18} className={`text-${color}-600`} />
            </div>
            <p className="text-2xl font-bold text-gray-900 animate-count-up">{value}</p>
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <p className="text-xs text-gray-400 mt-1">{delta}</p>
          </div>
        ))}
      </div>

      {/* ── Row 1: Mastery Pie + Topic Score Bar ───────────────────── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Mastery distribution pie chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 mb-4">Mastery Distribution</h2>
          <div className="flex items-center">
            <ResponsiveContainer width="55%" height={200}>
              <PieChart>
                <Pie
                  data={masteryDistribution}
                  cx="50%" cy="50%"
                  innerRadius={50} outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {masteryDistribution.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => [`${v} topics`, ""]} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {masteryDistribution.map(({ name, value, color }) => (
                <div key={name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color }} />
                  <span className="text-xs text-gray-600 flex-1">{name}</span>
                  <span className="text-xs font-bold text-gray-800">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Score by topic bar chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-700 mb-4">Score by Topic</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={topicData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="topic" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={50} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => [`${v}%`, "Score"]} />
              <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                {topicData.map((entry, i) => (
                  <Cell key={i} fill={entry.score >= 80 ? "#10b981" : entry.score >= 60 ? "#f59e0b" : "#ef4444"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Ebbinghaus Forgetting Curve ────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in hover:shadow-lg transition-shadow duration-300">
        <div className="flex items-center justify-between mb-1">
          <div>
            <h2 className="font-semibold text-gray-800">Ebbinghaus Forgetting Curve</h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Memory retention decays exponentially without review. <strong>Spaced repetition</strong> resets the curve at optimal intervals, dramatically improving long-term retention.
            </p>
          </div>
          <div className="flex gap-1">
            {(["both", "noReview", "spaced"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setCurveView(v)}
                className={clsx(
                  "px-2.5 py-1 text-[10px] font-medium rounded-full transition-colors",
                  curveView === v ? "bg-blue-100 text-blue-700" : "text-gray-400 hover:text-gray-600",
                )}
              >
                {v === "both" ? "Compare" : v === "noReview" ? "Without Review" : "With Spaced Rep"}
              </button>
            ))}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={forgettingCurveData} margin={{ left: -10, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="day" tick={{ fontSize: 11 }} label={{ value: "Days since learning", position: "insideBottom", offset: -2, fontSize: 10 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              formatter={(v: number, name: string) => [
                `${v}%`,
                name === "withoutReview" ? "Without Review" : "With Spaced Repetition",
              ]}
              labelFormatter={(d) => `Day ${d}`}
            />
            {(curveView === "both" || curveView === "noReview") && (
              <Area
                type="monotone" dataKey="withoutReview" name="withoutReview"
                stroke="#ef4444" fill="#fee2e2" fillOpacity={0.5} strokeWidth={2}
                dot={false}
              />
            )}
            {(curveView === "both" || curveView === "spaced") && (
              <Area
                type="monotone" dataKey="withSpacedRep" name="withSpacedRep"
                stroke="#10b981" fill="#d1fae5" fillOpacity={0.5} strokeWidth={2}
                dot={false}
              />
            )}
            <Legend
              formatter={(value) => (value === "withoutReview" ? "Without Review" : "With Spaced Repetition")}
              wrapperStyle={{ fontSize: 11 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* ── Row 2: Spaced Repetition Schedule + Memory Retention ──── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Spaced repetition review schedule */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-4">
            <CalendarClock size={16} className="text-blue-600" />
            <h2 className="font-semibold text-gray-800">Review Schedule</h2>
            {overdueCount > 0 && (
              <span className="bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full">
                {overdueCount} overdue
              </span>
            )}
          </div>
          <div className="space-y-2">
            {reviewSchedule.map(({ topic, nextReview, retention, interval, urgency }) => (
              <div
                key={topic}
                className={clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 border transition-all hover:shadow-sm",
                  urgency === "overdue" ? "bg-red-50 border-red-200" :
                  urgency === "soon"    ? "bg-amber-50 border-amber-200" :
                                          "bg-gray-50 border-gray-100",
                )}
              >
                <div className={clsx(
                  "w-2 h-2 rounded-full shrink-0",
                  urgency === "overdue" ? "bg-red-500 animate-pulse" :
                  urgency === "soon"    ? "bg-amber-500" : "bg-green-500",
                )} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{topic}</p>
                  <p className="text-[10px] text-gray-400">Interval: {interval}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className={clsx("text-xs font-semibold", urgency === "overdue" ? "text-red-600" : "text-gray-600")}>
                    {nextReview}
                  </p>
                  <p className="text-[10px] text-gray-400">{retention}% retained</p>
                </div>
                {urgency === "overdue" && (
                  <button className="shrink-0 bg-red-600 hover:bg-red-700 text-white text-[10px] font-semibold px-2 py-1 rounded-md transition-colors flex items-center gap-1">
                    <RefreshCw size={10} /> Review
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Memory retention per topic */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-4">
            <Brain size={16} className="text-purple-600" />
            <h2 className="font-semibold text-gray-800">Predicted Memory Retention</h2>
          </div>
          <div className="space-y-3">
            {topicData.map(({ topic, retention, stability }) => (
              <div key={topic} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{topic}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-gray-400">S={stability.toFixed(1)}</span>
                    <span className={clsx(
                      "text-sm font-bold",
                      retention >= 80 ? "text-green-600" : retention >= 60 ? "text-amber-600" : "text-red-500",
                    )}>
                      {retention}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={clsx(
                      "h-2 rounded-full transition-all duration-1000",
                      retention >= 80 ? "bg-gradient-to-r from-green-400 to-green-500" :
                      retention >= 60 ? "bg-gradient-to-r from-amber-400 to-amber-500" :
                                        "bg-gradient-to-r from-red-400 to-red-500",
                    )}
                    style={{ width: `${retention}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-gray-400 mt-3">
            S = memory stability factor. Higher values mean slower forgetting. Based on the Ebbinghaus model: R(t) = e<sup>-t/S</sup>
          </p>
        </div>
      </div>

      {/* ── Study Time + Learning Method Effectiveness ───────────── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Study time line chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-700 mb-4">Daily Study Activity</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timelineData} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line type="monotone" dataKey="minutes" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} name="Minutes" />
              <Line type="monotone" dataKey="questions" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} name="Questions" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Learning method effectiveness */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={16} className="text-amber-600" />
            <h2 className="font-semibold text-gray-800">Learning Method Effectiveness</h2>
          </div>
          <p className="text-[10px] text-gray-400 mb-3">
            Based on cognitive science research. EduLoop prioritises the most effective methods.
          </p>
          <div className="space-y-2.5">
            {methodEffectiveness.map(({ method, effectiveness }) => (
              <div key={method} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-700">{method}</span>
                  <span className={clsx(
                    "text-xs font-bold",
                    effectiveness >= 80 ? "text-green-600" : effectiveness >= 60 ? "text-amber-600" : "text-red-500",
                  )}>
                    {effectiveness}%
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className={clsx(
                      "h-1.5 rounded-full transition-all duration-700",
                      effectiveness >= 80 ? "bg-green-500" : effectiveness >= 60 ? "bg-amber-500" : "bg-red-400",
                    )}
                    style={{ width: `${effectiveness}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
            <p className="text-[10px] text-blue-600 font-medium">
              EduLoop uses <strong>active recall</strong> (flashcards), <strong>spaced repetition</strong> (review scheduling), and <strong>interleaved practice</strong> (mixed topic questions) to maximise your retention.
            </p>
          </div>
        </div>
      </div>

      {/* ── Knowledge gaps ──────────────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in hover:shadow-lg transition-shadow duration-300">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={16} className="text-amber-600" />
          <h2 className="font-semibold text-gray-700">Identified Knowledge Gaps</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {gaps.map(({ topic, gap, priority }) => (
            <div key={topic} className="flex items-center gap-4 py-3">
              <span className={clsx(
                "text-xs font-semibold px-2 py-1 rounded-md whitespace-nowrap",
                priority === "high" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700",
              )}>
                {topic}
              </span>
              <p className="text-sm text-gray-700 flex-1">{gap}</p>
              <span className={clsx(
                "text-[10px] font-bold uppercase px-1.5 py-0.5 rounded",
                priority === "high" ? "bg-red-50 text-red-600" : "bg-amber-50 text-amber-600",
              )}>
                {priority}
              </span>
              <button className="text-blue-600 hover:text-blue-700 transition-colors">
                <ArrowRight size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* ── Detailed mastery table ──────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in">
        <h2 className="font-semibold text-gray-700 mb-3">Topic Mastery Detail</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
              <th className="pb-2">Topic</th>
              <th className="pb-2 text-center">Attempts</th>
              <th className="pb-2 text-center">Score</th>
              <th className="pb-2 text-center">Retention</th>
              <th className="pb-2 text-center">Stability</th>
              <th className="pb-2">Mastery</th>
              <th className="pb-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {topicData.map(({ topic, attempts, score, retention, stability }) => (
              <tr key={topic} className="hover:bg-gray-50 transition-colors">
                <td className="py-2.5 font-medium text-gray-800">{topic}</td>
                <td className="py-2.5 text-center text-gray-500">{attempts}</td>
                <td className={clsx("py-2.5 text-center font-semibold", score >= 80 ? "text-green-600" : score >= 60 ? "text-amber-600" : "text-red-500")}>
                  {score}%
                </td>
                <td className={clsx("py-2.5 text-center font-semibold", retention >= 80 ? "text-green-600" : retention >= 60 ? "text-amber-600" : "text-red-500")}>
                  {retention}%
                </td>
                <td className="py-2.5 text-center text-gray-500">{stability.toFixed(1)}</td>
                <td className="py-2.5">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5 w-28">
                    <div
                      className={clsx("h-1.5 rounded-full", score >= 80 ? "bg-green-500" : score >= 60 ? "bg-amber-500" : "bg-red-400")}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </td>
                <td className="py-2.5 text-center">
                  {score >= 80 ? (
                    <CheckCircle2 size={14} className="text-green-500 mx-auto" />
                  ) : retention < 60 ? (
                    <AlertTriangle size={14} className="text-red-500 mx-auto" />
                  ) : (
                    <TrendingUp size={14} className="text-amber-500 mx-auto" />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── How EduLoop personalises your learning ──────────────────── */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-5 animate-fade-in">
        <h2 className="font-semibold text-blue-900 mb-3">How EduLoop Personalises Your Learning</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              icon: Brain,
              title: "Spaced Repetition",
              desc: "Reviews are scheduled at optimal intervals using the Ebbinghaus forgetting curve model to maximise long-term retention.",
            },
            {
              icon: Target,
              title: "Adaptive Difficulty",
              desc: "Question difficulty adjusts based on your performance history — challenging enough to grow, not so hard you get stuck.",
            },
            {
              icon: Zap,
              title: "Active Recall",
              desc: "Flashcards and retrieval practice strengthen neural pathways more effectively than passive re-reading.",
            },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-white/70 rounded-lg p-4 hover:shadow-md transition-shadow duration-300">
              <div className="bg-blue-100 rounded-full p-2 w-fit mb-2">
                <Icon size={16} className="text-blue-600" />
              </div>
              <p className="text-sm font-semibold text-blue-900">{title}</p>
              <p className="text-xs text-blue-700 mt-1 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
