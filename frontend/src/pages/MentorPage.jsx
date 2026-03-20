import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Send, Bot, User, Loader2, Sparkles } from "lucide-react";
import { chatApi } from "../services/api";
import { Card, Button } from "../components/ui";
import clsx from "clsx";

const SUGGESTIONS = [
  "What should I learn first?",
  "How long will it take to close my skill gaps?",
  "Can you explain the learning roadmap?",
  "What resources do you recommend for Python?",
  "How do I prepare for a technical interview?",
];

function Message({ msg }) {
  const isBot = msg.role === "bot";
  return (
    <div className={clsx("flex gap-3 max-w-[85%]", isBot ? "self-start" : "self-end flex-row-reverse")}>
      <div className={clsx(
        "w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5",
        isBot ? "bg-blue-100" : "bg-gray-100"
      )}>
        {isBot ? <Bot size={14} className="text-blue-600" /> : <User size={14} className="text-gray-600" />}
      </div>
      <div className={clsx(
        "px-4 py-2.5 rounded-2xl text-sm leading-relaxed",
        isBot
          ? "bg-white border border-gray-200 text-gray-800 rounded-tl-sm"
          : "bg-blue-600 text-white rounded-tr-sm"
      )}>
        {msg.loading ? (
          <div className="flex gap-1 items-center py-1">
            {[0, 1, 2].map((i) => (
              <div key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
            ))}
          </div>
        ) : msg.text}
      </div>
    </div>
  );
}

export default function MentorPage() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi! I'm your AI career mentor. I can help you understand your skill gaps, plan your learning, and prepare for interviews. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  const mutation = useMutation({
    mutationFn: chatApi.send,
    onMutate: ({ question }) => {
      setMessages((m) => [
        ...m,
        { role: "user", text: question },
        { role: "bot", text: "", loading: true },
      ]);
    },
    onSuccess: (data) => {
      setMessages((m) => {
        const updated = [...m];
        const lastBot = [...updated].reverse().findIndex((x) => x.role === "bot" && x.loading);
        if (lastBot !== -1) {
          const idx = updated.length - 1 - lastBot;
          updated[idx] = { role: "bot", text: data.answer, loading: false };
        }
        return updated;
      });
    },
    onError: () => {
      setMessages((m) => {
        const updated = [...m];
        const lastBot = [...updated].reverse().findIndex((x) => x.role === "bot" && x.loading);
        if (lastBot !== -1) {
          const idx = updated.length - 1 - lastBot;
          updated[idx] = { role: "bot", text: "Sorry, I couldn't connect. Please try again.", loading: false };
        }
        return updated;
      });
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (text) => {
    const q = text || input.trim();
    if (!q || mutation.isPending) return;
    setInput("");
    mutation.mutate({ question: q });
  };

  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-gray-900">AI Mentor</h1>
        <p className="text-sm text-gray-500">Personalized career and learning guidance</p>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="px-5 pb-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => handleSend(s)}
                className="text-xs px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-full hover:bg-blue-100 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="border-t border-gray-100 px-4 py-3 flex items-center gap-3">
          <input
            className="flex-1 text-sm bg-gray-50 rounded-xl px-4 py-2.5 outline-none border border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400"
            placeholder="Ask about your learning path..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || mutation.isPending}
            size="sm"
          >
            {mutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          </Button>
        </div>
      </Card>
    </div>
  );
}
