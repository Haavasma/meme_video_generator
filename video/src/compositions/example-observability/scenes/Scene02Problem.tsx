import { AbsoluteFill } from "remotion";
import {
  ScreenMockup,
  SpringIn,
  StaggerGroup,
  Typewriter,
} from "../../../lib/primitives";

const BG = "#1a0c0c";

const LOG_LINES = [
  "$ kubectl logs pod-abc-7f -n default",
  "2026-04-15T08:00:01Z  info  GET /api/foo 200",
  "2026-04-15T08:00:02Z  info  GET /api/foo 200",
  "2026-04-15T08:00:03Z  warn  slow query 1220ms",
  "2026-04-15T08:00:04Z  error upstream timeout",
  "2026-04-15T08:00:05Z  info  GET /api/foo 200",
  "... (2 hours later) ...",
];

const PROM_LINES = [
  "$ curl prom:9090/api/v1/query ",
  "   ?query=rate(http_500s[5m])",
  "{\"status\":\"success\",",
  " \"data\":{\"result\":[]}}",
  "# …it's empty.",
];

export function Scene02Problem() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: BG,
        padding: "80px 120px",
        justifyContent: "center",
      }}
    >
      <SpringIn at={0} fromY={-20}>
        <h2
          style={{
            margin: 0,
            marginBottom: 40,
            fontFamily: "Impact, sans-serif",
            fontSize: 84,
            color: "#ff6b6b",
            textAlign: "center",
            letterSpacing: "0.02em",
            WebkitTextStroke: "2px #000",
            paintOrder: "stroke fill",
          }}
        >
          DEBUGGING, ACROSS FIVE TOOLS
        </h2>
      </SpringIn>
      <StaggerGroup offset={15} startAt={10} style={{ gap: 30 }}>
        <ScreenMockup kind="terminal" title="~ kubectl logs (one of four terminals)">
          <div style={{ fontSize: 26, lineHeight: 1.5, color: "#9fe0a0" }}>
            {LOG_LINES.map((line, i) => (
              <div key={i}>
                <Typewriter text={line} at={i * 6} cps={3} caret="" />
              </div>
            ))}
          </div>
        </ScreenMockup>
        <div style={{ display: "flex", gap: 30 }}>
          <ScreenMockup kind="terminal" title="prometheus? maybe?" style={{ flex: 1 }}>
            <div style={{ fontSize: 24, lineHeight: 1.5, color: "#cfd4dc" }}>
              {PROM_LINES.map((line, i) => (
                <div key={i}>
                  <Typewriter text={line} at={30 + i * 7} cps={3} caret="" />
                </div>
              ))}
            </div>
          </ScreenMockup>
          <ScreenMockup
            kind="browser"
            title="tempo.ui.local"
            style={{ flex: 1, opacity: 0.65 }}
          >
            <div
              style={{
                padding: 40,
                color: "#777",
                fontFamily: "Inter, sans-serif",
                fontSize: 42,
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 120, opacity: 0.4 }}>?</div>
              <div>TRACES?</div>
              <div style={{ fontSize: 24, opacity: 0.5, marginTop: 10 }}>
                (no datasource configured)
              </div>
            </div>
          </ScreenMockup>
        </div>
      </StaggerGroup>
    </AbsoluteFill>
  );
}
