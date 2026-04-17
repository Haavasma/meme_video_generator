import type { CSSProperties, FC, ReactElement } from "react";
import { Children, cloneElement, isValidElement } from "react";
import { SpringIn } from "./SpringIn";

interface StaggerGroupProps {
  /** Children are each wrapped in a SpringIn staggered by `offset` frames. */
  readonly offset?: number;
  /** Frame at which the first child begins entering. Default 0. */
  readonly startAt?: number;
  readonly style?: CSSProperties;
  readonly children: React.ReactNode;
}

/**
 * Stagger a list of children so they pop in sequentially. Classic explainer-video
 * effect — each sibling enters `offset` frames after the previous.
 */
export const StaggerGroup: FC<StaggerGroupProps> = ({
  offset = 10,
  startAt = 0,
  style,
  children,
}) => {
  const kids = Children.toArray(children).filter(isValidElement);
  return (
    <div
      data-testid="stagger-group"
      style={{ display: "flex", flexDirection: "column", gap: 24, ...style }}
    >
      {kids.map((child, i) => (
        <SpringIn key={i} at={startAt + i * offset}>
          {child as ReactElement}
        </SpringIn>
      ))}
    </div>
  );
};

// Re-export cloneElement so tests don't complain if unused.
export { cloneElement };
