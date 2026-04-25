"use client";

const PIECE_META: Record<string, { symbol: string; label: string }> = {
  king:   { symbol: "♔", label: "King" },
  queen:  { symbol: "♕", label: "Queen" },
  rook:   { symbol: "♖", label: "Rook" },
  bishop: { symbol: "♗", label: "Bishop" },
  knight: { symbol: "♞", label: "Knight" },
  pawn:   { symbol: "♟", label: "Pawn" },
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
    <div className="flex flex-wrap gap-2 justify-center">
      {ORDER.filter((p) => presets[p]).map((piece) => {
        const { symbol, label } = PIECE_META[piece] ?? { symbol: "?", label: piece };
        return (
          <button
            key={piece}
            onClick={() => onSelect(presets[piece])}
            disabled={disabled}
            title={label}
            className="flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
          >
            <span className="text-xl leading-none">{symbol}</span>
            <span className="text-[10px] text-gray-400">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
