import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { ScreenMockup, SpringIn } from "../../../lib/primitives";

const PURPLE = "#c084fc";
const ORANGE = "#f79009";

/**
 * Tempo trace waterfall showcase. Uses a real Grafana-Tempo screenshot
 * (nais.io docs) rendered in a browser mockup. Adds an animated scan line
 * sweeping across to suggest "reading the waterfall" plus a pair of
 * callouts pointing at a span and its child spans.
 */
export function Scene06bTraceView() {
  const frame = useCurrentFrame();
  const scanX = interpolate(frame, [20, 150], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0e14",
        padding: 60,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <SpringIn at={0} fromY={-20}>
        <div
          style={{
            fontFamily: "Impact, sans-serif",
            fontSize: 68,
            color: PURPLE,
            textAlign: "center",
            letterSpacing: "0.02em",
            marginBottom: 20,
            WebkitTextStroke: "2px #000",
            paintOrder: "stroke fill",
          }}
        >
          TEMPO · TRACE WATERFALL
        </div>
      </SpringIn>
      <SpringIn at={8} fromY={20} fromScale={0.92} style={{ flex: 1 }}>
        <ScreenMockup
          kind="browser"
          title="grafana.internal — Tempo / Trace ID"
          style={{ width: "100%", height: "100%" }}
        >
          <Img
            src={staticFile("assets/tempo_trace_view.jpg")}
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
          {/* Vertical scan line sweeping left-to-right */}
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `${scanX}%`,
              width: 3,
              backgroundColor: PURPLE,
              boxShadow: `0 0 18px ${PURPLE}`,
              opacity: 0.85,
            }}
          />
          {/* Callout 1: root span */}
          <Callout
            at={30}
            xPct={4}
            yPct={18}
            widthPct={40}
            heightPct={10}
            color={PURPLE}
            label="root span · request enters"
          />
          {/* Callout 2: child spans */}
          <Callout
            at={95}
            xPct={32}
            yPct={38}
            widthPct={58}
            heightPct={30}
            color={ORANGE}
            label="child spans · db + upstream calls"
          />
        </ScreenMockup>
      </SpringIn>
      <div style={{ marginTop: 16, textAlign: "center" }}>
        <SpringIn at={170} fromY={15}>
          <div
            style={{
              fontFamily: "Inter, sans-serif",
              fontSize: 34,
              color: "#cfd4dc",
              fontWeight: 600,
            }}
          >
            every span · every service · every latency
          </div>
        </SpringIn>
      </div>
    </AbsoluteFill>
  );
}

interface CalloutProps {
  readonly at: number;
  readonly xPct: number;
  readonly yPct: number;
  readonly widthPct: number;
  readonly heightPct: number;
  readonly label: string;
  readonly color: string;
}

function Callout({
  at,
  xPct,
  yPct,
  widthPct,
  heightPct,
  label,
  color,
}: CalloutProps) {
  const frame = useCurrentFrame();
  const elapsed = frame - at;
  if (elapsed < 0) return null;
  const pulse = interpolate(Math.sin(elapsed / 6), [-1, 1], [0.3, 1]);
  const opacity = interpolate(elapsed, [0, 10, 70, 110], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: `${xPct}%`,
        top: `${yPct}%`,
        width: `${widthPct}%`,
        height: `${heightPct}%`,
        border: `5px solid ${color}`,
        borderRadius: 12,
        boxShadow: `0 0 ${12 + pulse * 28}px ${color}`,
        opacity,
      }}
    >
      <div
        style={{
          position: "absolute",
          bottom: -44,
          left: 0,
          padding: "6px 14px",
          backgroundColor: color,
          color: "#0a0e14",
          fontFamily: "Inter, sans-serif",
          fontWeight: 800,
          fontSize: 24,
          borderRadius: 8,
          letterSpacing: "0.02em",
        }}
      >
        {label}
      </div>
    </div>
  );
}
