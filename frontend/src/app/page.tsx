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

  // Animation state
  const [savedA, setSavedA] = useState<number[] | null>(null);
  const [savedB, setSavedB] = useState<number[] | null>(null);
  const [animating, setAnimating] = useState(false);
  const [frameLabel, setFrameLabel] = useState("");
  const animFrames = useRef<string[]>([]);
  const animTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const animIdx = useRef(0);

  // Load presets on mount
  useEffect(() => {
    fetchPresets()
      .then(setPresets)
      .catch(() => {}); // silently skip if backend not ready
  }, []);

  const fetchImage = useCallback(
    debounce(async (vec: number[]) => {
      setLoading(true);
      setError(null);
      try {
        const src = await generatePiece(vec);
        setImageSrc(src);
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

  // Animation logic
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
      // Also reverse so it loops A→B→A
      const loop = [...frames, ...[...frames].reverse()];
      animFrames.current = loop;
      animIdx.current = 0;
      setImageSrc(loop[0]);
      setFrameLabel(`1/${ANIMATE_FRAMES}`);

      animTimer.current = setInterval(() => {
        animIdx.current = (animIdx.current + 1) % loop.length;
        const i = animIdx.current;
        setImageSrc(loop[i]);
        // Show 1-based frame within the forward pass only
        const display = (i % ANIMATE_FRAMES) + 1;
        setFrameLabel(`${display}/${ANIMATE_FRAMES}`);
      }, FRAME_MS);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Interpolation failed");
      setAnimating(false);
    }
  }, [savedA, savedB]);

  // Cleanup on unmount
  useEffect(() => () => stopAnimation(), [stopAnimation]);

  const handleRandomize = () => {
    stopAnimation();
    setLatent(sampleRandom(LATENT_DIM));
  };
  const handleReset = () => {
    stopAnimation();
    setLatent(Array(LATENT_DIM).fill(0));
  };
  const handlePreset = (lat: number[]) => {
    stopAnimation();
    setLatent(lat);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 gap-8">
      <h1 className="text-3xl font-bold tracking-tight">
        Chess<span className="text-indigo-400">Morph</span>
      </h1>

      <PresetBar presets={presets} onSelect={handlePreset} disabled={animating} />

      <div className="flex flex-col lg:flex-row gap-10 items-start justify-center w-full max-w-4xl">
        <div className="flex flex-col gap-5 w-full max-w-sm">
          <SliderPanel values={latent} onChange={handleSliderChange} disabled={animating} />
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
          {error && <p className="text-red-400 text-xs">Error: {error}</p>}
        </div>

        <div className="flex flex-col items-center gap-4">
          <PieceDisplay
            src={imageSrc}
            loading={loading}
            animating={animating}
            theme={theme}
            frame={frameLabel}
          />
          <ThemeSelector current={theme} onChange={setTheme} />
          <p className="text-xs text-gray-500">
            {animating ? "Morphing…" : loading ? "Generating…" : "64 × 64 silhouette from VAE decoder"}
          </p>
        </div>
      </div>
    </main>
  );
}
