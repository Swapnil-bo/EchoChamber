import { useState } from "react";

/**
 * AudioPlayer — native HTML5 audio with Tailwind styling.
 *
 * wavesurfer.js was explicitly rejected: too heavy, requires backend
 * waveform preprocessing, and adds complexity with no meaningful
 * UX gain for this project.
 *
 * The onError handler gracefully handles Render ephemeral disk wipes.
 * Render free tier deletes all generated files when the instance spins down.
 */
export default function AudioPlayer({ audioUrl }) {
  const [audioError, setAudioError] = useState(null);

  return (
    <div className="glass-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4">
        Your Podcast
      </h2>

      <audio
        controls
        src={audioUrl}
        className="w-full rounded-lg"
        onError={() => {
          setAudioError(
            "Audio session expired. Please regenerate the podcast."
          );
        }}
      />

      {audioError && (
        <p className="text-red-400 text-sm mt-3">{audioError}</p>
      )}
    </div>
  );
}
