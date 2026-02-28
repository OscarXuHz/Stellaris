import type { Lesson, AssessmentResult, RagChunk, StudentProfile, ChatMessage, ChatResponse } from "./types";

// All requests go to /api/* which next.config.js proxies to http://localhost:8000
const API = "/api";

// ── Teach ─────────────────────────────────────────────────────────────
export async function generateLesson(
  topic: string,
  level: string,
  studentProfile: Partial<StudentProfile> = {},
): Promise<Lesson> {
  const res = await fetch(`${API}/teach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, level, student_profile: studentProfile }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Questions ─────────────────────────────────────────────────────────
export async function getQuestions(
  topic: string,
  n: number,
): Promise<{ questions: RagChunk[]; marking: RagChunk[] }> {
  const res = await fetch(`${API}/questions?topic=${encodeURIComponent(topic)}&n=${n}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Format questions with LaTeX ───────────────────────────────────────
export async function formatQuestionsLatex(
  rawQuestions: RagChunk[],
  topic: string,
): Promise<RagChunk[]> {
  const body = rawQuestions.map((q) => ({ raw_text: q.text, topic }));
  try {
    const res = await fetch(`${API}/format-questions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      // 150 s — backend now parallelises, but give it plenty of headroom
      signal: AbortSignal.timeout(150_000),
    });
    if (!res.ok) {
      const errText = await res.text().catch(() => "(no body)");
      console.error(`[formatQuestionsLatex] ${res.status} ${res.statusText}: ${errText}`);
      return rawQuestions;            // graceful fallback — show original on error
    }
    const data: { formatted: { original: string; formatted: string; answer?: string }[] } = await res.json();
    return rawQuestions.map((q, i) => ({
      ...q,
      text: data.formatted[i]?.formatted ?? q.text,
      answer: data.formatted[i]?.answer ?? "",
    }));
  } catch (err) {
    console.error("[formatQuestionsLatex] fetch failed:", err);
    return rawQuestions;              // network / timeout error — show originals
  }
}

// ── Assess ────────────────────────────────────────────────────────────
export async function evaluateAnswer(
  topic: string,
  questionText: string,
  studentAnswer: string,
  difficulty: string,
): Promise<AssessmentResult> {
  const res = await fetch(`${API}/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic,
      question_text: questionText,
      student_answer: studentAnswer,
      difficulty,
    }),
    signal: AbortSignal.timeout(150_000),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Text-to-Speech (MiniMax T2A) ──────────────────────────────────────
export async function paraphraseForTTS(
  rawContent: string,
  topic: string,
  context: "lesson" | "practice" = "lesson",
): Promise<string> {
  const res = await fetch(`${API}/paraphrase`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_content: rawContent, topic, context }),
    signal: AbortSignal.timeout(90_000),
  });
  if (!res.ok) throw new Error(await res.text());
  const data: { paraphrased: string } = await res.json();
  return data.paraphrased;
}

export async function generateTTS(
  text: string,
  voiceId = "English_Insightful_Speaker",
  speed = 1.0,
): Promise<{ audio_hex: string; audio_length_ms: number; format: string }> {
  const res = await fetch(`${API}/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voice_id: voiceId, speed }),
    signal: AbortSignal.timeout(60_000),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Video generation (MiniMax Hailuo) ─────────────────────────────────
export async function createVideo(
  prompt: string,
  duration = 6,
): Promise<{ task_id: string }> {
  const res = await fetch(`${API}/video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, duration }),
    signal: AbortSignal.timeout(30_000),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getVideoStatus(
  taskId: string,
): Promise<{ task_id: string; status: string; file_id: string; download_url: string }> {
  const res = await fetch(`${API}/video/${taskId}`, {
    signal: AbortSignal.timeout(15_000),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ── Chat / Orchestrator ───────────────────────────────────────────────
export async function chatWithOrchestrator(
  message: string,
  topic: string,
  history: ChatMessage[],
): Promise<ChatResponse> {
  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      topic,
      history: history.map((m) => ({ role: m.role, content: m.content })),
    }),
    signal: AbortSignal.timeout(150_000),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
