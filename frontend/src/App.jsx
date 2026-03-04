import { useState, useEffect } from "react";
import InputForm from "./components/InputForm";
import ProgressTracker from "./components/ProgressTracker";
import AudioPlayer from "./components/AudioPlayer";
import Transcript from "./components/Transcript";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * App — manages three views: input -> loading -> result
 *
 * On mount, pings GET /health. If Render has been idle 15+ minutes,
 * the instance needs 30-50s to boot. A slow/failed health check
 * triggers a "Backend waking up..." banner instead of a silent hang.
 */
export default function App() {
  const [view, setView] = useState("input"); // "input" | "loading" | "result"
  const [jobId, setJobId] = useState(null);
  const [result, setResult] = useState(null); // { audio_url, script }
  const [backendReady, setBackendReady] = useState(false);
  const [waking, setWaking] = useState(false);

  // Health check on mount — detect Render cold start
  useEffect(() => {
    let timeout;
    const controller = new AbortController();

    // If health check takes > 3s, show waking banner
    timeout = setTimeout(() => setWaking(true), 3000);

    fetch(`${API_BASE}/health`, { signal: controller.signal })
      .then((res) => {
        if (res.ok) {
          setBackendReady(true);
          setWaking(false);
          clearTimeout(timeout);
        }
      })
      .catch(() => {
        setWaking(true);
        // Retry after a delay
        setTimeout(() => {
          fetch(`${API_BASE}/health`)
            .then((res) => {
              if (res.ok) {
                setBackendReady(true);
                setWaking(false);
              }
            })
            .catch(() => {});
        }, 10000);
      });

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, []);

  const handleGenerate = async (input) => {
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      const data = await res.json();
      setJobId(data.job_id);
      setView("loading");
    } catch {
      alert("Failed to start generation. Is the backend running?");
    }
  };

  const handleComplete = (data) => {
    setResult(data);
    setView("result");
  };

  const handleReset = () => {
    setView("input");
    setJobId(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
          EchoChamber
        </h1>

        {/* Animated sound wave */}
        <div className="flex items-end justify-center gap-[3px] mt-4 h-8">
          {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <span
              key={i}
              className="inline-block w-[3px] rounded-full bg-gradient-to-t from-purple-500 to-pink-400 soundwave-bar"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>

        <p className="text-gray-400 mt-3 text-lg">
          Transform any article into a 5-minute AI podcast
        </p>
      </div>

      {/* Cold start banner */}
      {waking && !backendReady && (
        <div className="mb-6 px-6 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-gray-400 text-sm text-center max-w-md">
          Backend is waking up from sleep. This may take 30 seconds on first
          load...
        </div>
      )}

      {/* Main content */}
      <div className="w-full max-w-2xl">
        {view === "input" && <InputForm onSubmit={handleGenerate} />}

        {view === "loading" && jobId && (
          <ProgressTracker
            jobId={jobId}
            apiBase={API_BASE}
            onComplete={handleComplete}
            onError={handleReset}
          />
        )}

        {view === "result" && result && (
          <div className="space-y-6">
            <AudioPlayer audioUrl={`${API_BASE}${result.audio_url}`} />
            <Transcript script={result.script} />
            <div className="text-center">
              <button
                onClick={handleReset}
                className="px-6 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition text-sm text-gray-300"
              >
                Generate Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
