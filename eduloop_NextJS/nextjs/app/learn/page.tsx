"use client";

import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import {
  BookOpen, Loader2, ChevronDown, ChevronUp, AlertCircle,
  Volume2, Video, RefreshCw, Target, ChevronLeft, ChevronRight, Lightbulb,
} from "lucide-react";
import MathContent from "@/components/MathContent";
import { generateLesson, generateTTS, paraphraseForTTS, createVideo, getVideoStatus } from "@/lib/api";
import { SYLLABUSES, TOPICS, type Lesson, type ContentBlock } from "@/lib/types";
import clsx from "clsx";

const TABS = ["Lesson", "Flashcards", "Objectives & Advice", "Practice Ideas", "RAG Sources"] as const;
type Tab = (typeof TABS)[number];

const BLOCK_STYLES: Record<ContentBlock["type"], { label: string; className: string; warn?: boolean }> = {
  introduction:   { label: "Introduction",    className: "bg-blue-50 border-blue-200" },
  concept:        { label: "Concept",          className: "bg-white border-gray-200" },
  example:        { label: "Worked Example",   className: "bg-green-50 border-green-200" },
  common_pitfall: { label: "Common Pitfall",   className: "bg-amber-50 border-amber-200", warn: true },
  summary:        { label: "Summary",          className: "bg-emerald-50 border-emerald-200" },
};

