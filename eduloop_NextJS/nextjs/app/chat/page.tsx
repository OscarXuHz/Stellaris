"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Bot, User, Sparkles } from "lucide-react";
import MathContent from "@/components/MathContent";
import { chatWithOrchestrator } from "@/lib/api";
import { SYLLABUSES, TOPICS, type ChatMessage } from "@/lib/types";
import clsx from "clsx";

const AGENT_STYLES: Record<string, { label: string; color: string; bg: string }> = {
  orchestrator: { label: "🤖 Orchestrator",  color: "text-blue-700",   bg: "bg-blue-50 border-blue-200" },
  teaching:     { label: "📘 Teaching Agent", color: "text-green-700",  bg: "bg-green-50 border-green-200" },
  assessment:   { label: "📊 Assessment Agent", color: "text-purple-700", bg: "bg-purple-50 border-purple-200" },
  error:        { label: "⚠️ Error",          color: "text-red-700",    bg: "bg-red-50 border-red-200" },
};

export default function ChatPage() {
  const [syllabus, setSyllabus] = useState<string>(SYLLABUSES[0]);
  const [topic, setTopic]       = useState(TOPICS[SYLLABUSES[0]][0]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  const topics = TOPICS[syllabus] ?? [];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await chatWithOrchestrator(text, topic, [...messages, userMsg]);
      const botMsg: ChatMessage = {
        role: "assistant",
        content: res.reply,
        agent_used: res.agent_used,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (e) {
      const errMsg: ChatMessage = {
        role: "assistant",
        content: `Error: ${e instanceof Error ? e.message : "Unknown error"}`,
        agent_used: "error",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-h-[calc(100vh-2rem)]">
      <h1 className="text-2xl font-bold text-gray-900 mb-4 shrink-0">
        💬 Chat with the Orchestrator
      </h1>

      <div className="grid grid-cols-[240px_1fr] gap-6 flex-1 min-h-0">
        {/* ── Left panel ─────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4 self-start sticky top-0">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">
            Topic Context
          </h2>

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
              {SYLLABUSES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-gray-500">Topic</label>
            <select
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            >
              {topics.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </div>

          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs text-gray-500 leading-relaxed">
              The Orchestrator automatically routes your messages to the
              <strong> Teaching Agent</strong> or <strong>Assessment Agent</strong> based on your intent.
            </p>
          </div>

          <div className="border-t border-gray-100 pt-4 space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Agent Legend</p>
            {Object.entries(AGENT_STYLES).filter(([k]) => k !== "error").map(([key, style]) => (
              <div key={key} className="flex items-center gap-2">
                <span className={clsx("w-2.5 h-2.5 rounded-full", style.bg.split(" ")[0])} />
                <span className={clsx("text-xs font-medium", style.color)}>{style.label}</span>
              </div>
            ))}
          </div>

          {messages.length > 0 && (
            <button
              onClick={() => setMessages([])}
              className="w-full text-xs text-gray-400 hover:text-gray-600 transition-colors py-1"
            >
              Clear conversation
            </button>
          )}
        </div>

        {/* ── Right panel — Chat area ───────────────────────────────── */}
        <div className="flex flex-col min-h-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-3 pr-1 mb-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Sparkles size={48} className="mb-3 opacity-30" />
                <p className="text-lg font-medium">Start a conversation</p>
                <p className="text-sm mt-1">
                  Ask about a topic, submit an answer for evaluation, or just say hello!
                </p>
              </div>
            )}

            {messages.map((msg, i) => {
              const isUser = msg.role === "user";
              const agentStyle = AGENT_STYLES[msg.agent_used ?? "orchestrator"];

              return (
                <div
                  key={i}
                  className={clsx(
                    "flex gap-3",
                    isUser ? "justify-end" : "justify-start",
                  )}
                >
                  {!isUser && (
                    <div className="shrink-0 mt-1">
                      <div className="bg-blue-100 text-blue-600 rounded-full p-1.5">
                        <Bot size={16} />
                      </div>
                    </div>
                  )}

                  <div
                    className={clsx(
                      "max-w-[75%] rounded-xl px-4 py-3 border",
                      isUser
                        ? "bg-blue-600 text-white border-blue-600"
                        : clsx(agentStyle?.bg ?? "bg-gray-50 border-gray-200"),
                    )}
                  >
                    {!isUser && agentStyle && (
                      <p className={clsx("text-[10px] font-semibold mb-1.5", agentStyle.color)}>
                        {agentStyle.label}
                      </p>
                    )}
                    <div className={clsx("text-sm", isUser ? "text-white" : "text-gray-800")}>
                      {isUser ? (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <MathContent content={msg.content} />
                      )}
                    </div>
                  </div>

                  {isUser && (
                    <div className="shrink-0 mt-1">
                      <div className="bg-gray-200 text-gray-600 rounded-full p-1.5">
                        <User size={16} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="shrink-0 mt-1">
                  <div className="bg-blue-100 text-blue-600 rounded-full p-1.5">
                    <Bot size={16} />
                  </div>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 size={14} className="animate-spin" />
                    Thinking…
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input bar */}
          <div className="shrink-0 bg-white rounded-xl border border-gray-200 p-3 flex items-end gap-3">
            <textarea
              ref={inputRef}
              rows={2}
              placeholder="Ask anything about HKDSE Math, or submit your answer for evaluation…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 resize-none border-0 text-sm focus:outline-none placeholder:text-gray-400"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="shrink-0 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg p-2.5 transition-colors"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
