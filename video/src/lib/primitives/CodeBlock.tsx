import type { CSSProperties, FC } from "react";
import { Typewriter } from "./Typewriter";

interface CodeBlockProps {
  readonly code: string;
  /** When to start typing. */
  readonly at?: number;
  readonly language?: string; // displayed as a tag; no real highlighting
  readonly cps?: number;
  readonly highlight?: number[]; // 1-indexed line numbers to glow
  readonly style?: CSSProperties;
  /** Reveal all code instantly (no typewriter) if true. */
  readonly instant?: boolean;
}

const BG = "#0b0f14";
const HEADER_BG = "#1b2230";
const FG = "#e5e9f0";
const LINE_GLOW = "rgba(247, 144, 9, 0.18)";
const LINE_BORDER = "#f79009";

/**
 * IDE-ish code block with optional typewriter reveal and glowing highlight lines.
 * Not a real syntax highlighter — meme aesthetic over perfect token coloring.
 */
export const CodeBlock: FC<CodeBlockProps> = ({
  code,
  at = 0,
  language,
  cps = 1.2,
  highlight = [],
  instant = false,
  style,
}) => {
  const highlightSet = new Set(highlight);
  return (
    <div
      data-testid="code-block"
      style={{
        backgroundColor: BG,
        color: FG,
        borderRadius: 16,
        overflow: "hidden",
        boxShadow: "0 30px 80px rgba(0,0,0,0.6)",
        fontFamily: "'Fira Code', 'JetBrains Mono', Consolas, monospace",
        fontSize: 32,
        lineHeight: 1.45,
        ...style,
      }}
    >
      <div
        style={{
          backgroundColor: HEADER_BG,
          padding: "10px 20px",
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#ff5f56" }} />
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#ffbd2e" }} />
        <span style={{ width: 14, height: 14, borderRadius: 14, background: "#27c93f" }} />
        {language ? (
          <span style={{ marginLeft: 16, color: "#8a94a6", fontSize: 22 }}>
            {language}
          </span>
        ) : null}
      </div>
      <div style={{ padding: "24px 32px" }}>
        {code.split("\n").map((line, idx) => {
          const lineNo = idx + 1;
          const isHighlighted = highlightSet.has(lineNo);
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 24,
                padding: "2px 8px",
                borderLeft: isHighlighted
                  ? `4px solid ${LINE_BORDER}`
                  : "4px solid transparent",
                backgroundColor: isHighlighted ? LINE_GLOW : "transparent",
              }}
            >
              <span
                style={{
                  width: 30,
                  color: "#555f73",
                  textAlign: "right",
                  userSelect: "none",
                }}
              >
                {lineNo}
              </span>
              <span style={{ flex: 1 }}>
                {instant ? (
                  line || " "
                ) : (
                  <Typewriter text={line || " "} at={at + idx * 8} cps={cps} caret="" />
                )}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
