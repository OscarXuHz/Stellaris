"use client";

import { useState } from "react";
import { PenLine, Loader2, ChevronDown, ChevronUp, CheckCircle2, AlertCircle } from "lucide-react";
import MathContent from "@/components/MathContent";
import { getQuestions, formatQuestionsLatex, evaluateAnswer } from "@/lib/api";
import {
  SYLLABUSES, TOPICS,
  type RagChunk, type AssessmentResult,
} from "@/lib/types";
import clsx from "clsx";

interface QuestionState {
  question: RagChunk;
  answer: string;
  result: AssessmentResult | null;
  loading: boolean;
  open: boolean;
}

export default function PracticePage() {
  const [syllabus, setSyllabus]       = useState<string>(SYLLABUSES[0]);
  const [topic, setTopic]             = useState(TOPICS[SYLLABUSES[0]][0]);
  const [numQ, setNumQ]               = useState(3);
  const [showMS, setShowMS]           = useState(false);
  const [loadingQ, setLoadingQ]       = useState(false);
  const [marking, setMarking]         = useState<RagChunk[]>([]);
  const [questions, setQuestions]     = useState<QuestionState[]>([]);
  const [loadErr, setLoadErr]         = useState<string | null>(null);

  const topics = TOPICS[syllabus] ?? [];

  // ── Load + format questions ────────────────────────────────────────
  async function handleStart() {
    setLoadingQ(true);
    setLoadErr(null);
    setQuestions([]);
    try {
      const { questions: raw, marking: ms } = await getQuestions(topic, numQ);
      // Format with LaTeX via MiniMax
      const formatted = await formatQuestionsLatex(raw, topic);
      setMarking(ms);
      setQuestions(
        formatted.map((q) => ({ question: q, answer: "", result: null, loading: false, open: true })),
      );
    } catch (e) {
      setLoadErr(e instanceof Error ? e.message : "Failed to load questions");
    } finally {
      setLoadingQ(false);
    }
  }

  // ── Submit a single answer ─────────────────────────────────────────
  async function handleSubmit(idx: number) {
    const qs = questions[idx];
    if (!qs.answer.trim()) return;

    setQuestions((prev) =>
      prev.map((q, i) => (i === idx ? { ...q, loading: true } : q)),
    );
    try {
      const result = await evaluateAnswer(topic, qs.question.text, qs.answer, "intermediate");
      setQuestions((prev) =>
        prev.map((q, i) => (i === idx ? { ...q, result, loading: false } : q)),
      );
    } catch {
      setQuestions((prev) =>
        prev.map((q, i) => (i === idx ? { ...q, loading: false } : q)),
      );
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">✏️ Practice & Assessment</h1>

      <div className="grid grid-cols-[260px_1fr] gap-6 items-start">
        {/* ── Left panel ─────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4 sticky top-0">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Assessment Setup</h2>

          <div className="space-y-1">
            <label className="text-xs text-gray-500">Syllabus</label>
            <select
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={syllabus}
              onChange={(e) => { setSyllabus(e.target.value); setTopic(TOPICS[e.target.value][0]); }}
            >
              {SYLLABUSES.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-gray-500">Topic</label>
            <select
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            >
              {topics.map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-gray-500">Questions: {numQ}</label>
            <input
              type="range" min={1} max={8} value={numQ}
              onChange={(e) => setNumQ(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
          </div>

          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={showMS} onChange={(e) => setShowMS(e.target.checked)} className="accent-blue-600" />
            Show marking schemes
          </label>

          <button
            onClick={handleStart}
            disabled={loadingQ}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors"
          >
            {loadingQ ? <Loader2 size={15} className="animate-spin" /> : <PenLine size={15} />}
            {loadingQ ? "Loading & formatting…" : "Start Assessment"}
          </button>
        </div>

        {/* ── Right panel ────────────────────────────────────────────── */}
        <div className="space-y-4">
          {loadErr && (
            <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              {loadErr}
            </div>
          )}

          {questions.length === 0 && !loadingQ && (
            <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400">
              <PenLine size={40} className="mx-auto mb-3 opacity-30" />
              <p>Configure and click <strong>Start Assessment</strong></p>
            </div>
          )}

          {questions.map((qs, idx) => {
            const meta = qs.question.metadata;
            const label = meta.year ? `DSE ${meta.year} ${meta.paper ?? ""}` : qs.question.source;
            const eval_ = qs.result?.llm_response;

            return (
              <div key={idx} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                {/* Question header */}
                <button
                  className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
                  onClick={() =>
                    setQuestions((prev) =>
                      prev.map((q, i) => (i === idx ? { ...q, open: !q.open } : q)),
                    )
                  }
                >
                  <div className="flex items-center gap-3">
                    <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-1 rounded-md">
                      Q{idx + 1}
                    </span>
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    {qs.result && (
                      <CheckCircle2 size={15} className="text-green-500" />
                    )}
                  </div>
                  {qs.open ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </button>

                {qs.open && (
                  <div className="px-5 pb-5 space-y-4 border-t border-gray-100 pt-4">
                    {/* Question text (LaTeX rendered) */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <MathContent content={qs.question.text} />
                    </div>
                    <p className="text-xs text-gray-400">Source: {qs.question.source} · Score: {qs.question.score}</p>

                    {/* Answer input */}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-600">Your Answer</label>
                      <textarea
                        rows={4}
                        placeholder="Write your working and answer here…"
                        value={qs.answer}
                        onChange={(e) =>
                          setQuestions((prev) =>
                            prev.map((q, i) => (i === idx ? { ...q, answer: e.target.value } : q)),
                          )
                        }
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                      />
                    </div>

                    <button
                      onClick={() => handleSubmit(idx)}
                      disabled={qs.loading || !qs.answer.trim()}
                      className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors"
                    >
                      {qs.loading && <Loader2 size={13} className="animate-spin" />}
                      {qs.loading ? "Evaluating…" : "Submit & Evaluate"}
                    </button>

                    {/* Evaluation result */}
                    {eval_ && (
                      <div className="space-y-3 border-t border-gray-100 pt-4">
                        <p className="text-sm font-semibold text-gray-800">📊 AI Evaluation</p>

                        {eval_.status === "error" ? (
                          <p className="text-sm text-red-600">{eval_.error}</p>
                        ) : (
                          <>
                            {eval_.score_percentage !== undefined && (
                              <div className="flex items-center gap-3">
                                <div className={clsx(
                                  "text-2xl font-bold",
                                  (eval_.score_percentage ?? 0) >= 70 ? "text-green-600" : "text-amber-600",
                                )}>
                                  {eval_.score_percentage}%
                                </div>
                                <div className="flex-1 bg-gray-200 rounded-full h-2">
                                  <div
                                    className={clsx("h-2 rounded-full", (eval_.score_percentage ?? 0) >= 70 ? "bg-green-500" : "bg-amber-500")}
                                    style={{ width: `${eval_.score_percentage}%` }}
                                  />
                                </div>
                              </div>
                            )}

                            {(eval_.diagnostic_report?.strengths ?? []).length > 0 && (
                              <div className="bg-green-50 border border-green-200 rounded-lg p-3 space-y-1">
                                <p className="text-xs font-semibold text-green-700">✅ Strengths</p>
                                {eval_.diagnostic_report!.strengths.map((s, i) => (
                                  <div key={i}><MathContent content={s} compact /></div>
                                ))}
                              </div>
                            )}

                            {(eval_.diagnostic_report?.knowledge_gaps ?? []).length > 0 && (
                              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 space-y-1">
                                <p className="text-xs font-semibold text-amber-700">⚠️ Knowledge Gaps</p>
                                {eval_.diagnostic_report!.knowledge_gaps.map((g, i) => (
                                  <div key={i}><MathContent content={g} compact /></div>
                                ))}
                              </div>
                            )}

                            {eval_.diagnostic_report?.constructive_feedback && (
                              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                <p className="text-xs font-semibold text-blue-700 mb-1">💬 Feedback</p>
                                <MathContent content={eval_.diagnostic_report.constructive_feedback} compact />
                              </div>
                            )}

                            {eval_.diagnostic_report?.misconception_analysis && (
                              <div className="bg-rose-50 border border-rose-200 rounded-lg p-3">
                                <p className="text-xs font-semibold text-rose-700 mb-1">🔍 Misconception</p>
                                <MathContent content={eval_.diagnostic_report.misconception_analysis} compact />
                              </div>
                            )}

                            {eval_.next_step_recommendation && (
                              <p className="text-xs text-gray-500">
                                Next step: <strong>{eval_.next_step_recommendation.action}</strong>
                                {" — "}focus on: {eval_.next_step_recommendation.focus_topics_for_teacher.join(", ")}
                              </p>
                            )}
                          </>
                        )}
                      </div>
                    )}

                    {/* Marking scheme toggle */}
                    {showMS && marking[idx] && (
                      <div className="border-t border-gray-100 pt-4">
                        <p className="text-xs font-semibold text-gray-600 mb-2">📋 Official Marking Scheme</p>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <MathContent content={marking[idx].text} compact />
                        </div>
                        <p className="text-xs text-gray-400 mt-1">Source: {marking[idx].source}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
