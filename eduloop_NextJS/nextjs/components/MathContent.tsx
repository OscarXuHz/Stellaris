"use client";

import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import clsx from "clsx";

interface MathContentProps {
  content: string;
  className?: string;
  compact?: boolean;
}

/** Renders markdown with inline ($...$) and block ($$...$$) LaTeX via KaTeX. */
export default function MathContent({ content, className, compact = false }: MathContentProps) {
  return (
    <ReactMarkdown
      className={clsx(
        "prose prose-slate max-w-none",
        compact ? "prose-sm" : "prose-base",
        className,
      )}
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
    >
      {content}
    </ReactMarkdown>
  );
}
