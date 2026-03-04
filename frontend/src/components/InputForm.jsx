import { useState } from "react";

/**
 * InputForm — single text input accepting URL, Wikipedia link, PDF path, or raw text.
 * Auto-detection logic lives entirely in the backend — frontend just passes the raw string.
 */
export default function InputForm({ onSubmit }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

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
        <textarea
          id="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence"
          rows={4}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 resize-none"
        />
        <p className="text-xs text-gray-500 mt-2">
          Supports: Any URL, Wikipedia pages, PDF file paths, or raw text
        </p>
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
