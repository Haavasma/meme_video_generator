/**
 * Registry of bespoke per-video compositions.
 *
 * To add a new video: create a folder under `src/compositions/<slug>/`
 * with an `index.tsx` exporting a `BespokeComposition`, then append
 * an entry to `COMPOSITIONS` below.
 */
import type { ComponentType } from "react";

export interface BespokeComposition {
  readonly id: string;
  readonly component: ComponentType<Record<string, never>>;
  readonly durationInFrames: number;
  readonly fps: number;
  readonly width: number;
  readonly height: number;
}

export const COMPOSITIONS: readonly BespokeComposition[] = [];
