"use client";

interface Props {
  values: number[];
  onChange: (index: number, value: number) => void;
  disabled?: boolean;
}

export default function SliderPanel({ values, onChange, disabled }: Props) {
  return (
    <div className={`grid grid-cols-2 gap-x-6 gap-y-3 ${disabled ? "opacity-40 pointer-events-none" : ""}`}>
      {values.map((val, i) => (
        <div key={i} className="flex flex-col gap-1">
          <div className="flex justify-between text-xs text-gray-400">
            <span>PC{i + 1}</span>
            <span>{val.toFixed(1)}</span>
          </div>
          <input
            type="range"
            min={-3}
            max={3}
            step={0.1}
            value={val}
            onChange={(e) => onChange(i, parseFloat(e.target.value))}
            className="w-full h-1.5 accent-indigo-500 cursor-pointer"
          />
        </div>
      ))}
    </div>
  );
}
