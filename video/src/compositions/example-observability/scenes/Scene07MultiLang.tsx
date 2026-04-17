import { AbsoluteFill, Img, staticFile } from "remotion";
import { SpringIn, StaggerGroup } from "../../../lib/primitives";

const LANGS = [
  { annotation: "inject-python", color: "#3776ab" },
  { annotation: "inject-java", color: "#e76f00" },
  { annotation: "inject-nodejs", color: "#8cc84b" },
  { annotation: "inject-dotnet", color: "#512bd4" },
  { annotation: "inject-go", color: "#00add8" },
];

export function Scene07MultiLang() {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0b0b" }}>
      <AbsoluteFill
        style={{
          opacity: 0.45,
          transform: "scale(1.2)",
        }}
      >
        <Img
          src={staticFile("assets/26jxvz.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          backgroundColor: "rgba(0,0,0,0.55)",
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
        }}
      >
        <SpringIn at={0} fromY={-30}>
          <div
            style={{
              fontFamily: "Impact, sans-serif",
              fontSize: 72,
              color: "#f79009",
              marginBottom: 30,
              letterSpacing: "0.02em",
              textAlign: "center",
              WebkitTextStroke: "2px #000",
              paintOrder: "stroke fill",
            }}
          >
            ONE LINE · FIVE LANGUAGES
          </div>
        </SpringIn>
        <StaggerGroup offset={10} startAt={18} style={{ gap: 16 }}>
          {LANGS.map((lang) => (
            <div
              key={lang.annotation}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 24,
                padding: "18px 34px",
                borderRadius: 14,
                backgroundColor: "rgba(20,25,34,0.9)",
                border: `3px solid ${lang.color}`,
                minWidth: 800,
              }}
            >
              <span
                style={{
                  fontFamily: "'Fira Code', Consolas, monospace",
                  fontSize: 40,
                  color: "#fff",
                }}
              >
                <span style={{ color: "#8a94a6" }}>
                  instrumentation.opentelemetry.io/
                </span>
                <span style={{ color: lang.color, fontWeight: 700 }}>
                  {lang.annotation}
                </span>
              </span>
            </div>
          ))}
        </StaggerGroup>
        <SpringIn at={90} fromY={20}>
          <div
            style={{
              marginTop: 40,
              fontFamily: "Inter, sans-serif",
              fontSize: 40,
              color: "#fff",
              fontWeight: 700,
            }}
          >
            same contract · zero refactor
          </div>
        </SpringIn>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
