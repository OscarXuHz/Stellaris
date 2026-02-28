import type { Lesson, AssessmentResult, RagChunk, StudentProfile } from "./types";

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
  const res = await fetch(`${API}/format-questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) return rawQuestions; // graceful fallback — show original on error
  const data: { formatted: { original: string; formatted: string }[] } = await res.json();
  return rawQuestions.map((q, i) => ({
    ...q,
    text: data.formatted[i]?.formatted ?? q.text,
  }));
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
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
