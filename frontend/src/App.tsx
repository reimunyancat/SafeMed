import { useState } from "react";
import { analyzeRequest } from "./api/client";
import { AnalyzeButton } from "./components/AnalyzeButton";
import { Disclaimer } from "./components/Disclaimer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { MedicineSearch } from "./components/MedicineSearch";
import { ProfileForm } from "./components/ProfileForm";
import { ResultDashboard } from "./components/ResultDashboard";
import { SelectedMedicineList } from "./components/SelectedMedicineList";
import { useAccessibility } from "./hooks/useAccessibility";
import type { AnalyzeResponse, Drug, Profile } from "./types";

export default function App() {
  const a11y = useAccessibility();
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [profile, setProfile] = useState<Profile>({
    age: 70,
    is_pregnant: false,
    conditions: [],
  });
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addDrug = (d: Drug) => {
    setDrugs((cur) => (cur.some((x) => x.item_seq === d.item_seq) ? cur : [...cur, d]));
  };
  const removeDrug = (seq: string) => {
    setDrugs((cur) => cur.filter((d) => d.item_seq !== seq));
  };

  const analyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeRequest(drugs, profile);
      setResult(res);
      setTimeout(() => {
        document
          .getElementById("safemed-result")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 50);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-frame">
        <Header a11y={a11y} />
        <Hero />
        <Disclaimer />
        <MedicineSearch onAdd={addDrug} selected={drugs} />
        <SelectedMedicineList drugs={drugs} onRemove={removeDrug} />
        <ProfileForm value={profile} onChange={setProfile} />
        <AnalyzeButton
          disabled={drugs.length === 0}
          loading={loading}
          onClick={analyze}
        />
        {error && (
          <div className="mx-5 mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
            {error}
          </div>
        )}
        <div id="safemed-result">
          {result && <ResultDashboard result={result} drugs={drugs} />}
        </div>
      </div>
    </div>
  );
}
