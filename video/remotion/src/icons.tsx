import React from "react";
import { C, clamp01, easeOut } from "./lib";

type P = { t: number; size?: number };
const svg = (size: number) => ({ width: size, height: size, viewBox: "0 0 100 100", fill: "none" as const, strokeLinecap: "round" as const, strokeLinejoin: "round" as const });

export const BulbIcon: React.FC<P & { cue: number }> = ({ t, cue, size = 150 }) => {
  const on = easeOut((t - cue) / 0.4);
  const flick = 0.85 + 0.15 * Math.sin(t * 14);
  return (
    <svg {...svg(size)} style={{ filter: `drop-shadow(0 0 ${24 * on * flick}px ${C.green})` }}>
      <path d="M50 12 C32 12 22 26 22 40 C22 52 30 58 34 66 L66 66 C70 58 78 52 78 40 C78 26 68 12 50 12 Z" stroke={C.green} strokeWidth={5} fill={`rgba(0,255,160,${0.25 * on})`} />
      <path d="M38 76 H62 M42 86 H58" stroke={C.white} strokeWidth={5} />
      {[[-34, -6], [0, -22], [34, -6]].map(([dx, dy], i) => (
        <path key={i} d={`M${50 + dx * 1.2} ${28 + dy * 0.2} l${dx * 0.3} ${dy * 0.3}`} stroke={C.green} strokeWidth={4} opacity={on} />
      ))}
    </svg>
  );
};

export const UsersIcon: React.FC<P & { cue: number }> = ({ t, cue, size = 150 }) => {
  const p = easeOut((t - cue) / 0.5);
  return (
    <svg {...svg(size)} style={{ opacity: p, filter: `drop-shadow(0 0 ${16 * p}px ${C.green})` }}>
      <circle cx="50" cy="34" r="14" stroke={C.green} strokeWidth={5} />
      <path d="M24 82 C24 62 36 54 50 54 C64 54 76 62 76 82" stroke={C.green} strokeWidth={5} />
      <circle cx="20" cy="42" r="9" stroke={C.white} strokeWidth={4} opacity={0.8} />
      <circle cx="80" cy="42" r="9" stroke={C.white} strokeWidth={4} opacity={0.8} />
    </svg>
  );
};

export const gearPoints = (cx: number, cy: number, r1: number, r2: number, teeth = 8) => {
  const pts: string[] = [];
  for (let k = 0; k < teeth * 4; k++) {
    const a = (Math.PI * 2 * k) / (teeth * 4);
    const r = k % 4 === 0 || k % 4 === 1 ? r1 : r2;
    pts.push(`${cx + Math.cos(a) * r},${cy + Math.sin(a) * r}`);
  }
  return pts.join(" ");
};
export const GearIcon: React.FC<P & { speed?: number; color?: string }> = ({ t, size = 100, speed = 40, color = C.green }) => (
  <svg {...svg(size)}>
    <g transform={`rotate(${t * speed} 50 50)`}>
      <polygon points={gearPoints(50, 50, 40, 30)} stroke={color} strokeWidth={5} fill={`${color}22`} />
      <circle cx="50" cy="50" r="12" stroke={C.white} strokeWidth={5} />
    </g>
  </svg>
);

export const PlanIcon: React.FC<P & { cue: number }> = ({ t, cue, size = 100 }) => {
  const row = (i: number) => easeOut((t - cue - 0.25 - i * 0.35) / 0.3);
  return (
    <svg {...svg(size)}>
      <rect x="22" y="18" width="56" height="70" rx="9" stroke={C.green} strokeWidth={5} />
      <rect x="38" y="10" width="24" height="14" rx="5" stroke={C.white} strokeWidth={4} fill={C.bg} />
      {[0, 1, 2].map((i) => {
        const y = 42 + i * 17, r = row(i);
        return (
          <g key={i}>
            <path d={`M30 ${y} l5 6 l9 -11`} stroke={C.green} strokeWidth={4.5} strokeDasharray={30} strokeDashoffset={30 * (1 - r)} />
            <path d="M52 0 H70" transform={`translate(0 ${y + 1})`} stroke={C.white} strokeWidth={4} opacity={0.35 + 0.65 * r} />
          </g>
        );
      })}
    </svg>
  );
};

export const CodeIcon: React.FC<P & { cue: number }> = ({ t, cue, size = 100 }) => {
  const typed = clamp01((t - cue - 0.2) / 1.2);
  const full = "</>";
  const caret = Math.floor(t * 2.4) % 2 === 0;
  return (
    <div style={{ width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", fontWeight: 800, fontSize: size * 0.42, color: C.green }}>
      {full.slice(0, Math.ceil(typed * full.length))}
      <span style={{ opacity: caret ? 1 : 0, color: C.white }}>▍</span>
    </div>
  );
};

export const BugIcon: React.FC<P & { cue: number; fixCue: number }> = ({ t, cue, fixCue, size = 100 }) => {
  const fixed = easeOut((t - fixCue) / 0.4);
  const col = fixed > 0.5 ? C.green : C.red;
  const wob = t > cue && fixed < 0.5 ? Math.sin(t * 16) * 8 : 0;
  return (
    <svg {...svg(size)}>
      <g transform={`rotate(${wob} 50 55)`} opacity={1 - 0.0 * fixed}>
        <ellipse cx="50" cy="58" rx="18" ry="24" stroke={col} strokeWidth={5} fill={`${col}33`} />
        <circle cx="50" cy="30" r="9" stroke={col} strokeWidth={5} />
        {[44, 56, 68].map((y, i) => (
          <g key={i}>
            <path d={`M33 ${y} L18 ${y + (i - 1) * 6}`} stroke={col} strokeWidth={4} />
            <path d={`M67 ${y} L82 ${y + (i - 1) * 6}`} stroke={col} strokeWidth={4} />
          </g>
        ))}
        <path d="M44 22 L38 12 M56 22 L62 12" stroke={col} strokeWidth={4} />
      </g>
      <path d="M26 54 l16 18 l32 -38" stroke={C.green} strokeWidth={9} strokeDasharray={90} strokeDashoffset={90 * (1 - fixed)} />
    </svg>
  );
};

export const RocketIcon: React.FC<P & { cue: number }> = ({ t, cue, size = 100 }) => {
  const up = easeOut((t - cue) / 1.4);
  const bob = Math.sin(t * 5) * 3;
  const flame = 0.7 + 0.3 * Math.sin(t * 40);
  return (
    <svg {...svg(size)} style={{ overflow: "visible" }}>
      <g transform={`translate(0 ${bob - up * 6}) rotate(${up * 18} 50 50)`}>
        <path d="M50 8 C66 24 68 48 62 66 L38 66 C32 48 34 24 50 8 Z" stroke={C.green} strokeWidth={5} fill={`${C.green}22`} />
        <circle cx="50" cy="38" r="7" stroke={C.white} strokeWidth={4} />
        <path d="M38 56 L24 74 L38 70 Z M62 56 L76 74 L62 70 Z" stroke={C.green} strokeWidth={4} fill={`${C.green}33`} />
        <polygon points="42,68 50,96 58,68" fill={C.green} opacity={0.9} transform={`scale(1 ${flame}) translate(0 ${(1 - flame) * 40})`} />
      </g>
    </svg>
  );
};
