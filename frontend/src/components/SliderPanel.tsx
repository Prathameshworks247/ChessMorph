"use client";

interface Props {
  values: number[];
  onChange: (index: number, value: number) => void;
  disabled?: boolean;
}

export default function SliderPanel({ values, onChange, disabled }: Props) {
  return (
    <div
      className={`grid grid-cols-2 gap-x-5 gap-y-3.5 ${
        disabled ? "opacity-30 pointer-events-none" : ""
      }`}
    >
      {values.map((val, i) => {
        // map [-3, 3] → [0%, 100%] for the CSS fill variable
        const fillPct = ((val + 3) / 6) * 100;
        return (
          <div key={i} className="flex flex-col gap-1">
            <div className="flex justify-between items-baseline">
              <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                z{i + 1}
              </span>
              <span
                className="text-[11px] tabular-nums text-slate-400"
                style={{ fontFamily: "var(--font-dm-mono, monospace)" }}
              >
                {val >= 0 ? "+" : ""}
                {val.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min={-3}
              max={3}
              step={0.1}
              value={val}
              onChange={(e) => onChange(i, parseFloat(e.target.value))}
              style={{ "--slider-fill": `${fillPct}%` } as React.CSSProperties}
            />
          </div>
        );
      })}
    </div>
  );
}
