"use client";

import { useState } from "react";
import {
  Shield, Clock, Target, CheckCircle, FileText, TrendingUp, Brain,
  ChevronRight, BookOpen, Award, Zap, AlertTriangle, Download,
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, PieChart, Pie, Cell, LineChart, Line, Legend,
} from "recharts";

/* ── Simulated Data ──────────────────────────────────────────────────── */

const topics = [
  "Quadratic Equations",
  "Trigonometry",
  "Coordinate Geometry",
  "Logarithms",
  "Polynomials",
  "Statistics & Probability",
];

const difficultyLevels = ["Foundation", "Standard", "Extended"];

const mockQuestions = [
  { id: 1, q: "Solve x² - 5x + 6 = 0", topic: "Quadratic Equations", difficulty: "Foundation", correct: true, time: 42 },
  { id: 2, q: "Find the vertex of y = 2x² - 8x + 3", topic: "Quadratic Equations", difficulty: "Standard", correct: true, time: 78 },
  { id: 3, q: "If sin θ = 3/5, find cos θ (0° < θ < 90°)", topic: "Trigonometry", difficulty: "Foundation", correct: false, time: 95 },
  { id: 4, q: "Solve 2sin²x - sinx - 1 = 0 for 0° ≤ x ≤ 360°", topic: "Trigonometry", difficulty: "Extended", correct: false, time: 120 },
  { id: 5, q: "Find the distance between A(2,3) and B(-1,7)", topic: "Coordinate Geometry", difficulty: "Foundation", correct: true, time: 35 },
  { id: 6, q: "Simplify log₂8 + log₂4", topic: "Logarithms", difficulty: "Foundation", correct: true, time: 28 },
  { id: 7, q: "Factorise x³ - 6x² + 11x - 6", topic: "Polynomials", difficulty: "Standard", correct: true, time: 88 },
  { id: 8, q: "Find P(A∩B) given P(A)=0.4, P(B)=0.5, P(A∪B)=0.7", topic: "Statistics & Probability", difficulty: "Standard", correct: true, time: 55 },
  { id: 9, q: "Find the equation of the tangent to y=x² at (1,1)", topic: "Coordinate Geometry", difficulty: "Extended", correct: false, time: 110 },
  { id: 10, q: "Solve log(x+1) + log(x-1) = log 3", topic: "Logarithms", difficulty: "Standard", correct: true, time: 65 },
];

const topicScores = [
  { topic: "Quadratic",  score: 85 },
  { topic: "Trig",       score: 42 },
  { topic: "Coord Geom", score: 68 },
  { topic: "Logarithms", score: 78 },
  { topic: "Poly",       score: 75 },
  { topic: "Stats",      score: 82 },
];

const radarSkills = [
  { skill: "Accuracy",       value: 70 },
  { skill: "Speed",          value: 62 },
  { skill: "Problem Solving",value: 75 },
  { skill: "Application",    value: 58 },
  { skill: "Reasoning",      value: 68 },
  { skill: "Computation",    value: 82 },
];

const timeDistribution = [
  { name: "Quick (<45s)",   value: 3, color: "#10b981" },
  { name: "Normal (45-90s)",value: 4, color: "#3b82f6" },
  { name: "Slow (>90s)",    value: 3, color: "#ef4444" },
];

const historicalScores = [
  { test: "Test 1", score: 55 },
  { test: "Test 2", score: 62 },
  { test: "Test 3", score: 58 },
  { test: "Test 4", score: 71 },
  { test: "Test 5", score: 70 },
];

/* ── Component ────────────────────────────────────────────────────────── */

type Phase = "setup" | "test" | "report";

