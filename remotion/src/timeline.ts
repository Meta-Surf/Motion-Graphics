export type FrameScene = { durationInFrames: number };
export type PositionedScene<T> = { scene: T; from: number };

export const getTimelineLayout = <T extends FrameScene>(
  scenes: readonly T[],
  overlapFrames = 12,
): { items: PositionedScene<T>[]; durationInFrames: number } => {
  if (!Number.isFinite(overlapFrames) || overlapFrames < 0) {
    throw new Error("overlapFrames must be a finite non-negative number.");
  }
  const overlap = Math.floor(overlapFrames);
  let cursor = 0;
  const items = scenes.map((scene, index) => {
    if (!Number.isInteger(scene.durationInFrames) || scene.durationInFrames <= 0) {
      throw new Error("Every scene must have a positive integer durationInFrames.");
    }
    if (index < scenes.length - 1 && scene.durationInFrames <= overlap) {
      throw new Error("Every scene before the last must be longer than the overlap.");
    }
    const item = { scene, from: cursor };
    cursor += scene.durationInFrames - (index < scenes.length - 1 ? overlap : 0);
    return item;
  });
  return { items, durationInFrames: cursor };
};

export const getTimelineDuration = <T extends FrameScene>(
  scenes: readonly T[],
  overlapFrames = 12,
): number => getTimelineLayout(scenes, overlapFrames).durationInFrames;
