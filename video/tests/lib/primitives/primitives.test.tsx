import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  AnimatedArrow,
  CodeBlock,
  ScreenMockup,
  SpringIn,
  StaggerGroup,
  Typewriter,
} from "../../../src/lib/primitives";

// Shared Remotion stub — frame=10 so interpolations are mid-flight.
vi.mock("remotion", async () => {
  const actual = await vi.importActual<typeof import("remotion")>("remotion");
  return {
    ...actual,
    useCurrentFrame: () => 10,
    useVideoConfig: () => ({ fps: 30, width: 1920, height: 1080, durationInFrames: 300 }),
    interpolate: (v: number, i: number[], o: number[]) => {
      const [i0, i1] = i as [number, number];
      const [o0, o1] = o as [number, number];
      if (v <= i0) return o0;
      if (v >= i1) return o1;
      return o0 + ((v - i0) / (i1 - i0)) * (o1 - o0);
    },
    spring: ({ frame }: { frame: number }) => {
      // Simple proxy for the real spring — monotonic saturation up to 1.
      if (frame <= 0) return 0;
      return Math.min(1, frame / 20);
    },
  };
});

describe("SpringIn", () => {
  it("renders children", () => {
    render(
      <SpringIn>
        <span>hello</span>
      </SpringIn>,
    );
    expect(screen.getByText("hello")).toBeInTheDocument();
    expect(screen.getByTestId("spring-in")).toBeInTheDocument();
  });
});

describe("Typewriter", () => {
  it("reveals partial text based on cps and frame", () => {
    // cps=1 at frame=10 means 10 chars revealed.
    render(<Typewriter text="hello world!" cps={1} caret="" />);
    const el = screen.getByTestId("typewriter");
    expect(el.textContent?.trim()).toBe("hello worl");
  });

  it("reveals nothing before at-frame", () => {
    render(<Typewriter text="hi there" at={100} cps={1} caret="" />);
    const el = screen.getByTestId("typewriter");
    expect(el.textContent?.trim()).toBe("");
  });
});

describe("StaggerGroup", () => {
  it("wraps each child in a SpringIn", () => {
    render(
      <StaggerGroup>
        <span>one</span>
        <span>two</span>
        <span>three</span>
      </StaggerGroup>,
    );
    expect(screen.getAllByTestId("spring-in").length).toBe(3);
  });
});

describe("AnimatedArrow", () => {
  it("renders an svg with a line element", () => {
    const { container } = render(
      <AnimatedArrow from={{ x: 0, y: 0 }} to={{ x: 100, y: 100 }} at={0} duration={10} />,
    );
    expect(container.querySelector("svg")).not.toBeNull();
    expect(container.querySelector("line")).not.toBeNull();
  });

  it("progresses via strokeDashoffset as frame advances", () => {
    // At frame 10, duration 10, progress should be 1 → dashoffset ~0.
    const { container } = render(
      <AnimatedArrow from={{ x: 0, y: 0 }} to={{ x: 10, y: 0 }} at={0} duration={10} />,
    );
    const line = container.querySelector("line")!;
    const offset = Number(line.getAttribute("stroke-dashoffset"));
    expect(offset).toBeLessThanOrEqual(0.01);
  });
});

describe("CodeBlock", () => {
  it("renders each line of code with line numbers", () => {
    render(
      <CodeBlock
        code={"line one\nline two\nline three"}
        instant
        highlight={[2]}
      />,
    );
    expect(screen.getByTestId("code-block")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("shows language tag when provided", () => {
    render(<CodeBlock code="x" language="yaml" instant />);
    expect(screen.getByText("yaml")).toBeInTheDocument();
  });
});

describe("ScreenMockup", () => {
  it("renders terminal variant with content", () => {
    render(
      <ScreenMockup kind="terminal" title="~/ (bash)">
        <div>$ echo hi</div>
      </ScreenMockup>,
    );
    expect(screen.getByTestId("screen-mockup")).toBeInTheDocument();
    expect(screen.getByText("~/ (bash)")).toBeInTheDocument();
    expect(screen.getByText("$ echo hi")).toBeInTheDocument();
  });

  it("renders browser variant", () => {
    render(
      <ScreenMockup kind="browser" title="grafana.local">
        <div>body</div>
      </ScreenMockup>,
    );
    expect(screen.getByText("grafana.local")).toBeInTheDocument();
    expect(screen.getByText("body")).toBeInTheDocument();
  });
});
