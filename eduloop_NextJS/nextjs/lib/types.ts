// Shared TypeScript types matching FastAPI response shapes

export interface ContentBlock {
  type: "introduction" | "concept" | "example" | "common_pitfall" | "summary";
  text: string;
}

export interface LlmLessonResponse {
  status: "success" | "error";
  error?: string;
  lesson_id?: string;
  topic?: string;
  content_blocks: ContentBlock[];
  constructive_advice: string;
  learning_objectives: string[];
  suggested_questions_for_assessment: string[];
}

export interface Lesson {
  lesson_id: string;
  topic: string;
  level: string;
  created_at: string;
  rag_chunks_used: number;
  dse_references: string[];
  llm_response: LlmLessonResponse;
}

export interface RagChunk {
  id: string;
  text: string;
  source: string;
  score: number;
  metadata: {
    year?: string;
    paper?: string;
    document_type?: string;
    detected_topics?: string;
    [key: string]: unknown;
  };
}

export interface DiagnosticReport {
  strengths: string[];
  knowledge_gaps: string[];
  constructive_feedback: string;
  misconception_analysis: string;
}

export interface NextStepRecommendation {
  action: "advance" | "review" | "reteach_specifics";
  focus_topics_for_teacher: string[];
}

export interface LlmAssessResponse {
  status: "success" | "error";
  error?: string;
  assessment_id?: string;
  score_percentage?: number;
  diagnostic_report?: DiagnosticReport;
  next_step_recommendation?: NextStepRecommendation;
}

export interface AssessmentResult {
  assessment_id: string;
  topic: string;
  difficulty: string;
  created_at: string;
  student_answer: string;
  rag_chunks_used: number;
  llm_response: LlmAssessResponse;
}

export interface StudentProfile {
  name: string;
  level: "Foundational" | "Intermediate" | "Advanced";
  learning_style: "Visual" | "Auditory" | "Mixed";
  language: "English" | "Cantonese (粵語)" | "Mixed";
}

// ── DSE syllabus / topic constants ─────────────────────────────────────
export const SYLLABUSES = [
  "Compulsory Part",
  "Module 1 (Calculus & Statistics)",
  "Module 2 (Algebra & Calculus)",
] as const;

export const TOPICS: Record<string, string[]> = {
  "Compulsory Part": [
    "Quadratic Equations in One Unknown",
    "Functions and Graphs",
    "Exponential and Logarithmic Functions",
    "More about Polynomials",
    "More about Equations",
    "Inequalities and Linear Programming",
    "Trigonometry — Formulae and Identities",
    "Applications of Trigonometry",
    "More about Trigonometry",
    "Straight Lines and Rectilinear Figures",
    "Circles",
    "Loci",
    "Permutation and Combination",
    "More about Probability",
    "Measures of Dispersion",
    "More about Statistics",
  ],
  "Module 1 (Calculus & Statistics)": [
    "Binomial Expansion",
    "Exponential and Logarithmic Functions (M1)",
    "Differentiation (M1)",
    "Applications of Differentiation (M1)",
    "Integration (M1)",
    "Applications of Integration (M1)",
    "Probability Distributions",
    "Further Statistics",
  ],
  "Module 2 (Algebra & Calculus)": [
    "Vectors",
    "Matrices",
    "Systems of Linear Equations",
    "Introduction to Calculus",
    "Differentiation (M2)",
    "Integration (M2)",
    "Applications of Calculus (M2)",
  ],
};


