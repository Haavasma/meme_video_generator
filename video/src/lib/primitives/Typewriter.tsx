import type { CSSProperties, FC } from "react";
import { useCurrentFrame } from "remotion";

interface TypewriterProps {
  readonly text: string;
  /** Frame offset within the current Sequence when typing should start. */
  readonly at?: number;
  /** Characters per frame. Default 0.5 = 15 cps at 30fps (brisk, readable). */
  readonly cps?: number;
  /** Blinking caret char. Use "" to hide. Default "▋". */
  readonly caret?: string;
  readonly style?: CSSProperties;
}

/**
 * Reveal text one character at a time. Good for code blocks, terminal lines,
 * any "I'm typing this in front of you" beat.
 */
export const Typewriter: FC<TypewriterProps> = ({
  text,
  at = 0,
  cps = 0.5,
  caret = "▋",
  style,
}) => {
  const frame = useCurrentFrame();
  const elapsed = Math.max(0, frame - at);
  const chars = Math.min(text.length, Math.floor(elapsed * cps));
  const revealed = text.slice(0, chars);
  const showCaret = caret && Math.floor(frame / 8) % 2 === 0;
  return (
    <span
      data-testid="typewriter"
      style={{
        fontFamily:
          "'Fira Code', 'JetBrains Mono', 'SF Mono', Consolas, monospace",
        whiteSpace: "pre-wrap",
        ...style,
      }}
    >
      {revealed}
      {showCaret ? caret : " "}
    </span>
  );
};
