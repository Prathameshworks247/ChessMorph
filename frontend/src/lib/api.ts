const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export async function fetchPresets(): Promise<Record<string, number[]>> {
  const res = await fetch(`${API_BASE}/presets`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json() as Promise<Record<string, number[]>>;
}

export async function generatePiece(latent: number[]): Promise<string> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latent }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = (await res.json()) as { image: string };
  return `data:image/png;base64,${data.image}`;
}

export async function interpolatePieces(
  latentA: number[],
  latentB: number[],
  steps: number = 8
): Promise<string[]> {
  const res = await fetch(`${API_BASE}/interpolate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latent_a: latentA, latent_b: latentB, steps }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = (await res.json()) as { images: string[] };
  return data.images.map((b64) => `data:image/png;base64,${b64}`);
}
