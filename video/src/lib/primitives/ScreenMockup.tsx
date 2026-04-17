import type { CSSProperties, FC, ReactNode } from "react";

interface ScreenMockupProps {
  readonly kind: "browser" | "terminal";
  readonly title?: string;
  readonly children: ReactNode;
  readonly style?: CSSProperties;
}

const BROWSER_BG = "#1a1a1a";
const TERMINAL_BG = "#0a0e14";
const CHROME_BG = "#2a2f3a";

/**
 * Frame children inside a mock browser or terminal window — for Grafana tour
 * scenes or "terminal running curl" beats. Pure CSS; no real window.
 */
export const ScreenMockup: FC<ScreenMockupProps> = ({
  kind,
  title,
  children,
  style,
}) => {
  const bg = kind === "terminal" ? TERMINAL_BG : BROWSER_BG;
  return (
    <div
      data-testid="screen-mockup"
      style={{
        backgroundColor: bg,
        borderRadius: 18,
        overflow: "hidden",
        boxShadow: "0 40px 120px rgba(0,0,0,0.6)",
        border: "1px solid rgba(255,255,255,0.08)",
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      <div
        style={{
          backgroundColor: CHROME_BG,
          padding: "12px 18px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          color: "#cfd4dc",
          fontFamily: "'SF Pro Display', Inter, sans-serif",
          fontSize: 20,
        }}
      >
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#ff5f56" }} />
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#ffbd2e" }} />
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#27c93f" }} />
        {title ? (
          <div
            style={{
              flex: 1,
              textAlign: "center",
              marginRight: 42, // offset the left traffic lights
              fontFamily:
                kind === "terminal"
                  ? "'Fira Code', 'JetBrains Mono', Consolas, monospace"
                  : "Inter, sans-serif",
              opacity: 0.9,
            }}
          >
            {title}
          </div>
        ) : null}
      </div>
      <div
        style={{
          flex: 1,
          position: "relative",
          padding: kind === "terminal" ? 28 : 0,
          overflow: "hidden",
        }}
      >
        {children}
      </div>
    </div>
  );
};
