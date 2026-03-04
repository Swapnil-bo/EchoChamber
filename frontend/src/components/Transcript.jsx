/**
 * Transcript — renders the script JSON below the audio player.
 *
 * HOST (Alex) lines: gray text with bold label
 * EXPERT (Maya) lines: blue text with bold label
 *
 * Zero extra backend work — the JSON script is already in the job result payload.
 * In a portfolio demo, this makes the app dramatically more impressive.
 */
export default function Transcript({ script }) {
  if (!script || script.length === 0) return null;

  return (
    <div className="glass-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4">Transcript</h2>

      <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
        {script.map((entry, i) => {
          const isHost = entry.speaker === "HOST";
          return (
            <div key={i} className="text-sm leading-relaxed">
              <span
                className={`font-bold ${
                  isHost ? "text-gray-300" : "text-blue-400"
                }`}
              >
                {isHost ? "Alex" : "Maya"}:
              </span>{" "}
              <span className={isHost ? "text-gray-400" : "text-blue-300/80"}>
                {entry.line}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
