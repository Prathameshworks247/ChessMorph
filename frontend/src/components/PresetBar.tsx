"use client";

const PIECE_META: Record<string, { symbol: string; label: string; color: string }> = {
  king:   { symbol: "♔", label: "King",   color: "rgba(251,191,36,0.12)"  },
  queen:  { symbol: "♕", label: "Queen",  color: "rgba(139,92,246,0.12)"  },
  rook:   { symbol: "♖", label: "Rook",   color: "rgba(99,102,241,0.12)"  },
  bishop: { symbol: "♗", label: "Bishop", color: "rgba(236,72,153,0.10)"  },
  knight: { symbol: "♞", label: "Knight", color: "rgba(20,184,166,0.10)"  },
  pawn:   { symbol: "♟", label: "Pawn",   color: "rgba(148,163,184,0.08)" },
};

const ORDER = ["king", "queen", "rook", "bishop", "knight", "pawn"];

interface Props {
  presets: Record<string, number[]>;
  onSelect: (latent: number[]) => void;
  disabled?: boolean;
}

export default function PresetBar({ presets, onSelect, disabled }: Props) {
  if (Object.keys(presets).length === 0) return null;

  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-600">
        Presets
      </span>
      <div className="flex flex-wrap gap-2 justify-center">
        {ORDER.filter((p) => presets[p]).map((piece) => {
          const meta = PIECE_META[piece] ?? { symbol: "?", label: piece, color: "transparent" };
          return (
            <button
              key={piece}
              onClick={() => onSelect(presets[piece])}
              disabled={disabled}
              title={meta.label}
              className="
                group flex flex-col items-center gap-1
                px-4 py-3 rounded-xl
                border border-white/6
                disabled:opacity-30 disabled:cursor-not-allowed
                transition-all duration-200
                hover:border-white/15 hover:scale-105 active:scale-100
              "
              style={{
                background: meta.color,
              }}
            >
              <span className="text-2xl leading-none group-hover:scale-110 transition-transform duration-200">
                {meta.symbol}
              </span>
              <span className="text-[10px] text-slate-500 group-hover:text-slate-300 transition-colors font-medium tracking-wide">
                {meta.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
