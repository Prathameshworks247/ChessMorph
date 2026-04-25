"use client";

interface Props {
  onRandomize: () => void;
  onReset: () => void;
  onSaveA: () => void;
  onSaveB: () => void;
  onAnimate: () => void;
  onStop: () => void;
  hasSavedA: boolean;
  hasSavedB: boolean;
  animating: boolean;
}

function gaussianRandom(): number {
  const u = 1 - Math.random();
  const v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

export function sampleRandom(dim: number): number[] {
  return Array.from({ length: dim }, () =>
    Math.max(-3, Math.min(3, gaussianRandom()))
  );
}

export default function ControlBar({
  onRandomize,
  onReset,
  onSaveA,
  onSaveB,
  onAnimate,
  onStop,
  hasSavedA,
  hasSavedB,
  animating,
}: Props) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-2">
        <button
          onClick={onRandomize}
          disabled={animating}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-medium transition-colors"
        >
          Randomize
        </button>
        <button
          onClick={onReset}
          disabled={animating}
          className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-white text-sm font-medium transition-colors"
        >
          Reset
        </button>
      </div>

      <div className="flex gap-2 items-center">
        <button
          onClick={onSaveA}
          disabled={animating}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            hasSavedA
              ? "bg-emerald-700 text-emerald-200"
              : "bg-gray-700 hover:bg-gray-600 text-gray-300"
          }`}
        >
          {hasSavedA ? "✓ A saved" : "Save A"}
        </button>
        <button
          onClick={onSaveB}
          disabled={animating}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            hasSavedB
              ? "bg-emerald-700 text-emerald-200"
              : "bg-gray-700 hover:bg-gray-600 text-gray-300"
          }`}
        >
          {hasSavedB ? "✓ B saved" : "Save B"}
        </button>

        {animating ? (
          <button
            onClick={onStop}
            className="px-3 py-1.5 rounded-lg bg-red-700 hover:bg-red-600 text-white text-xs font-medium transition-colors"
          >
            ■ Stop
          </button>
        ) : (
          <button
            onClick={onAnimate}
            disabled={!hasSavedA || !hasSavedB}
            title={!hasSavedA || !hasSavedB ? "Save A and B first" : "Animate morph"}
            className="px-3 py-1.5 rounded-lg bg-violet-700 hover:bg-violet-600 disabled:opacity-30 disabled:cursor-not-allowed text-white text-xs font-medium transition-colors"
          >
            ▶ Animate
          </button>
        )}
      </div>
    </div>
  );
}
