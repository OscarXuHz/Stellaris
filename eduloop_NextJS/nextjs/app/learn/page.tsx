"use client";

import { useState } from "react";
import { BookOpen, Loader2, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import MathContent from "@/components/MathContent";
import { generateLesson } from "@/lib/api";
import { SYLLABUSES, TOPICS, type Lesson, type ContentBlock } from "@/lib/types";
import clsx from "clsx";

const TABS = ["📘 Lesson", "🎯 Objectives & Advice", "💡 Practice Ideas", "📚 RAG Sources"] as const;
type Tab = (typeof TABS)[number];

const BLOCK_STYLES: Record<ContentBlock["type"], { label: string; className: string; warn?: boolean }> = {
  introduction:   { label: "📖 Introduction",   className: "bg-blue-50 border-blue-200" },
  concept:        { label: "📘 Concept",         className: "bg-white border-gray-200" },
  example:        { label: "📝 Worked Example",  className: "bg-green-50 border-green-200" },
  common_pitfall: { label: "⚠️ Common Pitfall",  className: "bg-amber-50 border-amber-200", warn: true },
  summary:        { label: "✅ Summary",          className: "bg-emerald-50 border-emerald-200" },
};

export default function LearnPage() {
  const [syllabus, setSyllabus] = useState<string>(SYLLABUSES[0]);
  const [topic, setTopic]       = useState(TOPICS[SYLLABUSES[0]][0]);
  const [loading, setLoading]   = useState(false);
  const [lesson, setLesson]     = useState<Lesson | null>(null);
  const [error, setError]       = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("📘 Lesson");

  const topics = TOPICS[syllabus] ?? [];

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const result = await generateLesson(topic, "intermediate", {});
      setLesson(result);
      setActiveTab("📘 Lesson");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const llm = lesson?.llm_response;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">📖 Learn with Your Personal Tutor</h1>

      <div className="grid grid-cols-[260px_1fr] gap-6 items-start">
        {/* ── Left panel ─────────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4 sticky top-0">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Select Topic</h2>

          <div className="space-y-1">
            <label className="text-xs text-gray-500">Syllabus</label>
            <select
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={syllabus}
              onChange={(e) => {
                setSyllabus(e.target.value);
                setTopic(TOPICS[e.target.value][0]);
              }}
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

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors"
          >
            {loading ? <Loader2 size={15} className="animate-spin" /> : <BookOpen size={15} />}
            {loading ? "Generating…" : "Generate Lesson"}
          </button>

          {lesson && (
            <p className="text-xs text-gray-400 text-center">
              {lesson.rag_chunks_used} RAG chunks · {lesson.dse_references.length} sources
            </p>
          )}
        </div>

        {/* ── Right panel ────────────────────────────────────────────────── */}
        <div className="space-y-4">
          {error && (
            <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!lesson && !loading && (
            <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400">
              <BookOpen size={40} className="mx-auto mb-3 opacity-30" />
              <p>Select a topic and click <strong>Generate Lesson</strong></p>
            </div>
          )}

          {lesson && (
            <>
              {/* Topic header */}
              <div className="bg-white rounded-xl border border-gray-200 px-5 py-4">
                <p className="text-xs text-gray-400 uppercase tracking-wide">{syllabus}</p>
                <h2 className="text-xl font-bold text-gray-900">{lesson.topic}</h2>
              </div>

              {/* Error from LLM */}
              {llm?.status === "error" && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
                  {llm.error}
                </div>
              )}

              {/* Tabs */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="flex border-b border-gray-100 overflow-x-auto">
                  {TABS.map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={clsx(
                        "px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2",
                        activeTab === tab
                          ? "border-blue-600 text-blue-700"
                          : "border-transparent text-gray-500 hover:text-gray-800",
                      )}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                <div className="p-5">
                  {/* ── Tab: Lesson ─────────────────────────────────────── */}
                  {activeTab === "📘 Lesson" && (
                    <div className="space-y-4">
                      {(llm?.content_blocks ?? []).length === 0 && (
                        <p className="text-gray-400 text-sm">No content blocks returned.</p>
                      )}
                      {(llm?.content_blocks ?? []).map((block, i) => {
                        const style = BLOCK_STYLES[block.type] ?? BLOCK_STYLES.concept;
                        return (
                          <div key={i} className={clsx("rounded-xl border p-4", style.className)}>
                            <p className="text-xs font-semibold text-gray-500 mb-2">{style.label}</p>
                            <MathContent content={block.text} />
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* ── Tab: Objectives & Advice ─────────────────────────── */}
                  {activeTab === "🎯 Objectives & Advice" && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="font-semibold text-gray-800 mb-3">🎯 Learning Objectives</h3>
                        <ul className="space-y-2">
                          {(llm?.learning_objectives ?? []).map((obj, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <span className="text-blue-500 mt-0.5">✓</span>
                              <MathContent content={obj} compact />
                            </li>
                          ))}
                        </ul>
                      </div>
                      {llm?.constructive_advice && (
                        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                          <p className="text-xs font-semibold text-blue-600 mb-2">💬 Tutor's Advice</p>
                          <MathContent content={llm.constructive_advice} />
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── Tab: Practice Ideas ───────────────────────────────── */}
                  {activeTab === "💡 Practice Ideas" && (
                    <div className="space-y-3">
                      <p className="text-xs text-gray-500 mb-1">
                        Suggested questions generated by the AI tutor — try them in the Practice section.
                      </p>
                      {(llm?.suggested_questions_for_assessment ?? []).map((q, i) => (
                        <div key={i} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                          <span className="text-xs font-bold text-gray-400 mr-2">Q{i + 1}</span>
                          <MathContent content={q} compact />
                        </div>
                      ))}
                    </div>
                  )}

                  {/* ── Tab: RAG Sources ─────────────────────────────────── */}
                  {activeTab === "📚 RAG Sources" && (
                    <div className="space-y-2 text-sm">
                      <p className="text-xs text-gray-500">
                        These source documents were fed to MiniMax as context.
                      </p>
                      {(lesson.dse_references ?? []).map((src) => (
                        <div key={src} className="flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
                          <span className="text-gray-400">📄</span>
                          <span className="text-gray-700">{src}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
