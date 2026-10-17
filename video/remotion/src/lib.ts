import sync from "./day6-sync.json";
import { interpolate, spring } from "remotion";

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const DURATION_SEC = 64.208938;

export const C = {
  bg: "#0a0a0a", grid: "#141414", green: "#00ffa0", white: "#ffffff", grey: "#6e6e6e",
  dim: "#2d2d2d", red: "#ff5f5f", text2: "#b8b8b8",
};
export const SANS = '"DejaVu Sans", "Noto Sans", Arial, sans-serif';
export const MONO = '"DejaVu Sans Mono", "Noto Sans Mono", monospace';

export type Phrase = { a: number; b: number; text: string; times: number[] };
export const PH: Phrase[] = sync as Phrase[];

const clean = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
/** Start time (s) of `word` in phrase i (default: first word), from forced alignment of the script to the voiceover. */
export function T(i: number, word?: string, occ = 0): number {
  const p = PH[i];
  if (word === undefined) return p.times[0];
  let n = 0;
  const toks = p.text.split(/\s+/);
  for (let k = 0; k < toks.length; k++) {
    if (clean(toks[k]).startsWith(clean(word))) {
      if (n === occ) return p.times[k];
      n++;
    }
  }
  throw new Error(`cue not found: ${i} ${word}`);
}

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const easeOut = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
/** 0→1 over `dur` seconds starting at `cue` (eased). */
export const pop = (t: number, cue: number, dur = 0.45) => easeOut((t - cue) / dur);
/** Springy 0→~1 (overshoots) starting at `cue`. */
export const bounce = (frame: number, cue: number, damping = 11, stiffness = 140) =>
  spring({ frame: frame - cue * FPS, fps: FPS, config: { damping, stiffness, mass: 0.7 } });
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const mixHex = (a: string, b: string, t: number) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return "#" + pa.map((v, i) => Math.round(lerp(v, pb[i], t)).toString(16).padStart(2, "0")).join("");
};
export { interpolate };

/** Caption chunks: <= ~50 chars, broken after punctuation when the line is already long enough. */
export type Chunk = { start: number; end: number; words: { w: string; t: number }[] };
export function captionChunks(): Chunk[] {
  const out: Chunk[] = [];
  PH.forEach((p, pi) => {
    const toks = p.text.split(/\s+/);
    const groups: number[][] = [];
    let cur: number[] = [];
    toks.forEach((tk, k) => {
      cur.push(k);
      const n = cur.map((j) => toks[j]).join(" ").length;
      if (k + 1 < toks.length && (n + toks[k + 1].length > 50 || (/[,?!…]$/.test(tk) && n >= 22))) { groups.push(cur); cur = []; }
    });
    groups.push(cur);
    groups.forEach((g, gi) => {
      const first = g[0], last = g[g.length - 1];
      const start = p.times[first] - 0.04;
      let end = last + 1 < toks.length ? p.times[last + 1] : p.b + 0.15;
      if (last + 1 >= toks.length && pi + 1 < PH.length && PH[pi + 1].a - p.b < 0.5) end = PH[pi + 1].times[0];
      out.push({ start, end, words: g.map((j) => ({ w: toks[j], t: p.times[j] })) });
    });
  });
  return out;
}
