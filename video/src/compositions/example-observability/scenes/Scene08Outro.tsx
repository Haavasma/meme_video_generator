import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { SpringIn } from "../../../lib/primitives";

const ORANGE = "#f79009";

interface SignalIconProps {
  readonly label: string;
  readonly color: string;
  readonly angle: number; // degrees; where the icon starts before converging
  readonly distance: number;
}

function SignalIcon({ label, color, angle, distance }: SignalIconProps) {
  const frame = useCurrentFrame();
  // Converge from outer ring → center over frames 0..60, hold → fade at 100+
  const t = interpolate(frame, [0, 60], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rad = (angle * Math.PI) / 180;
  const dx = Math.cos(rad) * distance * t;
  const dy = Math.sin(rad) * distance * t;
  const opacity = interpolate(frame, [0, 20, 95, 130], [0, 1, 1, 0.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: `calc(50% + ${dx}px - 100px)`,
        top: `calc(50% + ${dy}px - 100px)`,
        width: 200,
        height: 200,
        borderRadius: 200,
        backgroundColor: color,
        boxShadow: `0 0 60px ${color}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#0a0e14",
        fontFamily: "Impact, sans-serif",
        fontSize: 36,
        fontWeight: 900,
        opacity,
      }}
    >
      {label}
    </div>
  );
}

export function Scene08Outro() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0e14",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <SignalIcon label="TRACE" color="#c084fc" angle={210} distance={420} />
      <SignalIcon label="LOG" color="#27c93f" angle={-30} distance={420} />
      <SignalIcon label="METRIC" color="#4fc3f7" angle={90} distance={420} />

      <SpringIn at={60} fromScale={0.2} fromY={0}>
        <div
          style={{
            width: 340,
            height: 340,
            borderRadius: 340,
            backgroundColor: ORANGE,
            boxShadow: `0 0 120px ${ORANGE}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "Impact, sans-serif",
            color: "#0a0e14",
            fontSize: 180,
            fontWeight: 900,
          }}
        >
          G
        </div>
      </SpringIn>

      <div
        style={{
          position: "absolute",
          bottom: 160,
          width: "100%",
          textAlign: "center",
        }}
      >
        <SpringIn at={90} fromY={30}>
          <div
            style={{
              fontFamily: "Impact, sans-serif",
              fontSize: 90,
              color: "#fff",
              letterSpacing: "0.02em",
              WebkitTextStroke: "2px #000",
              paintOrder: "stroke fill",
            }}
          >
            HAPPY DEBUGGING
          </div>
        </SpringIn>
        <SpringIn at={110} fromY={20}>
          <div
            style={{
              fontFamily: "'Fira Code', monospace",
              fontSize: 36,
              color: "#9ba1ad",
              marginTop: 14,
            }}
          >
            #cdp-platform
          </div>
        </SpringIn>
      </div>
    </AbsoluteFill>
  );
}
