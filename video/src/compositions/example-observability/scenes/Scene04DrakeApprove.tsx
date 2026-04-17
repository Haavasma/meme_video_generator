import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { SpringIn } from "../../../lib/primitives";

/** Focus on Drake approve (bottom half) — opposite framing to Scene03. */
export function Scene04DrakeApprove() {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 30], [1.6, 1.45], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const glow = interpolate(frame, [10, 40], [0, 24], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0b0b", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transform: `translateY(-20%) scale(${zoom})`,
          transformOrigin: "center",
        }}
      >
        <Img
          src={staticFile("assets/30b1gx.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 120,
        }}
      >
        <SpringIn at={4} fromY={30} fromScale={0.8}>
          <div
            style={{
              fontFamily: "Impact, sans-serif",
              fontSize: 96,
              color: "#f79009",
              WebkitTextStroke: "4px #000",
              paintOrder: "stroke fill",
              textAlign: "center",
              letterSpacing: "0.01em",
              textShadow: `0 0 ${glow}px #f79009`,
            }}
          >
            one OTel annotation
          </div>
        </SpringIn>
      </AbsoluteFill>
      {/* Green check pulses in */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "flex-start",
          paddingBottom: 260,
          paddingLeft: 200,
          pointerEvents: "none",
        }}
      >
        <SpringIn at={18} fromScale={0.2}>
          <div
            style={{
              fontSize: 200,
              color: "#27c93f",
              fontFamily: "Impact, sans-serif",
              WebkitTextStroke: "6px #000",
              paintOrder: "stroke fill",
              transform: "rotate(-8deg)",
            }}
          >
            ✓
          </div>
        </SpringIn>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
