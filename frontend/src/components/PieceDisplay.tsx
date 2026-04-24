"use client";

interface Props {
  src: string | null;
  loading: boolean;
}

export default function PieceDisplay({ src, loading }: Props) {
  return (
    <div className="relative flex items-center justify-center w-64 h-64 bg-gray-900 rounded-2xl border border-gray-700">
      {loading && (
        <div className="absolute inset-0 rounded-2xl bg-gray-800 animate-pulse" />
      )}
      {src ? (
        <img
          src={src}
          alt="Generated chess piece"
          className={`w-56 h-56 object-contain transition-opacity duration-150 ${
            loading ? "opacity-30" : "opacity-100"
          }`}
          style={{ imageRendering: "pixelated" }}
        />
      ) : (
        !loading && (
          <span className="text-gray-500 text-sm">Move a slider to generate</span>
        )
      )}
    </div>
  );
}
