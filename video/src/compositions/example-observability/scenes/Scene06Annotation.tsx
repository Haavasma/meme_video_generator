import { AbsoluteFill } from "remotion";
import { CodeBlock, SpringIn } from "../../../lib/primitives";

const ANNOTATION_YAML = `spec:
  template:
    metadata:
      annotations:
        instrumentation.opentelemetry.io/inject-python: "monitoring/default"
    spec:
      containers:
        - name: app
          image: your-image:latest`;

export function Scene06Annotation() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0e14",
        padding: "80px 180px",
        justifyContent: "center",
      }}
    >
      <SpringIn at={0} fromY={-40}>
        <div
          style={{
            textAlign: "center",
            fontFamily: "Impact, sans-serif",
            color: "#f79009",
            fontSize: 80,
            marginBottom: 32,
            letterSpacing: "0.02em",
          }}
        >
          ONE LINE · FULL OBSERVABILITY
        </div>
      </SpringIn>
      <SpringIn at={12} fromScale={0.92} fromY={30}>
        <CodeBlock
          code={ANNOTATION_YAML}
          language="deployment.yml"
          at={20}
          cps={2.2}
          highlight={[5]}
        />
      </SpringIn>
      <div style={{ marginTop: 36, display: "flex", justifyContent: "center", gap: 40 }}>
        <SpringIn at={150} fromY={20}>
          <Badge text="↪ operator injects init container" />
        </SpringIn>
        <SpringIn at={165} fromY={20}>
          <Badge text="↪ sets OTEL_EXPORTER env" />
        </SpringIn>
        <SpringIn at={180} fromY={20}>
          <Badge text="↪ your code stays the same" />
        </SpringIn>
      </div>
    </AbsoluteFill>
  );
}

function Badge({ text }: { text: string }) {
  return (
    <div
      style={{
        padding: "12px 22px",
        borderRadius: 999,
        backgroundColor: "rgba(247, 144, 9, 0.15)",
        border: "2px solid #f79009",
        color: "#fff",
        fontFamily: "Inter, sans-serif",
        fontSize: 26,
        fontWeight: 600,
      }}
    >
      {text}
    </div>
  );
}
