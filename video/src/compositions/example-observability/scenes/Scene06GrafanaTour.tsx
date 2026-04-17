import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { ScreenMockup, SpringIn } from "../../../lib/primitives";

const ORANGE = "#f79009";

interface Callout {
  readonly at: number;
  readonly xPct: number;
  readonly yPct: number;
  readonly widthPct: number;
  readonly heightPct: number;
  readonly label: string;
}

const CALLOUTS: readonly Callout[] = [
  {
    at: 20,
    xPct: 6,
    yPct: 8,
    widthPct: 38,
    heightPct: 20,
    label: "time series · metrics",
  },
  {
    at: 90,
    xPct: 50,
    yPct: 8,
    widthPct: 44,
    heightPct: 40,
    label: "logs · loki",
  },
  {
    at: 165,
    xPct: 6,
    yPct: 55,
    widthPct: 88,
    heightPct: 38,
    label: "traces · tempo waterfall",
  },
];

/**
 * Real Grafana screenshot (Wikimedia Commons, CC BY-SA 4.0; re-encoded to
 * 1920-wide JPEG so Remotion's bundler / Chromium reliably loads it)
 * framed in a browser mockup with pulsing orange callouts that fire in
 * sequence to label each signal region of the dashboard.
 */
export function Scene06GrafanaTour() {
  const frame = useCurrentFrame();
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
            color: ORANGE,
            textAlign: "center",
            letterSpacing: "0.02em",
            marginBottom: 24,
            WebkitTextStroke: "2px #000",
            paintOrder: "stroke fill",
          }}
        >
          ONE PANE OF GLASS
        </div>
      </SpringIn>
      <SpringIn at={8} fromY={20} fromScale={0.92} style={{ flex: 1 }}>
        <ScreenMockup
          kind="browser"
          title="grafana.internal — Explore"
          style={{ width: "100%", height: "100%" }}
        >
          <Img
            src={staticFile("assets/grafana_screenshot.jpg")}
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
          {CALLOUTS.map((c) => (
            <PulseBox key={c.at} frame={frame} callout={c} />
          ))}
        </ScreenMockup>
      </SpringIn>
      <div style={{ marginTop: 16, textAlign: "center" }}>
        <SpringIn at={210} fromY={15}>
          <div
            style={{
              fontFamily: "Inter, sans-serif",
              fontSize: 34,
              color: "#cfd4dc",
              fontWeight: 600,
            }}
          >
            metrics · logs · traces · one dashboard
          </div>
        </SpringIn>
      </div>
    </AbsoluteFill>
  );
}

function PulseBox({ frame, callout }: { frame: number; callout: Callout }) {
  const elapsed = frame - callout.at;
  if (elapsed < 0) return null;
  const pulse = interpolate(Math.sin(elapsed / 6), [-1, 1], [0.25, 1]);
  const opacity = interpolate(elapsed, [0, 12, 70, 100], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: `${callout.xPct}%`,
        top: `${callout.yPct}%`,
        width: `${callout.widthPct}%`,
        height: `${callout.heightPct}%`,
        border: `5px solid ${ORANGE}`,
        borderRadius: 12,
        boxShadow: `0 0 ${12 + pulse * 30}px ${ORANGE}`,
        opacity,
      }}
    >
      <div
        style={{
          position: "absolute",
          bottom: -48,
          left: 0,
          padding: "6px 14px",
          backgroundColor: ORANGE,
          color: "#0a0e14",
          fontFamily: "Inter, sans-serif",
          fontWeight: 800,
          fontSize: 24,
          borderRadius: 8,
          letterSpacing: "0.02em",
        }}
      >
        {callout.label}
      </div>
    </div>
  );
}
