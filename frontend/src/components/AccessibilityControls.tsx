interface Props {
  largeText: boolean;
  onToggleLargeText: () => void;
}

export function AccessibilityControls({ largeText, onToggleLargeText }: Props) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        aria-pressed={largeText}
        aria-label="큰 글씨 토글"
        onClick={onToggleLargeText}
        className={
          largeText ? "access-button access-button-active" : "access-button"
        }
      >
        가<span className="text-xs">+</span>
      </button>
    </div>
  );
}
