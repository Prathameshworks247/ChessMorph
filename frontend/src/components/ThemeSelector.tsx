"use client";

export type Theme = "classic" | "gold" | "marble" | "neon" | "wood";

export const THEMES: Record<Theme, { label: string; swatch: string; filter: string; ring: string }> = {
  classic: {
    label: "Classic",
    swatch: "bg-white",
    filter: "",
    ring: "ring-slate-300/60",
  },
  gold: {
    label: "Gold",
    swatch: "bg-yellow-400",
    filter: "invert(1) sepia(1) saturate(8) hue-rotate(5deg) brightness(1.1)",
    ring: "ring-yellow-400/60",
  },
  marble: {
    label: "Marble",
    swatch: "bg-slate-300",
    filter: "invert(1) sepia(0.2) saturate(1.5) brightness(1.2)",
    ring: "ring-slate-300/60",
  },
  neon: {
    label: "Neon",
    swatch: "bg-green-400",
    filter: "invert(1) sepia(1) saturate(10) hue-rotate(80deg) brightness(1.3)",
    ring: "ring-green-400/60",
  },
  wood: {
    label: "Wood",
    swatch: "bg-amber-700",
    filter: "invert(1) sepia(0.8) saturate(3) hue-rotate(25deg) brightness(0.9)",
    ring: "ring-amber-600/60",
  },
};

interface Props {
  current: Theme;
  onChange: (theme: Theme) => void;
}

export default function ThemeSelector({ current, onChange }: Props) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-600">
        Tint
      </span>
      <div className="flex gap-2">
        {(Object.keys(THEMES) as Theme[]).map((t) => {
          const active = current === t;
          return (
            <button
              key={t}
              onClick={() => onChange(t)}
              title={THEMES[t].label}
              className={`
                w-6 h-6 rounded-full
                ${THEMES[t].swatch}
                transition-all duration-200
                ${active
                  ? `ring-2 ring-offset-2 ring-offset-[#07070f] scale-125 ${THEMES[t].ring}`
                  : "hover:scale-115 opacity-60 hover:opacity-100"
                }
              `}
            />
          );
        })}
      </div>
    </div>
  );
}
