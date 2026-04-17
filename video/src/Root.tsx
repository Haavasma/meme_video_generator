import { Composition } from "remotion";
import { COMPOSITIONS } from "./compositions";

export function RemotionRoot() {
  return (
    <>
      {COMPOSITIONS.map((c) => (
        <Composition
          key={c.id}
          id={c.id}
          component={c.component}
          durationInFrames={c.durationInFrames}
          fps={c.fps}
          width={c.width}
          height={c.height}
        />
      ))}
    </>
  );
}
