import type { FC } from "react";
import { interpolate, useCurrentFrame } from "remotion";

interface AnimatedArrowProps {
  readonly from: { x: number; y: number };
  readonly to: { x: number; y: number };
  /** Frame on which the draw-in begins. */
  readonly at?: number;
  /** Total frames to complete the draw. Default 20. */
  readonly duration?: number;
  readonly color?: string;
  readonly strokeWidth?: number;
  /** Show arrowhead at the "to" end. Default true. */
  readonly head?: boolean;
  /** Optional dash pattern for stylized arrows. */
  readonly dash?: string;
}

/**
 * SVG arrow that draws itself from `from` to `to` via strokeDashoffset.
 * Use for flow diagrams: Pod → Alloy → Tempo. Pair multiple arrows with
 * different `at` values to show the pipeline light up step-by-step.
 */
export const AnimatedArrow: FC<AnimatedArrowProps> = ({
  from,
  to,
  at = 0,
  duration = 20,
  color = "#f79009",
  strokeWidth = 6,
  head = true,
  dash,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - at, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const length = Math.hypot(to.x - from.x, to.y - from.y);
  const dashOffset = length * (1 - progress);

  return (
    <svg
      data-testid="animated-arrow"
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      width="100%"
      height="100%"
    >
      <defs>
        <marker
          id={`head-${color.replace("#", "")}`}
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill={color} />
        </marker>
      </defs>
      <line
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={dash ?? `${length}`}
        strokeDashoffset={dashOffset}
        markerEnd={head ? `url(#head-${color.replace("#", "")})` : undefined}
        opacity={progress > 0 ? 1 : 0}
      />
    </svg>
  );
};
