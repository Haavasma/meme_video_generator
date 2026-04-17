import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { AnimatedArrow, SpringIn } from "../../../lib/primitives";

const BG = "#0a0e14";
const ORANGE = "#f79009";

interface NodeBoxProps {
  readonly at: number;
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly label: string;
  readonly sublabel?: string;
  readonly color?: string;
  readonly glow?: boolean;
}

function NodeBox(props: NodeBoxProps) {
  const frame = useCurrentFrame();
  const pulse = props.glow
    ? interpolate(
        Math.sin((frame - props.at) / 10),
        [-1, 1],
        [0.25, 0.9],
      )
    : 0;
  return (
    <div
      style={{
        position: "absolute",
        left: props.x,
        top: props.y,
        width: props.width,
        height: props.height,
      }}
    >
      <SpringIn at={props.at}>
        <div
          style={{
            width: props.width,
            height: props.height,
            borderRadius: 18,
            backgroundColor: "#141922",
            border: `3px solid ${props.color ?? "#444"}`,
            boxShadow: props.glow
              ? `0 0 ${20 + pulse * 40}px ${props.color ?? ORANGE}`
              : "0 8px 40px rgba(0,0,0,0.5)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontFamily: "Inter, sans-serif",
            fontWeight: 700,
          }}
        >
          <div style={{ fontSize: 42, color: props.color ?? "#fff" }}>
            {props.label}
          </div>
          {props.sublabel ? (
            <div
              style={{
                fontSize: 22,
                color: "#9ba1ad",
                marginTop: 6,
                fontWeight: 500,
              }}
            >
              {props.sublabel}
            </div>
          ) : null}
        </div>
      </SpringIn>
    </div>
  );
}

/**
 * Traveling signal dot — moves along a polyline of given waypoints.
 * Loops every `period` frames starting at `startFrame`.
 */
function SignalDot({
  waypoints,
  startFrame,
  period,
  color,
  size = 18,
}: {
  waypoints: { x: number; y: number }[];
  startFrame: number;
  period: number;
  color: string;
  size?: number;
}) {
  const frame = useCurrentFrame();
  const elapsed = frame - startFrame;
  if (elapsed < 0) return null;
  const t = (elapsed % period) / period;
  const seg = t * (waypoints.length - 1);
  const i = Math.min(waypoints.length - 2, Math.floor(seg));
  const local = seg - i;
  const a = waypoints[i]!;
  const b = waypoints[i + 1]!;
  const x = a.x + (b.x - a.x) * local;
  const y = a.y + (b.y - a.y) * local;
  return (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: size,
        backgroundColor: color,
        boxShadow: `0 0 20px ${color}, 0 0 40px ${color}`,
      }}
    />
  );
}

