import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { SpringIn } from "../../../lib/primitives";

/**
 * Focus on the top/reject half of the Drake template. We zoom a full-size Img
 * and shift it upward so the top panel fills the frame.
 */
export function Scene03DrakeReject() {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 30], [1.6, 1.45], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0b0b", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transform: `translateY(20%) scale(${zoom})`,
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
          justifyContent: "flex-start",
          alignItems: "center",
          paddingTop: 60,
        }}
      >
        <SpringIn at={4} fromY={-30} fromScale={0.8}>
          <div
            style={{
              fontFamily: "Impact, sans-serif",
              fontSize: 86,
              color: "#fff",
              WebkitTextStroke: "4px #000",
              paintOrder: "stroke fill",
              textAlign: "center",
              maxWidth: 1600,
              lineHeight: 1.05,
              letterSpacing: "0.01em",
            }}
          >
            grepping kubectl logs
            <br />
            for 3 hours
          </div>
        </SpringIn>
      </AbsoluteFill>
      {/* Red X overlay pulses in for comic effect */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-start",
          alignItems: "flex-end",
          paddingTop: 260,
          paddingRight: 200,
          pointerEvents: "none",
        }}
      >
        <SpringIn at={20} fromScale={0.2} fromY={0}>
          <div
            style={{
              fontSize: 200,
              color: "#ff3030",
              fontFamily: "Impact, sans-serif",
              WebkitTextStroke: "6px #000",
              paintOrder: "stroke fill",
              transform: "rotate(-12deg)",
            }}
          >
            ✗
          </div>
        </SpringIn>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
