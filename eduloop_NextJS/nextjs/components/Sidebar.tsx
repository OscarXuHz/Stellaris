"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BookOpen,
  PenLine,
  BarChart2,
  Settings,
  GraduationCap,
  MessageCircle,
  Shield,
  Bot,
} from "lucide-react";
import clsx from "clsx";

const NAV = [
  { href: "/",         label: "Dashboard", icon: LayoutDashboard },
  { href: "/learn",    label: "Learn",     icon: BookOpen },
  { href: "/practice", label: "Practice",  icon: PenLine },
  { href: "/chat",     label: "Chat",      icon: MessageCircle },
  { href: "/progress",   label: "Progress",   icon: BarChart2 },
  { href: "/evaluation", label: "Evaluation", icon: Shield },
  { href: "/settings",   label: "Settings",   icon: Settings },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-60 shrink-0 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-200">
        <div className="flex items-center gap-3 group">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-lg p-1.5 group-hover:scale-110 transition-transform duration-300">
            <GraduationCap size={20} />
          </div>
          <div>
            <p className="font-bold text-gray-900 leading-none">EduLoop</p>
            <p className="text-[11px] text-gray-400 mt-0.5">DSE Mathematics</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
              )}
            >
              <Icon size={17} className={active ? "text-blue-600" : "text-gray-400"} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-gray-200 space-y-2">
        <div className="flex items-center gap-2">
          <Bot size={13} className="text-blue-500" />
          <p className="text-[10px] text-gray-500 font-medium">2 AI Agents Active</p>
        </div>
        <div className="flex gap-1">
          <span className="text-[9px] bg-green-50 text-green-600 font-semibold px-1.5 py-0.5 rounded">Teaching</span>
          <span className="text-[9px] bg-purple-50 text-purple-600 font-semibold px-1.5 py-0.5 rounded">Assessment</span>
        </div>
        <p className="text-[10px] text-gray-400">Powered by MiniMax AI + RAG</p>
      </div>
    </aside>
  );
}