export function Scene05Architecture() {
  // Layout: Pod (L) → Alloy (center) → fan out to Prom/Tempo/Loki → merge → Grafana (R)
  const pod = { x: 140, y: 480, w: 260, h: 140 };
  const alloy = { x: 620, y: 480, w: 300, h: 140 };
  const prom = { x: 1080, y: 240, w: 260, h: 120 };
  const tempo = { x: 1080, y: 480, w: 260, h: 120 };
  const loki = { x: 1080, y: 720, w: 260, h: 120 };
  const grafana = { x: 1480, y: 480, w: 300, h: 140 };

  const cx = (b: { x: number; y: number; w: number; h: number }) => ({
    x: b.x + b.w / 2,
    y: b.y + b.h / 2,
  });

  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {/* Title */}
      <div style={{ position: "absolute", top: 60, width: "100%", textAlign: "center" }}>
        <SpringIn at={0} fromY={-20}>
          <div
            style={{
              fontFamily: "Impact, sans-serif",
              fontSize: 72,
              color: "#fff",
              letterSpacing: "0.02em",
            }}
          >
            ONE PIPELINE · THREE SIGNALS
          </div>
        </SpringIn>
      </div>

      {/* Nodes */}
      <NodeBox
        at={8}
        x={pod.x}
        y={pod.y}
        width={pod.w}
        height={pod.h}
        label="Your Pod"
        sublabel="OTLP exporter"
        color="#4fc3f7"
      />
      <NodeBox
        at={40}
        x={alloy.x}
        y={alloy.y}
        width={alloy.w}
        height={alloy.h}
        label="Alloy"
        sublabel="universal collector"
        color={ORANGE}
        glow
      />
      <NodeBox
        at={80}
        x={prom.x}
        y={prom.y}
        width={prom.w}
        height={prom.h}
        label="Prometheus"
        sublabel="metrics"
        color="#4fc3f7"
      />
      <NodeBox
        at={90}
        x={tempo.x}
        y={tempo.y}
        width={tempo.w}
        height={tempo.h}
        label="Tempo"
        sublabel="traces"
        color="#c084fc"
      />
      <NodeBox
        at={100}
        x={loki.x}
        y={loki.y}
        width={loki.w}
        height={loki.h}
        label="Loki"
        sublabel="logs"
        color="#27c93f"
      />
      <NodeBox
        at={140}
        x={grafana.x}
        y={grafana.y}
        width={grafana.w}
        height={grafana.h}
        label="Grafana"
        sublabel="single pane of glass"
        color={ORANGE}
        glow
      />

      {/* Arrows: each draws at the moment its destination appears */}
      <AnimatedArrow
        from={{ x: pod.x + pod.w, y: cx(pod).y }}
        to={{ x: alloy.x, y: cx(alloy).y }}
        at={30}
        duration={16}
        color={ORANGE}
      />
      <AnimatedArrow
        from={{ x: alloy.x + alloy.w, y: cx(alloy).y - 20 }}
        to={{ x: prom.x, y: cx(prom).y }}
        at={70}
        duration={16}
        color="#4fc3f7"
      />
      <AnimatedArrow
        from={{ x: alloy.x + alloy.w, y: cx(alloy).y }}
        to={{ x: tempo.x, y: cx(tempo).y }}
        at={80}
        duration={16}
        color="#c084fc"
      />
      <AnimatedArrow
        from={{ x: alloy.x + alloy.w, y: cx(alloy).y + 20 }}
        to={{ x: loki.x, y: cx(loki).y }}
        at={90}
        duration={16}
        color="#27c93f"
      />
      <AnimatedArrow
        from={{ x: prom.x + prom.w, y: cx(prom).y }}
        to={{ x: grafana.x, y: cx(grafana).y - 20 }}
        at={130}
        duration={14}
        color="#4fc3f7"
      />
      <AnimatedArrow
        from={{ x: tempo.x + tempo.w, y: cx(tempo).y }}
        to={{ x: grafana.x, y: cx(grafana).y }}
        at={135}
        duration={14}
        color="#c084fc"
      />
      <AnimatedArrow
        from={{ x: loki.x + loki.w, y: cx(loki).y }}
        to={{ x: grafana.x, y: cx(grafana).y + 20 }}
        at={140}
        duration={14}
        color="#27c93f"
      />

      {/* Traveling purple trace dot: Pod → Alloy → Tempo → Grafana */}
      <SignalDot
        waypoints={[
          { x: pod.x + pod.w, y: cx(pod).y },
          { x: cx(alloy).x, y: cx(alloy).y },
          { x: cx(tempo).x, y: cx(tempo).y },
          { x: cx(grafana).x, y: cx(grafana).y },
        ]}
        startFrame={170}
        period={40}
        color="#c084fc"
      />

      {/* Footer callouts */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
        }}
      >
        <SpringIn at={180} fromY={20}>
          <div style={{ color: ORANGE, fontSize: 40, fontFamily: "Inter, sans-serif", fontWeight: 800 }}>
            Alloy fans out · Grafana reads it all
          </div>
        </SpringIn>
      </div>
    </AbsoluteFill>
  );
}
