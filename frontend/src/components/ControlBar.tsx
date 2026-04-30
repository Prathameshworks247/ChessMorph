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
    <div className="flex flex-col gap-3">
      {/* Row 1: Randomize + Reset */}
      <div className="flex gap-2">
        <button
          onClick={onRandomize}
          disabled={animating}
          className="
            flex-1 flex items-center justify-center gap-2
            px-4 py-2.5 rounded-xl text-sm font-semibold
            text-white disabled:opacity-30
            transition-all duration-150 active:scale-95
          "
          style={{
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
            boxShadow: animating ? "none" : "0 0 18px rgba(99,102,241,0.35), inset 0 1px 0 rgba(255,255,255,0.1)",
          }}
        >
          <svg className="w-3.5 h-3.5 opacity-80" viewBox="0 0 16 16" fill="currentColor">
            <path d="M13.5 3.5a1 1 0 0 0-1.414 0L10 5.586 7.914 3.5A1 1 0 0 0 6.5 4.914L8.586 7 6.5 9.086A1 1 0 1 0 7.914 10.5L10 8.414l2.086 2.086a1 1 0 0 0 1.414-1.414L11.414 7l2.086-2.086a1 1 0 0 0 0-1.414Z"/>
            <path d="M4 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm0 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"/>
          </svg>
          Randomize
        </button>
        <button
          onClick={onReset}
          disabled={animating}
          className="
            px-4 py-2.5 rounded-xl text-sm font-medium
            bg-white/5 hover:bg-white/10 border border-white/8
            text-slate-300 hover:text-white
            disabled:opacity-30
            transition-all duration-150 active:scale-95
          "
        >
          Reset
        </button>
      </div>

      {/* Row 2: Save A / B / Animate */}
      <div className="flex gap-2 items-center">
        <button
          onClick={onSaveA}
          disabled={animating}
          className={`
            flex-1 px-3 py-2 rounded-xl text-xs font-semibold
            transition-all duration-200 active:scale-95 disabled:opacity-30
            border
            ${hasSavedA
              ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
              : "bg-white/5 border-white/8 text-slate-400 hover:text-white hover:bg-white/10"
            }
          `}
        >
          {hasSavedA ? "✓ A" : "Save A"}
        </button>

        <button
          onClick={onSaveB}
          disabled={animating}
          className={`
            flex-1 px-3 py-2 rounded-xl text-xs font-semibold
            transition-all duration-200 active:scale-95 disabled:opacity-30
            border
            ${hasSavedB
              ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
              : "bg-white/5 border-white/8 text-slate-400 hover:text-white hover:bg-white/10"
            }
          `}
        >
          {hasSavedB ? "✓ B" : "Save B"}
        </button>

        {animating ? (
          <button
            onClick={onStop}
            className="
              flex-1 px-3 py-2 rounded-xl
              bg-red-500/15 border border-red-500/30
              text-red-400 hover:text-red-300 hover:bg-red-500/20
              text-xs font-semibold
              transition-all duration-150 active:scale-95
            "
          >
            ■ Stop
          </button>
        ) : (
          <button
            onClick={onAnimate}
            disabled={!hasSavedA || !hasSavedB}
            title={!hasSavedA || !hasSavedB ? "Save A and B first" : "Interpolate and animate"}
            className="
              flex-1 px-3 py-2 rounded-xl
              text-xs font-semibold
              transition-all duration-150 active:scale-95
              disabled:opacity-25 disabled:cursor-not-allowed
            "
            style={{
              background: (!hasSavedA || !hasSavedB)
                ? "rgba(255,255,255,0.05)"
                : "linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)",
              border: "1px solid rgba(139,92,246,0.3)",
              color: (!hasSavedA || !hasSavedB) ? "#64748b" : "#e9d5ff",
              boxShadow: (!hasSavedA || !hasSavedB)
                ? "none"
                : "0 0 14px rgba(139,92,246,0.3)",
            }}
          >
            ▶ Morph
          </button>
        )}
      </div>

      {/* Interpolation hint */}
      {!animating && (hasSavedA || hasSavedB) && (
        <p className="text-[10px] text-slate-600 text-center">
          {hasSavedA && hasSavedB
            ? "Ready to interpolate A → B"
            : hasSavedA
            ? "A saved — now save B"
            : "B saved — now save A"}
        </p>
      )}
    </div>
  );
}