export default function EvaluationPage() {
  const [phase, setPhase] = useState<Phase>("setup");
  const [selectedTopics, setSelectedTopics] = useState<string[]>(["Quadratic Equations", "Trigonometry"]);
  const [difficulty, setDifficulty] = useState("Standard");
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [showReport, setShowReport] = useState(false);

  function toggleTopic(t: string) {
    setSelectedTopics((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t],
    );
  }

  function startTest() {
    setPhase("test");
    setCurrentQ(0);
    setAnswers({});
  }

  function finishTest() {
    setPhase("report");
    setShowReport(true);
  }

  /* ── Setup phase ──────────────────────────────────────────────────── */
  if (phase === "setup") {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="relative bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 rounded-2xl p-6 text-white overflow-hidden animate-fade-in">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-white rounded-full" />
            <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-white rounded-full" />
          </div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-1">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <Shield size={20} />
              </div>
              <h1 className="text-2xl font-bold">Personalised Evaluation</h1>
            </div>
            <p className="text-emerald-100 text-sm mt-1 max-w-xl">
              Generate a custom test tailored to your learning history. Our Assessment Agent analyses your performance to identify areas that need attention.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Topic selection */}
          <div className="col-span-2 bg-white rounded-xl border border-gray-200 p-6 animate-fade-in-left">
            <h2 className="font-semibold text-gray-800 mb-1">Select Topics</h2>
            <p className="text-xs text-gray-400 mb-4">Choose the topics you want to be evaluated on</p>
            <div className="grid grid-cols-2 gap-3">
              {topics.map((t) => {
                const sel = selectedTopics.includes(t);
                return (
                  <button
                    key={t}
                    onClick={() => toggleTopic(t)}
                    className={`flex items-center gap-3 p-3.5 rounded-xl border-2 text-sm font-medium transition-all duration-300 text-left ${
                      sel
                        ? "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm shadow-emerald-100"
                        : "border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 transition-colors duration-300 ${sel ? "bg-emerald-500" : "bg-gray-200"}`}>
                      {sel && <CheckCircle size={12} className="text-white" />}
                    </div>
                    {t}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Settings panel */}
          <div className="space-y-5 animate-fade-in-right">
            {/* Difficulty */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-800 text-sm mb-3">Difficulty Level</h3>
              <div className="space-y-2">
                {difficultyLevels.map((d) => (
                  <button
                    key={d}
                    onClick={() => setDifficulty(d)}
                    className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                      difficulty === d
                        ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-sm"
                        : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Test info */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-800 text-sm mb-3">Test Configuration</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2"><Target size={13} /> Questions</span>
                  <span className="font-semibold text-gray-800">10</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2"><Clock size={13} /> Est. Time</span>
                  <span className="font-semibold text-gray-800">15 min</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2"><Brain size={13} /> Agent</span>
                  <span className="font-semibold text-purple-600">Assessment</span>
                </div>
              </div>
            </div>

            {/* AI insight */}
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-4">
              <div className="flex items-start gap-2">
                <Zap size={14} className="text-amber-600 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-amber-800">AI Recommendation</p>
                  <p className="text-[11px] text-amber-700 mt-1">Based on your retention forecast, we suggest focusing on <strong>Trigonometry</strong> and <strong>Coordinate Geometry</strong> -- both are predicted to decay below 50% this week.</p>
                </div>
              </div>
            </div>

            <button
              onClick={startTest}
              disabled={selectedTopics.length === 0}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-3 rounded-xl transition-all duration-300 hover:shadow-lg hover:scale-[1.02] disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              Generate Test <ChevronRight size={16} />
            </button>
          </div>
        </div>

        {/* Historical performance */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 animate-fade-in">
          <h2 className="font-semibold text-gray-800 mb-1">Your Evaluation History</h2>
          <p className="text-xs text-gray-400 mb-4">Performance trend across your last 5 evaluations</p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={historicalScores} margin={{ left: -20, right: 10, top: 5, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="test" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
              <Tooltip formatter={(v: number) => [`${v}%`, "Score"]} />
              <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4, fill: "#10b981" }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  /* ── Test phase ───────────────────────────────────────────────────── */
  if (phase === "test") {
    const question = mockQuestions[currentQ];
    const progress = ((currentQ + 1) / mockQuestions.length) * 100;

    return (
      <div className="space-y-6">
        {/* Progress bar header */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Shield size={16} className="text-emerald-600" />
              <h2 className="font-semibold text-gray-800">Evaluation in Progress</h2>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1"><Target size={13} /> {currentQ + 1} / {mockQuestions.length}</span>
              <span className="flex items-center gap-1"><Clock size={13} /> 12:34</span>
            </div>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-teal-500 h-full rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question card */}
        <div className="bg-white rounded-2xl border border-gray-200 p-8 animate-scale-in" key={currentQ}>
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-emerald-50 text-emerald-700 text-[10px] font-semibold px-2 py-0.5 rounded-full">{question.topic}</span>
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
              question.difficulty === "Foundation" ? "bg-blue-50 text-blue-600" :
              question.difficulty === "Standard" ? "bg-amber-50 text-amber-600" :
              "bg-red-50 text-red-600"
            }`}>{question.difficulty}</span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-3 mb-6">Q{currentQ + 1}. {question.q}</h3>

          {/* Answer area */}
          <textarea
            className="w-full border border-gray-200 rounded-xl p-4 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none transition-all duration-200"
            rows={4}
            placeholder="Type your working and answer here..."
            value={answers[currentQ] || ""}
            onChange={(e) => setAnswers({ ...answers, [currentQ]: e.target.value })}
          />

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
              disabled={currentQ === 0}
              className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 disabled:hover:bg-gray-100 rounded-lg transition-colors"
            >
              Previous
            </button>

            {/* Question dots */}
            <div className="flex gap-1.5">
              {mockQuestions.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentQ(i)}
                  className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                    i === currentQ
                      ? "bg-emerald-500 scale-125"
                      : answers[i]
                        ? "bg-emerald-300"
                        : "bg-gray-200"
                  }`}
                />
              ))}
            </div>

            {currentQ < mockQuestions.length - 1 ? (
              <button
                onClick={() => setCurrentQ(currentQ + 1)}
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg transition-all duration-300 flex items-center gap-1 hover:shadow-md"
              >
                Next <ChevronRight size={14} />
              </button>
            ) : (
              <button
                onClick={finishTest}
                className="px-5 py-2 text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 rounded-lg transition-all duration-300 flex items-center gap-1 hover:shadow-md animate-pulse-ring"
              >
                Submit Test
              </button>
            )}
          </div>
        </div>

        {/* Quick overview */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Question Overview</h3>
          <div className="grid grid-cols-10 gap-2">
            {mockQuestions.map((mq, i) => (
              <button
                key={i}
                onClick={() => setCurrentQ(i)}
                className={`h-9 rounded-lg text-xs font-semibold transition-all duration-300 ${
                  i === currentQ
                    ? "bg-emerald-600 text-white shadow-md scale-105"
                    : answers[i]
                      ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                      : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  /* ── Report phase ─────────────────────────────────────────────────── */
  const totalCorrect = mockQuestions.filter((q) => q.correct).length;
  const totalScore = Math.round((totalCorrect / mockQuestions.length) * 100);
  const avgTime = Math.round(mockQuestions.reduce((s, q) => s + q.time, 0) / mockQuestions.length);

  return (
    <div className="space-y-6">
      {/* Report header */}
      <div className="relative bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-2xl p-6 text-white overflow-hidden animate-fade-in">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white rounded-full" />
          <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-white rounded-full" />
        </div>
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <FileText size={20} />
              </div>
              <h1 className="text-2xl font-bold">Evaluation Report</h1>
            </div>
            <p className="text-purple-200 text-sm mt-1">
              Generated by Assessment Agent -- personalised analysis of your performance
            </p>
          </div>
          <button className="flex items-center gap-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Download size={14} />
            Export PDF
          </button>
        </div>
      </div>

      {/* Score hero cards */}
      <div className="grid grid-cols-4 gap-4 stagger-children">
        {[
          { label: "Overall Score",   value: `${totalScore}%`,      icon: Award,       gradient: "from-emerald-500 to-emerald-600", detail: `${totalCorrect}/${mockQuestions.length} correct` },
          { label: "Avg. Time/Q",     value: `${avgTime}s`,         icon: Clock,       gradient: "from-blue-500 to-blue-600", detail: "Target: 60s" },
          { label: "Strongest Topic", value: "Algebra",             icon: TrendingUp,  gradient: "from-violet-500 to-violet-600", detail: "85% accuracy" },
          { label: "Needs Attention", value: "Trigonometry",        icon: AlertTriangle, gradient: "from-red-500 to-red-600", detail: "42% accuracy" },
        ].map(({ label, value, icon: Icon, gradient, detail }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5 animate-scale-in hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
            <div className={`inline-flex p-2.5 rounded-xl bg-gradient-to-br ${gradient} mb-3 shadow-sm group-hover:scale-110 transition-transform duration-300`}>
              <Icon size={16} className="text-white" />
            </div>
            <p className="text-xl font-bold text-gray-900">{value}</p>
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <p className="text-xs text-gray-400 mt-1">{detail}</p>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-3 gap-5">
        {/* Topic scores bar chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-1">Score by Topic</h2>
          <p className="text-[10px] text-gray-400 mb-3">Performance breakdown per topic</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={topicScores} margin={{ left: -20, right: 5, top: 5, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="topic" tick={{ fontSize: 9 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 9 }} unit="%" />
              <Tooltip formatter={(v: number) => [`${v}%`, "Score"]} />
              <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                {topicScores.map((entry, i) => (
                  <Cell key={i} fill={entry.score >= 70 ? "#10b981" : entry.score >= 50 ? "#f59e0b" : "#ef4444"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Skills radar */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-scale-in hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-1">Skill Profile</h2>
          <p className="text-[10px] text-gray-400 mb-3">Multi-dimensional assessment</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarSkills} cx="50%" cy="50%" outerRadius="68%">
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="skill" tick={{ fontSize: 9 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Time pie */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <h2 className="font-semibold text-gray-800 text-sm mb-1">Time Distribution</h2>
          <p className="text-[10px] text-gray-400 mb-3">Answer speed analysis</p>
          <ResponsiveContainer width="100%" height={140}>
            <PieChart>
              <Pie data={timeDistribution} cx="50%" cy="50%" innerRadius={38} outerRadius={60} paddingAngle={3} dataKey="value" stroke="none">
                {timeDistribution.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip formatter={(v) => [`${v} questions`, ""]} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-3 gap-y-1 justify-center mt-2">
            {timeDistribution.map(({ name, color }) => (
              <div key={name} className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-[10px] text-gray-500">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed question results */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-fade-in">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Detailed Results</h2>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-emerald-600"><CheckCircle size={11} /> {totalCorrect} Correct</span>
            <span className="flex items-center gap-1 text-red-500"><AlertTriangle size={11} /> {mockQuestions.length - totalCorrect} Incorrect</span>
          </div>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="px-5 py-3 text-left">#</th>
              <th className="px-5 py-3 text-left">Question</th>
              <th className="px-5 py-3 text-left">Topic</th>
              <th className="px-5 py-3 text-left">Difficulty</th>
              <th className="px-5 py-3 text-center">Time</th>
              <th className="px-5 py-3 text-center">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {mockQuestions.map((q) => (
              <tr key={q.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3 text-gray-400 font-medium">{q.id}</td>
                <td className="px-5 py-3 text-gray-800 max-w-xs truncate">{q.q}</td>
                <td className="px-5 py-3"><span className="text-[10px] bg-gray-100 text-gray-600 font-medium px-2 py-0.5 rounded-full">{q.topic}</span></td>
                <td className="px-5 py-3">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    q.difficulty === "Foundation" ? "bg-blue-50 text-blue-600" :
                    q.difficulty === "Standard" ? "bg-amber-50 text-amber-600" :
                    "bg-red-50 text-red-600"
                  }`}>{q.difficulty}</span>
                </td>
                <td className="px-5 py-3 text-center text-gray-600">{q.time}s</td>
                <td className="px-5 py-3 text-center">
                  {q.correct ? (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                      <CheckCircle size={10} /> Correct
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-red-600 bg-red-50 px-2 py-0.5 rounded-full">
                      <AlertTriangle size={10} /> Incorrect
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* AI Diagnostics */}
      <div className="grid grid-cols-2 gap-5">
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border border-red-200 rounded-xl p-5 animate-fade-in-left hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="bg-red-500 rounded-lg p-1.5">
              <AlertTriangle size={14} className="text-white" />
            </div>
            <h3 className="font-semibold text-red-800 text-sm">Misconceptions Detected</h3>
          </div>
          <ul className="space-y-2.5 text-sm text-red-700">
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
              <span><strong>Trigonometry:</strong> Confusing sine and cosine ratios when angle is not in standard position</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
              <span><strong>Trig Equations:</strong> Missing solutions in the 3rd and 4th quadrants for sin-based equations</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
              <span><strong>Coord Geometry:</strong> Incorrect application of point-slope form for tangent lines</span>
            </li>
          </ul>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-5 animate-fade-in-right hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="bg-emerald-500 rounded-lg p-1.5">
              <Zap size={14} className="text-white" />
            </div>
            <h3 className="font-semibold text-emerald-800 text-sm">Personalised Next Steps</h3>
          </div>
          <ul className="space-y-2.5 text-sm text-emerald-700">
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span>Schedule a <strong>Trigonometry review</strong> lesson with the Teaching Agent within 24 hours</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span>Practice <strong>CAST rule exercises</strong> to reinforce quadrant identification</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span>Use <strong>flashcard mode</strong> on Learn page for active recall of coordinate geometry formulas</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span>Re-evaluate in <strong>3 days</strong> to confirm retention (spaced repetition)</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-4">
        <button
          onClick={() => { setPhase("setup"); setShowReport(false); }}
          className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-semibold py-3 rounded-xl transition-all duration-300 hover:shadow-lg flex items-center justify-center gap-2"
        >
          <Shield size={16} /> Take Another Evaluation
        </button>
        <button
          onClick={() => {}}
          className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-xl transition-all duration-300 hover:shadow-lg flex items-center justify-center gap-2"
        >
          <BookOpen size={16} /> Study Weak Topics
        </button>
      </div>
    </div>
  );
}
