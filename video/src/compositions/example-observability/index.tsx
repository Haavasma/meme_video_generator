import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import type { BespokeComposition } from "../index";
import { Scene01Title } from "./scenes/Scene01Title";
import { Scene02Problem } from "./scenes/Scene02Problem";
import { Scene03DrakeReject } from "./scenes/Scene03DrakeReject";
import { Scene04DrakeApprove } from "./scenes/Scene04DrakeApprove";
import { Scene05Architecture } from "./scenes/Scene05Architecture";
import { Scene06GrafanaTour } from "./scenes/Scene06GrafanaTour";
import { Scene06bTraceView } from "./scenes/Scene06bTraceView";
import { Scene06Annotation } from "./scenes/Scene06Annotation";
import { Scene07MultiLang } from "./scenes/Scene07MultiLang";
import { Scene08Outro } from "./scenes/Scene08Outro";

const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;

// Durations per scene in frames @ 30fps. Sized to each scene's voiceover
// length + ~10 frame buffer so audio never clips at the Sequence boundary.
// Measured at dramatic @ +0% (see scripts/synth_obs_vo.sh).
const DUR = {
  title: 170, // 5.67s  (VO 5.38s)
  problem: 210, // 7.00s (VO 6.31s)
  drakeReject: 160, // 5.33s (VO 4.75s)
  drakeApprove: 130, // 4.33s (VO 3.67s)
  architecture: 250, // 8.33s (VO 7.56s)
  grafanaTour: 240, // 8.00s (VO 7.27s)
  traceView: 240, // 8.00s (VO pending)
  annotation: 200, // 6.67s (VO 5.90s)
  multiLang: 250, // 8.33s (VO 7.30s)
  outro: 120, // 4.00s  (VO 2.06s)
} as const;

const SCENE_ORDER = [
  "title",
  "problem",
  "drakeReject",
  "drakeApprove",
  "architecture",
  "grafanaTour",
  "traceView",
  "annotation",
  "multiLang",
  "outro",
] as const;

const OFFSETS: Record<(typeof SCENE_ORDER)[number], number> = (() => {
  const out = {} as Record<(typeof SCENE_ORDER)[number], number>;
  let acc = 0;
  for (const name of SCENE_ORDER) {
    out[name] = acc;
    acc += DUR[name];
  }
  return out;
})();

const TOTAL_FRAMES = OFFSETS.outro + DUR.outro;

/**
 * Voiceover mp3 filenames generated out-of-band by `uv run kb tts synthesize`
 * and copied into `video/public/assets/`. Paths are resolved via staticFile().
 * Each scene pulls its own voiceover via a <Audio> alongside the scene component.
 */
export const VO_FILES = {
  title: "obs_vo_title.mp3",
  problem: "obs_vo_problem.mp3",
  drakeReject: "obs_vo_drake_reject.mp3",
  drakeApprove: "obs_vo_drake_approve.mp3",
  architecture: "obs_vo_architecture.mp3",
  grafanaTour: "obs_vo_grafana_tour.mp3",
  traceView: "obs_vo_trace_view.mp3",
  annotation: "obs_vo_annotation.mp3",
  multiLang: "obs_vo_multilang.mp3",
  outro: "obs_vo_outro.mp3",
} as const;

function ObservabilityMemeComponent() {
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a1a" }}>
      <Sequence from={OFFSETS.title} durationInFrames={DUR.title} name="title">
        <Scene01Title />
        <Audio src={staticFile(`assets/${VO_FILES.title}`)} volume={1.0} />
      </Sequence>

      <Sequence from={OFFSETS.problem} durationInFrames={DUR.problem} name="problem">
        <Scene02Problem />
        <Audio src={staticFile(`assets/${VO_FILES.problem}`)} volume={1.0} />
        <Audio src={staticFile("assets/tf_nemesis.mp3")} volume={0.25} />
      </Sequence>

      <Sequence
        from={OFFSETS.drakeReject}
        durationInFrames={DUR.drakeReject}
        name="drake-reject"
      >
        <Scene03DrakeReject />
        <Audio src={staticFile(`assets/${VO_FILES.drakeReject}`)} volume={1.0} />
        <Audio
          src={staticFile("assets/emotional-damage-meme.mp3")}
          volume={0.45}
        />
      </Sequence>

      <Sequence
        from={OFFSETS.drakeApprove}
        durationInFrames={DUR.drakeApprove}
        name="drake-approve"
      >
        <Scene04DrakeApprove />
        <Audio src={staticFile(`assets/${VO_FILES.drakeApprove}`)} volume={1.0} />
        <Audio
          src={staticFile("assets/dun-dun-dun-sound-effect-brass_8nFBccR.mp3")}
          volume={0.35}
        />
      </Sequence>

      <Sequence
        from={OFFSETS.architecture}
        durationInFrames={DUR.architecture}
        name="architecture"
      >
        <Scene05Architecture />
        <Audio src={staticFile(`assets/${VO_FILES.architecture}`)} volume={1.0} />
      </Sequence>

      <Sequence
        from={OFFSETS.grafanaTour}
        durationInFrames={DUR.grafanaTour}
        name="grafana-tour"
      >
        <Scene06GrafanaTour />
        <Audio src={staticFile(`assets/${VO_FILES.grafanaTour}`)} volume={1.0} />
      </Sequence>

      <Sequence
        from={OFFSETS.traceView}
        durationInFrames={DUR.traceView}
        name="trace-view"
      >
        <Scene06bTraceView />
        <Audio src={staticFile(`assets/${VO_FILES.traceView}`)} volume={1.0} />
      </Sequence>

      <Sequence
        from={OFFSETS.annotation}
        durationInFrames={DUR.annotation}
        name="annotation"
      >
        <Scene06Annotation />
        <Audio src={staticFile(`assets/${VO_FILES.annotation}`)} volume={1.0} />
      </Sequence>

      <Sequence
        from={OFFSETS.multiLang}
        durationInFrames={DUR.multiLang}
        name="multi-lang"
      >
        <Scene07MultiLang />
        <Audio src={staticFile(`assets/${VO_FILES.multiLang}`)} volume={1.0} />
        <Audio src={staticFile("assets/cat-laugh-meme-1.mp3")} volume={0.3} />
      </Sequence>

      <Sequence from={OFFSETS.outro} durationInFrames={DUR.outro} name="outro">
        <Scene08Outro />
        <Audio src={staticFile(`assets/${VO_FILES.outro}`)} volume={1.0} />
      </Sequence>
    </AbsoluteFill>
  );
}

export const observabilityMeme: BespokeComposition = {
  id: "ObservabilityMeme",
  component: ObservabilityMemeComponent,
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: WIDTH,
  height: HEIGHT,
};
