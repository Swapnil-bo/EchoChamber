import { useState } from "react";

/**
 * InputForm — single text input accepting URL, Wikipedia link, PDF path, or raw text.
 * Auto-detection logic lives entirely in the backend — frontend just passes the raw string.
 */
export default function InputForm({ onSubmit }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState(false);

  const examples = [
    { label: "Wikipedia", value: "https://en.wikipedia.org/wiki/Artificial_intelligence" },
    { label: "URL", value: "https://www.paulgraham.com/greatwork.html" },
    { label: "PDF", value: "research_paper.pdf" },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    await onSubmit(input.trim());
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
      <div>
        <label
          htmlFor="input"
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          Paste a URL, Wikipedia link, or article text
        </label>
        <div
          className={`rounded-xl p-[1px] transition-all duration-300 ${
            focused
              ? "bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 gradient-border-spin"
              : "bg-white/10"
          }`}
        >
          <textarea
            id="input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence"
            rows={4}
            className="w-full bg-gray-950 rounded-[11px] px-4 py-3 text-white placeholder-gray-500 focus:outline-none resize-none"
          />
        </div>
        <div className="flex items-center gap-2 mt-3">
          <span className="text-xs text-gray-500">Try:</span>
          {examples.map((ex) => (
            <button
              key={ex.label}
              type="button"
              onClick={() => setInput(ex.value)}
              className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:border-purple-500/50 hover:bg-purple-500/10 transition-all duration-200"
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !input.trim()}
        className="w-full py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 hover:from-purple-400 hover:via-pink-400 hover:to-orange-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-purple-500/20"
      >
        {loading ? "Starting..." : "Generate Podcast"}
      </button>
    </form>
  );
}
