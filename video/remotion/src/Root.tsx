import React from "react";
import { Composition } from "remotion";
import { Day6 } from "./Day6";
import { DURATION_SEC, FPS, H, W } from "./lib";

export const Root: React.FC = () => (
  <Composition
    id="Day6"
    component={Day6}
    durationInFrames={Math.ceil(DURATION_SEC * FPS)}
    fps={FPS}
    width={W}
    height={H}
  />
);
