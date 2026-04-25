"use client";

import { THEMES, type Theme } from "./ThemeSelector";

interface Props {
  src: string | null;
  loading: boolean;
  animating?: boolean;
  theme: Theme;
  frame?: string;
}

export default function PieceDisplay({ src, loading, animating, theme, frame }: Props) {
  const filter = THEMES[theme].filter;

  return (
    <div className="relative flex items-center justify-center w-64 h-64 bg-gray-900 rounded-2xl border border-gray-700">
      {loading && !animating && (
        <div className="absolute inset-0 rounded-2xl bg-gray-800 animate-pulse" />
      )}

      {animating && (
        <div className="absolute top-2 right-2 flex items-center gap-1 z-10">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-[10px] text-red-400 font-mono">{frame ?? "LIVE"}</span>
        </div>
      )}

      {src ? (
        <img
          src={src}
          alt="Generated chess piece"
          className="w-56 h-56 object-contain transition-opacity duration-75"
          style={{
            imageRendering: "pixelated",
            filter,
            opacity: loading && !animating ? 0.3 : 1,
          }}
        />
      ) : (
        !loading && (
          <span className="text-gray-500 text-sm text-center px-4">
            Move a slider or pick a preset
          </span>
        )
      )}
    </div>
  );
}
