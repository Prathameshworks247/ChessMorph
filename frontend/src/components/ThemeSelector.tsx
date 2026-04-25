"use client";

export type Theme = "classic" | "gold" | "marble" | "neon" | "wood";

export const THEMES: Record<Theme, { label: string; swatch: string; filter: string }> = {
  classic: {
    label: "Classic",
    swatch: "bg-white border border-gray-600",
    filter: "",
  },
  gold: {
    label: "Gold",
    swatch: "bg-yellow-400",
    filter: "invert(1) sepia(1) saturate(8) hue-rotate(5deg) brightness(1.1)",
  },
  marble: {
    label: "Marble",
    swatch: "bg-slate-300",
    filter: "invert(1) sepia(0.2) saturate(1.5) brightness(1.2)",
  },
  neon: {
    label: "Neon",
    swatch: "bg-green-400",
    filter: "invert(1) sepia(1) saturate(10) hue-rotate(80deg) brightness(1.3)",
  },
  wood: {
    label: "Wood",
    swatch: "bg-amber-700",
    filter: "invert(1) sepia(0.8) saturate(3) hue-rotate(25deg) brightness(0.9)",
  },
};

interface Props {
  current: Theme;
  onChange: (theme: Theme) => void;
}

export default function ThemeSelector({ current, onChange }: Props) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500">Theme</span>
      <div className="flex gap-1.5">
        {(Object.keys(THEMES) as Theme[]).map((t) => (
          <button
            key={t}
            onClick={() => onChange(t)}
            title={THEMES[t].label}
            className={`w-5 h-5 rounded-full ${THEMES[t].swatch} transition-transform ${
              current === t ? "ring-2 ring-indigo-400 scale-110" : "hover:scale-110"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
