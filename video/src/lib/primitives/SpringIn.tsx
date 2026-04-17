import type { CSSProperties, ReactNode } from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

interface SpringInProps {
  /** Frame offset within the current Sequence when the spring should start. */
  readonly at?: number;
  /** Spring damping — lower = bouncier. Default 12 gives a friendly product-demo feel. */
  readonly damping?: number;
  /** Stiffness — higher = snappier. Default 120. */
  readonly stiffness?: number;
  /** Scale at start; spring animates from this to 1. Default 0.6. */
  readonly fromScale?: number;
  /** Vertical pixel offset at start; spring animates to 0. Default 40 (pops up). */
  readonly fromY?: number;
  /**
   * Style merged onto the transform wrapper. Use e.g. `{ flex: 1 }` so the
   * wrapped child participates in the parent flex layout; without this,
   * `display: contents` on an outer shell would swallow the layout role.
   */
  readonly style?: CSSProperties;
  readonly children: ReactNode;
}

/**
 * Wrap children to give them a spring-based "pop-in" (scale + rise + fade).
 *
 * Renders as a single div whose transform animates in. `style` is applied
 * directly to this transform div so callers can set `flex: 1`, `width: "100%"`,
 * etc. and have the effect survive the wrapper.
 */
export function SpringIn({
  at = 0,
  damping = 12,
  stiffness = 120,
  fromScale = 0.6,
  fromY = 40,
  style,
  children,
}: SpringInProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({
    frame: frame - at,
    fps,
    config: { damping, stiffness, mass: 1 },
  });
  const scale = fromScale + (1 - fromScale) * progress;
  const y = fromY * (1 - progress);
  const opacity = Math.max(0, Math.min(1, progress));
  return (
    <div
      data-testid="spring-in"
      style={{
        transform: `translateY(${y}px) scale(${scale})`,
        opacity,
        transformOrigin: "center",
        willChange: "transform, opacity",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
