import React from "react";
import { AbsoluteFill, random, useCurrentFrame } from "remotion";
import { C, FPS, H, MONO, SANS, W, easeOut, clamp01 } from "./lib";

/** Absolutely positioned, centred text. */
export const Txt: React.FC<{
  x?: number; y: number; size: number; color?: string; weight?: number; mono?: boolean;
  opacity?: number; scale?: number; rotate?: number; tx?: number; ty?: number; glow?: string;
  children: React.ReactNode; style?: React.CSSProperties;
}> = ({ x = 540, y, size, color = C.white, weight = 800, mono = false, opacity = 1, scale = 1, rotate = 0, tx = 0, ty = 0, glow, children, style }) => (
  <div style={{
    position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) translate(${tx}px,${ty}px) rotate(${rotate}deg) scale(${scale})`,
    fontFamily: mono ? MONO : SANS, fontSize: size, fontWeight: weight, color, whiteSpace: "nowrap", textAlign: "center",
    opacity, textShadow: glow ? `0 0 ${size * 0.35}px ${glow}` : undefined, lineHeight: 1.05, ...style,
  }}>{children}</div>
);

export const Pill: React.FC<{
  x: number; y: number; w: number; h: number; label?: string; color?: string; size?: number; fill?: number;
  opacity?: number; scale?: number; mono?: boolean; textColor?: string; radius?: number;
}> = ({ x, y, w, h, label, color = C.green, size = 40, fill = 0, opacity = 1, scale = 1, mono, textColor, radius = 30 }) => (
  <div style={{
    position: "absolute", left: x - w / 2, top: y - h / 2, width: w, height: h, borderRadius: radius, boxSizing: "border-box",
    border: `4px solid ${color}`, background: fill > 0 ? `rgba(0,255,160,${0.1 + 0.9 * fill})` : "rgba(0,0,0,.55)", opacity,
    transform: `scale(${scale})`, display: "flex", alignItems: "center", justifyContent: "center",
    fontFamily: mono ? MONO : SANS, fontWeight: 800, fontSize: size, color: textColor ?? (fill > 0.5 ? C.bg : C.white),
    boxShadow: `0 0 ${24 + 30 * fill}px ${color}55`,
  }}>{label}</div>
);

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const drift = (frame * 0.4) % 90;
  const pulse = 0.5 + 0.5 * Math.sin(t * 0.9);
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: "hidden" }}>
      <div style={{
        position: "absolute", inset: -90,
        backgroundImage: `linear-gradient(${C.grid} 2px, transparent 2px), linear-gradient(90deg, ${C.grid} 2px, transparent 2px)`,
        backgroundSize: "90px 90px", transform: `translate(${drift * 0.5}px, ${drift}px)`,
      }} />
      <div style={{ position: "absolute", left: -300, top: 200, width: 900, height: 900, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,255,160,.16), transparent 65%)", opacity: 0.5 + 0.5 * pulse, transform: `translateY(${Math.sin(t * 0.5) * 60}px)` }} />
      <div style={{ position: "absolute", right: -350, top: 1000, width: 1000, height: 1000, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,255,160,.12), transparent 65%)", opacity: 1 - 0.5 * pulse, transform: `translateY(${Math.cos(t * 0.6) * 60}px)` }} />
      {Array.from({ length: 36 }).map((_, i) => {
        const x = random(`px${i}`) * W, sp = 18 + random(`ps${i}`) * 60, r = 2 + random(`pr${i}`) * 4;
        const y = H - ((t * sp + random(`py${i}`) * H) % H);
        const o = 0.12 + 0.3 * (0.5 + 0.5 * Math.sin(t * 2 + i));
        return <div key={i} style={{ position: "absolute", left: x + Math.sin(t + i) * 20, top: y, width: r * 2, height: r * 2, borderRadius: "50%", background: C.green, opacity: o }} />;
      })}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.55) 100%)" }} />
    </AbsoluteFill>
  );
};

export const Header: React.FC<{ progress: number }> = ({ progress }) => (
  <>
    <div style={{ position: "absolute", left: 0, top: 0, width: W * progress, height: 12, background: C.green, boxShadow: `0 0 20px ${C.green}` }} />
    <Txt y={70} size={30} color={C.grey} mono weight={700} style={{ letterSpacing: 6 }}>100 DAYS OF DEVOPS</Txt>
  </>
);

export const Scene: React.FC<{ a: number; b: number; fade?: number; children: React.ReactNode }> = ({ a, b, fade = 0.25, children }) => {
  const t = useCurrentFrame() / FPS;
  if (t < a - 0.01 || t > b + 0.01) return null;
  const fin = easeOut((t - a) / fade), fout = 1 - easeOut((t - (b - fade)) / fade);
  return <AbsoluteFill style={{ opacity: Math.min(fin, fout), transform: `translateY(${(1 - fin) * 30}px) scale(${1 + (1 - fout) * 0.02})` }}>{children}</AbsoluteFill>;
};

export const Confetti: React.FC<{ t: number; cue: number; x?: number; y?: number; n?: number }> = ({ t, cue, x = 540, y = 800, n = 46 }) => {
  const dt = t - cue;
  if (dt < 0 || dt > 2.2) return null;
  return <>{Array.from({ length: n }).map((_, i) => {
    const ang = random(`ca${i}${cue}`) * Math.PI * 2, v = 300 + random(`cv${i}${cue}`) * 600;
    const px = x + Math.cos(ang) * v * dt, py = y + Math.sin(ang) * v * dt + 700 * dt * dt;
    const col = [C.green, C.white, "#7dffd0", C.grey][i % 4];
    return <div key={i} style={{ position: "absolute", left: px, top: py, width: 14, height: 22, background: col, opacity: clamp01(1.6 - dt),
      transform: `rotate(${dt * 500 * (random(`cr${i}`) - 0.5)}deg)` }} />;
  })}</>;
};
