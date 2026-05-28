import { useTTS } from "../hooks/useTTS";

interface Props {
  text: string;
  label?: string;
}

export function TTSButton({ text, label = "시너시오" }: Props) {
  const { supported, speaking, speak, stop } = useTTS();
  if (!supported) return null;
  return (
    <button
      type="button"
      onClick={() => (speaking ? stop() : speak(text))}
      className="text-xs px-3 py-1 rounded-full border border-brand-line text-brand-ink bg-white hover:bg-brand-surface"
      aria-pressed={speaking}
    >
      {speaking ? "■ 멈춤" : `🔊 ${label}`}
    </button>
  );
}
