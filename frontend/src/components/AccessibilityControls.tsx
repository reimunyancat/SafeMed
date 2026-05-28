interface Props {
  largeText: boolean;
  highContrast: boolean;
  onToggleLargeText: () => void;
  onToggleHighContrast: () => void;
}

export function AccessibilityControls({
  largeText,
  highContrast,
  onToggleLargeText,
  onToggleHighContrast,
}: Props) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        aria-pressed={largeText}
        aria-label="큰 글씨 토글"
        onClick={onToggleLargeText}
        className={largeText ? "access-button access-button-active" : "access-button"}
      >
        가<span className="text-xs">+</span>
      </button>
      <button
        type="button"
        aria-pressed={highContrast}
        aria-label="고대비 모드 토글"
        onClick={onToggleHighContrast}
        className={highContrast ? "access-button access-button-active" : "access-button"}
      >
        ◑
      </button>
    </div>
  );
}
