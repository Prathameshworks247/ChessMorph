"use client";

interface Props {
  onRandomize: () => void;
  onReset: () => void;
}

function gaussianRandom(): number {
  // Box-Muller transform
  const u = 1 - Math.random();
  const v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

export function sampleRandom(dim: number): number[] {
  return Array.from({ length: dim }, () =>
    Math.max(-3, Math.min(3, gaussianRandom()))
  );
}

export default function ControlBar({ onRandomize, onReset }: Props) {
  return (
    <div className="flex gap-3">
      <button
        onClick={onRandomize}
        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
      >
        Randomize
      </button>
      <button
        onClick={onReset}
        className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium transition-colors"
      >
        Reset
      </button>
    </div>
  );
}
