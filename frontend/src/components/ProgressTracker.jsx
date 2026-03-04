import { useState, useEffect, useRef } from "react";

/**
 * ProgressTracker — Glass-box UX showing real-time pipeline status.
 *
 * This component is the biggest UX differentiator in the project.
 * Polls GET /status/{job_id} every 2 seconds and renders each pipeline
 * stage as a checklist with completion indicators.
 *
 * Turns a 45-second wait into a transparent, engaging experience.
 */

const PIPELINE_STAGES = [
  "Detecting input type...",
  "Extracting text...",
  "Chunking and summarizing content...",
  "Checking script cache...",
  "Agents debating (Gemini Flash)...",
  "Synthesizing audio",
  "Mixing and mastering audio...",
  "Podcast ready!",
];

function getStageIndex(message) {
  if (!message) return -1;
  if (message.includes("Detecting")) return 0;
  if (message.includes("Extracting")) return 1;
  if (message.includes("Chunking")) return 2;
  if (message.includes("cache")) return 3;
  if (message.includes("debating")) return 4;
  if (message.includes("Synthesizing")) return 5;
  if (message.includes("Mixing")) return 6;
  if (message.includes("ready")) return 7;
  return -1;
}

export default function ProgressTracker({ jobId, apiBase, onComplete, onError }) {
  const [message, setMessage] = useState("Job queued...");
  const [status, setStatus] = useState("queued");
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    // Poll /status/{job_id} every 2 seconds
    intervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${apiBase}/status/${jobId}`);
        const data = await res.json();

        setMessage(data.message);
        setStatus(data.status);

        if (data.status === "complete") {
          clearInterval(intervalRef.current);
          onComplete(data.result);
        } else if (data.status === "failed") {
          clearInterval(intervalRef.current);
          setError(data.error);
        }
      } catch {
        // Network error — keep polling, Render may be slow
      }
    }, 2000);

    return () => clearInterval(intervalRef.current);
  }, [jobId, apiBase, onComplete]);

  const currentStageIndex = getStageIndex(message);

  if (error) {
    return (
      <div className="glass-card p-8 text-center space-y-4">
        <div className="text-red-400 text-lg font-medium">
          Generation Failed
        </div>
        <p className="text-gray-400 text-sm">{error}</p>
        <button
          onClick={onError}
          className="px-6 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition text-sm text-gray-300"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="glass-card p-8 space-y-4">
      <h2 className="text-lg font-semibold text-white mb-4">
        Generating your podcast...
      </h2>

      <div className="space-y-3">
        {PIPELINE_STAGES.map((stage, i) => {
          const isComplete = i < currentStageIndex;
          const isCurrent = i === currentStageIndex;
          const isPending = i > currentStageIndex;

          return (
            <div key={stage} className="flex items-center gap-3">
              {/* Status icon */}
              <div className="w-6 h-6 flex items-center justify-center flex-shrink-0">
                {isComplete && (
                  <svg
                    className="w-5 h-5 text-green-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
                {isCurrent && (
                  <div className="w-3 h-3 rounded-full bg-purple-400 animate-pulse-glow" />
                )}
                {isPending && (
                  <div className="w-3 h-3 rounded-full bg-white/10" />
                )}
              </div>

              {/* Stage label */}
              <span
                className={`text-sm ${
                  isComplete
                    ? "text-green-400"
                    : isCurrent
                      ? "text-white font-medium"
                      : "text-gray-600"
                }`}
              >
                {/* Show detailed message for TTS stage */}
                {isCurrent && stage === "Synthesizing audio"
                  ? message
                  : stage}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