export default function LearnPage() {
  const [syllabus, setSyllabus] = useState<string>(SYLLABUSES[0]);
  const [topic, setTopic]       = useState(TOPICS[SYLLABUSES[0]][0]);
  const [loading, setLoading]   = useState(false);
  const [lesson, setLesson]     = useState<Lesson | null>(null);
  const [error, setError]       = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("Lesson");

  // ── Audio state ────────────────────────────────────────────────────
  const [audioSrc, setAudioSrc]       = useState<string | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  // ── Video state ────────────────────────────────────────────────────
  const [videoUrl, setVideoUrl]       = useState<string | null>(null);
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoStatus, setVideoStatus] = useState<string>("");
  const videoTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Flashcard state ──────────────────────────────────────────────
  const [currentCard, setCurrentCard] = useState(0);
  const [cardFlipped, setCardFlipped] = useState(false);

  const topics = TOPICS[syllabus] ?? [];

  // cleanup video polling on unmount
  useEffect(() => {
    return () => {
      if (videoTimerRef.current) clearInterval(videoTimerRef.current);
    };
  }, []);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setAudioSrc(null);
    setVideoUrl(null);
    setVideoStatus("");
    try {
      const result = await generateLesson(topic, "intermediate", {});
      setLesson(result);
      setActiveTab("Lesson");
      setCurrentCard(0);
      setCardFlipped(false);
      // Auto-generate audio narration after lesson loads
      autoNarrate(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  // ── Auto-narrate: paraphrase + TTS ─────────────────────────────────
  async function autoNarrate(lessonData: Lesson) {
    setAudioLoading(true);
    try {
      const llm = lessonData.llm_response;
      const rawContent = (llm.content_blocks ?? [])
        .map((b) => `[${b.type}] ${b.text}`)
        .join("\n\n");
      const paraphrased = await paraphraseForTTS(rawContent, lessonData.topic, "lesson");
      const { audio_hex } = await generateTTS(paraphrased.substring(0, 3000));
      const bytes = new Uint8Array(audio_hex.match(/.{1,2}/g)!.map((b) => parseInt(b, 16)));
      const blob = new Blob([bytes], { type: "audio/mpeg" });
      const url = URL.createObjectURL(blob);
      setAudioSrc(url);
      setTimeout(() => { audioRef.current?.play().catch(() => {}); }, 300);
    } catch (e) {
      console.error("Auto-narrate failed:", e);
    } finally {
      setAudioLoading(false);
    }
  }

  // ── Generate audio narration (manual) ──────────────────────────────
  const handleAudio = useCallback(async () => {
    if (!lesson?.llm_response) return;
    setAudioLoading(true);
    try {
      const llm = lesson.llm_response;
      const rawContent = (llm.content_blocks ?? [])
        .map((b) => `[${b.type}] ${b.text}`)
        .join("\n\n");
      const paraphrased = await paraphraseForTTS(rawContent, lesson.topic, "lesson");
      const { audio_hex } = await generateTTS(paraphrased.substring(0, 3000));
      const bytes = new Uint8Array(audio_hex.match(/.{1,2}/g)!.map((b) => parseInt(b, 16)));
      const blob = new Blob([bytes], { type: "audio/mpeg" });
      const url = URL.createObjectURL(blob);
      setAudioSrc(url);
      setTimeout(() => { audioRef.current?.play().catch(() => {}); }, 100);
    } catch (e) {
      console.error("TTS failed:", e);
      setError("Audio generation failed — check console for details.");
    } finally {
      setAudioLoading(false);
    }
  }, [lesson]);

  // ── Generate instruction video ─────────────────────────────────────
  const handleVideo = useCallback(async () => {
    setVideoLoading(true);
    setVideoStatus("Submitting…");
    setVideoUrl(null);
    try {
      const prompt =
        `A warm, professional math teacher sitting at a desk, directly facing the camera in a medium close-up shot. ` +
        `The teacher speaks to the viewer about "${topic}" with natural hand gestures, ` +
        `maintaining steady eye contact. Soft studio lighting, modern minimalist classroom background, ` +
        `shallow depth of field. The teacher smiles and nods encouragingly. Cinematic, 4K quality.`;

      const { task_id } = await createVideo(prompt);
      setVideoStatus("Processing (this may take a few minutes)…");

      if (videoTimerRef.current) clearInterval(videoTimerRef.current);
      videoTimerRef.current = setInterval(async () => {
        try {
          const st = await getVideoStatus(task_id);
          if (st.status === "Success" && st.download_url) {
            setVideoUrl(st.download_url);
            setVideoStatus("Ready!");
            setVideoLoading(false);
            if (videoTimerRef.current) clearInterval(videoTimerRef.current);
          } else if (st.status === "Fail") {
            setVideoStatus("Video generation failed.");
            setVideoLoading(false);
            if (videoTimerRef.current) clearInterval(videoTimerRef.current);
          } else {
            setVideoStatus(`Processing… (status: ${st.status})`);
          }
        } catch {
          // keep polling
        }
      }, 10_000);
    } catch (e) {
      console.error("Video generation failed:", e);
      setVideoStatus("Failed to start video generation.");
      setVideoLoading(false);
    }
  }, [topic]);

  const llm = lesson?.llm_response;

  // ── Flashcard data (active recall from lesson content) ─────────────
  const flashcards = useMemo(() => {
    if (!llm?.content_blocks) return [];
    return llm.content_blocks
      .filter((b) => b.type === "concept" || b.type === "example")
      .map((b, i) => ({
        front: b.type === "concept" ? `Key Concept ${i + 1}` : `Worked Example ${i + 1}`,
        back: b.text,
      }));
  }, [llm]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 animate-fade-in">Personalised Learning</h1>

      <div className="grid grid-cols-[260px_1fr] gap-6 items-start">
        {/* ── Left panel ─────────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4 sticky top-0 animate-fade-in-left">
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

          {/* ── Media buttons ─────────────────────────────────────── */}
          {lesson && (
            <div className="border-t border-gray-100 pt-4 space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">AI Media</p>

              <button
                onClick={handleAudio}
                disabled={audioLoading}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors"
              >
                {audioLoading ? <Loader2 size={14} className="animate-spin" /> : <Volume2 size={14} />}
                {audioLoading ? "Generating…" : "Audio Narration"}
              </button>

              <button
                onClick={handleVideo}
                disabled={videoLoading}
                className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors"
              >
                {videoLoading ? <Loader2 size={14} className="animate-spin" /> : <Video size={14} />}
                {videoLoading ? "Generating…" : "Video Instruction"}
              </button>
            </div>
          )}
        </div>

        {/* ── Right panel ────────────────────────────────────────────────── */}
        <div className="space-y-4">
          {/* ── Audio player ─────────────────────────────────────────── */}
          {audioSrc && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 space-y-2 animate-scale-in">
              <p className="text-sm font-semibold text-indigo-800">Audio Narration</p>
              <audio ref={audioRef} controls src={audioSrc} className="w-full" />
            </div>
          )}
          {audioLoading && !audioSrc && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 animate-fade-in">
              <div className="flex items-center gap-2 text-sm text-indigo-600">
                <Loader2 size={14} className="animate-spin" />
                Preparing personalised audio narration…
              </div>
              <div className="mt-2 h-2 rounded-full overflow-hidden bg-indigo-100">
                <div className="h-full bg-gradient-to-r from-indigo-400 via-blue-400 to-indigo-400 animate-gradient-x rounded-full" />
              </div>
            </div>
          )}

          {/* ── Video player ─────────────────────────────────────────── */}
          {(videoUrl || videoStatus) && (
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 space-y-2 animate-scale-in">
              <p className="text-sm font-semibold text-purple-800">Video Instruction</p>
              {videoUrl ? (
                <video controls className="w-full rounded-lg" src={videoUrl} />
              ) : (
                <div className="flex items-center gap-2 text-sm text-purple-600">
                  <RefreshCw size={14} className="animate-spin" />
                  {videoStatus}
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!lesson && !loading && (
            <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-400 animate-fade-in">
              <BookOpen size={40} className="mx-auto mb-3 opacity-30" />
              <p>Select a topic and click <strong>Generate Lesson</strong></p>
            </div>
          )}

          {loading && (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center animate-fade-in">
              <Loader2 size={40} className="mx-auto mb-4 text-blue-500 animate-spin" />
              <p className="text-gray-600 font-medium">Generating your personalised lesson…</p>
              <p className="text-gray-400 text-sm mt-1">This may take up to a minute</p>
              <div className="mt-4 mx-auto w-64 h-2 rounded-full overflow-hidden bg-gray-100">
                <div className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-blue-500 animate-gradient-x rounded-full" />
              </div>
            </div>
          )}

          {lesson && (
            <>
              {/* Topic header */}
              <div className="bg-white rounded-xl border border-gray-200 px-5 py-4 animate-fade-in">
                <p className="text-xs text-gray-400 uppercase tracking-wide">{syllabus}</p>
                <h2 className="text-xl font-bold text-gray-900">{lesson.topic}</h2>
              </div>

              {/* Personalisation indicator */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl px-5 py-3 flex items-center gap-3 animate-fade-in">
                <div className="bg-blue-100 rounded-full p-1.5">
                  <Target size={14} className="text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-800">Lesson adapted to your learning profile</p>
                  <p className="text-xs text-blue-500">Intermediate level · Visual learner · Focus on conceptual understanding</p>
                </div>
                <span className="shrink-0 bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide">Adapted</span>
              </div>

              {/* Error from LLM */}
              {llm?.status === "error" && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
                  {llm.error}
                </div>
              )}

              {/* Tabs */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-scale-in">
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
                  {activeTab === "Lesson" && (
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

                  {/* ── Tab: Flashcards (Active Recall) ──────────────────── */}
                  {activeTab === "Flashcards" && (
                    <div className="space-y-4">
                      <p className="text-xs text-gray-500">
                        Active recall practice — click a card to reveal, then self-assess.
                        Based on the <strong>testing effect</strong>: retrieving information strengthens memory more than re-reading.
                      </p>
                      {flashcards.length === 0 ? (
                        <p className="text-gray-400 text-sm">Generate a lesson first to create flashcards.</p>
                      ) : (
                        <>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-500">Card {currentCard + 1} of {flashcards.length}</span>
                            <div className="flex gap-1">
                              {flashcards.map((_, i) => (
                                <div key={i} className={clsx("w-2 h-2 rounded-full transition-colors", i === currentCard ? "bg-blue-500" : "bg-gray-200")} />
                              ))}
                            </div>
                          </div>
                          <button
                            onClick={() => setCardFlipped(!cardFlipped)}
                            className="w-full text-left min-h-[180px] bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6 transition-all duration-300 hover:shadow-md hover:border-blue-300 cursor-pointer animate-scale-in"
                          >
                            {!cardFlipped ? (
                              <div className="flex flex-col items-center justify-center gap-3">
                                <Lightbulb size={28} className="text-blue-400" />
                                <p className="text-lg font-bold text-blue-800">{flashcards[currentCard].front}</p>
                                <p className="text-xs text-blue-400">Click to reveal</p>
                              </div>
                            ) : (
                              <MathContent content={flashcards[currentCard].back} />
                            )}
                          </button>
                          <div className="flex items-center justify-between">
                            <button
                              onClick={() => { setCurrentCard((c) => Math.max(0, c - 1)); setCardFlipped(false); }}
                              disabled={currentCard === 0}
                              className="flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-blue-600 disabled:opacity-30 transition-colors"
                            >
                              <ChevronLeft size={16} /> Previous
                            </button>
                            <button
                              onClick={() => { setCurrentCard((c) => Math.min(flashcards.length - 1, c + 1)); setCardFlipped(false); }}
                              disabled={currentCard === flashcards.length - 1}
                              className="flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-blue-600 disabled:opacity-30 transition-colors"
                            >
                              Next <ChevronRight size={16} />
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* ── Tab: Objectives & Advice ─────────────────────────── */}
                  {activeTab === "Objectives & Advice" && (
                    <div className="space-y-6">
                      <div>
                        <h3 className="font-semibold text-gray-800 mb-3">Learning Objectives</h3>
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
                          <p className="text-xs font-semibold text-blue-600 mb-2">Tutor's Advice</p>
                          <MathContent content={llm.constructive_advice} />
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── Tab: Practice Ideas ───────────────────────────────── */}
                  {activeTab === "Practice Ideas" && (
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
                  {activeTab === "RAG Sources" && (
                    <div className="space-y-2 text-sm">
                      <p className="text-xs text-gray-500">
                        These source documents were fed to MiniMax as context.
                      </p>
                      {(lesson.dse_references ?? []).map((src) => (
                        <div key={src} className="flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-gray-400 shrink-0" />
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
