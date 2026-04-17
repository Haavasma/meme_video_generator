import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { SpringIn } from "../../../lib/primitives";
import { Typewriter } from "../../../lib/primitives";

const ORANGE = "#f79009";
const BG = "#0a0e14";

/**
 * Title card with a moving "trace waterfall" particle background.
 * Title springs in, subtitle types, tagline fades.
 */
export function Scene01Title() {
  return (
    <AbsoluteFill style={{ backgroundColor: BG, overflow: "hidden" }}>
      <TraceWaterfall />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <SpringIn at={0} fromScale={0.5} fromY={80}>
          <h1
            style={{
              fontFamily: "'Impact', 'Anton', 'Arial Black', sans-serif",
              fontSize: 230,
              margin: 0,
              color: ORANGE,
              letterSpacing: "0.02em",
              WebkitTextStroke: "3px #000",
              paintOrder: "stroke fill",
              lineHeight: 1,
            }}
          >
            OBSERVABILITY
          </h1>
        </SpringIn>
        <div style={{ marginTop: 60, fontSize: 44, color: "#9ba1ad" }}>
          <Typewriter
            text="traces · logs · metrics · one place"
            at={50}
            cps={0.7}
            caret=""
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}

/** Horizontal particle flow mimicking a trace waterfall — purely decorative. */
function TraceWaterfall() {
  const frame = useCurrentFrame();
  const rows = 8;
  const cols = 20;
  return (
    <AbsoluteFill style={{ opacity: 0.35 }}>
      {Array.from({ length: rows }).map((_, r) => (
        <div
          key={r}
          style={{
            position: "absolute",
            top: `${8 + r * 12}%`,
            left: 0,
            right: 0,
            height: 4,
            display: "flex",
            gap: 6,
            paddingLeft: `${((frame * (0.8 + r * 0.1)) % 200) - 100}px`,
          }}
        >
          {Array.from({ length: cols }).map((_, c) => {
            const phase = (frame + r * 7 + c * 3) / 12;
            const w = 14 + Math.abs(Math.sin(phase)) * 120;
            const hue = (r * 40 + c * 6) % 360;
            const opacity = interpolate(
              Math.sin(phase + 0.5),
              [-1, 1],
              [0.15, 0.9],
            );
            return (
              <div
                key={c}
                style={{
                  width: w,
                  height: 4,
                  borderRadius: 4,
                  backgroundColor: `hsl(${30 + hue * 0.1}, 80%, 55%)`,
                  opacity,
                }}
              />
            );
          })}
        </div>
      ))}
    </AbsoluteFill>
  );
}
