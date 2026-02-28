"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { MessageCircle, X, Send, Loader2, Bot, User, Minimize2 } from "lucide-react";
import MathContent from "@/components/MathContent";
import { chatWithOrchestrator } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import clsx from "clsx";

const AGENT_BADGE: Record<string, { label: string; cls: string }> = {
  orchestrator: { label: "Orchestrator", cls: "bg-blue-100 text-blue-700" },
  teaching:     { label: "Teaching",     cls: "bg-green-100 text-green-700" },
  assessment:   { label: "Assessment",   cls: "bg-purple-100 text-purple-700" },
  error:        { label: "Error",        cls: "bg-red-100 text-red-700" },
};

interface FloatingChatProps {
  /** Current topic context passed to the orchestrator */
  topic?: string;
}

export default function FloatingChat({ topic = "" }: FloatingChatProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 200);
  }, [open]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await chatWithOrchestrator(text, topic, [...messages, userMsg]);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply, agent_used: res.agent_used },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${e instanceof Error ? e.message : "Unknown error"}`,
          agent_used: "error",
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [input, loading, messages, topic]);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <>
      {/* ── FAB button ──────────────────────────────────────────── */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className={clsx(
            "fixed bottom-6 right-6 z-50",
            "bg-gradient-to-br from-blue-600 to-indigo-600 text-white",
            "rounded-full p-4 shadow-lg shadow-blue-500/30",
            "hover:scale-110 active:scale-95 transition-all duration-200",
            "animate-bounce-slow",
          )}
          title="Chat with AI Tutor"
        >
          <MessageCircle size={24} />
          {/* Unread badge */}
          {messages.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-[10px] font-bold flex items-center justify-center">
              {messages.filter((m) => m.role === "assistant").length}
            </span>
          )}
        </button>
      )}

      {/* ── Chat panel ──────────────────────────────────────────── */}
      {open && (
        <div
          className={clsx(
            "fixed bottom-6 right-6 z-50",
            "w-[400px] h-[560px] max-h-[80vh]",
            "bg-white rounded-2xl shadow-2xl border border-gray-200",
            "flex flex-col overflow-hidden",
            "animate-slide-up",
          )}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 rounded-full p-1">
                <Bot size={16} className="text-white" />
              </div>
              <div>
                <p className="text-white text-sm font-semibold">AI Study Assistant</p>
                <p className="text-blue-200 text-[10px]">
                  {topic ? `Topic: ${topic}` : "Ask me anything about HKDSE Math"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setMessages([])}
                className="text-white/60 hover:text-white p-1 transition-colors"
                title="Clear chat"
              >
                <Minimize2 size={14} />
              </button>
              <button
                onClick={() => setOpen(false)}
                className="text-white/60 hover:text-white p-1 transition-colors"
                title="Close"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-8 space-y-2">
                <Bot size={32} className="mx-auto opacity-30" />
                <p className="text-sm">Hi! 👋 I&apos;m your AI study assistant.</p>
                <p className="text-xs text-gray-300">
                  Ask about a concept, or paste a question you&apos;re stuck on.
                </p>
              </div>
            )}

            {messages.map((msg, i) => {
              const isUser = msg.role === "user";
              const badge = AGENT_BADGE[msg.agent_used ?? "orchestrator"];

              return (
                <div key={i} className={clsx("flex gap-2", isUser ? "justify-end" : "justify-start")}>
                  {!isUser && (
                    <div className="shrink-0 mt-1">
                      <div className="bg-blue-100 text-blue-600 rounded-full p-1">
                        <Bot size={12} />
                      </div>
                    </div>
                  )}
                  <div
                    className={clsx(
                      "max-w-[80%] rounded-xl px-3 py-2 text-[13px]",
                      isUser
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-gray-100 text-gray-800 border border-gray-200 rounded-bl-sm",
                    )}
                  >
                    {!isUser && badge && (
                      <span className={clsx("inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded-full mb-1", badge.cls)}>
                        {badge.label}
                      </span>
                    )}
                    {isUser ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <MathContent content={msg.content} compact />
                    )}
                  </div>
                  {isUser && (
                    <div className="shrink-0 mt-1">
                      <div className="bg-gray-200 text-gray-500 rounded-full p-1">
                        <User size={12} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex gap-2 justify-start">
                <div className="shrink-0 mt-1">
                  <div className="bg-blue-100 text-blue-600 rounded-full p-1">
                    <Bot size={12} />
                  </div>
                </div>
                <div className="bg-gray-100 border border-gray-200 rounded-xl px-3 py-2">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400">
                    <Loader2 size={12} className="animate-spin" />
                    Thinking…
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="shrink-0 border-t border-gray-100 px-3 py-2 flex items-end gap-2">
            <textarea
              ref={inputRef}
              rows={1}
              placeholder="Type a message…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 resize-none border-0 text-sm focus:outline-none placeholder:text-gray-400 bg-transparent"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="shrink-0 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-lg p-2 transition-colors"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
