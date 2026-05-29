import type { AnalyzeResponse, Drug, MfdsItem, Profile } from "../types";

const BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

export async function analyzeRequest(
  drugs: Drug[],
  profile: Profile,
): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      drugs: drugs.map((d) => ({
        item_seq: d.item_seq,
        item_name: d.item_name,
        ingredient_codes: d.ingredient_codes ?? [],
      })),
      profile,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`분석 요청 실패 (${res.status}): ${text}`);
  }
  return res.json();
}

export async function searchMfds(query: string): Promise<MfdsItem[]> {
  if (!query.trim()) return [];
  try {
    const res = await fetch(
      `${BASE}/api/medicines/search?q=${encodeURIComponent(query)}`,
    );
    if (!res.ok) return [];
    return (await res.json()) as MfdsItem[];
  } catch {
    return [];
  }
}
