"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ControlBar, { sampleRandom } from "@/components/ControlBar";
import PieceDisplay from "@/components/PieceDisplay";
import PresetBar from "@/components/PresetBar";
import SliderPanel from "@/components/SliderPanel";
import ThemeSelector, { type Theme } from "@/components/ThemeSelector";
import { fetchPresets, generatePiece, interpolatePieces } from "@/lib/api";
import { debounce } from "@/lib/debounce";

const LATENT_DIM = 16;
const DEBOUNCE_MS = 100;
const ANIMATE_FRAMES = 12;
const FRAME_MS = 80;

export default function Home() {
  const [latent, setLatent] = useState<number[]>(Array(LATENT_DIM).fill(0));
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<Theme>("gold");
  const [presets, setPresets] = useState<Record<string, number[]>>({});
  const [hasLoaded, setHasLoaded] = useState(false);

  const [savedA, setSavedA] = useState<number[] | null>(null);
  const [savedB, setSavedB] = useState<number[] | null>(null);
  const [animating, setAnimating] = useState(false);
  const [frameLabel, setFrameLabel] = useState("");
  const animFrames = useRef<string[]>([]);
  const animTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const animIdx = useRef(0);

  useEffect(() => {
    fetchPresets()
      .then(setPresets)
      .catch(() => {});
  }, []);

  const fetchImage = useCallback(
    debounce(async (vec: number[]) => {
      setLoading(true);
      setError(null);
      try {
        const src = await generatePiece(vec);
        setImageSrc(src);
        setHasLoaded(true);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }, DEBOUNCE_MS),
    []
  );

  useEffect(() => {
    if (!animating) fetchImage(latent);
  }, [latent, fetchImage, animating]);

  const handleSliderChange = (index: number, value: number) => {
    setLatent((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  };

  const stopAnimation = useCallback(() => {
    if (animTimer.current) {
      clearInterval(animTimer.current);
      animTimer.current = null;
    }
    setAnimating(false);
    setFrameLabel("");
  }, []);

  const startAnimation = useCallback(async () => {
    if (!savedA || !savedB) return;
    setAnimating(true);
    setError(null);
    try {
      const frames = await interpolatePieces(savedA, savedB, ANIMATE_FRAMES);
      const loop = [...frames, ...[...frames].reverse()];
      animFrames.current = loop;
      animIdx.current = 0;
      setImageSrc(loop[0]);
      setFrameLabel(`1/${ANIMATE_FRAMES}`);

      animTimer.current = setInterval(() => {
        animIdx.current = (animIdx.current + 1) % loop.length;
        const i = animIdx.current;
        setImageSrc(loop[i]);
        const display = (i % ANIMATE_FRAMES) + 1;
        setFrameLabel(`${display}/${ANIMATE_FRAMES}`);
      }, FRAME_MS);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Interpolation failed");
      setAnimating(false);
    }
  }, [savedA, savedB]);

  useEffect(() => () => stopAnimation(), [stopAnimation]);

  const handleRandomize = () => { stopAnimation(); setLatent(sampleRandom(LATENT_DIM)); };
  const handleReset = () => { stopAnimation(); setLatent(Array(LATENT_DIM).fill(0)); };
  const handlePreset = (lat: number[]) => { stopAnimation(); setLatent(lat); };

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-start pt-10 pb-16 px-6 gap-10 overflow-hidden">

      {/* Dot grid background layer */}
      <div className="dot-grid fixed inset-0 pointer-events-none opacity-40" />

      {/* ── Header ─────────────────────────────────────────── */}
      <header className="flex flex-col items-center gap-2 z-10">
        <div className="flex items-center gap-3">
          <span className="text-3xl leading-none select-none">♟</span>
          <h1 className="text-4xl font-bold tracking-tight">
            <span className="text-white">Chess</span>
            <span
              className="bg-clip-text text-transparent"
              style={{
                backgroundImage: "linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #c4b5fd 100%)",
              }}
            >
              Morph
            </span>
          </h1>
        </div>
        <p className="text-sm text-slate-400 font-light tracking-wide">
          Beta-VAE latent space explorer &mdash; 16 dimensions, real-time inference
        </p>
      </header>

      {/* ── Preset bar ─────────────────────────────────────── */}
      <div className="z-10">
        <PresetBar presets={presets} onSelect={handlePreset} disabled={animating} />
      </div>

      {/* ── Main two-column layout ──────────────────────────── */}
      <div className="flex flex-col lg:flex-row gap-6 items-start justify-center w-full max-w-5xl z-10">

        {/* Left: Sliders + Controls */}
        <div className="glass rounded-2xl p-5 flex flex-col gap-5 w-full max-w-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest text-slate-500">
              Latent Dimensions
            </span>
            <span className="font-mono text-[10px] text-slate-600">16-dim β-VAE</span>
          </div>
          <SliderPanel values={latent} onChange={handleSliderChange} disabled={animating} />
          <div className="border-t border-white/5 pt-4">
            <ControlBar
              onRandomize={handleRandomize}
              onReset={handleReset}
              onSaveA={() => setSavedA([...latent])}
              onSaveB={() => setSavedB([...latent])}
              onAnimate={startAnimation}
              onStop={stopAnimation}
              hasSavedA={savedA !== null}
              hasSavedB={savedB !== null}
              animating={animating}
            />
          </div>
          {error && (
            <p className="text-red-400 text-xs bg-red-950/40 border border-red-800/40 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
        </div>

        {/* Right: Piece + Theme + Status */}
        <div className="flex flex-col items-center gap-5">
          <PieceDisplay
            src={imageSrc}
            loading={loading}
            animating={animating}
            theme={theme}
            frame={frameLabel}
          />

          <ThemeSelector current={theme} onChange={setTheme} />

          <p className="text-xs text-slate-600 font-mono tracking-wide">
            {animating
              ? "▶ morphing…"
              : loading
              ? "⟳ decoding…"
              : "64 × 64 · VAE decoder · ONNX Runtime"}
          </p>

          {!hasLoaded && (
            <div className="flex items-start gap-2.5 max-w-[17rem] rounded-xl border border-amber-700/40 bg-amber-950/30 px-4 py-3 text-amber-300/80">
              <svg className="mt-0.5 h-3.5 w-3.5 shrink-0 opacity-80" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1Zm0 3a.75.75 0 1 1 0 1.5A.75.75 0 0 1 8 4Zm-.25 3h1.5v4.5h-1.5V7Z" />
              </svg>
              <p className="text-[11px] leading-snug">
                First request may take{" "}
                <span className="font-semibold text-amber-200">1–2 minutes</span>
                {" "}— backend wakes from sleep on first visit.
              </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
