"use client";

import { THEMES, type Theme } from "./ThemeSelector";

interface Props {
  src: string | null;
  loading: boolean;
  animating?: boolean;
  theme: Theme;
  frame?: string;
}

const THEME_GLOW: Record<Theme, string> = {
  classic: "piece-glow-classic",
  gold:    "piece-glow-gold",
  marble:  "piece-glow-marble",
  neon:    "piece-glow-neon",
  wood:    "piece-glow-wood",
};

export default function PieceDisplay({ src, loading, animating, theme, frame }: Props) {
  const filter = THEMES[theme].filter;
  const glowClass = THEME_GLOW[theme];

  return (
    <div
      className={`
        relative flex items-center justify-center
        w-80 h-80
        rounded-3xl
        bg-[#0d0d1a]
        transition-shadow duration-700
        ${glowClass}
      `}
    >
      {/* Corner accent lines */}
      <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-8 h-px bg-gradient-to-r from-white/20 to-transparent" />
        <div className="absolute top-0 left-0 w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
        <div className="absolute top-0 right-0 w-8 h-px bg-gradient-to-l from-white/20 to-transparent" />
        <div className="absolute top-0 right-0 w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
        <div className="absolute bottom-0 left-0 w-8 h-px bg-gradient-to-r from-white/20 to-transparent" />
        <div className="absolute bottom-0 left-0 w-px h-8 bg-gradient-to-t from-white/20 to-transparent" />
        <div className="absolute bottom-0 right-0 w-8 h-px bg-gradient-to-l from-white/20 to-transparent" />
        <div className="absolute bottom-0 right-0 w-px h-8 bg-gradient-to-t from-white/20 to-transparent" />
      </div>

      {/* Shimmer loading overlay */}
      {loading && !animating && (
        <div className="absolute inset-0 rounded-3xl animate-shimmer opacity-60" />
      )}

      {/* Animating indicator */}
      {animating && (
        <div className="absolute top-3 right-3 flex items-center gap-1.5 z-10 bg-black/50 backdrop-blur-sm rounded-full px-2.5 py-1">
          <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
          <span className="text-[10px] text-red-300 font-mono tracking-wider">{frame ?? "LIVE"}</span>
        </div>
      )}

      {src ? (
        <img
          src={src}
          alt="Generated chess piece"
          className={`w-64 h-64 object-contain transition-all duration-100 ${
            loading && !animating ? "opacity-20" : "opacity-100 animate-float"
          }`}
          style={{
            imageRendering: "pixelated",
            filter,
          }}
        />
      ) : (
        !loading && (
          <div className="flex flex-col items-center gap-3 text-slate-600">
            <span className="text-5xl opacity-20 select-none">♟</span>
            <span className="text-xs text-center leading-relaxed max-w-[10rem]">
              Move a slider or pick a preset to generate
            </span>
          </div>
        )
      )}
    </div>
  );
}
