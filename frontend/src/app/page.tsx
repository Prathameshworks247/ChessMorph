"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ControlBar, { sampleRandom } from "@/components/ControlBar";
import PieceDisplay from "@/components/PieceDisplay";
import SliderPanel from "@/components/SliderPanel";
import { generatePiece } from "@/lib/api";
import { debounce } from "@/lib/debounce";

const LATENT_DIM = 16;
const DEBOUNCE_MS = 100;

export default function Home() {
  const [latent, setLatent] = useState<number[]>(Array(LATENT_DIM).fill(0));
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    fetchImage(latent);
  }, [latent, fetchImage]);

  const handleSliderChange = (index: number, value: number) => {
    setLatent((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  };

  const handleRandomize = () => setLatent(sampleRandom(LATENT_DIM));
  const handleReset = () => setLatent(Array(LATENT_DIM).fill(0));

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 gap-8">
      <h1 className="text-3xl font-bold tracking-tight">
        Chess<span className="text-indigo-400">Morph</span>
      </h1>

      <div className="flex flex-col lg:flex-row gap-10 items-start justify-center w-full max-w-4xl">
        <div className="flex flex-col gap-5 w-full max-w-sm">
          <SliderPanel values={latent} onChange={handleSliderChange} />
          <ControlBar onRandomize={handleRandomize} onReset={handleReset} />
          {error && (
            <p className="text-red-400 text-xs">Error: {error}</p>
          )}
        </div>

        <div className="flex flex-col items-center gap-4">
          <PieceDisplay src={imageSrc} loading={loading} />
          <p className="text-xs text-gray-500">
            {loading ? "Generating…" : "64 × 64 silhouette from VAE decoder"}
          </p>
        </div>
      </div>
    </main>
  );
}
